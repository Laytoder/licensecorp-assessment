from fastapi import APIRouter, Depends
from app.core.redis_utils import get_counter
from app.dependencies import rate_limit
from app.core.constants import AnalyticsCounters

router = APIRouter(prefix="/analytics", tags=["Analytics"], dependencies=[Depends(rate_limit)])

@router.get("/")
def get_analytics():
    return {
        "tasks_created": get_counter(AnalyticsCounters.TASKS_CREATED),
        "tasks_updated": get_counter(AnalyticsCounters.TASKS_UPDATED),
        "tasks_deleted": get_counter(AnalyticsCounters.TASKS_DELETED)
    }