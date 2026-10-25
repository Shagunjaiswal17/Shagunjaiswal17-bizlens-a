from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field, field_validator


class LineItemExtraction(BaseModel):
    """Schema for individual line items on an invoice or receipt."""
    description: str = Field(default="", description="Description of the item or service")
    quantity: float = Field(default=1.0, description="Quantity billed or purchased")
    unit_price: float = Field(default=0.0, description="Price per unit")
    total_price: float = Field(default=0.0, description="Total amount for this line item")


class VendorDetails(BaseModel):
    """Schema for vendor or entity contact details."""
    name: Optional[str] = Field(default=None, description="Legal business or trading name")
    gstin: Optional[str] = Field(default=None, description="15-character Indian GSTIN identification number")
    address: Optional[str] = Field(default=None, description="Physical postal address")
    email: Optional[str] = Field(default=None, description="Official email address")
    phone: Optional[str] = Field(default=None, description="Telephone or mobile contact number")
    website: Optional[str] = Field(default=None, description="Website URL")


class CardContactDetails(BaseModel):
    """Schema for business card contact extraction."""
    person_name: Optional[str] = Field(default=None, description="Full name of person on card")
    job_title: Optional[str] = Field(default=None, description="Job title, designation or executive role")
    company_name: Optional[str] = Field(default=None, description="Company or firm name")
    email: Optional[str] = Field(default=None, description="Primary email address")
    phone_numbers: List[str] = Field(default_factory=list, description="Direct phone numbers or WhatsApp")
    address: Optional[str] = Field(default=None, description="Office address")
    website: Optional[str] = Field(default=None, description="Company website")
    tags: List[str] = Field(default_factory=list, description="Keywords, industries, or services")


class FieldConfidences(BaseModel):
    """Per-field confidence scores assessed by the model from 0.0 to 1.0."""
    vendor_name: float = Field(default=0.95, description="Confidence in vendor identification")
    document_number: float = Field(default=0.92, description="Confidence in document number")
    total_amount: float = Field(default=0.98, description="Confidence in total amount")
    dates: float = Field(default=0.90, description="Confidence in date extraction")
    line_items: float = Field(default=0.88, description="Confidence in line items")

    def get(self, key: str, default: float = 0.90) -> float:
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> float:
        return getattr(self, key)


class UnifiedDocumentExtraction(BaseModel):
    """
    Unified extraction schema passed directly to Gemini 2.5 Flash `response_schema`.
    Enforces deterministic classification and structured data extraction.
    """
    document_type: Literal["INVOICE", "RECEIPT", "BUSINESS_CARD"] = Field(
        ...,
        description="Auto-classified document type: INVOICE for bills with due dates, RECEIPT for retail payment slips, BUSINESS_CARD for contact cards"
    )

    # Vendor / Entity
    vendor: VendorDetails = Field(default_factory=VendorDetails, description="Vendor or business identification")

    # Document Numbers & Dates
    document_number: Optional[str] = Field(default=None, description="Invoice or receipt number / reference code")
    issue_date: Optional[str] = Field(default=None, description="Date of transaction or bill issue (YYYY-MM-DD)")
    due_date: Optional[str] = Field(default=None, description="Payment due date if invoice (YYYY-MM-DD)")

    # Financial breakdown
    currency: str = Field(default="INR", description="Three-letter currency code (INR, USD, EUR, GBP)")
    subtotal: Optional[float] = Field(default=None, description="Subtotal amount before tax")
    tax_amount: Optional[float] = Field(default=None, description="Total tax, GST or VAT amount")
    total_amount: Optional[float] = Field(default=None, description="Grand total amount payable or paid")

    # Expense categorization
    expense_category: Optional[
        Literal["IT & Cloud", "Travel", "Office", "Utilities", "Logistics", "Kitchen Supplies", "Professional Services", "General"]
    ] = Field(
        default="General",
        description="Categorization of the transaction"
    )

    # Line Items
    line_items: List[LineItemExtraction] = Field(default_factory=list, description="Itemized billing breakdown")

    # Business Card specific
    card_details: Optional[CardContactDetails] = Field(default=None, description="Populated if document_type is BUSINESS_CARD")

    # Confidence assessment
    field_confidences: FieldConfidences = Field(
        default_factory=FieldConfidences,
        description="Per-field confidence scores assessed by the model from 0.0 to 1.0"
    )

    demo_mode: bool = Field(default=False, description="Flag indicating if offline fallback mock data was utilized")

    @field_validator("line_items", mode="before")
    @classmethod
    def ensure_line_items_list(cls, v):
        return v if v is not None else []
