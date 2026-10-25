import io
import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.document import Document
from ..models.ledger import LedgerEntry
from ..schemas.extraction import UnifiedDocumentExtraction
from ..schemas.document import SmartActions
from ..schemas.ledger import AnalyticsSummary, CategorySpend, MonthlyTrend, VendorStat


class LedgerService:
    """
    Financial Ledger and Accounting Intelligence Service.
    Handles:
    - Smart contextual actions (Outreach drafting, cashflow payment prioritization)
    - Aggregated analytics for dashboard charts (Donut, Area, Bar)
    - SMB accounting export generation (CSV, Tally-compatible XML, Zoho Books JSON)
    """

    @classmethod
    def generate_smart_actions(cls, extraction: UnifiedDocumentExtraction) -> SmartActions:
        """Generate high-utility contextual actions based on extracted intelligence."""
        doc_type = extraction.document_type
        vendor_name = extraction.vendor.name or "Business Partner"

        # 1. Business Card Smart Actions: 1-Click Outreach
        if doc_type == "BUSINESS_CARD":
            card = extraction.card_details
            person_name = card.person_name if card and card.person_name else "Colleague"
            company = card.company_name if card and card.company_name else vendor_name
            email = card.email if card and card.email else (extraction.vendor.email or "")
            tags = ", ".join(card.tags) if card and card.tags else "innovative solutions"

            email_draft = (
                f"Subject: Great meeting you, {person_name}! Let's connect on {tags}\n\n"
                f"Hi {person_name},\n\n"
                f"It was a pleasure connecting with you and learning about your work at {company}. "
                f"I was particularly impressed by your initiatives in {tags}.\n\n"
                f"I'd love to explore synergies and schedule a brief 15-minute catch-up sometime next week. "
                f"Let me know what day suits your calendar best!\n\n"
                f"Best regards,\n[Your Name]\n[Your Company]"
            )

            whatsapp_msg = (
                f"Hi {person_name}! Great connecting today regarding {company}. "
                f"Saving your contact in my BizLens ledger. Would love to stay in touch and collaborate! 🚀"
            )

            return SmartActions(
                email_draft=email_draft,
                whatsapp_message=whatsapp_msg,
                payment_priority="LOW",
                due_date_alert="No payment due for business networking contact.",
                ledger_category="Networking & Business Development",
                suggested_action="Sync contact & dispatch follow-up outreach"
            )

        # 2. Commercial Invoice Smart Actions: Payment Priority & Reminders
        if doc_type == "INVOICE":
            due_date_str = extraction.due_date
            total_amt = extraction.total_amount or 0.0
            currency = extraction.currency or "INR"

            priority = "MEDIUM"
            urgency_msg = "Standard payment window applies."

            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                    today = date.today()
                    days_remaining = (due_date - today).days

                    if days_remaining < 0:
                        priority = "URGENT"
                        urgency_msg = f"OVERDUE by {abs(days_remaining)} days! Immediate clearance recommended to preserve vendor terms."
                    elif days_remaining <= 7:
                        priority = "URGENT"
                        urgency_msg = f"Due in {days_remaining} days ({due_date_str}). Schedule disbursement now to avoid late penalties."
                    elif days_remaining <= 21:
                        priority = "MEDIUM"
                        urgency_msg = f"Due in {days_remaining} days ({due_date_str}). Queued for next bi-weekly payout batch."
                    else:
                        priority = "LOW"
                        urgency_msg = f"Due in {days_remaining} days. Scheduled for end-of-month review."
                except Exception:
                    pass

            return SmartActions(
                email_draft=None,
                whatsapp_message=None,
                payment_priority=priority,
                due_date_alert=urgency_msg,
                ledger_category=extraction.expense_category or "IT & Cloud",
                suggested_action=f"Approve {priority} priority disbursement of {currency} {total_amt:,.2f}"
            )

        # 3. Retail Expense Receipt: Auto-Ledger Categorization
        cat = extraction.expense_category or "General"
        return SmartActions(
            email_draft=None,
            whatsapp_message=None,
            payment_priority="LOW",
            due_date_alert="Paid at point-of-sale. Auto-reconciled with corporate expense card.",
            ledger_category=cat,
            suggested_action=f"Post verified expense of INR {(extraction.total_amount or 0.0):,.2f} to {cat} ledger"
        )

    @classmethod
    def get_analytics_summary(cls, db: Session, user_id: Optional[int] = None) -> AnalyticsSummary:
        """Compute aggregated statistics for high-impact executive dashboard charts."""
        doc_query = db.query(Document)
        ledger_query = db.query(LedgerEntry)

        if user_id:
            doc_query = doc_query.filter(Document.user_id == user_id)
            ledger_query = ledger_query.join(Document).filter(Document.user_id == user_id)

        all_docs = doc_query.all()
        all_ledger = ledger_query.all()

        total_spend = sum(e.total_amount for e in all_ledger if e.total_amount)
        total_docs = len(all_docs)

        invoices_count = sum(1 for d in all_docs if d.document_type == "INVOICE")
        receipts_count = sum(1 for d in all_docs if d.document_type == "RECEIPT")
        cards_count = sum(1 for d in all_docs if d.document_type == "BUSINESS_CARD")

        anomalies_caught = sum(1 for d in all_docs if d.fraud_status in ["SUSPICIOUS", "DUPLICATE"])
        documents_notarized = sum(1 for d in all_docs if d.on_chain_status == "NOTARIZED")

        # Estimated SMB accounting hours saved (15 mins = 0.25 hours per document)
        hours_saved = round(total_docs * 0.25, 1)

        # 1. Category Breakdown (Donut Chart)
        category_map: Dict[str, float] = {}
        category_count: Dict[str, int] = {}
        for entry in all_ledger:
            cat = entry.expense_category or "General"
            category_map[cat] = category_map.get(cat, 0.0) + (entry.total_amount or 0.0)
            category_count[cat] = category_count.get(cat, 0) + 1

        category_breakdown: List[CategorySpend] = []
        for cat, amt in category_map.items():
            pct = round((amt / total_spend * 100), 1) if total_spend > 0 else 0.0
            category_breakdown.append(
                CategorySpend(category=cat, amount=round(amt, 2), percentage=pct, count=category_count[cat])
            )
        category_breakdown.sort(key=lambda x: x.amount, reverse=True)

        # 2. Monthly Trend (Area Chart)
        monthly_map: Dict[str, float] = {}
        monthly_counts: Dict[str, int] = {}
        for entry in all_ledger:
            date_str = entry.issue_date
            month_label = "Recent"
            if date_str:
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    month_label = dt.strftime("%b %Y")
                except Exception:
                    pass
            monthly_map[month_label] = monthly_map.get(month_label, 0.0) + (entry.total_amount or 0.0)
            monthly_counts[month_label] = monthly_counts.get(month_label, 0) + 1

        monthly_trend: List[MonthlyTrend] = [
            MonthlyTrend(month=m, spend=round(amt, 2), documents_count=monthly_counts[m])
            for m, amt in monthly_map.items()
        ]

        # 3. Vendor Leaderboard (Bar Chart)
        vendor_map: Dict[str, float] = {}
        vendor_counts: Dict[str, int] = {}
        vendor_latest_dates: Dict[str, str] = {}
        for entry in all_ledger:
            v_name = entry.vendor_name or "Unknown Vendor"
            vendor_map[v_name] = vendor_map.get(v_name, 0.0) + (entry.total_amount or 0.0)
            vendor_counts[v_name] = vendor_counts.get(v_name, 0) + 1
            if entry.issue_date:
                vendor_latest_dates[v_name] = max(vendor_latest_dates.get(v_name, ""), entry.issue_date)

        vendor_leaderboard: List[VendorStat] = [
            VendorStat(
                vendor_name=v,
                total_spend=round(amt, 2),
                invoice_count=vendor_counts[v],
                latest_date=vendor_latest_dates.get(v)
            )
            for v, amt in vendor_map.items()
        ]
        vendor_leaderboard.sort(key=lambda x: x.total_spend, reverse=True)
        vendor_leaderboard = vendor_leaderboard[:10]  # Top 10 vendors

        return AnalyticsSummary(
            total_spend=round(total_spend, 2),
            total_documents=total_docs,
            invoices_count=invoices_count,
            receipts_count=receipts_count,
            business_cards_count=cards_count,
            anomalies_caught=anomalies_caught,
            documents_notarized=documents_notarized,
            hours_saved=hours_saved,
            scans_used=total_docs,
            scans_limit=50,
            category_breakdown=category_breakdown,
            monthly_trend=monthly_trend,
            vendor_leaderboard=vendor_leaderboard
        )

    @classmethod
    def export_csv(cls, db: Session) -> str:
        """Export normalized ledger entries into standard CSV format."""
        entries = db.query(LedgerEntry).all()
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Entry ID", "Vendor Name", "GSTIN", "Document Number",
            "Issue Date", "Due Date", "Category", "Subtotal", "Tax", "Total Amount", "Priority", "Status"
        ])

        for e in entries:
            writer.writerow([
                e.id, e.vendor_name, e.vendor_gstin or "", e.invoice_or_receipt_number or "",
                e.issue_date or "", e.due_date or "", e.expense_category or "General",
                f"{e.subtotal:.2f}", f"{e.tax_amount:.2f}", f"{e.total_amount:.2f}",
                e.payment_priority, e.payment_status
            ])

        return output.getvalue()

    @classmethod
    def export_tally_xml(cls, entry: LedgerEntry) -> str:
        """Generate official Tally-compatible XML voucher markup for Indian accounting."""
        root = ET.Element("ENVELOPE")
        header = ET.SubElement(root, "HEADER")
        ET.SubElement(header, "TALLYREQUEST").text = "Import Data"

        body = ET.SubElement(root, "BODY")
        import_data = ET.SubElement(body, "IMPORTDATA")
        req_data = ET.SubElement(import_data, "REQUESTDATA")
        tally_msg = ET.SubElement(req_data, "TALLYMESSAGE")

        voucher = ET.SubElement(tally_msg, "VOUCHER", VCHTYPE="Purchase", ACTION="Create")
        ET.SubElement(voucher, "DATE").text = (entry.issue_date or "").replace("-", "")
        ET.SubElement(voucher, "VOUCHERNUMBER").text = entry.invoice_or_receipt_number or f"VCH-{entry.id}"
        ET.SubElement(voucher, "PARTYLEDGERNAME").text = entry.vendor_name
        ET.SubElement(voucher, "GSTIN").text = entry.vendor_gstin or ""
        ET.SubElement(voucher, "AMOUNT").text = f"{entry.total_amount:.2f}"
        ET.SubElement(voucher, "NARRATION").text = f"Imported via BizLens AI - Document #{entry.document_id}"

        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

    @classmethod
    def export_zoho_json(cls, entry: LedgerEntry) -> Dict[str, Any]:
        """Generate Zoho Books compatible invoice/bill payload."""
        line_items_data = []
        try:
            raw_items = json.loads(entry.line_items_json or "[]")
            for item in raw_items:
                line_items_data.append({
                    "name": item.get("description", "Standard Item"),
                    "rate": item.get("unit_price", 0.0),
                    "quantity": item.get("quantity", 1.0),
                    "item_total": item.get("total_price", 0.0)
                })
        except Exception:
            line_items_data = [{
                "name": f"Expense - {entry.expense_category}",
                "rate": entry.subtotal,
                "quantity": 1.0,
                "item_total": entry.subtotal
            }]

        return {
            "vendor_name": entry.vendor_name,
            "bill_number": entry.invoice_or_receipt_number or f"BILL-{entry.id}",
            "date": entry.issue_date,
            "due_date": entry.due_date,
            "line_items": line_items_data,
            "sub_total": entry.subtotal,
            "tax_total": entry.tax_amount,
            "total": entry.total_amount,
            "notes": f"Auto-imported by BizLens AI. Proof-of-Document registered on Polygon Amoy."
        }
