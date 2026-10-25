from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class CategorySpend(BaseModel):
    category: str
    amount: float
    percentage: float
    count: int


class MonthlyTrend(BaseModel):
    month: str  # e.g., "May 2026", "Jun 2026"
    spend: float
    documents_count: int


class VendorStat(BaseModel):
    vendor_name: str
    total_spend: float
    invoice_count: int
    latest_date: Optional[str] = None


class AnalyticsSummary(BaseModel):
    total_spend: float
    total_documents: int
    invoices_count: int
    receipts_count: int
    business_cards_count: int
    anomalies_caught: int
    documents_notarized: int
    hours_saved: float
    scans_used: int
    scans_limit: int

    category_breakdown: List[CategorySpend]
    monthly_trend: List[MonthlyTrend]
    vendor_leaderboard: List[VendorStat]
