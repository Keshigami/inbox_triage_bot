"""Ops inbox triage: email text -> category, urgency, summary, route. Pure functions, validated with pydantic.

LLM calls go through common/llm.py (Anthropic by default, OpenAI / Gemini via env, deterministic offline mode
with no key). Routing is SIMULATED: `simulate_routing` only returns log lines, nothing is sent anywhere.
"""
from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import llm  # noqa: E402  (sys.path set above)

CATEGORIES = ["Sales", "Support", "Billing", "Partnerships", "Spam"]
URGENCIES = ["Low", "Medium", "High"]
ROUTES = ["CRM", "Slack #support", "Slack #finance", "Slack #partnerships", "Ignore"]
ROUTE_FOR_CATEGORY = {
    "Sales": "CRM",
    "Support": "Slack #support",
    "Billing": "Slack #finance",
    "Partnerships": "Slack #partnerships",
    "Spam": "Ignore",
}
Category = Literal["Sales", "Support", "Billing", "Partnerships", "Spam"]
Urgency = Literal["Low", "Medium", "High"]
Route = Literal["CRM", "Slack #support", "Slack #finance", "Slack #partnerships", "Ignore"]

SYSTEM_PROMPT = (
    "You are an operations inbox triage bot for a B2B SaaS company. Read one email and return structured metadata. "
    f"category is one of {', '.join(CATEGORIES)}. urgency is one of {', '.join(URGENCIES)}: High when revenue, "
    "an outage or a deadline inside 48 hours is involved, Medium for normal requests, Low for FYI or newsletters. "
    "summary is one sentence, under 25 words, naming who wants what. "
    f"route is one of {', '.join(ROUTES)}: Sales leads go to the CRM, support and billing to their Slack channels, "
    "partnership and press to Slack #partnerships, spam and cold outreach are ignored."
)
SCHEMA_HINT = {
    "category": "|".join(CATEGORIES),
    "urgency": "|".join(URGENCIES),
    "summary": "<one sentence>",
    "route": "|".join(ROUTES),
}


class EmailTriage(BaseModel):
    category: Category = "Support"
    urgency: Urgency = "Medium"
    summary: str = ""
    route: Route = "Slack #support"
    provider: str = "offline"
    model: str = "offline"

    @field_validator("category", mode="before")
    @classmethod
    def _cat(cls, v):
        s = str(v or "").strip().capitalize()
        return s if s in CATEGORIES else "Support"

    @field_validator("urgency", mode="before")
    @classmethod
    def _urg(cls, v):
        s = str(v or "").strip().capitalize()
        aliases = {"Urgent": "High", "Critical": "High", "Normal": "Medium"}
        s = aliases.get(s, s)
        return s if s in URGENCIES else "Medium"

    @model_validator(mode="before")
    @classmethod
    def _route_from_category(cls, data):
        """Normalise the route; when it is missing or unknown, derive it from the (normalised) category."""
        if not isinstance(data, dict):
            return data
        data = dict(data)
        raw = str(data.get("route") or "").strip()
        low = raw.lower().replace("#", "").replace("slack:", "").replace("slack ", "").strip()
        match = next((r for r in ROUTES if low == r.lower().replace("#", "").replace("slack ", "")), None)
        if match is None:
            cat = str(data.get("category") or "").strip().capitalize()
            match = ROUTE_FOR_CATEGORY.get(cat, "Slack #support")
        data["route"] = match
        return data

    @field_validator("summary", mode="before")
    @classmethod
    def _sum(cls, v):
        return " ".join(str(v or "").split())[:300]


def route_for(category: str) -> str:
    return ROUTE_FOR_CATEGORY.get(category, "Slack #support")


def triage_email(email_text: str) -> EmailTriage:
    """Triage one email. Raises ValueError on empty text."""
    text = (email_text or "").strip()
    if not text:
        raise ValueError("email text is empty")
    raw = llm.complete_json(SYSTEM_PROMPT, text, schema_hint=SCHEMA_HINT)
    return EmailTriage(
        category=raw.get("category"),
        urgency=raw.get("urgency"),
        summary=raw.get("summary", ""),
        route=raw.get("route", ""),
        provider=llm.provider(),
        model=llm.model(),
    )


def simulate_routing(result: EmailTriage, email_id: str = "email") -> list[str]:
    """Return the log lines a real router would emit. Nothing is sent: these are labelled simulations."""
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [f"{ts} [SIMULATED] triage {email_id}: category={result.category} urgency={result.urgency}"]
    if result.route == "CRM":
        lines.append(f"{ts} [SIMULATED] CRM: would create lead from {email_id} (no API call made)")
    elif result.route.startswith("Slack"):
        ch = result.route.split(" ", 1)[1]
        lines.append(f"{ts} [SIMULATED] Slack {ch}: would post '{result.summary[:80]}' (no message sent)")
    else:
        lines.append(f"{ts} [SIMULATED] ignore: {email_id} archived, no action")
    if result.urgency == "High":
        lines.append(f"{ts} [SIMULATED] pager: would flag {email_id} as High urgency for the on-call owner")
    return lines


SAMPLE_EMAILS: list[dict] = [
    {
        "id": "S1",
        "from": "john@acme.example",
        "subject": "Enterprise plan for 50 seats",
        "body": "Hi team, I'm interested in your premium plan for 50 users. We need SSO and an invoice-based contract. "
        "Can we hop on a call this week? - John, Head of Ops at Acme Corp",
        "expected": "Sales",
    },
    {
        "id": "S2",
        "from": "maria@northwind.example",
        "subject": "Dashboard down since 9am",
        "body": "Our whole team gets a 500 error on the dashboard since this morning. We have a board meeting at 2pm "
        "and need the reports. Please treat as urgent.",
        "expected": "Support",
    },
    {
        "id": "S3",
        "from": "accounts@globex.example",
        "subject": "Duplicate invoice #4821",
        "body": "We were charged twice for October (invoices 4821 and 4822). Please refund the duplicate and confirm "
        "which invoice stays valid for our records.",
        "expected": "Billing",
    },
    {
        "id": "S4",
        "from": "press@techdaily.example",
        "subject": "Co-marketing webinar?",
        "body": "We run a monthly webinar for RevOps leaders and would love to feature your product in December. "
        "Open to a joint session and a case study?",
        "expected": "Partnerships",
    },
    {
        "id": "S5",
        "from": "winner@lottery-prize.example",
        "subject": "You have been selected!!!",
        "body": "Congratulations! Claim your $5,000 gift card now by confirming your bank details at the link below. "
        "Offer expires in 24 hours!!!",
        "expected": "Spam",
    },
    {
        "id": "S6",
        "from": "dev@initech.example",
        "subject": "Question about API rate limits",
        "body": "Quick one: what is the rate limit on the /export endpoint for the Team plan? We see 429s when we "
        "run nightly syncs. Not blocking, just planning.",
        "expected": "Support",
    },
]


def triage_many(emails: list[dict]) -> list[dict]:
    """Triage a batch and return flat rows for a table."""
    rows = []
    for e in emails:
        r = triage_email(e["body"])
        rows.append({
            "id": e["id"], "from": e["from"], "subject": e["subject"], "category": r.category,
            "urgency": r.urgency, "route": r.route, "summary": r.summary, "expected": e.get("expected", ""),
            "match": r.category == e.get("expected", ""),
        })
    return rows
