"""
Groq AI endpoints:
  POST /api/chat                      — cricket chatbot (BESSA)
  generate_coaching_commentary()      — async, JSON-structured coaching output
  _generate_coaching_commentary_legacy() — retained for any callers not yet
                                          migrated; Task C will replace usages
"""
import json
import logging
import os
import re
from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from groq import Groq
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


# ── Coaching commentary ───────────────────────────────────────────────────────

_COACHING_MODEL = "llama-3.1-8b-instant"

# System prompt for the new JSON-structured coaching function
_COACHING_SYSTEM_PROMPT_V2 = (
    "You are an ECB Level 2 certified batting coach with 15 years experience "
    "coaching Pakistani grassroots cricketers aged 14-25. You give honest, "
    "encouraging, actionable feedback. Reference Pakistani cricket context "
    "naturally where relevant (Babar Azam, PSL, domestic cricket). You "
    "understand biomechanics but explain things in plain language. You never "
    "say a player is bad — you say what specifically to improve and how."
)

# Legacy system prompt retained for _generate_coaching_commentary_legacy
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
    """Serialise the analysis result into a structured coaching brief (legacy helper)."""
    shot       = analysis_result.get("prediction", "Unknown Shot")
    confidence = analysis_result.get("confidence", 0.0)
    fa         = analysis_result.get("form_analysis", {})
    score      = fa.get("overall_score", 0)
    grade      = fa.get("grade", "N/A")
    checks     = fa.get("checks", [])
    strengths  = fa.get("strengths", [])
    improvements = fa.get("key_improvements", [])

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


def _generate_coaching_commentary_legacy(
    analysis_result: dict,
    context: Optional[dict] = None,
) -> str:
    """
    Legacy sync coaching commentary (prose string output).
    Retained until inference_v9_5.py is updated in Task C.
    New callers should use generate_coaching_commentary() instead.
    """
    if not GROQ_API_KEY:
        logger.warning("_generate_coaching_commentary_legacy: GROQ_API_KEY not set — skipping")
        return ""

    user_message = _build_user_message(analysis_result, context)

    try:
        client = Groq(api_key=GROQ_API_KEY, timeout=20.0)
        response = client.chat.completions.create(
            model=_COACHING_MODEL,
            messages=[
                {"role": "system", "content": _COACHING_SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=700,
            temperature=0.65,
            stream=False,
        )
        commentary = response.choices[0].message.content.strip()
        tokens     = getattr(response.usage, "total_tokens", "?")
        logger.info(f"Legacy coaching commentary generated: {tokens} tokens")
        return commentary

    except Exception as exc:
        logger.warning(f"_generate_coaching_commentary_legacy failed ({exc}); returning empty string")
        return ""


# ── New async JSON-structured coaching commentary ─────────────────────────────

async def generate_coaching_commentary(
    analysis_result: dict,
    bowling_context: str = "unknown",
    ball_pitch: str = "unknown",
    camera_context: str = "unknown",
    feature_completeness: float = 1.0,
    player_history: list = None,
) -> Optional[dict]:
    """
    Generate JSON-structured coaching commentary via Groq.

    Parameters
    ----------
    analysis_result      : dict returned by ShotRules.analyze_shot() or the
                           full predict_video() result (checks nested under
                           form_analysis or at top level — both handled)
    bowling_context      : fast | spin | medium | tape_ball | default | unknown
    ball_pitch           : good_length | short | full | yorker | unknown
    camera_context       : front_on | angled | side_on | unknown
    feature_completeness : fraction of landmarks detected (0.0–1.0)
    player_history       : list of previous analysis dicts with 'overall_score'

    Returns
    -------
    dict with keys: headline, coaching_paragraphs, quick_tips,
                    pakistan_player_reference, next_session_focus
    Returns None if GROQ_API_KEY is not set.
    Returns fallback dict on Groq/parse errors.
    """
    if not GROQ_API_KEY:
        logger.warning("generate_coaching_commentary: GROQ_API_KEY not set — returning None")
        return None

    if player_history is None:
        player_history = []

    # Handle insufficient data from Task A's new status field
    if analysis_result.get("status") == "insufficient_data":
        return {
            "headline": "Not enough data to analyse this shot",
            "coaching_paragraphs": [
                analysis_result.get(
                    "message",
                    "Too few body landmarks were detected to produce a reliable analysis."
                )
            ],
            "quick_tips": ["Ensure your full body is visible in the frame"],
            "pakistan_player_reference": "",
            "next_session_focus": "Film from a better angle with full body in frame",
        }

    # Resolve nested vs flat dict — predict_video() wraps under form_analysis
    fa     = analysis_result.get("form_analysis", analysis_result)
    shot   = analysis_result.get("prediction", fa.get("shot_type", "Unknown Shot"))
    conf   = analysis_result.get("confidence", fa.get("confidence", 0.0))
    score  = fa.get("overall_score", analysis_result.get("overall_score", 0))
    grade  = fa.get("grade",         analysis_result.get("grade", "N/A"))
    checks = fa.get("checks",        analysis_result.get("checks", []))
    key_improvements = fa.get("key_improvements", analysis_result.get("key_improvements", []))
    perf_level       = fa.get("performance_level", analysis_result.get("performance_level", ""))

    # Build checks block — include bowling_adjusted tag from Task A
    check_lines = []
    for c in checks:
        line = (
            f"  • {c.get('name', '')}: measured {c.get('value', 'N/A')} "
            f"(ideal {c.get('ideal_range', 'N/A')}) — {c.get('status', '')}. "
            f"{c.get('advice', '')}"
        )
        if c.get("bowling_adjusted"):
            line += f" [threshold adjusted for {bowling_context} bowling]"
        if c.get("camera_warning"):
            line += " [camera tolerance applied]"
        check_lines.append(line)
    checks_block = "\n".join(check_lines) if check_lines else "  (no check data)"

    # Delivery context block
    ctx_parts = []
    if bowling_context not in ("unknown", "default", ""):
        ctx_parts.append(f"Bowling type: {bowling_context}")
    if ball_pitch not in ("unknown", ""):
        ctx_parts.append(f"Ball pitch: {ball_pitch}")
    if camera_context not in ("unknown", ""):
        ctx_parts.append(f"Camera angle: {camera_context}")
    ctx_block = "\n".join(ctx_parts) if ctx_parts else "Not specified"

    # Feature completeness warning
    fc_note = ""
    if feature_completeness < 0.80:
        fc_note = (
            f"\nWARNING: Only {feature_completeness:.0%} of expected body "
            "landmarks were detected. Analysis may be less precise than usual."
        )

    # Player history comparison
    history_note = ""
    if player_history:
        prev_scores = [
            e.get("overall_score")
            for e in player_history
            if isinstance(e.get("overall_score"), (int, float))
        ]
        if prev_scores and score is not None:
            last = prev_scores[-1]
            diff = score - last
            if diff > 0:
                history_note = (
                    f"\nPROGRESS: Score improved by {diff} points from last "
                    f"session (was {last}, now {score}). Acknowledge this."
                )
            elif diff < 0:
                history_note = (
                    f"\nREGRESSION: Score dropped {abs(diff)} points from last "
                    f"session (was {last}, now {score}). Address this in commentary."
                )
            else:
                history_note = (
                    f"\nCONSISTENCY: Score unchanged from last session ({score})."
                )

    bc_label = bowling_context if bowling_context not in ("unknown", "") else "general"

    user_message = (
        f"Shot analysed: {shot}\n"
        f"Model confidence: {conf:.1f}%\n"
        f"Overall score: {score}/100 | Grade: {grade} | Level: {perf_level}\n"
        f"\nDelivery context:\n{ctx_block}"
        f"{fc_note}"
        f"{history_note}"
        f"\n\nBiomechanical check results:\n{checks_block}"
        "\n\nReturn ONLY valid JSON — no markdown, no backticks, no code fences."
        " Use exactly this structure:\n"
        '{\n'
        '  "headline": "One sentence verdict, max 15 words",\n'
        '  "coaching_paragraphs": [\n'
        '    "What the batter did well — cite specific measurements, 2-3 sentences",\n'
        '    "Primary area to improve — include a specific drill, 2-3 sentences",\n'
        f'    "{bc_label.capitalize()} bowling-specific tip — 2-3 sentences"\n'
        '  ],\n'
        '  "quick_tips": ["tip 1 max 10 words", "tip 2 max 10 words", "tip 3 max 10 words"],\n'
        '  "pakistan_player_reference": "Pakistani batter known for this shot, 1-2 sentences",\n'
        '  "next_session_focus": "One specific thing to practise next session"\n'
        '}'
    )

    payload = {
        "model":       _COACHING_MODEL,
        "messages":    [
            {"role": "system", "content": _COACHING_SYSTEM_PROMPT_V2},
            {"role": "user",   "content": user_message},
        ],
        "max_tokens":  700,
        "temperature": 0.65,
        "stream":      False,
    }

    fallback = {
        "headline": f"{perf_level} {grade} technique".strip(),
        "coaching_paragraphs": (
            key_improvements if key_improvements
            else ["Keep working on your technique."]
        ),
        "quick_tips": [],
        "pakistan_player_reference": "",
        "next_session_focus": (
            key_improvements[0] if key_improvements else "Keep practicing"
        ),
    }

    # --- Groq request ---
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                GROQ_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type":  "application/json",
                },
            )

        if resp.status_code != 200:
            logger.error(
                f"generate_coaching_commentary: Groq {resp.status_code}: {resp.text}"
            )
            return fallback

        data   = resp.json()
        raw    = data["choices"][0]["message"]["content"].strip()
        tokens = data.get("usage", {}).get("total_tokens", 0)
        logger.info(f"Coaching commentary generated: {tokens} tokens")

    except httpx.TimeoutException:
        logger.warning("generate_coaching_commentary: Groq timed out (10 s)")
        return fallback
    except Exception as exc:
        logger.warning(f"generate_coaching_commentary: request failed ({exc})")
        return fallback

    # --- JSON parse (with accidental fence stripping) ---
    commentary = None
    try:
        commentary = json.loads(raw)
    except json.JSONDecodeError:
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            commentary = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(
                "generate_coaching_commentary: JSON parse failed, using fallback"
            )
            return fallback

    # Ensure required keys exist
    commentary.setdefault("headline",                  fallback["headline"])
    commentary.setdefault("coaching_paragraphs",       fallback["coaching_paragraphs"])
    commentary.setdefault("quick_tips",                [])
    commentary.setdefault("pakistan_player_reference", "")
    commentary.setdefault("next_session_focus",        fallback["next_session_focus"])

    paras = commentary["coaching_paragraphs"]

    # Post-processing rule 1: spin + hip_rotation < 65 → mention footwork in para 2
    if bowling_context == "spin":
        hip_score = next(
            (
                c.get("score_pct", 100)
                for c in checks
                if "hip" in c.get("name", "").lower()
            ),
            100,
        )
        if hip_score < 65 and len(paras) >= 2:
            if "footwork" not in paras[1].lower():
                paras[1] = (
                    "Against spin, getting your footwork right unlocks better "
                    "hip rotation. " + paras[1]
                )

    # Post-processing rule 3: fast + elbow_angle < 65 → add compact swing tip
    if bowling_context == "fast":
        elbow_score = next(
            (
                c.get("score_pct", 100)
                for c in checks
                if "elbow" in c.get("name", "").lower()
            ),
            100,
        )
        if elbow_score < 65:
            tip = "Compact swing is OK vs pace"
            if tip not in commentary["quick_tips"]:
                commentary["quick_tips"].append(tip)

    return commentary
