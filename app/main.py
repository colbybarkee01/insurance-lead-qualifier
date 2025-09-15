import os, json, re, datetime, asyncio
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx

# -------------------------------------------------------------------
# Setup
# -------------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")  # safe default
# CRM / webhook configuration
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL", "")
CRM_API_KEY = os.getenv("CRM_API_KEY", "")



app = FastAPI(title="Insurance Lead Qualifier")

SYSTEM = (
    "You are a helpful insurance intake assistant. "
    "Gather the user's details conversationally: Name, Age, State, "
    "Coverage type (health/life/auto), Existing provider, Budget/month, "
    "Urgency (1–5). Be concise and friendly—one or two questions per turn."
)

# -------------------------------------------------------------------
# Pydantic models
# -------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    thread_id: str = Field(..., description="Client-provided thread id to group a conversation")
    messages: List[ChatMessage]

class ExtractedLead(BaseModel):
    name: str | None = None
    age: int | None = None
    state: str | None = None
    coverage: str | None = None
    provider: str | None = None
    budget: float | None = None
    urgency: int | None = None
    score: float | None = None

# -------------------------------------------------------------------
# OpenAI helper (used as a *fallback*)
# -------------------------------------------------------------------
async def call_openai(messages: list[dict]) -> str:
    if not OPENAI_API_KEY:
        return "[Missing OPENAI_API_KEY]"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": MODEL,
        "messages": messages,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post("https://api.openai.com/v1/chat/completions",
                                  headers=headers, json=payload)
            r.raise_for_status()
            j = r.json()
            return j["choices"][0]["message"]["content"]
    except Exception as e:
        # We treat any failure (including 429) as a signal to use local logic
        return f"[LLM error: {e}]"

async def post_to_crm(lead: dict) -> tuple[int, str]:
    """
    Sends the structured lead to a CRM/webhook.
    Returns (status_code, short_message). If CRM_WEBHOOK_URL is empty, returns (0, reason).
    """
    if not CRM_WEBHOOK_URL:
        return 0, "CRM webhook not configured"

    headers = {"Content-Type": "application/json"}
    if CRM_API_KEY:
        headers["Authorization"] = f"Bearer {CRM_API_KEY}"

    payload = {
        "source": "insurance-lead-qualifier",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "lead": lead,
    }

    last_err = ""
    for _ in range(3):  # simple retry
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(CRM_WEBHOOK_URL, headers=headers, json=payload)
                return r.status_code, (r.text[:200] if r.text else "")
        except Exception as e:
            last_err = str(e)
            await asyncio.sleep(0.5)

    return -1, last_err

# -------------------------------------------------------------------
# Simple deterministic parser (local logic)
# -------------------------------------------------------------------
STATES = set("""
AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO
MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC
""".split())

def extract_entities(text: str) -> dict:
    """
    Very small rule-based extractor for a demo.
    Pulls out: coverage type, budget, age, US state, urgency (1–5), provider.
    Works on free text like:
      "Hi, I need life insurance in CA. I'm 29. $120/month, urgency 4. Provider is Acme."
    """
    t = text.lower()

    # coverage
    coverage = None
    for key in ["life", "auto", "car", "home", "renters", "health", "business"]:
        if key in t:
            coverage = "auto" if key == "car" else key
            break

    # budget (prefer amounts near the word "budget"; else fall back to any $amount[/mo])
    budget = None
    m = re.search(r"budget[^0-9]{0,12}\$?\s*([0-9]+(?:\.[0-9]{1,2})?)", t)
    if not m:
        m = re.search(r"\$\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:/mo|per month|monthly)?", t)
    if m:
        try:
            budget = float(m.group(1))
        except:
            pass

    # age (16–99)
    age = None
    m = re.search(r"\b(1[6-9]|[2-9][0-9])\b", t)
    if m:
        age = int(m.group(1))

    # urgency 1–5 (e.g., "urgency 4", "urgency is 4", "4/5")
    urgency = None
    m = re.search(r"\burgency\b[^0-9]{0,8}([1-5])\b", t)
    if not m:
        m = re.search(r"\b([1-5])\s*(?:/|of)\s*5\b", t)
    if m:
        try:
            urgency = int(m.group(1))
        except:
            pass

    # state (prefer "state XX"; otherwise only ALL-CAPS two-letter codes)
    state = None
    m = re.search(r"\bstate[:\s]+([A-Za-z]{2})\b", text, flags=re.IGNORECASE)
    if m and m.group(1).upper() in STATES:
        state = m.group(1).upper()
    else:
        m = re.search(r"\b([A-Z]{2})\b", text)
        if m and m.group(1).upper() in STATES:
            state = m.group(1).upper()

    # provider (simple heuristic: "... provider is <word>")
    provider = None
    m = re.search(r"provider\s+is\s+([A-Za-z][A-Za-z0-9\- ]{1,40})", t)
    if m:
        provider = m.group(1).strip().title()

    return {
        "coverage": coverage,
        "budget": budget,
        "age": age,
        "state": state,
        "urgency": urgency,
        "provider": provider,
    }

def next_question(entities: dict) -> str | None:
    if not entities.get("coverage"):
        return "What kind of insurance do you need (life, auto, home, renters, health, or business)?"
    if not entities.get("state"):
        return "Which U.S. state are you in? (2–letter code like CA or TX)"
    if not entities.get("age"):
        return "What is your age?"
    if entities.get("budget") is None:
        return "What is your monthly budget in dollars?"
    if entities.get("urgency") is None:
        return "On a scale of 1–5, how urgent is your request?"
    return None

def score_lead(entities: dict) -> float:
    score = 0
    if entities.get("coverage"): score += 1
    if entities.get("state"): score += 1
    if entities.get("age"): score += 1
    if entities.get("budget") is not None: score += 1
    if entities.get("urgency") is not None: score += 1
    if (entities.get("budget") or 0) >= 100: score += 1
    if (entities.get("urgency") or 0) >= 4: score += 1
    return min(score, 10)

def local_qualifier_reply(user_msg: str) -> str:
    e = extract_entities(user_msg)
    nq = next_question(e)
    if nq:
        collected = ", ".join(f"{k}={v}" for k, v in e.items() if v not in (None, ""))
        prefix = f"Got it ({collected}). " if collected else ""
        return prefix + nq

    s = score_lead(e)
    return (
        "Thanks! Here’s what I captured:\n"
        f"- Coverage: {e['coverage']}\n"
        f"- State: {e['state']}\n"
        f"- Age: {e['age']}\n"
        f"- Budget: ${e['budget']:.0f}/mo\n"
        f"- Urgency: {e['urgency']}/5\n"
        f"Lead score: {s}/10.\n"
        "Want me to submit this to an agent and have someone contact you?"
    )
# ---------------------------------------------------------------------
# CRM helper (optional; safe no-op if env vars are missing)
# ---------------------------------------------------------------------
async def post_to_crm(lead: dict) -> tuple[str, str]:
    """
    Send the structured lead to a CRM/webhook.
    Returns (status, note) where:
      - status: "sent" | "skipped" | "error"
      - note: short detail (HTTP code, reason, etc.)
    """
    url = os.getenv("CRM_WEBHOOK_URL", "").strip()
    api_key = os.getenv("CRM_API_KEY", "").strip()

    # If you haven’t set these yet, don’t fail the request—just report "skipped".
    if not url:
        return "skipped", "No CRM_WEBHOOK_URL set"

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "lead": lead,
        "source": "insurance-lead-qualifier"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, json=payload, headers=headers)
            if 200 <= r.status_code < 300:
                return "sent", f"{r.status_code}"
            else:
                # Trim body so errors don’t get too big
                return "error", f"status={r.status_code} body={r.text[:200]}"
    except Exception as e:
        return "error", f"exception: {e}"

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.post("/chat")
async def chat(req: ChatRequest):
    user_msg = req.messages[-1].content if req.messages else ""

    # 1) Local rule-based qualifier (no LLM)
    local = local_qualifier_reply(user_msg)

    # 2) Try LLM; if it fails (e.g., 429), fall back to local
    try:
        llm = await call_openai(
            [{"role": "system", "content": SYSTEM}] + [m.model_dump() for m in req.messages]
        )
        if llm and "[LLM error" not in llm and len(llm.strip()) > 10:
            return {"reply": llm}
    except Exception:
        pass

    return {"reply": local}

@app.post("/extract")
async def extract(payload: dict):
    text = payload.get("transcript", "")
    # produce a structured lead object
    e = extract_entities(text)
    lead = ExtractedLead(**e)
    # IMPORTANT: score_lead expects a dict
    lead.score = score_lead(lead.model_dump())

    # Send to CRM/webhook (non-blocking retry inside)
    status, note = await post_to_crm(lead.model_dump())

    # Map to clean CRM-friendly fields
    out = {
        "customer_name":  lead.name,
        "customer_age":   lead.age,
        "state_code":     lead.state,
        "insurance_type": lead.coverage,
        "current_provider": lead.provider,
        "monthly_budget": lead.budget,
        "priority_level": lead.urgency,
        "lead_score":     lead.score,
        "crm_status":     status,
        "crm_note":       note
    }
    return out

