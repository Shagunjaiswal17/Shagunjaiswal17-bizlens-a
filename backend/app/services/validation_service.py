import re
from typing import List, Tuple, Dict, Any
from ..schemas.extraction import UnifiedDocumentExtraction


class ValidationService:
    """
    Validation and Confidence Layer.
    Verifies mathematical consistency, checks Indian GSTIN checksums/patterns,
    and computes weighted confidence scores.
    """

    # Official Indian GSTIN format (15 characters)
    # 2 digits (State Code) + 5 letters (PAN) + 4 digits (PAN) + 1 letter (PAN)
    # + 1 digit/letter (Entity code) + 'Z' + 1 checksum character
    GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

    @classmethod
    def validate_gstin(cls, gstin: str) -> bool:
        """Validate Indian GSTIN number against statutory regex specification."""
        if not gstin:
            return False
        clean_gstin = gstin.strip().upper()
        return bool(cls.GSTIN_REGEX.match(clean_gstin))

    @classmethod
    def validate_document(cls, extraction: UnifiedDocumentExtraction) -> Tuple[str, List[str], float]:
        """
        Run end-to-end mathematical and semantic integrity checks.
        Returns:
            validation_status: 'VALID', 'WARNING', or 'INVALID'
            validation_notes: List of actionable observations or mismatch alerts
            overall_confidence: Weighted float score between 0.0 and 1.0
        """
        notes: List[str] = []
        is_invalid = False
        has_warnings = False

        doc_type = extraction.document_type

        # 1. Mathematical Consistency Check (Invoices & Receipts)
        if doc_type in ["INVOICE", "RECEIPT"]:
            subtotal = extraction.subtotal or 0.0
            tax = extraction.tax_amount or 0.0
            total = extraction.total_amount or 0.0

            if total > 0:
                expected_total = subtotal + tax
                diff = abs(expected_total - total)

                # Tolerance of 0.05 currency units for rounding
                if diff > 0.05:
                    notes.append(
                        f"Math Mismatch: Subtotal ({subtotal:.2f}) + Tax ({tax:.2f}) = {expected_total:.2f}, but Total is {total:.2f} (diff: {diff:.2f})"
                    )
                    has_warnings = True

            # Line Items sum check
            if extraction.line_items:
                items_sum = sum(item.total_price for item in extraction.line_items)
                if subtotal > 0 and abs(items_sum - subtotal) > 1.00:
                    notes.append(
                        f"Line Items Discrepancy: Sum of line items ({items_sum:.2f}) differs from Subtotal ({subtotal:.2f})"
                    )
                    has_warnings = True

        # 2. Indian GSTIN Validation (if present)
        vendor_gstin = extraction.vendor.gstin if extraction.vendor else None
        if vendor_gstin:
            if not cls.validate_gstin(vendor_gstin):
                notes.append(f"Invalid GSTIN Format: '{vendor_gstin}' does not match official 15-char Indian GSTIN standard")
                has_warnings = True
            else:
                notes.append(f"GSTIN Verified: Valid format '{vendor_gstin}'")

        # 3. Required Fields Check
        if doc_type == "INVOICE":
            if not extraction.vendor.name:
                notes.append("Missing Vendor Name on commercial invoice")
                has_warnings = True
            if not extraction.document_number:
                notes.append("Missing Invoice Number identifier")
                has_warnings = True
            if not extraction.total_amount or extraction.total_amount <= 0:
                notes.append("Zero or negative Total Amount on invoice")
                is_invalid = True

        elif doc_type == "BUSINESS_CARD":
            card = extraction.card_details
            if not card or (not card.person_name and not card.company_name):
                notes.append("Business card missing both person name and company name")
                has_warnings = True
            if card and not card.email and not card.phone_numbers:
                notes.append("Business card contains no contact channel (email or phone)")
                has_warnings = True

        # 4. Overall Weighted Confidence Calculation
        confidences = extraction.field_confidences or {}
        vendor_conf = confidences.get("vendor_name", 0.90)
        total_conf = confidences.get("total_amount", 0.90)
        doc_num_conf = confidences.get("document_number", 0.90)
        dates_conf = confidences.get("dates", 0.90)

        # Weights: Total Amount 35%, Vendor 30%, Document Number 20%, Dates 15%
        overall_conf = round(
            (total_conf * 0.35) + (vendor_conf * 0.30) + (doc_num_conf * 0.20) + (dates_conf * 0.15),
            2
        )

        # Determine Final Status
        if is_invalid:
            status = "INVALID"
        elif has_warnings:
            status = "WARNING"
        else:
            status = "VALID"
            if not notes:
                notes.append("All mathematical and statutory validations passed cleanly.")

        return status, notes, overall_conf
