from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.analytics_model import AnalyticsCounter
from app.core.constants import AnalyticsCounters

class AnalyticsRepository:
    """
    Repository for handling analytics counter database operations.
    """
    
    @staticmethod
    def get_counter(db: Session, counter_name: str) -> int:
        """
        Get a counter value from the database.
        Returns 0 if the counter doesn't exist.
        """
        counter = db.query(AnalyticsCounter).filter(AnalyticsCounter.name == counter_name).first()
        return counter.value if counter else 0
        
    @staticmethod
    def get_all_counters(db: Session) -> dict:
        """
        Get all counters from the database.
        Returns a dictionary mapping counter names to values.
        """
        counters = db.query(AnalyticsCounter).all()
        return {counter.name: counter.value for counter in counters}
        
    @staticmethod
    def increment_counter(db: Session, counter_name: str) -> int:
        """
        Increment a counter by 1 in the database.
        Creates the counter if it doesn't exist.
        Returns the new value.
        """
        try:
            counter = db.query(AnalyticsCounter).filter(AnalyticsCounter.name == counter_name).first()
            
            if not counter:
                # Create a new counter if it doesn't exist
                counter = AnalyticsCounter(name=counter_name, value=1)
                db.add(counter)
            else:
                # Increment existing counter
                counter.value += 1
                
            db.commit()
            db.refresh(counter)
            return counter.value
        except SQLAlchemyError:
            db.rollback()
            raise
            
    @staticmethod
    def set_counter(db: Session, counter_name: str, value: int) -> int:
        """
        Set a counter to a specific value.
        Creates the counter if it doesn't exist.
        Returns the new value.
        """
        try:
            counter = db.query(AnalyticsCounter).filter(AnalyticsCounter.name == counter_name).first()
            
            if not counter:
                # Create a new counter if it doesn't exist
                counter = AnalyticsCounter(name=counter_name, value=value)
                db.add(counter)
            else:
                # Set value of existing counter
                counter.value = value
                
            db.commit()
            db.refresh(counter)
            return counter.value
        except SQLAlchemyError:
            db.rollback()
            raise
    
    @staticmethod
    def ensure_counters_exist(db: Session):
        """
        Ensure all counters defined in AnalyticsCounters enum exist in the database.
        """
        for counter in AnalyticsCounters:
            existing = db.query(AnalyticsCounter).filter(AnalyticsCounter.name == counter.value).first()
            if not existing:
                db.add(AnalyticsCounter(name=counter.value, value=0))
        
        db.commit() 