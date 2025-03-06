import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import StaleDataError
from typing import Optional, List
from app.models.task_model import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate
from datetime import datetime
from sqlalchemy import or_

class TaskRepository:
    @staticmethod
    def create_task(db: Session, task_data: TaskCreate) -> Task:
        new_task = Task(**task_data.dict())
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_all_tasks(db: Session) -> List[Task]:
        return db.query(Task).filter(
            or_(Task.expiry_date == None, Task.expiry_date > datetime.utcnow())
        ).order_by(Task.created_at.asc()).all()

    @staticmethod
    def update_task(db: Session, task: Task, updates: TaskUpdate) -> Task:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                for field, value in updates.dict(exclude_unset=True).items():
                    setattr(task, field, value)
                db.commit()
                db.refresh(task)
                return task
            except StaleDataError as e:
                db.rollback()
                raise e
            except OperationalError as e:
                db.rollback()
                if "deadlock detected" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(0.1)
                        continue
                    else:
                        raise e
                else:
                    raise e

    @staticmethod
    def delete_task(db: Session, task: Task) -> None:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                db.delete(task)
                db.commit()
                return
            except StaleDataError as e:
                db.rollback()
                raise e
            except OperationalError as e:
                db.rollback()
                if "deadlock detected" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(0.1)
                        continue
                    else:
                        raise e
                else:
                    raise e