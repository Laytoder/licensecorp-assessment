from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base
import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    expiry_date = Column(DateTime, nullable=True, index=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    # version control to avoid race conditions
    __mapper_args__ = {
        "version_id_col": version
    }