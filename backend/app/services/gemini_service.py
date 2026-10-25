import os
import json
import time
import logging
from typing import Optional, Tuple
from ..core.config import settings
from ..schemas.extraction import UnifiedDocumentExtraction, VendorDetails, LineItemExtraction, CardContactDetails

logger = logging.getLogger("bizlens.gemini")

# Try importing modern google-genai SDK
try:
    from google import genai
    from google.genai import types as genai_types
    HAVE_GOOGLE_GENAI = True
except ImportError:
    HAVE_GOOGLE_GENAI = False

# Try importing legacy google-generativeai SDK as fallback
try:
    import google.generativeai as legacy_genai
    HAVE_LEGACY_GENAI = True
except ImportError:
    HAVE_LEGACY_GENAI = False


class GeminiService:
    """
    Dedicated AI extraction service leveraging Google Gemini 2.5 Flash.
    Utilizes strict `response_schema` for 100% deterministic JSON output.
    Includes exponential retries and bulletproof offline fallback mock data
    for zero-crash hackathon stage presentations.
    """

    EXTRACTION_PROMPT = """
You are BizLens AI, an expert enterprise document understanding engine.
Analyze the provided document (Invoice, Receipt, or Business Card).
1. Classify the document accurately into:
   - "INVOICE": B2B commercial bills with line items, due dates, GST/tax, buyer/seller.
   - "RECEIPT": Cash register / retail payment slips, restaurant bills, POS receipts.
   - "BUSINESS_CARD": Professional networking cards with personal contact details.
2. Extract all vendor details, GSTIN (if Indian document), line items, financial totals, and transaction dates.
3. Classify into an appropriate expense category: 'IT & Cloud', 'Travel', 'Office', 'Utilities', 'Logistics', 'Kitchen Supplies', 'Professional Services', or 'General'.
4. Provide realistic confidence scores between 0.0 and 1.0 for each primary field.
Extract everything faithfully conforming to the requested schema.
"""

    @classmethod
    def extract_document(
        cls,
        file_bytes: bytes,
        mime_type: str,
        filename: str = ""
    ) -> UnifiedDocumentExtraction:
        """
        Extract structured data from file bytes using Gemini 2.5 Flash.
        Falls back seamlessly to offline preset data if the API key is absent or unreachable.
        """
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

        # If no API key is configured, immediately use offline fallback demo data
        if not api_key.strip():
            logger.warning("No GEMINI_API_KEY found. Utilizing offline fallback demo mode for deterministic presentation.")
            return cls._get_offline_fallback(filename)

        # Attempt extraction with exponential backoff
        max_retries = settings.GEMINI_MAX_RETRIES
        delay = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                if HAVE_GOOGLE_GENAI:
                    client = genai.Client(api_key=api_key)
                    logger.info(f"Invoking Gemini 2.5 Flash via google-genai (Attempt {attempt}/{max_retries})")

                    response = client.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=[
                            genai_types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                            cls.EXTRACTION_PROMPT,
                        ],
                        config=genai_types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=UnifiedDocumentExtraction,
                            temperature=0.0,
                        ),
                    )

                    if response.text:
                        parsed = UnifiedDocumentExtraction.model_validate_json(response.text)
                        parsed.demo_mode = False
                        return parsed

                elif HAVE_LEGACY_GENAI:
                    legacy_genai.configure(api_key=api_key)
                    model = legacy_genai.GenerativeModel(
                        model_name="gemini-1.5-flash",  # Legacy fallback name
                        generation_config={
                            "response_mime_type": "application/json",
                            "response_schema": UnifiedDocumentExtraction,
                            "temperature": 0.0,
                        },
                    )
                    response = model.generate_content([
                        {"mime_type": mime_type, "data": file_bytes},
                        cls.EXTRACTION_PROMPT,
                    ])
                    if response.text:
                        parsed = UnifiedDocumentExtraction.model_validate_json(response.text)
                        parsed.demo_mode = False
                        return parsed

            except Exception as e:
                logger.warning(f"Gemini API attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2
                else:
                    logger.error("All Gemini API attempts failed. Falling back to offline demo mode.")

        # If all retries failed, fallback to guaranteed demo response
        return cls._get_offline_fallback(filename)

    @classmethod
    def _get_offline_fallback(cls, filename: str) -> UnifiedDocumentExtraction:
        """
        Returns rich, realistic sample data if API is offline or key is missing.
        Tailored to realistic Indian SMB documents.
        """
        lower = filename.lower()

        # Business Card Fallback
        if "card" in lower or "contact" in lower or "biz" in lower:
            return UnifiedDocumentExtraction(
                document_type="BUSINESS_CARD",
                vendor=VendorDetails(
                    name="Apex Cloud Innovations Pvt Ltd",
                    gstin="27AABCA1234F1Z8",
                    address="Tower 4, Cyber City, Gurugram, Haryana 122002",
                    email="contact@apexcloud.in",
                    phone="+91-98765-43210",
                    website="https://apexcloud.in"
                ),
                document_number="CARD-092",
                issue_date="2026-10-15",
                due_date=None,
                currency="INR",
                subtotal=0.0,
                tax_amount=0.0,
                total_amount=0.0,
                expense_category="Professional Services",
                line_items=[],
                card_details=CardContactDetails(
                    person_name="Rajesh Sharma",
                    job_title="VP of Enterprise Engineering",
                    company_name="Apex Cloud Innovations Pvt Ltd",
                    email="rajesh.sharma@apexcloud.in",
                    phone_numbers=["+91-98765-43210", "+91-11-45678900"],
                    address="Tower 4, Cyber City, Gurugram, Haryana 122002",
                    website="https://apexcloud.in",
                    tags=["Cloud Architecture", "DevOps", "AI Infrastructure"]
                ),
                field_confidences={
                    "vendor_name": 0.98,
                    "person_name": 0.99,
                    "email": 0.97,
                    "phone": 0.96
                },
                demo_mode=True
            )

        # Receipt Fallback
        if "receipt" in lower or "food" in lower or "cab" in lower or "fuel" in lower:
            return UnifiedDocumentExtraction(
                document_type="RECEIPT",
                vendor=VendorDetails(
                    name="Chai Point & Quick Bites",
                    gstin="29ABCDE1234F1Z5",
                    address="Indiranagar 100ft Road, Bengaluru, Karnataka 560038",
                    email="billing@chaipoint.com",
                    phone="+91-80-49112233",
                    website="https://chaipoint.com"
                ),
                document_number="RCPT-8841",
                issue_date="2026-10-22",
                due_date=None,
                currency="INR",
                subtotal=520.00,
                tax_amount=26.00,
                total_amount=546.00,
                expense_category="Kitchen Supplies",
                line_items=[
                    LineItemExtraction(description="Masala Chai Flask (1000ml)", quantity=2.0, unit_price=210.0, total_price=420.0),
                    LineItemExtraction(description="Banana Walnut Cake Slice", quantity=2.0, unit_price=50.0, total_price=100.0)
                ],
                field_confidences={
                    "vendor_name": 0.96,
                    "total_amount": 0.99,
                    "tax_amount": 0.94,
                    "issue_date": 0.95
                },
                demo_mode=True
            )

        # Default: Invoice Fallback (e.g. AWS/Azure IT & Cloud Invoice)
        return UnifiedDocumentExtraction(
            document_type="INVOICE",
            vendor=VendorDetails(
                name="Infosys BPM & Cloud Services Ltd",
                gstin="29AAACI0123F1Z1",
                address="Electronics City, Hosur Road, Bengaluru, Karnataka 560100",
                email="invoices@infosysbpm.com",
                phone="+91-80-28520261",
                website="https://infosys.com"
            ),
            document_number="INV-2026-8819",
            issue_date="2026-10-18",
            due_date="2026-11-15",
            currency="INR",
            subtotal=75000.00,
            tax_amount=13500.00,  # 18% GST
            total_amount=88500.00,
            expense_category="IT & Cloud",
            line_items=[
                LineItemExtraction(description="Managed Cloud VPS Hosting (October)", quantity=1.0, unit_price=45000.0, total_price=45000.0),
                LineItemExtraction(description="Dedicated Kubernetes Cluster SRE Support", quantity=1.0, unit_price=30000.0, total_price=30000.0)
            ],
            field_confidences={
                "vendor_name": 0.99,
                "document_number": 0.97,
                "gstin": 0.98,
                "subtotal": 0.96,
                "tax_amount": 0.95,
                "total_amount": 0.99
            },
            demo_mode=True
        )
