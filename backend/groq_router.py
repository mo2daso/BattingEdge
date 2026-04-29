"""
Groq AI endpoints:
  POST /api/chat          — cricket chatbot
  POST /api/subscribe     — weekly email subscription
  DELETE /api/unsubscribe — cancel subscription
"""
import os
import json
import logging
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("GroqRouter")
router = APIRouter()

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_URL      = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL    = "llama-3.1-8b-instant"   # free, fast

GMAIL_USER    = os.getenv("GMAIL_ADDRESS", "")
GMAIL_PASS    = os.getenv("GMAIL_APP_PASSWORD", "")

DB_PATH = Path(__file__).resolve().parent / "shot_analysis.db"

SYSTEM_PROMPT = """You are BESSA (Batting Edge Smart Sports Assistant) — the dedicated cricket AI inside BattingEdge, an AI cricket batting analysis platform.

STRICT RULE: You ONLY answer cricket-related questions or questions about how BattingEdge works. If the user asks about anything completely unrelated to cricket, respond with:
"I'm BESSA, your cricket assistant! I only know about cricket techniques, rules, history, training tips, and how BattingEdge works. What cricket question can I help you with? 🏏"

Your expertise:
• Batting techniques — cover drive, cut shot, pull shot, sweep shot, defense, and all other shots
• MCC Laws of Cricket and ECB batting standards
• Pakistani cricket legends — Babar Azam, Younis Khan, Javed Miandad, Zaheer Abbas, Inzamam, Saeed Anwar, Wasim Akram
• World cricket history, records, and current events
• Training drills, footwork, biomechanics
• Shot selection vs different bowling styles (pace/spin)
• Equipment, fitness, and mental game for batters
• BattingEdge's 5 shots: cover_drive, cut_shot, defense, pull_shot, sweep_shot
• How BattingEdge analysis works, what grades mean, how to film for best results

Tone: Friendly, enthusiastic, encouraging — like a knowledgeable cricket coach who genuinely wants to help. Keep responses concise (2-4 sentences unless more detail is needed). Use cricket terms naturally. Reference Pakistani legends for relatability when relevant."""


# ── Request / Response models ─────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str   # 'user' | 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class SubscribeRequest(BaseModel):
    email: str
    name: str = "Cricket Fan"

class UnsubscribeRequest(BaseModel):
    email: str


# ── Ensure subscriptions table exists ────────────────────────────────────────

def _init_subs_table():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS email_subscriptions (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                email     TEXT    UNIQUE NOT NULL,
                name      TEXT    DEFAULT 'Cricket Fan',
                active    INTEGER DEFAULT 1,
                created   TEXT    DEFAULT (datetime('now')),
                last_sent TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Subscription table init failed: {e}")

_init_subs_table()


# ── POST /api/chat ────────────────────────────────────────────────────────────

@router.post("/api/chat")
async def chat(body: ChatRequest):
    if not GROQ_API_KEY:
        raise HTTPException(503, "Cricket assistant not configured (missing GROQ_API_KEY)")

    # Build messages for Groq
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in body.messages[-12:]:  # cap context to 12 turns
        messages.append({"role": m.role, "content": m.content})

    payload = {
        "model":       GROQ_MODEL,
        "messages":    messages,
        "max_tokens":  400,
        "temperature": 0.7,
        "stream":      False,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                GROQ_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type":  "application/json",
                },
            )
        if resp.status_code != 200:
            logger.error(f"Groq error {resp.status_code}: {resp.text}")
            raise HTTPException(502, "Cricket assistant temporarily unavailable")

        data    = resp.json()
        reply   = data["choices"][0]["message"]["content"]
        tokens  = data.get("usage", {}).get("total_tokens", 0)
        logger.info(f"Groq chat: {tokens} tokens")
        return {"reply": reply}

    except httpx.TimeoutException:
        raise HTTPException(504, "Cricket assistant timed out — please try again")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Groq chat error: {e}")
        raise HTTPException(500, "Cricket assistant error")


# ── POST /api/subscribe ───────────────────────────────────────────────────────

@router.post("/api/subscribe")
async def subscribe(body: SubscribeRequest):
    email = body.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(400, "Invalid email address")

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """INSERT INTO email_subscriptions (email, name, active)
               VALUES (?, ?, 1)
               ON CONFLICT(email) DO UPDATE SET active=1, name=excluded.name""",
            (email, body.name.strip()[:80])
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Subscribe DB error: {e}")
        raise HTTPException(500, "Could not save subscription")

    # Send welcome email (best-effort)
    try:
        _send_welcome_email(email, body.name)
    except Exception as e:
        logger.warning(f"Welcome email failed (non-fatal): {e}")

    return {"message": "Subscribed! You'll receive weekly cricket tips."}


# ── DELETE /api/unsubscribe ───────────────────────────────────────────────────

@router.delete("/api/unsubscribe")
async def unsubscribe(body: UnsubscribeRequest):
    email = body.email.strip().lower()
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE email_subscriptions SET active=0 WHERE email=?", (email,)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Unsubscribe DB error: {e}")
        raise HTTPException(500, "Could not update subscription")

    return {"message": "Unsubscribed. You won't receive further cricket tips."}


# ── Email sending helpers ─────────────────────────────────────────────────────

def _send_welcome_email(email: str, name: str):
    if not GMAIL_USER or not GMAIL_PASS:
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Welcome to BattingEdge Weekly Tips! 🏏"
    msg["From"]    = f"BattingEdge <{GMAIL_USER}>"
    msg["To"]      = email

    html = f"""
    <div style="background:#0a0a0f;color:#fff;font-family:Inter,sans-serif;padding:32px;border-radius:12px;max-width:600px;margin:0 auto">
      <h1 style="color:#00d4ff;margin-bottom:8px">Welcome to BattingEdge! 🏏</h1>
      <p style="color:#9ca3af">Hi {name},</p>
      <p style="color:#d1d5db;line-height:1.6">
        You've subscribed to <strong style="color:#00ff88">weekly cricket tips</strong> powered by AI.
        Every week you'll receive:
      </p>
      <ul style="color:#d1d5db;line-height:2">
        <li>🏏 Shot technique tips from MCC/ECB standards</li>
        <li>⚡ Batting drills to improve your game</li>
        <li>📊 Cricket facts and history</li>
      </ul>
      <p style="color:#6b7280;font-size:12px;margin-top:24px">
        To unsubscribe, visit your BattingEdge settings page at any time.
      </p>
    </div>
    """
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_USER, GMAIL_PASS)
        s.sendmail(GMAIL_USER, email, msg.as_string())


async def generate_and_send_weekly_tips():
    """Called by the scheduler every Sunday. Generates Groq tips and emails active subscribers."""
    if not GROQ_API_KEY:
        logger.warning("Weekly tips skipped: no GROQ_API_KEY")
        return

    # Generate tip content
    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content":
         "Give me this week's cricket batting tip. Include: (1) a technique focus with a drill, "
         "(2) a motivational quote from a Pakistani legend, and (3) one fun cricket fact. "
         "Format nicely in 150 words max."}
    ]
    tip_text = "No tip available this week."
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                GROQ_URL,
                json={"model": GROQ_MODEL, "messages": prompt, "max_tokens": 300},
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            )
        if resp.status_code == 200:
            tip_text = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq weekly tip generation failed: {e}")

    # Fetch subscribers
    try:
        conn  = sqlite3.connect(DB_PATH)
        rows  = conn.execute(
            "SELECT email, name FROM email_subscriptions WHERE active=1"
        ).fetchall()
        conn.close()
    except Exception as e:
        logger.error(f"Weekly tips: DB fetch failed: {e}")
        return

    sent = 0
    for (email, name) in rows:
        try:
            _send_tip_email(email, name, tip_text)
            conn2 = sqlite3.connect(DB_PATH)
            conn2.execute(
                "UPDATE email_subscriptions SET last_sent=? WHERE email=?",
                (datetime.utcnow().isoformat(), email)
            )
            conn2.commit()
            conn2.close()
            sent += 1
        except Exception as e:
            logger.warning(f"Weekly tip email failed for {email}: {e}")

    logger.info(f"Weekly tips sent to {sent}/{len(rows)} subscribers")


def _send_tip_email(email: str, name: str, tip: str):
    if not GMAIL_USER or not GMAIL_PASS:
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Weekly Cricket Tip from BattingEdge 🏏"
    msg["From"]    = f"BattingEdge <{GMAIL_USER}>"
    msg["To"]      = email

    html = f"""
    <div style="background:#0a0a0f;color:#fff;font-family:Inter,sans-serif;padding:32px;border-radius:12px;max-width:600px;margin:0 auto">
      <h2 style="color:#00d4ff">This Week's Cricket Tip 🏏</h2>
      <p style="color:#9ca3af">Hi {name},</p>
      <div style="background:#141420;border:1px solid rgba(0,212,255,0.2);border-radius:12px;padding:20px;margin:16px 0">
        <p style="color:#d1d5db;line-height:1.8;white-space:pre-line">{tip}</p>
      </div>
      <a href="{os.getenv('FRONTEND_URL','http://localhost:5173')}/analyze"
         style="display:inline-block;background:#00d4ff;color:#000;padding:12px 24px;border-radius:8px;font-weight:bold;text-decoration:none;margin-top:12px">
        Analyze Your Batting
      </a>
      <p style="color:#4b5563;font-size:11px;margin-top:24px">
        Unsubscribe in BattingEdge → Settings → Email Preferences.
      </p>
    </div>
    """
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_USER, GMAIL_PASS)
        s.sendmail(GMAIL_USER, email, msg.as_string())
