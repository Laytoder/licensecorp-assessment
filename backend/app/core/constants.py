from enum import Enum

class AnalyticsCounters(Enum):
    TASKS_CREATED = "tasks_created"
    TASKS_UPDATED = "tasks_updated"
    TASKS_DELETED = "tasks_deleted"

PAGE_SIZE = 20
MAX_TASK_TTL = 3600
MAX_REDIS_MEMORY = "512mb"