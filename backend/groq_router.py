"""
Groq AI endpoints:
  POST /api/chat          — cricket chatbot (BESSA)
  generate_coaching_commentary() — sync utility called from background task
"""
import os
import logging
from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import Groq

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


# ── Coaching commentary ───────────────────────────────────────────────────────

_COACHING_MODEL = "llama-3.1-8b-instant"

_COACHING_SYSTEM_PROMPT = """\
You are an ECB Level 2 certified batting coach with 15 years of professional \
coaching experience across county and international cricket. You provide precise, \
evidence-based technical feedback grounded in ECB and MCC batting methodology.

Your commentary must:
- Reference specific biomechanical data points from the provided analysis \
(joint angles, scores, individual check outcomes)
- Explain how each technical finding affects shot execution, timing, and \
run-scoring ability in a match context
- Factor in the delivery context (bowling type, ball pitch) when provided, \
addressing appropriate footwork and shot selection for that scenario
- Acknowledge genuine strengths before prescribing corrections
- Prescribe specific, drill-ready corrections the batter can apply in their \
next net session
- Use correct coaching terminology: head position, weight transfer, bat arc, \
trigger movement, high elbow, body coil, follow-through

Write exactly 3-4 paragraphs of flowing prose. No bullet points, no headers, \
no markdown. Address the batter directly in the second person ("you", "your").\
"""


def _build_user_message(analysis_result: dict, context: Optional[dict]) -> str:
    """Serialise the analysis result into a structured coaching brief."""
    shot       = analysis_result.get("prediction", "Unknown Shot")
    confidence = analysis_result.get("confidence", 0.0)
    fa         = analysis_result.get("form_analysis", {})
    score      = fa.get("overall_score", 0)
    grade      = fa.get("grade", "N/A")
    checks     = fa.get("checks", [])
    strengths  = fa.get("strengths", [])
    improvements = fa.get("key_improvements", [])

    # Biomechanical checks table
    check_lines = []
    for c in checks:
        name   = c.get("name", "")
        value  = c.get("value", "N/A")
        ideal  = c.get("ideal_range", "N/A")
        status = c.get("status", "")
        advice = c.get("advice", "")
        check_lines.append(
            f"  • {name}: measured {value} (ideal {ideal}) — {status}. {advice}"
        )
    checks_block = "\n".join(check_lines) if check_lines else "  (no check data)"

    # Optional delivery context
    bowling = (context or {}).get("bowling_type", "unknown")
    pitch   = (context or {}).get("ball_pitch",   "unknown")
    context_parts = []
    if bowling != "unknown":
        context_parts.append(f"bowling type: {bowling}")
    if pitch != "unknown":
        context_parts.append(f"ball pitch: {pitch}")
    context_line = (
        f"\nDelivery context — {', '.join(context_parts)}." if context_parts else ""
    )

    strengths_line    = ", ".join(strengths)    if strengths    else "none recorded"
    improvements_line = ", ".join(improvements) if improvements else "none recorded"

    return (
        f"Shot analysed: {shot}\n"
        f"Overall score: {score}/100  |  Grade: {grade}  |  "
        f"Model confidence: {confidence:.1f}%"
        f"{context_line}\n\n"
        f"Biomechanical check results:\n{checks_block}\n\n"
        f"Identified strengths: {strengths_line}\n"
        f"Key areas for improvement: {improvements_line}\n\n"
        "Write 3-4 paragraphs of coaching commentary based on the above. "
        "If delivery context was provided, factor it into footwork and "
        "shot-selection advice."
    )


def generate_coaching_commentary(
    analysis_result: dict,
    context: Optional[dict] = None,
) -> str:
    """
    Generate contextual coaching commentary for a completed batting analysis.

    Args:
        analysis_result: Full prediction dict from StackingEnsembleClassifier.predict_video()
        context: Optional {"bowling_type": str, "ball_pitch": str}

    Returns:
        3-4 paragraph coaching commentary string, or a brief fallback on error.
    """
    if not GROQ_API_KEY:
        logger.warning("generate_coaching_commentary: GROQ_API_KEY not set — skipping")
        return ""

    user_message = _build_user_message(analysis_result, context)

    try:
        client = Groq(api_key=GROQ_API_KEY, timeout=20.0)
        response = client.chat.completions.create(
            model=_COACHING_MODEL,
            messages=[
                {"role": "system",  "content": _COACHING_SYSTEM_PROMPT},
                {"role": "user",    "content": user_message},
            ],
            max_tokens=700,
            temperature=0.65,
            stream=False,
        )
        commentary = response.choices[0].message.content.strip()
        tokens     = getattr(response.usage, "total_tokens", "?")
        logger.info(f"Coaching commentary generated: {tokens} tokens")
        return commentary

    except Exception as exc:
        logger.warning(f"generate_coaching_commentary failed ({exc}); returning empty string")
        return ""
