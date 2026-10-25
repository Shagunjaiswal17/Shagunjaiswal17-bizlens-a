from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    message: str = Field(..., description="Natural language question from user, e.g. 'How much did we spend on IT last month?'")
    history: List[Dict[str, str]] = Field(default_factory=list, description="Recent conversation turns [{'role': 'user', 'content': '...'}]")


class SafeQueryFilter(BaseModel):
    """
    Validated filter parameter schema produced by Gemini.
    Guarantees no raw SQL injection can ever reach the database layer.
    """
    query_type: Literal["SPEND_SUM", "CATEGORY_CHECK", "VENDOR_LOOKUP", "DOCUMENT_SEARCH", "GENERAL_ADVICE"] = "SPEND_SUM"
    vendor_pattern: Optional[str] = Field(default=None, description="Fuzzy or partial vendor name filter")
    category: Optional[str] = Field(default=None, description="Exact or normalized expense category")
    date_from: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")
    min_amount: Optional[float] = Field(default=None, description="Minimum transaction value")
    max_amount: Optional[float] = Field(default=None, description="Maximum transaction value")
    payment_status: Optional[str] = Field(default=None, description="PENDING, PAID, or OVERDUE")
    aggregation: Literal["SUM", "COUNT", "AVERAGE", "LIST"] = "SUM"


class DocumentCitation(BaseModel):
    document_id: int
    vendor_name: str
    amount: float
    date: Optional[str] = None
    document_type: str
    tx_hash: Optional[str] = None


class ChatQueryResponse(BaseModel):
    answer: str
    filter_applied: Optional[SafeQueryFilter] = None
    record_count: int = 0
    calculated_total: Optional[float] = None
    citations: List[DocumentCitation] = []
