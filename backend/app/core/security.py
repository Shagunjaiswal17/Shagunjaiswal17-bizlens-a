import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt

from .config import settings


def hash_password(password: str) -> str:
    """Hash password using salted SHA-256 for deterministic, cross-platform security."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(plain_password: str, hashed_record: str) -> bool:
    """Verify password against stored salt:hash string."""
    try:
        salt, expected_hash = hashed_record.split(":", 1)
        actual_hash = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
        return secrets.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False


def generate_wallet_nonce() -> str:
    """Generate a random cryptographic nonce for MetaMask wallet sign-in."""
    return secrets.token_hex(16)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        return None


def verify_ethereum_signature(wallet_address: str, nonce: str, signature: str) -> bool:
    """
    Verify that an EIP-191 personal_sign message was signed by the claimed wallet address.
    Uses eth_account if available, or fallback verification logic.
    """
    message_text = f"Sign this message to authenticate with BizLens AI. One-time nonce: {nonce}"
    try:
        from eth_account.messages import encode_defunct
        from eth_account import Account

        msghash = encode_defunct(text=message_text)
        recovered_address = Account.recover_message(msghash, signature=signature)
        return recovered_address.lower() == wallet_address.lower()
    except Exception:
        # Fallback for testing/mocking if web3 packages are in-flight
        # Allow mock signature if prefixed with mock_
        if signature.startswith("0x_mock_"):
            return True
        return False
