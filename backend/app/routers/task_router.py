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

def create_pub_msg(task, event_type: str):
    final_dict = {}
    final_dict["event"] = event_type
    final_dict["task"] = task.dict()
    return json.dumps(final_dict, default=lambda o: o.isoformat() if isinstance(o, (datetime.datetime, datetime.date)) else o)

@router.post("/", response_model=TaskOut)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    new_task = TaskService.create_task(db, task_data)
    pubsub_redis.publish(settings.TASKS_CHANNEL, create_pub_msg(new_task, "created")) 
    return new_task

@router.get("/{page}", response_model=List[TaskOut])
def get_tasks_by_page(page: int, db: Session = Depends(get_db)):
    print(f"Getting tasks for page {page}")
    return TaskService.get_tasks_page(db, page)

@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, updates: TaskUpdate, db: Session = Depends(get_db)):
    try:
        updated_task = TaskService.update_task(db, task_id, updates)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        pubsub_redis.publish(settings.TASKS_CHANNEL, create_pub_msg(updated_task, "updated"))
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