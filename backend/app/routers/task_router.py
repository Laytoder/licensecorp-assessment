from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from typing import List, Dict
from app.core.database import get_db
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskOut
from app.services.task_service import TaskService
from app.dependencies import rate_limit
import redis
from app.core.config import settings
import json
import datetime
import random
import time
import asyncio
from app.repositories.task_repository import TaskRepository

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

# Function to generate tasks in batches
async def _generate_tasks_in_background(total: int, batch_size: int):
    """Generate tasks in batches to avoid overloading the database"""
    db = next(get_db())
    
    # Sample titles and descriptions for variety
    titles = [
        "Complete project", "Review code", "Write documentation", 
        "Test functionality", "Fix bug", "Implement feature", 
        "Attend meeting", "Send email", "Schedule call",
        "Research solution", "Update database", "Deploy changes"
    ]
    
    descriptions = [
        "This needs to be done ASAP", "Low priority task", "Medium priority task",
        "High priority task", "Follow up required", "No rush on this one",
        "Part of the Q2 project", "Needs review from team", "Important client request",
        "Internal improvement", "Technical debt", "Long-term project"
    ]
    
    # Track progress
    created_count = 0
    start_time = time.time()
    last_log_time = start_time
    
    # Generate tasks in batches
    for batch_num in range(0, total, batch_size):
        batch_tasks = []
        
        # Only create as many as needed to reach the total
        current_batch_size = min(batch_size, total - created_count)
        
        for i in range(current_batch_size):
            # Create task with random title and description
            task_data = TaskCreate(
                title=f"{random.choice(titles)} {created_count + i + 1}",
                description=random.choice(descriptions),
                completed=random.random() > 0.7,  # 30% chance of being completed
                expiry_date=None if random.random() > 0.2 else (
                    datetime.datetime.utcnow() + 
                    datetime.timedelta(days=random.randint(1, 30))
                )  # 20% chance of having expiry date
            )
            
            # Directly use repository to bypass Redis for bulk operations
            task = TaskRepository.create_task(db, task_data)
            batch_tasks.append(task)
            
        # Commit the batch
        db.commit()
        
        # Update counter
        created_count += len(batch_tasks)
        
        # Log progress every 10 seconds or at the end
        current_time = time.time()
        if current_time - last_log_time >= 10 or created_count >= total:
            elapsed = current_time - start_time
            tasks_per_second = created_count / elapsed if elapsed > 0 else 0
            print(f"Created {created_count}/{total} tasks ({(created_count/total)*100:.2f}%) "
                  f"in {elapsed:.2f}s ({tasks_per_second:.2f} tasks/sec)")
            last_log_time = current_time
        
        # Small pause to avoid overloading the system
        if batch_num + batch_size < total:
            await asyncio.sleep(0.01)
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Task generation complete! Created {created_count} tasks in {total_time:.2f} seconds "
          f"({created_count/total_time:.2f} tasks/sec)")

@router.post("/populate/{count}")
async def populate_tasks(count: int, background_tasks: BackgroundTasks):
    """
    Populate the database with a specified number of tasks.
    
    - Use with caution! This will generate a large number of tasks.
    - Tasks are created in batches to avoid overloading the database.
    - Default batch size is 1000 tasks at a time.
    
    Example: POST /tasks/populate/1000000 to create 1 million tasks
    """
    if count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Count must be greater than 0"
        )
    
    if count > 10000000:  # 10 million limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create more than 10 million tasks at once"
        )
    
    # Determine batch size based on count
    batch_size = min(1000, count)
    
    # Start the task generation in the background
    background_tasks.add_task(_generate_tasks_in_background, count, batch_size)
    
    return {
        "message": f"Started generating {count} tasks in the background",
        "details": "This process will continue in the background and may take several minutes to complete. Check server logs for progress.",
        "estimated_time": f"~{count/50000:.2f} minutes (estimated)"
    }