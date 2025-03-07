from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import rate_limit
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"], dependencies=[Depends(rate_limit)])

@router.get("/")
def get_analytics(db: Session = Depends(get_db)):
    """
    Get all analytics counters.
    Will automatically repopulate Redis cache with database values if needed.
    """
    return AnalyticsService.get_all_counters(db)