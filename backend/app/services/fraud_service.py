import difflib
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from ..models.document import Document
from ..models.ledger import LedgerEntry
from ..schemas.extraction import UnifiedDocumentExtraction


class FraudService:
    """
    AI Fraud and Anomaly Detection Engine.
    Detects:
    1. Cryptographic SHA-256 duplicate uploads (Double-claiming prevention)
    2. Fuzzy vendor match + duplicate invoice number collision
    3. Vendor spending anomalies (statistical spike > 2.5x vendor historical average)
    4. Suspicious or illegal tax calculations (>28% GST ceiling or 0% tax anomaly)
    """

    @classmethod
    def check_file_duplicate(cls, db: Session, file_sha256: str) -> Optional[Document]:
        """Check if an identical file hash has already been notarized or recorded."""
        return db.query(Document).filter(Document.file_sha256 == file_sha256).first()

    @classmethod
    def evaluate_fraud(
        cls,
        db: Session,
        extraction: UnifiedDocumentExtraction,
        file_sha256: str
    ) -> Tuple[str, List[str]]:
        """
        Evaluate full spectrum of fraud heuristics.
        Returns:
            fraud_status: 'CLEAN', 'SUSPICIOUS', or 'DUPLICATE'
            fraud_reasons: List of human-readable fraud alerts
        """
        reasons: List[str] = []
        is_duplicate = False
        is_suspicious = False

        # 1. Exact File Hash Collision (Proof-of-Document duplicate prevention)
        existing_doc = cls.check_file_duplicate(db, file_sha256)
        if existing_doc:
            reasons.append(
                f"Double-Claim Detected: Exact SHA-256 document hash already registered in Document #{existing_doc.id} on {existing_doc.created_at.strftime('%Y-%m-%d')}"
            )
            is_duplicate = True

        vendor_name = (extraction.vendor.name or "").strip().lower()
        invoice_num = (extraction.document_number or "").strip().lower()
        total_amount = extraction.total_amount or 0.0

        # Only evaluate billing fraud heuristics for Invoices & Receipts
        if extraction.document_type in ["INVOICE", "RECEIPT"] and vendor_name:
            # Query recent historical transactions to compare against
            past_entries = db.query(LedgerEntry).all()

            vendor_entries: List[LedgerEntry] = []
            for entry in past_entries:
                entry_vendor = (entry.vendor_name or "").strip().lower()
                # Compute fuzzy string match ratio (tolerates minor OCR spelling variations)
                ratio = difflib.SequenceMatcher(None, vendor_name, entry_vendor).ratio()

                if ratio >= 0.85:
                    vendor_entries.append(entry)
                    # 2. Check for duplicate invoice number from same or fuzzy vendor
                    if invoice_num and entry.invoice_or_receipt_number:
                        if invoice_num == entry.invoice_or_receipt_number.strip().lower():
                            reasons.append(
                                f"Duplicate Invoice Collision: Vendor '{entry.vendor_name}' already billed invoice #{entry.invoice_or_receipt_number} (Entry ID #{entry.id})"
                            )
                            is_suspicious = True

            # 3. Vendor Historical Spending Outlier Anomaly (> 2.5x vendor average)
            if len(vendor_entries) >= 2 and total_amount > 0:
                past_amounts = [e.total_amount for e in vendor_entries if e.total_amount > 0]
                if past_amounts:
                    avg_spend = sum(past_amounts) / len(past_amounts)
                    ratio = total_amount / avg_spend
                    if ratio >= 2.5:
                        reasons.append(
                            f"Spending Spike Anomaly: Current amount (INR {total_amount:,.2f}) is {ratio:.1f}x higher than historical average (INR {avg_spend:,.2f}) for this vendor"
                        )
                        is_suspicious = True

            # 4. Tax Math & Statutory Slab Anomaly Check
            subtotal = extraction.subtotal or 0.0
            tax_amount = extraction.tax_amount or 0.0

            if subtotal > 0 and tax_amount > 0:
                effective_tax_rate = (tax_amount / subtotal) * 100
                # Highest standard GST slab in India is 28%
                if effective_tax_rate > 28.5:
                    reasons.append(
                        f"Suspicious Tax Math: Effective tax rate of {effective_tax_rate:.1f}% exceeds statutory 28% GST ceiling"
                    )
                    is_suspicious = True
            elif subtotal > 10000.0 and tax_amount == 0.0:
                reasons.append(
                    f"Missing Tax Anomaly: Commercial invoice of INR {subtotal:,.2f} has 0.00 tax reported"
                )
                is_suspicious = True

        # Final Status determination
        if is_duplicate:
            status = "DUPLICATE"
        elif is_suspicious:
            status = "SUSPICIOUS"
        else:
            status = "CLEAN"

        return status, reasons
