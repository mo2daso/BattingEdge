"""
Groq AI endpoints:
  POST /api/chat — cricket chatbot (BESSA)
"""
import os
import logging
from typing import List

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("GroqRouter")
router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.1-8b-instant"

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


# ── POST /api/chat ────────────────────────────────────────────────────────────

@router.post("/api/chat")
async def chat(body: ChatRequest):
    if not GROQ_API_KEY:
        raise HTTPException(503, "Cricket assistant not configured (missing GROQ_API_KEY)")

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

        data   = resp.json()
        reply  = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        logger.info(f"Groq chat: {tokens} tokens")
        return {"reply": reply}

    except httpx.TimeoutException:
        raise HTTPException(504, "Cricket assistant timed out — please try again")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Groq chat error: {e}")
        raise HTTPException(500, "Cricket assistant error")
