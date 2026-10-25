from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.ledger import LedgerEntry
from ..services.ledger_service import LedgerService

router = APIRouter(prefix="/documents", tags=["Export & Accounting Integrations"])


@router.get("/export/csv", summary="Export All Ledger Entries to CSV")
def export_all_csv(db: Session = Depends(get_db)):
    """Export complete financial ledger to RFC 4180 compliant CSV."""
    csv_content = LedgerService.export_csv(db)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bizlens_ledger_export.csv"}
    )


@router.get("/{document_id}/export/tally", summary="Export to Tally XML")
def export_tally_xml(document_id: int, db: Session = Depends(get_db)):
    """Export invoice or receipt as an XML Purchase Voucher compatible with Tally Prime / ERP 9."""
    entry = db.query(LedgerEntry).filter(LedgerEntry.document_id == document_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ledger record not found for this document.")

    xml_content = LedgerService.export_tally_xml(entry)
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={"Content-Disposition": f"attachment; filename=tally_voucher_{document_id}.xml"}
    )


@router.get("/{document_id}/export/zoho", summary="Export to Zoho Books Format")
def export_zoho_json(document_id: int, db: Session = Depends(get_db)):
    """Export invoice or receipt formatted for direct Zoho Books Bill API import."""
    entry = db.query(LedgerEntry).filter(LedgerEntry.document_id == document_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ledger record not found for this document.")

    return LedgerService.export_zoho_json(entry)
