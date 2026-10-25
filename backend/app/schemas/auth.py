from typing import Optional
from pydantic import BaseModel, Field


class NonceRequest(BaseModel):
    wallet_address: str = Field(..., description="Ethereum wallet address (0x...)")


class NonceResponse(BaseModel):
    wallet_address: str
    nonce: str
    message: str = Field(..., description="Exact personal_sign message string to be signed in MetaMask")


class VerifyWalletRequest(BaseModel):
    wallet_address: str
    signature: str = Field(..., description="Hex-encoded signature produced by MetaMask personal_sign")


class UserRegister(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: Optional[str] = None
    wallet_address: Optional[str] = None
    plan_tier: str
    scans_used: int
    scans_remaining: int


class UserProfileResponse(BaseModel):
    id: int
    email: Optional[str] = None
    wallet_address: Optional[str] = None
    plan_tier: str
    scans_used: int
    scans_remaining: int
