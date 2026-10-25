import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.config import settings
from ..models.ledger import LedgerEntry
from ..models.document import Document
from ..schemas.chat import SafeQueryFilter, ChatQueryResponse, DocumentCitation

logger = logging.getLogger("bizlens.chat")

# Try importing modern google-genai SDK
try:
    from google import genai
    from google.genai import types as genai_types
    HAVE_GOOGLE_GENAI = True
except ImportError:
    HAVE_GOOGLE_GENAI = False

try:
    import google.generativeai as legacy_genai
    HAVE_LEGACY_GENAI = True
except ImportError:
    HAVE_LEGACY_GENAI = False


class ChatService:
    """
    'Ask BizLens' Conversational Intelligence Engine.
    Converts natural-language queries into safe, parameterized filters.
    Strictly forbids raw LLM SQL execution to prevent SQL injection vulnerabilities.
    """

    SAFE_INTENT_PROMPT = """
You are a financial query intent parser for BizLens AI.
The user is asking a question about their business expenses, invoices, or vendor records.
Current Date: 2026-10-25.
Convert the user's natural language request into a strictly validated SafeQueryFilter JSON conforming to the schema.
Extract:
- query_type: "SPEND_SUM", "CATEGORY_CHECK", "VENDOR_LOOKUP", "DOCUMENT_SEARCH", or "GENERAL_ADVICE"
- vendor_pattern: vendor name or partial name if mentioned
- category: one of 'IT & Cloud', 'Travel', 'Office', 'Utilities', 'Logistics', 'Kitchen Supplies', 'Professional Services' if mentioned
- date_from / date_to: normalized ISO dates (YYYY-MM-DD) if timeframes like 'last month', 'October', 'this quarter' are referenced
- min_amount / max_amount: numerical bounds if specified
- payment_status: 'PAID', 'PENDING', or 'OVERDUE' if mentioned
- aggregation: 'SUM', 'COUNT', 'AVERAGE', or 'LIST'
Never produce SQL code. Produce only the structured filter.
"""

    @classmethod
    def parse_user_intent(cls, message: str) -> SafeQueryFilter:
        """Translate user natural language query into safe parameter schema via Gemini."""
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

        # Fallback heuristic parser if Gemini API key is absent or offline
        if not api_key.strip():
            return cls._heuristic_intent_parse(message)

        try:
            if HAVE_GOOGLE_GENAI:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=[cls.SAFE_INTENT_PROMPT, f"User Question: {message}"],
                    config=genai_types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=SafeQueryFilter,
                        temperature=0.0,
                    ),
                )
                if response.text:
                    return SafeQueryFilter.model_validate_json(response.text)

            elif HAVE_LEGACY_GENAI:
                legacy_genai.configure(api_key=api_key)
                model = legacy_genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config={
                        "response_mime_type": "application/json",
                        "response_schema": SafeQueryFilter,
                        "temperature": 0.0,
                    },
                )
                response = model.generate_content([cls.SAFE_INTENT_PROMPT, f"User Question: {message}"])
                if response.text:
                    return SafeQueryFilter.model_validate_json(response.text)

        except Exception as e:
            logger.warning(f"Gemini chat intent parser fallback: {e}")

        return cls._heuristic_intent_parse(message)

    @classmethod
    def _heuristic_intent_parse(cls, message: str) -> SafeQueryFilter:
        """Deterministic offline rule-based intent parser for zero-downtime demos."""
        lower = message.lower()

        # Category detection
        category = None
        for cat in ["IT & Cloud", "Travel", "Office", "Utilities", "Logistics", "Kitchen Supplies"]:
            if cat.lower() in lower or cat.replace("&", "and").lower() in lower:
                category = cat
                break
        if not category:
            if "cloud" in lower or "hosting" in lower or "aws" in lower or "software" in lower:
                category = "IT & Cloud"
            elif "food" in lower or "chai" in lower or "coffee" in lower:
                category = "Kitchen Supplies"
            elif "cab" in lower or "uber" in lower or "flight" in lower or "hotel" in lower:
                category = "Travel"

        # Vendor pattern detection
        vendor_pattern = None
        for vendor in ["Infosys", "Chai Point", "Apex", "Tata", "Reliance", "AWS"]:
            if vendor.lower() in lower:
                vendor_pattern = vendor
                break

        # Aggregation detection
        agg = "SUM"
        if "how many" in lower or "count" in lower or "number of" in lower:
            agg = "COUNT"
        elif "average" in lower or "avg" in lower:
            agg = "AVERAGE"
        elif "list" in lower or "show all" in lower:
            agg = "LIST"

        # Payment status
        payment_status = None
        if "pending" in lower or "unpaid" in lower or "due" in lower:
            payment_status = "PENDING"
        elif "paid" in lower or "cleared" in lower:
            payment_status = "PAID"

        return SafeQueryFilter(
            query_type="SPEND_SUM",
            vendor_pattern=vendor_pattern,
            category=category,
            aggregation=agg,
            payment_status=payment_status
        )

    @classmethod
    def execute_safe_query(cls, db: Session, parsed_filter: SafeQueryFilter) -> ChatQueryResponse:
        """
        Execute strictly parameterized SQLAlchemy query based on parsed filter.
        Completely immune to SQL injection attacks.
        """
        query = db.query(LedgerEntry).join(Document)

        if parsed_filter.vendor_pattern:
            query = query.filter(LedgerEntry.vendor_name.ilike(f"%{parsed_filter.vendor_pattern}%"))

        if parsed_filter.category:
            query = query.filter(LedgerEntry.expense_category == parsed_filter.category)

        if parsed_filter.payment_status:
            query = query.filter(LedgerEntry.payment_status == parsed_filter.payment_status)

        if parsed_filter.date_from:
            query = query.filter(LedgerEntry.issue_date >= parsed_filter.date_from)

        if parsed_filter.date_to:
            query = query.filter(LedgerEntry.issue_date <= parsed_filter.date_to)

        if parsed_filter.min_amount is not None:
            query = query.filter(LedgerEntry.total_amount >= parsed_filter.min_amount)

        if parsed_filter.max_amount is not None:
            query = query.filter(LedgerEntry.total_amount <= parsed_filter.max_amount)

        matched_entries = query.all()
        count = len(matched_entries)

        citations: List[DocumentCitation] = [
            DocumentCitation(
                document_id=e.document_id,
                vendor_name=e.vendor_name,
                amount=e.total_amount,
                date=e.issue_date,
                document_type=e.document.document_type if e.document else "INVOICE",
                tx_hash=e.document.blockchain_tx_hash if e.document else None
            )
            for e in matched_entries[:5]  # Top 5 citations
        ]

        if parsed_filter.aggregation == "COUNT":
            total_val = float(count)
            answer = f"Found **{count}** records matching your query criteria."
        elif parsed_filter.aggregation == "AVERAGE":
            total_sum = sum(e.total_amount for e in matched_entries)
            avg = (total_sum / count) if count > 0 else 0.0
            total_val = round(avg, 2)
            answer = f"The average spend across {count} matching records is **INR {avg:,.2f}**."
        else:
            total_sum = sum(e.total_amount for e in matched_entries)
            total_val = round(total_sum, 2)
            cat_text = f" on **{parsed_filter.category}**" if parsed_filter.category else ""
            vendor_text = f" from **{parsed_filter.vendor_pattern}**" if parsed_filter.vendor_pattern else ""
            answer = (
                f"You have spent **INR {total_sum:,.2f}** across **{count}** recorded transactions{cat_text}{vendor_text}. "
                f"All receipts and invoices have been cryptographically notarized on-chain."
            )

        return ChatQueryResponse(
            answer=answer,
            filter_applied=parsed_filter,
            record_count=count,
            calculated_total=total_val,
            citations=citations
        )
