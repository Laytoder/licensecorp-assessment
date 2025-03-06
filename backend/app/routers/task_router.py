from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from typing import List
from app.core.database import get_db
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskOut
from app.services.task_service import TaskService
from app.dependencies import rate_limit
import redis
from app.core.config import settings
import json
import datetime

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(rate_limit)]
)

# pub redis client
pubsub_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def serialize_task(task, event_type: str):
    task_dict = task.dict()
    task_dict["event"] = event_type
    return json.dumps(task_dict, default=lambda o: o.isoformat() if isinstance(o, (datetime.datetime, datetime.date)) else o)

@router.post("/", response_model=TaskOut)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    new_task = TaskService.create_task(db, task_data)
    pubsub_redis.publish(settings.TASKS_CHANNEL, serialize_task(new_task, "created")) 
    return new_task

@router.get("/", response_model=List[TaskOut])
def get_all_tasks(db: Session = Depends(get_db)):
    return TaskService.get_all_tasks(db)

@router.get("/{task_id}", response_model=TaskOut)
def get_task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, updates: TaskUpdate, db: Session = Depends(get_db)):
    try:
        updated_task = TaskService.update_task(db, task_id, updates)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        pubsub_redis.publish(settings.TASKS_CHANNEL, serialize_task(updated_task, "updated"))
        return updated_task
    except StaleDataError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Update conflict: the task was modified by another request. Please refresh and try again."
        )

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        success = TaskService.delete_task(db, task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        pubsub_redis.publish(settings.TASKS_CHANNEL, json.dumps({"id": task_id, "event": "deleted"}))
        return {"detail": "Task deleted successfully"}
    except StaleDataError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Delete conflict: the task was modified by another request. Please refresh and try again."
        )