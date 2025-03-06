from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskOut
from app.models.task_model import Task
from app.core import redis_utils
from app.core.constants import AnalyticsCounters

class TaskService:
    @staticmethod
    def create_task(db: Session, task_data: TaskCreate) -> TaskOut:
        new_task = TaskRepository.create_task(db, task_data)
        out_data = TaskOut.from_orm(new_task).dict()
        redis_utils.cache_set_task(new_task.id, out_data, new_task.expiry_date)
        redis_utils.increment_counter(AnalyticsCounters.TASKS_CREATED)
        return TaskOut.from_orm(new_task)
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Optional[TaskOut]:
        cached = redis_utils.cache_get_task(task_id)
        if cached:
            return TaskOut(**cached)
        task = TaskRepository.get_task_by_id(db, task_id)
        if not task:
            return None
        out_data = TaskOut.from_orm(task).dict()
        redis_utils.cache_set_task(task.id, out_data, task.expiry_date)
        return TaskOut(**out_data)

    @staticmethod
    def get_all_tasks(db: Session) -> List[TaskOut]:
        cached_list = redis_utils.cache_get_all_tasks()
        if cached_list:
            return [TaskOut(**task_dict) for task_dict in cached_list]
        tasks = TaskRepository.get_all_tasks(db)
        out_list = [TaskOut.from_orm(t).dict() for t in tasks]
        for t, item in zip(tasks, out_list):
            redis_utils.cache_set_task(item["id"], item, t.expiry_date)
        return [TaskOut(**item) for item in out_list]
    
    @staticmethod
    def get_tasks_page(db: Session, page: int, page_size: int) -> List[TaskOut]:
        ordered_ids, cached_tasks, missing_ids = redis_utils.cache_get_tasks_page_with_missing(page, page_size)

        if missing_ids:
            missing_tasks = TaskRepository.get_tasks_by_ids(db, missing_ids)
            for task in missing_tasks:
                out_data = TaskOut.from_orm(task).dict()
                redis_utils.cache_set_task(task.id, out_data, task.expiry_date)
                cached_tasks[task.id] = out_data

        tasks = []
        for task_id in ordered_ids:
            tasks.append(TaskOut(**cached_tasks[task_id]))
        return tasks

    @staticmethod
    def update_task(db: Session, task_id: int, updates: TaskUpdate) -> Optional[TaskOut]:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        updated = TaskRepository.update_task(db, task, updates)
        out_data = TaskOut.from_orm(updated).dict()
        redis_utils.cache_set_task(updated.id, out_data, updated.expiry_date)
        redis_utils.increment_counter(AnalyticsCounters.TASKS_UPDATED)
        return TaskOut(**out_data)

    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        TaskRepository.delete_task(db, task)
        redis_utils.cache_delete_task(task_id)
        redis_utils.increment_counter(AnalyticsCounters.TASKS_DELETED)
        return True
