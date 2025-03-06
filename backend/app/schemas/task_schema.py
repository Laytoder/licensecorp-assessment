from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    expiry_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    expiry_date: Optional[datetime] = None

class TaskOut(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True