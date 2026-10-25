import pytest
from app.schemas.extraction import UnifiedDocumentExtraction, VendorDetails, LineItemExtraction
from app.services.gemini_service import GeminiService


def test_schema_serialization():
    """Verify UnifiedDocumentExtraction round-trips cleanly through JSON."""
    doc = UnifiedDocumentExtraction(
        document_type="INVOICE",
        vendor=VendorDetails(name="Acme Tech", gstin="29AAACI0123F1Z1"),
        document_number="INV-101",
        total_amount=5000.0,
        line_items=[
            LineItemExtraction(description="Cloud Server", quantity=2.0, unit_price=2500.0, total_price=5000.0)
        ]
    )
    json_str = doc.model_dump_json()
    reloaded = UnifiedDocumentExtraction.model_validate_json(json_str)

    assert reloaded.vendor.name == "Acme Tech"
    assert reloaded.total_amount == 5000.0
    assert len(reloaded.line_items) == 1
    assert reloaded.line_items[0].total_price == 5000.0


def test_offline_fallback_generator():
    """Verify offline fallback guarantees non-null, valid schema instances."""
    card = GeminiService._get_offline_fallback("visiting_card_sample.jpg")
    assert card.document_type == "BUSINESS_CARD"
    assert card.card_details is not None
    assert card.demo_mode is True

    receipt = GeminiService._get_offline_fallback("cafe_receipt.png")
    assert receipt.document_type == "RECEIPT"
    assert receipt.total_amount > 0
    assert receipt.demo_mode is True

    invoice = GeminiService._get_offline_fallback("cloud_invoice.pdf")
    assert invoice.document_type == "INVOICE"
    assert invoice.total_amount > 0
    assert invoice.demo_mode is True
