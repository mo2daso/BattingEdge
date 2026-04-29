import os
import logging
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bcrypt as _bcrypt
from dotenv import load_dotenv
from jose import JWTError, jwt
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / '.env')

logger = logging.getLogger("AuthUtils")

# ── Secrets (all from .env) ─────────────────────────────────────────────────
SECRET_KEY        = os.getenv("SECRET_KEY", "INSECURE_DEV_KEY_REPLACE_IN_PROD")
ALGORITHM         = os.getenv("ALGORITHM", "HS256")
GMAIL_ADDRESS     = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
GOOGLE_CLIENT_ID  = os.getenv("GOOGLE_CLIENT_ID", "")


def _get_frontend_url() -> str:
    """Return FRONTEND_URL env var, or auto-detect LAN IP so email links work from phones."""
    explicit = os.getenv("FRONTEND_URL", "").strip()
    if explicit:
        return explicit
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
        return f"http://{lan_ip}:5173"
    except Exception:
        return "http://localhost:5173"


FRONTEND_URL = _get_frontend_url()

# ── Password hashing (bcrypt directly — compatible with bcrypt 4.x/5.x) ────

def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Returns False on any failure — never raises."""
    if not hashed:
        return False
    try:
        return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── JWT helpers ─────────────────────────────────────────────────────────────

def _encode(payload: dict) -> str:
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode(token: str) -> dict | None:
    """Returns decoded payload or None on any error."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def create_access_token(user_id: str, email: str) -> str:
    now = datetime.utcnow()
    return _encode({
        "sub":   user_id,
        "email": email,
        "type":  "access",
        "iat":   now,
        "exp":   now + timedelta(days=7),
    })


def decode_access_token(token: str) -> dict | None:
    """Returns payload dict or None. Validates type == 'access'."""
    payload = _decode(token)
    if not payload:
        return None
    if payload.get("type") != "access":
        return None
    if "sub" not in payload or "email" not in payload:
        return None
    return payload


def create_verification_token(user_id: str) -> str:
    now = datetime.utcnow()
    return _encode({
        "sub":  user_id,
        "type": "verification",
        "iat":  now,
        "exp":  now + timedelta(hours=24),
    })


def decode_verification_token(token: str) -> str | None:
    """Returns user_id or None."""
    payload = _decode(token)
    if not payload or payload.get("type") != "verification":
        return None
    return payload.get("sub")


def create_reset_token(user_id: str) -> str:
    now = datetime.utcnow()
    return _encode({
        "sub":  user_id,
        "type": "reset",
        "iat":  now,
        "exp":  now + timedelta(hours=1),
    })


def decode_reset_token(token: str) -> str | None:
    """Returns user_id or None."""
    payload = _decode(token)
    if not payload or payload.get("type") != "reset":
        return None
    return payload.get("sub")


# ── Email (Gmail SMTP SSL port 465) ─────────────────────────────────────────

def _send_email(to_email: str, subject: str, html_body: str) -> None:
    """Low-level mailer. Silently logs on failure — never raises."""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        logger.warning("[auth/email] GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set — skipping email")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"BattingEdge <{GMAIL_ADDRESS}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))

        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        logger.info(f"[auth/email] Sent '{subject}' to {to_email}")
    except Exception as e:
        logger.warning(f"[auth/email] Failed to send email to {to_email}: {e}")


def send_welcome_email(to_email: str, full_name: str) -> None:
    html = f"""
    <div style="font-family:Inter,Arial,sans-serif;max-width:520px;margin:auto;background:#0a0a0f;color:#fff;border-radius:12px;overflow:hidden;">
      <div style="background:#00d4ff;padding:24px;text-align:center;">
        <h1 style="margin:0;color:#0a0a0f;font-size:24px;font-weight:800;">BattingEdge</h1>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#00d4ff;margin-top:0;">Welcome to BattingEdge!</h2>
        <p>Hi {full_name},</p>
        <p>Your account is ready. Start analyzing your cricket shots with AI-powered feedback.</p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{FRONTEND_URL}"
             style="background:#00d4ff;color:#0a0a0f;padding:14px 32px;border-radius:8px;
                    text-decoration:none;font-weight:700;font-size:16px;display:inline-block;">
            START ANALYZING
          </a>
        </div>
        <p style="color:#a0a0b0;">— The BattingEdge Team</p>
      </div>
    </div>
    """
    _send_email(to_email, "Welcome to BattingEdge!", html)


def send_verification_email(to_email: str, full_name: str, token: str) -> None:
    link = f"{FRONTEND_URL}/verify?token={token}"
    html = f"""
    <div style="font-family:Inter,Arial,sans-serif;max-width:520px;margin:auto;background:#0a0a0f;color:#fff;border-radius:12px;overflow:hidden;">
      <div style="background:#00d4ff;padding:24px;text-align:center;">
        <h1 style="margin:0;color:#0a0a0f;font-size:24px;font-weight:800;">BattingEdge</h1>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#00d4ff;margin-top:0;">Verify Your Email</h2>
        <p>Hi {full_name},</p>
        <p>Click the button below to verify your BattingEdge account:</p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{link}"
             style="background:#00d4ff;color:#0a0a0f;padding:14px 32px;border-radius:8px;
                    text-decoration:none;font-weight:700;font-size:16px;display:inline-block;">
            VERIFY EMAIL
          </a>
        </div>
        <p style="color:#a0a0b0;font-size:13px;">This link expires in <strong>24 hours</strong>.</p>
        <p style="color:#a0a0b0;font-size:13px;">If you did not create a BattingEdge account, you can safely ignore this email.</p>
        <p style="color:#a0a0b0;">— The BattingEdge Team</p>
      </div>
    </div>
    """
    _send_email(to_email, "Verify your BattingEdge account", html)


def send_reset_email(to_email: str, full_name: str, token: str) -> None:
    link = f"{FRONTEND_URL}/reset-password?token={token}"
    html = f"""
    <div style="font-family:Inter,Arial,sans-serif;max-width:520px;margin:auto;background:#0a0a0f;color:#fff;border-radius:12px;overflow:hidden;">
      <div style="background:#00d4ff;padding:24px;text-align:center;">
        <h1 style="margin:0;color:#0a0a0f;font-size:24px;font-weight:800;">BattingEdge</h1>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#00d4ff;margin-top:0;">Reset Your Password</h2>
        <p>Hi {full_name},</p>
        <p>Click the button below to reset your BattingEdge password:</p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{link}"
             style="background:#00d4ff;color:#0a0a0f;padding:14px 32px;border-radius:8px;
                    text-decoration:none;font-weight:700;font-size:16px;display:inline-block;">
            RESET PASSWORD
          </a>
        </div>
        <p style="color:#a0a0b0;font-size:13px;">This link expires in <strong>1 hour</strong>.</p>
        <p style="color:#a0a0b0;font-size:13px;">If you did not request a password reset, you can safely ignore this email.</p>
        <p style="color:#a0a0b0;">— The BattingEdge Team</p>
      </div>
    </div>
    """
    _send_email(to_email, "Reset your BattingEdge password", html)


# ── Google OAuth ─────────────────────────────────────────────────────────────

def verify_google_token(google_token: str) -> dict | None:
    """
    Verifies a Google ID token and returns {email, full_name, google_id} or None.
    Never raises — returns None on any failure.
    """
    if not GOOGLE_CLIENT_ID:
        logger.warning("[auth/google] GOOGLE_CLIENT_ID not set")
        return None
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        idinfo = id_token.verify_oauth2_token(
            google_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return {
            "email":     idinfo.get("email", ""),
            "full_name": idinfo.get("name", idinfo.get("email", "").split("@")[0]),
            "google_id": idinfo.get("sub", ""),
        }
    except Exception as e:
        logger.warning(f"[auth/google] Token verification failed: {e}")
        return None


# ── FastAPI dependency ───────────────────────────────────────────────────────

from fastapi import Header, HTTPException


async def get_current_user(authorization: str = Header(default=None)) -> dict:
    """
    Extracts Bearer token from Authorization header.
    Raises 401 if missing, invalid, or user not found.
    """
    import auth_models
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = auth_models.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_current_user_optional(authorization: str = Header(default=None)) -> dict | None:
    """Same as get_current_user but returns None instead of raising."""
    import auth_models
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ", 1)[1]
        payload = decode_access_token(token)
        if not payload:
            return None
        return auth_models.get_user_by_id(payload["sub"])
    except Exception:
        return None
