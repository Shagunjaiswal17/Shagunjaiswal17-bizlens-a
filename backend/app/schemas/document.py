from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .extraction import UnifiedDocumentExtraction


class SmartActions(BaseModel):
    """Context-aware actions tailored to the processed document type."""
    email_draft: Optional[str] = Field(default=None, description="Personalized outreach email for business card contacts")
    whatsapp_message: Optional[str] = Field(default=None, description="Formatted WhatsApp follow-up message with 1-click copy")
    payment_priority: Optional[str] = Field(default="MEDIUM", description="Ranked payment priority: URGENT, MEDIUM, LOW")
    due_date_alert: Optional[str] = Field(default=None, description="Due date urgency reminder and cashflow advice")
    ledger_category: Optional[str] = Field(default=None, description="Auto-assigned expense category")
    suggested_action: str = Field(default="Review and save to ledger")


class DocumentResponse(BaseModel):
    """Comprehensive document response payload returned to dashboard UI."""
    id: int
    original_filename: str
    file_sha256: str
    data_sha256: Optional[str] = None
    document_type: str
    overall_confidence: float

    validation_status: str
    validation_notes: List[str] = []

    fraud_status: str
    fraud_reasons: List[str] = []

    on_chain_status: str
    blockchain_tx_hash: Optional[str] = None
    blockchain_block_number: Optional[int] = None
    polygonscan_url: Optional[str] = None

    extracted_data: UnifiedDocumentExtraction
    smart_actions: SmartActions

    created_at: str
    notarized_at: Optional[str] = None


class NotarizeRequest(BaseModel):
    """Payload to notarize an existing document on-chain."""
    tx_hash: Optional[str] = Field(default=None, description="MetaMask client-signed transaction hash if signed on frontend")
    ipfs_cid: Optional[str] = Field(default=None, description="Optional IPFS Pinata CID")


class NotarizeResponse(BaseModel):
    success: bool
    document_id: int
    on_chain_status: str
    tx_hash: str
    block_number: Optional[int] = None
    polygonscan_url: str
    message: str


class PublicVerifyRequest(BaseModel):
    file_sha256: Optional[str] = Field(default=None, description="Direct SHA-256 hash if already computed")


class PublicVerifyResponse(BaseModel):
    status: str = Field(..., description="VERIFIED, TAMPERED, or NOT_FOUND")
    is_valid: bool
    file_sha256: str
    data_sha256: Optional[str] = None
    uploader_wallet: Optional[str] = None
    timestamp: Optional[int] = None
    block_number: Optional[int] = None
    tx_hash: Optional[str] = None
    polygonscan_url: Optional[str] = None
    document_type: Optional[str] = None
    message: str
