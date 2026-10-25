import json
import hashlib
import datetime
from sqlalchemy.orm import Session
from ..core.database import SessionLocal, Base, engine
from ..models.user import User
from ..models.document import Document
from ..models.ledger import LedgerEntry
from ..schemas.extraction import UnifiedDocumentExtraction, VendorDetails, LineItemExtraction, CardContactDetails
from ..services.ledger_service import LedgerService
from ..services.blockchain_service import BlockchainService


SAMPLE_SMB_DOCUMENTS = [
    {
        "filename": "Infosys_Cloud_VPS_Oct2026.pdf",
        "doc_type": "INVOICE",
        "vendor": {
            "name": "Infosys BPM & Cloud Services Ltd",
            "gstin": "29AAACI0123F1Z1",
            "address": "Electronics City, Hosur Road, Bengaluru, Karnataka 560100",
            "email": "enterprise-billing@infosysbpm.com",
            "phone": "+91-80-28520261",
            "website": "https://infosys.com"
        },
        "doc_number": "INV-2026-8819",
        "issue_date": "2026-10-18",
        "due_date": "2026-11-15",
        "subtotal": 75000.0,
        "tax": 13500.0,
        "total": 88500.0,
        "category": "IT & Cloud",
        "items": [
            {"description": "Managed Cloud VPS Hosting (October)", "quantity": 1.0, "unit_price": 45000.0, "total_price": 45000.0},
            {"description": "Dedicated Kubernetes Cluster SRE Support", "quantity": 1.0, "unit_price": 30000.0, "total_price": 30000.0}
        ],
        "status": "VALID",
        "on_chain": True,
        "tx_hash": "0x3f5c78a912e4b6c8d7e0123456789abcdef0123456789abcdef0123456789abc"
    },
    {
        "filename": "MakeMyTrip_Flight_BLR_DEL.pdf",
        "doc_type": "RECEIPT",
        "vendor": {
            "name": "MakeMyTrip India Pvt Ltd",
            "gstin": "07AABCM2456K1Z9",
            "address": "Tower A, SP Infocity, Udyog Vihar, Gurugram, Haryana 122016",
            "email": "corporatesupport@makemytrip.com",
            "phone": "+91-124-4628747",
            "website": "https://makemytrip.com"
        },
        "doc_number": "MMT-FLT-99214",
        "issue_date": "2026-10-14",
        "due_date": None,
        "subtotal": 12076.27,
        "tax": 2173.73,
        "total": 14250.0,
        "category": "Travel",
        "items": [
            {"description": "Air Ticket BLR to DEL (IndiGo 6E-2134)", "quantity": 1.0, "unit_price": 12076.27, "total_price": 12076.27}
        ],
        "status": "VALID",
        "on_chain": True,
        "tx_hash": "0x8a9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b"
    },
    {
        "filename": "Staples_Office_Stationery_Bengaluru.pdf",
        "doc_type": "INVOICE",
        "vendor": {
            "name": "Staples Office Supplies India Ltd",
            "gstin": "27AABCS9876Q1Z3",
            "address": "Bandra Kurla Complex, Mumbai, Maharashtra 400051",
            "email": "orders@staplesindia.com",
            "phone": "+91-22-66998800",
            "website": "https://staples.in"
        },
        "doc_number": "STP-2026-4412",
        "issue_date": "2026-10-10",
        "due_date": "2026-10-31",
        "subtotal": 6000.0,
        "tax": 720.0,
        "total": 6720.0,
        "category": "Office",
        "items": [
            {"description": "A4 High-Bulk Copy Paper Reams (Box of 5)", "quantity": 4.0, "unit_price": 1000.0, "total_price": 4000.0},
            {"description": "Ergonomic Mesh Lumbar Support Cushions", "quantity": 2.0, "unit_price": 1000.0, "total_price": 2000.0}
        ],
        "status": "VALID",
        "on_chain": True,
        "tx_hash": "0x4b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c"
    },
    {
        "filename": "BESCOM_Commercial_Electricity_Sep2026.pdf",
        "doc_type": "INVOICE",
        "vendor": {
            "name": "Bangalore Electricity Supply Co (BESCOM)",
            "gstin": "29AAACB1122C1Z4",
            "address": "K.R. Circle, Bengaluru, Karnataka 560001",
            "email": "commercial@bescom.karnataka.gov.in",
            "phone": "1912",
            "website": "https://bescom.karnataka.gov.in"
        },
        "doc_number": "BES-0926-7811",
        "issue_date": "2026-10-02",
        "due_date": "2026-10-22",
        "subtotal": 18450.0,
        "tax": 0.0,
        "total": 18450.0,
        "category": "Utilities",
        "items": [
            {"description": "LT Commercial Tariff Energy Consumption (2100 kWh)", "quantity": 1.0, "unit_price": 18450.0, "total_price": 18450.0}
        ],
        "status": "VALID",
        "on_chain": True,
        "tx_hash": "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b"
    },
    {
        "filename": "Chai_Point_Team_Snacks_Receipt.jpg",
        "doc_type": "RECEIPT",
        "vendor": {
            "name": "Chai Point & Quick Bites",
            "gstin": "29ABCDE1234F1Z5",
            "address": "Indiranagar 100ft Road, Bengaluru, Karnataka 560038",
            "email": "billing@chaipoint.com",
            "phone": "+91-80-49112233",
            "website": "https://chaipoint.com"
        },
        "doc_number": "RCPT-8841",
        "issue_date": "2026-10-22",
        "due_date": None,
        "subtotal": 2300.0,
        "tax": 115.0,  # 5% GST on Restaurant food
        "total": 2415.0,
        "category": "Kitchen Supplies",
        "items": [
            {"description": "Ginger Chai Flask (2000ml)", "quantity": 3.0, "unit_price": 400.0, "total_price": 1200.0},
            {"description": "Samosa Platter with Mint Chutney (Pack of 10)", "quantity": 2.0, "unit_price": 350.0, "total_price": 700.0},
            {"description": "Banana Walnut Cake Slices", "quantity": 8.0, "unit_price": 50.0, "total_price": 400.0}
        ],
        "status": "VALID",
        "on_chain": True,
        "tx_hash": "0x6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a"
    },
    {
        "filename": "BlueDart_Logistics_Freight_Oct2026.pdf",
        "doc_type": "INVOICE",
        "vendor": {
            "name": "Blue Dart Express Ltd",
            "gstin": "27AAACB3344D1Z2",
            "address": "Sahar Airport Road, Andheri East, Mumbai 400099",
            "email": "billing@bluedart.com",
            "phone": "+91-22-28396444",
            "website": "https://bluedart.com"
        },
        "doc_number": "BLU-887410",
        "issue_date": "2026-10-12",
        "due_date": "2026-11-05",
        "subtotal": 4000.0,
        "tax": 720.0,  # 18% GST
        "total": 4720.0,
        "category": "Logistics",
        "items": [
            {"description": "Express Secure Hardware Server Dispatch (BLR to BOM)", "quantity": 1.0, "unit_price": 4000.0, "total_price": 4000.0}
        ],
        "status": "VALID",
        "on_chain": True,
        "tx_hash": "0x9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d"
    },
    {
        "filename": "Khaitan_Legal_Retainer_Q3.pdf",
        "doc_type": "INVOICE",
        "vendor": {
            "name": "Khaitan & Co Legal Advocates & Solicitors",
            "gstin": "07AAACK1100F1Z6",
            "address": "Barakhamba Road, Connaught Place, New Delhi 110001",
            "email": "accounts@khaitanco.com",
            "phone": "+91-11-41515454",
            "website": "https://khaitanco.com"
        },
        "doc_number": "KCO-Q3-1092",
        "issue_date": "2026-10-05",
        "due_date": "2026-11-04",
        "subtotal": 50000.0,
        "tax": 9000.0,  # 18% GST
        "total": 59000.0,
        "category": "Professional Services",
        "items": [
            {"description": "Corporate Regulatory Compliance & Web3 Advisory Retainer", "quantity": 1.0, "unit_price": 50000.0, "total_price": 50000.0}
        ],
        "status": "VALID",
        "on_chain": True,
        "tx_hash": "0x2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e"
    },
    {
        "filename": "Airtel_Corporate_Fiber_Internet_Oct2026.pdf",
        "doc_type": "INVOICE",
        "vendor": {
            "name": "Bharti Airtel Ltd (Airtel Business)",
            "gstin": "07AAACB2894G1ZG",
            "address": "Nelson Mandela Road, Vasant Kunj, New Delhi 110070",
            "email": "corporatecare@airtel.com",
            "phone": "+91-11-46666100",
            "website": "https://airtel.in"
        },
        "doc_number": "AIR-1026-993",
        "issue_date": "2026-10-15",
        "due_date": "2026-11-08",
        "subtotal": 2999.0,
        "tax": 539.82,  # 18% GST
        "total": 3538.82,
        "category": "Utilities",
        "items": [
            {"description": "1 Gbps Dedicated Symmetrical Fiber Broadband Plan", "quantity": 1.0, "unit_price": 2999.0, "total_price": 2999.0}
        ],
        "status": "VALID",
        "on_chain": False,
        "tx_hash": None
    },
    {
        "filename": "Rajesh_Sharma_ApexCloud_VisitingCard.jpg",
        "doc_type": "BUSINESS_CARD",
        "vendor": {
            "name": "Apex Cloud Innovations Pvt Ltd",
            "gstin": "27AABCA1234F1Z8",
            "address": "Tower 4, Cyber City, Gurugram, Haryana 122002",
            "email": "contact@apexcloud.in",
            "phone": "+91-98765-43210",
            "website": "https://apexcloud.in"
        },
        "doc_number": "CARD-092",
        "issue_date": "2026-10-20",
        "due_date": None,
        "subtotal": 0.0,
        "tax": 0.0,
        "total": 0.0,
        "category": "Professional Services",
        "items": [],
        "card_details": {
            "person_name": "Rajesh Sharma",
            "job_title": "VP of Enterprise Engineering",
            "company_name": "Apex Cloud Innovations Pvt Ltd",
            "email": "rajesh.sharma@apexcloud.in",
            "phone_numbers": ["+91-98765-43210", "+91-11-45678900"],
            "address": "Tower 4, Cyber City, Gurugram, Haryana 122002",
            "website": "https://apexcloud.in",
            "tags": ["Cloud Architecture", "DevOps", "AI Infrastructure"]
        },
        "status": "VALID",
        "on_chain": True,
        "tx_hash": "0x5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b"
    },
    {
        "filename": "Suspicious_Vendor_Duplicate_TaxTampered.pdf",
        "doc_type": "INVOICE",
        "vendor": {
            "name": "Infosys BPM & Cloud Services Ltd",  # Duplicate vendor test
            "gstin": "29AAACI0123F1Z1",
            "address": "Electronics City, Bengaluru",
            "email": "fake-billing@infosysbpm.com",
            "phone": "+91-80-28520261",
            "website": "https://infosys.com"
        },
        "doc_number": "INV-2026-8819",  # Identical invoice number collision!
        "issue_date": "2026-10-21",
        "due_date": "2026-10-28",
        "subtotal": 195000.0,  # > 2.5x historical average
        "tax": 68000.0,       # 34.8% tax rate! (Exceeds 28% GST ceiling)
        "total": 263000.0,
        "category": "IT & Cloud",
        "items": [
            {"description": "Unverified Specialized Cloud Migration Batch", "quantity": 1.0, "unit_price": 195000.0, "total_price": 195000.0}
        ],
        "status": "INVALID",
        "fraud_reasons": [
            "Duplicate Invoice Collision: Vendor 'Infosys BPM & Cloud Services Ltd' already billed invoice #INV-2026-8819",
            "Spending Spike Anomaly: Current amount (INR 263,000.00) is 2.9x higher than historical average",
            "Suspicious Tax Math: Effective tax rate of 34.9% exceeds statutory 28% GST ceiling"
        ],
        "on_chain": False,
        "tx_hash": None
    }
]


def seed_database(db: Session = None):
    """Seed the database with 10 realistic Indian SMB documents."""
    close_db = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_db = True

    try:
        # Check if already seeded
        existing_count = db.query(Document).count()
        if existing_count >= 10:
            print(f"Database already contains {existing_count} documents. Skipping seed.")
            return

        # Ensure demo user exists
        demo_wallet = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        user = db.query(User).filter(User.wallet_address == demo_wallet).first()
        if not user:
            user = User(
                email="founder@bizlens.ai",
                wallet_address=demo_wallet,
                plan_tier="PRO",
                scans_used_this_month=10
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        print("Seeding 10 realistic Indian SMB documents...")

        for data in SAMPLE_SMB_DOCUMENTS:
            doc_type = data["doc_type"]
            filename = data["filename"]

            # Compute pseudo-deterministic file hash
            file_hash = hashlib.sha256(f"bizlens_seed_{filename}".encode("utf-8")).hexdigest()

            line_items = [
                LineItemExtraction(
                    description=i["description"],
                    quantity=i["quantity"],
                    unit_price=i["unit_price"],
                    total_price=i["total_price"]
                )
                for i in data["items"]
            ]

            card_details = None
            if "card_details" in data:
                c = data["card_details"]
                card_details = CardContactDetails(
                    person_name=c["person_name"],
                    job_title=c["job_title"],
                    company_name=c["company_name"],
                    email=c["email"],
                    phone_numbers=c["phone_numbers"],
                    address=c["address"],
                    website=c["website"],
                    tags=c["tags"]
                )

            extraction = UnifiedDocumentExtraction(
                document_type=doc_type,
                vendor=VendorDetails(
                    name=data["vendor"]["name"],
                    gstin=data["vendor"]["gstin"],
                    address=data["vendor"]["address"],
                    email=data["vendor"]["email"],
                    phone=data["vendor"]["phone"],
                    website=data["vendor"]["website"]
                ),
                document_number=data["doc_number"],
                issue_date=data["issue_date"],
                due_date=data["due_date"],
                currency="INR",
                subtotal=data["subtotal"],
                tax_amount=data["tax"],
                total_amount=data["total"],
                expense_category=data["category"],
                line_items=line_items,
                card_details=card_details,
                field_confidences={
                    "vendor_name": 0.98,
                    "document_number": 0.96,
                    "total_amount": 0.99,
                    "dates": 0.95
                },
                demo_mode=False
            )

            data_hash = BlockchainService.compute_canonical_json_sha256(extraction.model_dump())
            smart_actions = LedgerService.generate_smart_actions(extraction)

            fraud_reasons = data.get("fraud_reasons", [])
            fraud_status = "SUSPICIOUS" if fraud_reasons else "CLEAN"
            val_status = data["status"]

            on_chain_status = "NOTARIZED" if data["on_chain"] else "NOT_NOTARIZED"
            tx_hash = data.get("tx_hash")

            doc = Document(
                user_id=user.id,
                original_filename=filename,
                file_path=f"uploads/{file_hash[:12]}_{filename}",
                file_sha256=file_hash,
                data_sha256=data_hash,
                document_type=doc_type,
                raw_gemini_json=extraction.model_dump_json(),
                overall_confidence=0.97,
                validation_status=val_status,
                validation_notes=json.dumps(["All checks verified"] if val_status == "VALID" else ["Validation alert"]),
                fraud_status=fraud_status,
                fraud_reasons=json.dumps(fraud_reasons),
                on_chain_status=on_chain_status,
                blockchain_tx_hash=tx_hash,
                blockchain_block_number=15894231 if on_chain_status == "NOTARIZED" else None,
                ipfs_cid=f"ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi/{file_hash[:16]}" if on_chain_status == "NOTARIZED" else None,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=int(file_hash[:2], 16) % 15),
                notarized_at=datetime.datetime.utcnow() if on_chain_status == "NOTARIZED" else None
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            # Add Ledger entry
            ledger = LedgerEntry(
                document_id=doc.id,
                vendor_name=extraction.vendor.name or "Unknown",
                vendor_gstin=extraction.vendor.gstin,
                vendor_email=extraction.vendor.email,
                vendor_phone=extraction.vendor.phone,
                invoice_or_receipt_number=extraction.document_number,
                issue_date=extraction.issue_date,
                due_date=extraction.due_date,
                subtotal=extraction.subtotal or 0.0,
                tax_amount=extraction.tax_amount or 0.0,
                total_amount=extraction.total_amount or 0.0,
                currency="INR",
                expense_category=extraction.expense_category or "General",
                payment_priority=smart_actions.payment_priority or "MEDIUM",
                payment_status="PAID" if doc_type == "RECEIPT" else "PENDING",
                line_items_json=json.dumps([item.model_dump() for item in line_items])
            )
            db.add(ledger)
            db.commit()

        print("Seeding completed successfully! 10 documents stored.")
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_database()
