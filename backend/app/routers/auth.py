from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import (
    hash_password, verify_password, generate_wallet_nonce,
    create_access_token, verify_ethereum_signature
)
from ..models.user import User
from ..schemas.auth import (
    NonceRequest, NonceResponse, VerifyWalletRequest,
    UserRegister, UserLogin, TokenResponse, UserProfileResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication & Web3 Identity"])


@router.post("/wallet-nonce", response_model=NonceResponse, summary="Generate MetaMask Nonce Challenge")
def request_wallet_nonce(req: NonceRequest, db: Session = Depends(get_db)):
    """
    Issue an EIP-191 personal_sign cryptographic nonce challenge for a connecting MetaMask wallet.
    Prevents replay attacks by generating a single-use random salt.
    """
    clean_addr = req.wallet_address.strip().lower()
    user = db.query(User).filter(User.wallet_address == clean_addr).first()
    nonce = generate_wallet_nonce()

    if not user:
        user = User(wallet_address=clean_addr, nonce=nonce)
        db.add(user)
    else:
        user.nonce = nonce

    db.commit()
    db.refresh(user)

    message = f"Sign this message to authenticate with BizLens AI. One-time nonce: {nonce}"
    return NonceResponse(wallet_address=clean_addr, nonce=nonce, message=message)


@router.post("/wallet-verify", response_model=TokenResponse, summary="Verify MetaMask Signature & Issue JWT")
def verify_wallet_signature_endpoint(req: VerifyWalletRequest, db: Session = Depends(get_db)):
    """
    Verify the cryptographic signature produced by MetaMask and authenticate the user.
    """
    clean_addr = req.wallet_address.strip().lower()
    user = db.query(User).filter(User.wallet_address == clean_addr).first()

    if not user or not user.nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nonce not found. Please request a new nonce challenge first."
        )

    is_valid = verify_ethereum_signature(clean_addr, user.nonce, req.signature)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cryptographic signature verification failed."
        )

    # Invalidate nonce after successful login
    user.nonce = None
    db.commit()

    token = create_access_token({"sub": str(user.id), "wallet": clean_addr})
    scans_remaining = max(0, 50 - (user.scans_used_this_month or 0))

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        wallet_address=clean_addr,
        plan_tier=user.plan_tier or "FREE",
        scans_used=user.scans_used_this_month or 0,
        scans_remaining=scans_remaining
    )


@router.post("/register", response_model=TokenResponse, summary="Email/Password Registration")
def register_user(req: UserRegister, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    new_user = User(
        email=clean_email,
        hashed_password=hash_password(req.password),
        plan_tier="FREE",
        scans_used_this_month=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id), "email": clean_email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        email=clean_email,
        plan_tier="FREE",
        scans_used=0,
        scans_remaining=50
    )


@router.post("/login", response_model=TokenResponse, summary="Email/Password Login")
def login_user(req: UserLogin, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()
    if not user or not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_access_token({"sub": str(user.id), "email": clean_email})
    scans_remaining = max(0, 50 - (user.scans_used_this_month or 0))

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=clean_email,
        plan_tier=user.plan_tier or "FREE",
        scans_used=user.scans_used_this_month or 0,
        scans_remaining=scans_remaining
    )
