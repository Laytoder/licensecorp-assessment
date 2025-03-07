from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class AnalyticsCounter(Base):
    """
    Database model for persisting analytics counters.
    """
    __tablename__ = "analytics_counters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    value = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AnalyticsCounter(name='{self.name}', value={self.value})>" 