import pytest
from app.services.validation_service import ValidationService
from app.schemas.extraction import UnifiedDocumentExtraction, VendorDetails, LineItemExtraction


def test_gstin_regex_valid():
    """Verify official 15-character Indian GSTIN format passes validation."""
    valid_gstins = [
        "29AAACI0123F1Z1",  # Karnataka Infosys
        "27AABCA1234F1Z8",  # Maharashtra
        "07AABCM2456K1Z9",  # Delhi MakeMyTrip
        "29ABCDE1234F1Z5",  # Karnataka
        "07AAACK1100F1Z6",  # Delhi Khaitan
    ]
    for gstin in valid_gstins:
        assert ValidationService.validate_gstin(gstin) is True, f"Failed for valid GSTIN: {gstin}"


def test_gstin_regex_invalid():
    """Verify improper, truncated, or forged GSTIN formats are flagged as invalid."""
    invalid_gstins = [
        "12345",                    # Too short
        "29AAACI0123F1",            # Truncated
        "29AAACI0123F1Z",           # 14 chars
        "INVALID_GSTIN_123",        # Garbage string
        "29AAACI0123F1X1",          # Missing mandatory 'Z' in 14th slot
    ]
    for gstin in invalid_gstins:
        assert ValidationService.validate_gstin(gstin) is False, f"Should fail for invalid GSTIN: {gstin}"


def test_math_validation_consistent():
    """Verify consistent invoice math passes without error notes."""
    extraction = UnifiedDocumentExtraction(
        document_type="INVOICE",
        vendor=VendorDetails(name="Test Vendor", gstin="29AAACI0123F1Z1"),
        document_number="INV-001",
        subtotal=1000.0,
        tax_amount=180.0,
        total_amount=1180.0,
        line_items=[
            LineItemExtraction(description="Dev Service", quantity=1.0, unit_price=1000.0, total_price=1000.0)
        ]
    )
    status, notes, conf = ValidationService.validate_document(extraction)
    assert status == "VALID"
    assert any("GSTIN Verified" in n or "passed cleanly" in n for n in notes)
    assert conf >= 0.85


def test_math_validation_mismatch():
    """Verify mismatched subtotal + tax != total is captured as warning with precise diff."""
    extraction = UnifiedDocumentExtraction(
        document_type="INVOICE",
        vendor=VendorDetails(name="Test Vendor", gstin="29AAACI0123F1Z1"),
        document_number="INV-002",
        subtotal=1000.0,
        tax_amount=180.0,
        total_amount=1500.0,  # Intentional discrepancy of 320.0
    )
    status, notes, conf = ValidationService.validate_document(extraction)
    assert status == "WARNING"
    assert any("Math Mismatch" in n for n in notes)
