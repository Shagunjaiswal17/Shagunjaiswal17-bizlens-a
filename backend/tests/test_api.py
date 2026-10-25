import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.seed.seed_data import seed_database


@pytest.fixture(autouse=True)
def setup_seed():
    db = SessionLocal()
    seed_database(db)
    db.close()


client = TestClient(app)


def test_health_check_endpoint():
    """Verify health check returns 200 and reports correct network configuration."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "BizLens AI"
    assert data["gemini_model"] == "gemini-2.5-flash"
    assert "Polygon Amoy" in data["blockchain_network"]


def test_analytics_summary_endpoint():
    """Verify analytics summary returns complete statistical aggregates."""
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_spend" in data
    assert "total_documents" in data
    assert "category_breakdown" in data
    assert "vendor_leaderboard" in data
    assert isinstance(data["category_breakdown"], list)


def test_documents_list_endpoint():
    """Verify documents listing returns structured items."""
    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()
    assert isinstance(docs, list)
    assert len(docs) >= 1  # At least 1 from auto-seeding


def test_chat_ledger_endpoint():
    """Verify natural language query over ledger functions safely."""
    response = client.post(
        "/api/chat",
        json={"message": "How much did we spend on IT and cloud services?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["record_count"] >= 0
    assert "citations" in data


def test_public_verify_not_found():
    """Verify unrecorded document hash returns NOT_FOUND status."""
    response = client.post(
        "/api/verify",
        data={"file_sha256": "0000000000000000000000000000000000000000000000000000000000000000"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NOT_FOUND"
    assert data["is_valid"] is False
