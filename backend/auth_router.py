import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

import auth_models
import auth_utils

logger = logging.getLogger("AuthRouter")
router = APIRouter()


# ── Request models ───────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleRequest(BaseModel):
    google_token: str

class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateEmailRequest(BaseModel):
    new_email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ResendVerificationRequest(BaseModel):
    email: str


# ── POST /auth/register ──────────────────────────────────────────────────────

@router.post("/auth/register", status_code=201)
async def register(body: RegisterRequest):
    # Validate email format
    email = body.email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Validate password length
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password too short — minimum 8 characters")

    # Validate name
    if not body.full_name.strip():
        raise HTTPException(status_code=400, detail="Name is required")

    # Check duplicate
    if auth_models.get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = auth_utils.hash_password(body.password)
    try:
        user_id = auth_models.create_user(email, body.full_name.strip(), password_hash=hashed)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Auto-verify — no email gate, login works immediately
    auth_models.set_verified(user_id)

    # Send welcome email (non-blocking — errors are swallowed)
    try:
        auth_utils.send_welcome_email(email, body.full_name.strip())
    except Exception as e:
        logger.warning(f"[auth/register] Welcome email failed (non-critical): {e}")

    logger.info(f"[auth/register] New user registered: {email}")
    return {
        "message": "Registration successful! You can now log in.",
        "user_id": user_id,
    }


# ── POST /auth/login ─────────────────────────────────────────────────────────

@router.post("/auth/login")
async def login(body: LoginRequest):
    user = auth_models.get_user_by_email(body.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Please login using Google")

    if not auth_utils.verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth_utils.create_access_token(user["user_id"], user["email"])
    logger.info(f"[auth/login] Login successful for user {user['user_id']}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id":        user["user_id"],
            "email":     user["email"],
            "full_name": user["name"],
        },
    }


# ── POST /auth/google ────────────────────────────────────────────────────────

@router.post("/auth/google")
async def google_login(body: GoogleRequest):
    info = auth_utils.verify_google_token(body.google_token)
    if not info:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    email     = info["email"].strip().lower()
    full_name = info["full_name"]
    google_id = info["google_id"]

    existing = auth_models.get_user_by_email(email)

    if existing:
        # Link Google ID if not already linked
        if not existing.get("google_id"):
            auth_models.set_google_id(existing["user_id"], google_id)
        user_id = existing["user_id"]
    else:
        # New Google user — auto-verified
        try:
            user_id = auth_models.create_user(email, full_name, google_id=google_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        auth_models.set_verified(user_id)

    user = auth_models.get_user_by_id(user_id)
    token = auth_utils.create_access_token(user_id, email)
    logger.info(f"[auth/google] Google login for {email}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id":        user_id,
            "email":     email,
            "full_name": user["name"] if user else full_name,
        },
    }


# ── GET /auth/verify-email?token= ────────────────────────────────────────────

@router.get("/auth/verify-email")
async def verify_email(token: str):
    user_id = auth_utils.decode_verification_token(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")
    auth_models.set_verified(user_id)
    logger.info(f"[auth/verify-email] Verified user {user_id}")
    return {"message": "Email verified successfully! You can now log in."}


# ── GET /auth/me ─────────────────────────────────────────────────────────────

@router.get("/auth/me")
async def me(current_user: dict = Depends(auth_utils.get_current_user)):
    return {
        "id":          current_user["user_id"],
        "email":       current_user["email"],
        "full_name":   current_user["name"],
        "is_verified": bool(current_user.get("is_verified")),
    }


# ── PUT /auth/update-password ────────────────────────────────────────────────

@router.put("/auth/update-password")
async def update_password(
    body: UpdatePasswordRequest,
    current_user: dict = Depends(auth_utils.get_current_user),
):
    if not current_user.get("password_hash"):
        raise HTTPException(status_code=400, detail="Password login not available for Google accounts")

    if not auth_utils.verify_password(body.current_password, current_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    auth_models.update_password(current_user["user_id"], auth_utils.hash_password(body.new_password))
    logger.info(f"[auth/update-password] Password updated for {current_user['user_id']}")
    return {"message": "Password updated successfully."}


# ── PUT /auth/update-email ───────────────────────────────────────────────────

@router.put("/auth/update-email")
async def update_email(
    body: UpdateEmailRequest,
    current_user: dict = Depends(auth_utils.get_current_user),
):
    if not current_user.get("password_hash"):
        raise HTTPException(status_code=400, detail="Cannot update email for Google accounts")

    if not auth_utils.verify_password(body.password, current_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Password is incorrect")

    new_email = body.new_email.strip().lower()
    if auth_models.get_user_by_email(new_email):
        raise HTTPException(status_code=400, detail="Email already in use")

    try:
        auth_models.update_email(current_user["user_id"], new_email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    auth_models.set_unverified(current_user["user_id"])

    try:
        token = auth_utils.create_verification_token(current_user["user_id"])
        auth_utils.send_verification_email(new_email, current_user["name"], token)
    except Exception as e:
        logger.warning(f"[auth/update-email] Verification email failed (non-critical): {e}")

    logger.info(f"[auth/update-email] Email updated for {current_user['user_id']}")
    return {"message": "Email updated. Please verify your new email address."}


# ── POST /auth/forgot-password ───────────────────────────────────────────────

@router.post("/auth/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    # Always return the same message — never reveal whether email exists
    user = auth_models.get_user_by_email(body.email)
    if user and user.get("password_hash"):
        try:
            token = auth_utils.create_reset_token(user["user_id"])
            auth_utils.send_reset_email(user["email"], user["name"], token)
        except Exception as e:
            logger.warning(f"[auth/forgot-password] Reset email failed (non-critical): {e}")
    return {
        "message": "If that email is registered, a password reset link has been sent."
    }


# ── POST /auth/reset-password ────────────────────────────────────────────────

@router.post("/auth/reset-password")
async def reset_password(body: ResetPasswordRequest):
    user_id = auth_utils.decode_reset_token(body.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    auth_models.update_password(user_id, auth_utils.hash_password(body.new_password))
    logger.info(f"[auth/reset-password] Password reset for {user_id}")
    return {"message": "Password reset successfully. You can now log in."}


# ── POST /auth/resend-verification ──────────────────────────────────────────

@router.post("/auth/resend-verification")
async def resend_verification(body: ResendVerificationRequest):
    # Always return same message
    user = auth_models.get_user_by_email(body.email)
    if user and not user.get("is_verified"):
        try:
            token = auth_utils.create_verification_token(user["user_id"])
            auth_utils.send_verification_email(user["email"], user["name"], token)
        except Exception as e:
            logger.warning(f"[auth/resend-verification] Email failed (non-critical): {e}")
    return {
        "message": "If your account exists and is unverified, a new link has been sent."
    }
