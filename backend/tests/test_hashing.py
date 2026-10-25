import pytest
from app.services.blockchain_service import BlockchainService


def test_file_sha256_determinism():
    """Verify SHA-256 produces identical hash for identical bytes."""
    data = b"BizLens AI Hackathon Test Document Content"
    hash1 = BlockchainService.compute_file_sha256(data)
    hash2 = BlockchainService.compute_file_sha256(data)
    assert hash1 == hash2
    assert len(hash1) == 64


def test_canonical_json_hashing_invariance():
    """Verify key ordering in dictionary does NOT affect the canonical SHA-256 hash."""
    dict1 = {"vendor": "Infosys", "total": 88500.0, "currency": "INR", "tax": 13500.0}
    dict2 = {"currency": "INR", "tax": 13500.0, "total": 88500.0, "vendor": "Infosys"}

    hash1 = BlockchainService.compute_canonical_json_sha256(dict1)
    hash2 = BlockchainService.compute_canonical_json_sha256(dict2)

    assert hash1 == hash2, "Canonical JSON hash must be key-order invariant"
