from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.ledger import AnalyticsSummary
from ..services.ledger_service import LedgerService

router = APIRouter(prefix="/analytics", tags=["Financial Analytics & Insights"])


@router.get("/summary", response_model=AnalyticsSummary, summary="Dashboard Stat Metrics and Chart Data")
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Returns aggregated figures for hero metrics and charts:
    - Total spend, documents processed, hours saved
    - Donut chart: spend by category
    - Area chart: monthly trend
    - Bar chart: top vendor leaderboard
    """
    return LedgerService.get_analytics_summary(db)
