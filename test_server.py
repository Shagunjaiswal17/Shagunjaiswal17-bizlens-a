import io
from fastapi.testclient import TestClient
from main import app, BusinessCardSchema, InvoiceSchema, ReceiptSchema

client = TestClient(app)

def test_health_check():
    """Verify GET /health returns expected status and service name."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok", "service": "BizLens AI"}

def test_cors_headers():
    """Verify CORS headers are set allowing origin *."""
    response = client.options(
        "/api/process/card",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers.get("access-control-allow-origin") in ["*", "http://localhost:3000"]

def test_missing_api_key_or_failure_card():
    """Verify 500 error format when API key is missing or call fails."""
    fake_image = io.BytesIO(b"fake image bytes")
    response = client.post(
        "/api/process/card",
        files={"file": ("test_card.jpg", fake_image, "image/jpeg")},
    )
    assert response.status_code == 500
    data = response.json()
    assert data == {"error": True, "message": "API Key missing or invalid image format."}

def test_missing_api_key_or_failure_invoice():
    """Verify 500 error format for invoice processing."""
    fake_image = io.BytesIO(b"fake invoice bytes")
    response = client.post(
        "/api/process/invoice",
        files={"file": ("test_invoice.png", fake_image, "image/png")},
    )
    assert response.status_code == 500
    data = response.json()
    assert data == {"error": True, "message": "API Key missing or invalid image format."}

def test_missing_api_key_or_failure_receipt():
    """Verify 500 error format for receipt processing."""
    fake_image = io.BytesIO(b"fake receipt bytes")
    response = client.post(
        "/api/process/receipt",
        files={"file": ("test_receipt.webp", fake_image, "image/webp")},
    )
    assert response.status_code == 500
    data = response.json()
    assert data == {"error": True, "message": "API Key missing or invalid image format."}

def test_schema_defaults_and_resilience():
    """Verify schemas enforce non-null lists and fallback flags."""
    card = BusinessCardSchema(
        person_name="Alex Mercer",
        phone_numbers=None,
        tags=None,
    )
    assert card.phone_numbers == []
    assert card.tags == []
    assert card.fallback is False

    invoice = InvoiceSchema(
        invoice_number="INV-100",
        line_items=None,
    )
    assert invoice.line_items == []
    assert invoice.fallback is False

    receipt = ReceiptSchema(
        merchant_name="Office Depot",
        expense_category="Office",
    )
    assert receipt.expense_category == "Office"
    assert receipt.fallback is False

if __name__ == "__main__":
    test_health_check()
    test_cors_headers()
    test_missing_api_key_or_failure_card()
    test_missing_api_key_or_failure_invoice()
    test_missing_api_key_or_failure_receipt()
    test_schema_defaults_and_resilience()
    print("All unit tests passed successfully!")
