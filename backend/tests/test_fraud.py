import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.document import Document
from app.models.ledger import LedgerEntry
from app.services.fraud_service import FraudService
from app.schemas.extraction import UnifiedDocumentExtraction, VendorDetails


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database session for unit testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Pre-populate historical entries for vendor 'Acme Tech Solutions'
    doc1 = Document(
        original_filename="past_bill_1.pdf",
        file_path="uploads/past_bill_1.pdf",
        file_sha256="abc123fixedhash",
        document_type="INVOICE"
    )
    doc2 = Document(
        original_filename="past_bill_2.pdf",
        file_path="uploads/past_bill_2.pdf",
        file_sha256="def456fixedhash",
        document_type="INVOICE"
    )
    session.add_all([doc1, doc2])
    session.commit()

    entry1 = LedgerEntry(
        document_id=doc1.id,
        vendor_name="Acme Tech Solutions Ltd",
        invoice_or_receipt_number="INV-2026-001",
        total_amount=10000.0,
        subtotal=8474.58,
        tax_amount=1525.42
    )
    entry2 = LedgerEntry(
        document_id=doc2.id,
        vendor_name="Acme Tech Solutions Ltd",
        invoice_or_receipt_number="INV-2026-002",
        total_amount=12000.0,
        subtotal=10169.49,
        tax_amount=1830.51
    )
    session.add_all([entry1, entry2])
    session.commit()

    yield session
    session.close()


def test_duplicate_file_hash_detection(test_db):
    """Verify exact file hash collision triggers duplicate status."""
    extraction = UnifiedDocumentExtraction(
        document_type="INVOICE",
        vendor=VendorDetails(name="Some Other Vendor"),
        document_number="INV-999",
        total_amount=5000.0
    )
    # Re-use known hash 'abc123fixedhash'
    status, reasons = FraudService.evaluate_fraud(test_db, extraction, "abc123fixedhash")
    assert status == "DUPLICATE"
    assert any("Double-Claim Detected" in r for r in reasons)


def test_duplicate_invoice_number_collision(test_db):
    """Verify duplicate invoice number for fuzzy-matched vendor is flagged as suspicious."""
    extraction = UnifiedDocumentExtraction(
        document_type="INVOICE",
        # Slightly altered vendor name (fuzzy match > 85%)
        vendor=VendorDetails(name="Acme Tech Solutions"),
        document_number="INV-2026-001",  # Same invoice number as entry1
        total_amount=11000.0
    )
    status, reasons = FraudService.evaluate_fraud(test_db, extraction, "brand_new_unique_hash")
    assert status == "SUSPICIOUS"
    assert any("Duplicate Invoice Collision" in r for r in reasons)


def test_spending_spike_anomaly(test_db):
    """Verify an invoice > 2.5x historical average for a vendor triggers outlier alert."""
    extraction = UnifiedDocumentExtraction(
        document_type="INVOICE",
        vendor=VendorDetails(name="Acme Tech Solutions Ltd"),
        document_number="INV-2026-099",
        # Historical average is 11,000. 35,000 is > 3.1x higher
        subtotal=30000.0,
        tax_amount=5000.0,
        total_amount=35000.0
    )
    status, reasons = FraudService.evaluate_fraud(test_db, extraction, "hash_spike")
    assert status == "SUSPICIOUS"
    assert any("Spending Spike Anomaly" in r for r in reasons)


def test_suspicious_tax_math(test_db):
    """Verify tax rate exceeding 28% GST statutory ceiling triggers tax anomaly alert."""
    extraction = UnifiedDocumentExtraction(
        document_type="INVOICE",
        vendor=VendorDetails(name="Fresh Vendor Corp"),
        document_number="INV-TAX-99",
        subtotal=10000.0,
        tax_amount=3500.0,  # 35% tax rate!
        total_amount=13500.0
    )
    status, reasons = FraudService.evaluate_fraud(test_db, extraction, "hash_tax")
    assert status == "SUSPICIOUS"
    assert any("Suspicious Tax Math" in r for r in reasons)
