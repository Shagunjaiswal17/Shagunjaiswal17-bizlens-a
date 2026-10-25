import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class Document(Base):
    """
    Core document model representing an uploaded and processed physical or digital record.
    Tracks file-level hash, AI-extracted JSON hash, validation results, and Web3 notarization status.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_sha256 = Column(String(64), index=True, nullable=False)  # Cryptographic proof of file
    data_sha256 = Column(String(64), index=True, nullable=True)   # Canonical SHA-256 of extracted JSON

    document_type = Column(String(32), default="INVOICE")  # INVOICE, RECEIPT, BUSINESS_CARD
    raw_gemini_json = Column(Text, nullable=True)          # Enforced JSON string
    overall_confidence = Column(Float, default=1.0)        # Aggregate confidence score (0.0 to 1.0)

    # Verification & Integrity status
    validation_status = Column(String(32), default="VALID") # VALID, WARNING, INVALID
    validation_notes = Column(Text, default="[]")           # JSON list of validation warnings/flags

    # Fraud & Anomaly detection
    fraud_status = Column(String(32), default="CLEAN")      # CLEAN, SUSPICIOUS, DUPLICATE
    fraud_reasons = Column(Text, default="[]")              # JSON list of flagged anomaly reasons

    # Web3 Proof-of-Document Notarization
    on_chain_status = Column(String(32), default="NOT_NOTARIZED") # NOT_NOTARIZED, PENDING, NOTARIZED
    blockchain_tx_hash = Column(String(66), nullable=True, index=True)
    blockchain_block_number = Column(Integer, nullable=True)
    ipfs_cid = Column(String(128), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    notarized_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="documents")
    ledger_entry = relationship("LedgerEntry", back_populates="document", uselist=False, cascade="all, delete-orphan")
