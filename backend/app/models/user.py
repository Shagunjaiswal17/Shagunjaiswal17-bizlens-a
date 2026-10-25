import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..core.database import Base


class User(Base):
    """
    User entity supporting dual authentication:
    - Traditional Email / Password
    - Web3 MetaMask Wallet (via EIP-191 personal_sign cryptographic challenge)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    wallet_address = Column(String(42), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    nonce = Column(String(64), nullable=True)  # For wallet sign-in challenge

    plan_tier = Column(String(50), default="FREE")  # "FREE", "PRO", "ENTERPRISE"
    scans_used_this_month = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationship to user's processed documents
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
