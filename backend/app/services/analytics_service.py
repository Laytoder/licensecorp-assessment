from sqlalchemy.orm import Session
from app.repositories.analytics_repository import AnalyticsRepository
from app.core.constants import AnalyticsCounters
from app.core.redis_utils import get_counter as redis_get_counter
from app.core.redis_utils import set_counter as redis_set_counter
from app.core.redis_utils import increment_counter as redis_increment_counter
import datetime

class AnalyticsService:
    """
    Service for analytics operations, coordinating between Redis cache and database.
    """
    
    @staticmethod
    def get_counter(db: Session, counter: AnalyticsCounters) -> int:
        """
        Get a counter value, preferring Redis cache but falling back to database.
        Will repopulate cache if value is fetched from database.
        """
        # Try to get from Redis first
        redis_value = redis_get_counter(counter)
        
        if redis_value is not None:
            # Return cached value if it exists
            return redis_value
            
        # If not in cache, get from database
        print(f"[{datetime.datetime.now()}] Counter {counter.value} not found in Redis, fetching from database")
        db_value = AnalyticsRepository.get_counter(db, counter.value)
        
        # Repopulate cache with database value
        redis_set_counter(counter, db_value)
        print(f"[{datetime.datetime.now()}] Repopulated Redis cache for counter {counter.value} with value {db_value}")
        
        return db_value
    
    @staticmethod
    def get_all_counters(db: Session) -> dict:
        """
        Get all counter values, repopulating cache for any missing values.
        """
        result = {}
        
        # For each counter in the enum
        for counter in AnalyticsCounters:
            result[counter.value] = AnalyticsService.get_counter(db, counter)
            
        return result
    
    @staticmethod
    def increment_counter(db: Session, counter: AnalyticsCounters) -> int:
        """
        Increment counter by 1 in both Redis and database, ensuring they stay in sync.
        Returns new counter value.
        """
        # Increment in Redis and publish update
        redis_value = redis_increment_counter(counter)
        
        # Increment in database
        db_value = AnalyticsRepository.increment_counter(db, counter.value)
        print(f"[{datetime.datetime.now()}] Incremented counter {counter.value} in database to {db_value}")
        
        # If Redis and DB values are out of sync, use DB value as source of truth
        if redis_value != db_value:
            print(f"[{datetime.datetime.now()}] Redis counter {counter.value} out of sync with database. Redis: {redis_value}, DB: {db_value}. Fixing...")
            redis_set_counter(counter, db_value)
            redis_value = db_value
            
        return db_value
    
    @staticmethod
    def ensure_counters_synced(db: Session):
        """
        Ensure all counters are synced between Redis and database.
        Called during startup to make sure Redis values are correct after restart.
        """
        print(f"[{datetime.datetime.now()}] Syncing analytics counters between Redis and database...")
        
        # Ensure all counters exist in database
        AnalyticsRepository.ensure_counters_exist(db)
        
        # Get all counters from database (source of truth)
        db_counters = AnalyticsRepository.get_all_counters(db)
        
        # Update Redis cache for all counters
        for counter_name, counter_value in db_counters.items():
            # Find the corresponding enum
            for counter_enum in AnalyticsCounters:
                if counter_enum.value == counter_name:
                    redis_set_counter(counter_enum, counter_value)
                    break
        
        print(f"[{datetime.datetime.now()}] Analytics counters synced. Values: {db_counters}") 