import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class LedgerEntry(Base):
    """
    Structured financial ledger record normalized from invoice or receipt data.
    Directly queryable for analytics, category aggregations, and safe natural language searches.
    """
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)

    vendor_name = Column(String(255), index=True, default="Unknown Vendor")
    vendor_gstin = Column(String(32), index=True, nullable=True)
    vendor_email = Column(String(255), nullable=True)
    vendor_phone = Column(String(64), nullable=True)

    invoice_or_receipt_number = Column(String(128), index=True, nullable=True)
    issue_date = Column(String(32), nullable=True)  # Format: YYYY-MM-DD
    due_date = Column(String(32), nullable=True)    # Format: YYYY-MM-DD

    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")

    # Expense categorization
    expense_category = Column(String(64), default="General", index=True)

    # Cashflow & action priorities
    payment_priority = Column(String(16), default="MEDIUM") # URGENT, MEDIUM, LOW
    payment_status = Column(String(16), default="PENDING")   # PENDING, PAID, OVERDUE

    line_items_json = Column(Text, default="[]")  # Detailed line items list

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship
    document = relationship("Document", back_populates="ledger_entry")
