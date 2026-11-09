"""Ops Inbox Triage Bot, Streamlit UI. Run: uv run streamlit run app.py --server.port 8114"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (str(HERE), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from common import llm  # noqa: E402
from common.streamlit_theme import apply  # noqa: E402
from triage import SAMPLE_EMAILS, EmailTriage, simulate_routing, triage_email, triage_many  # noqa: E402

st.set_page_config(page_title="Ops Inbox Triage Bot", page_icon=":material/mail:", layout="wide")
provider = llm.provider()
badge = "offline · deterministic" if provider == "offline" else f"{provider} · {llm.model()}"
apply("Ops Inbox Triage Bot", "Paste an email: category, urgency, one-line summary and a suggested route. "
      "Routing is simulated (log lines only). Port 8114.", badge=badge)

with st.sidebar:
    st.subheader("Provider")
    st.markdown(f'<span class="badge">{badge}</span>', unsafe_allow_html=True)
    if provider == "offline":
        st.info("No API key found: answers are deterministic placeholders. Set ANTHROPIC_API_KEY "
                "(or OPENAI_API_KEY / GOOGLE_API_KEY) and restart for real triage.")
    st.subheader("What is real")
    st.caption("Real: LLM call, pydantic validation, route derivation. Simulated: CRM, Slack and pager actions "
               "are log lines, nothing is sent.")

if "input" not in st.session_state:
    st.session_state["input"] = ""


def _use_sample(idx: int = 0):
    st.session_state["input"] = SAMPLE_EMAILS[idx]["body"]


left, right = st.columns([1, 1])
with left:
    st.subheader("Email")
    st.text_area("Email body", key="input", height=220, placeholder="Paste the email body here, or press Use sample.")
    c1, c2, _ = st.columns([1, 1, 2])
    run = c1.button("Triage", key="run", type="primary")
    c2.button("Use sample", key="use_sample", on_click=_use_sample, kwargs={"idx": 0})

with right:
    st.subheader("Result")
    result_box = st.container()
    if run:
        text = st.session_state.get("input", "").strip()
        if not text:
            result_box.warning("Paste an email or press Use sample first.")
        else:
            try:
                with st.spinner("Triaging..."):
                    r: EmailTriage = triage_email(text)
            except Exception as e:  # noqa: BLE001 provider errors surface to the user
                result_box.error(f"Triage failed: {e}. Check the provider key or run offline.")
            else:
                with result_box:
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Category", r.category)
                    m2.metric("Urgency", r.urgency)
                    m3.metric("Route", r.route)
                    st.markdown("**Summary**")
                    st.info(r.summary or "(no summary)")
                    st.markdown("**Simulated routing log** (nothing is sent)")
                    st.code("\n".join(simulate_routing(r, "pasted-email")), language="text")
                    st.caption(f"{r.provider} · {r.model}")
                    st.json(r.model_dump())
    else:
        result_box.markdown('<div style="color:#7c869d;padding:24px;text-align:center;border:1px dashed '
                            'rgba(226,232,245,.12);border-radius:12px">Press <b>Use sample</b> then <b>Triage</b>, '
                            'or paste your own email.</div>', unsafe_allow_html=True)

st.divider()
st.subheader("Six sample emails, one click")
if st.button("Triage all 6 samples", key="run_all"):
    with st.spinner("Triaging 6 emails..."):
        rows = triage_many(SAMPLE_EMAILS)
    df = pd.DataFrame(rows)[["id", "from", "subject", "category", "expected", "match", "urgency", "route", "summary"]]
    st.dataframe(df, width="stretch", hide_index=True)
    hits = int(df["match"].sum())
    note = " (offline mode always answers the first option, so this is the floor)" if provider == "offline" else ""
    st.caption(f"{hits}/{len(df)} categories match the hand label{note}")
    st.markdown("**Simulated routing log**")
    log = []
    for e, row in zip(SAMPLE_EMAILS, rows, strict=True):
        log += simulate_routing(EmailTriage(category=row["category"], urgency=row["urgency"],
                                            summary=row["summary"], route=row["route"]), e["id"])
    st.code("\n".join(log), language="text")
else:
    st.dataframe(pd.DataFrame(SAMPLE_EMAILS)[["id", "from", "subject", "expected"]], width="stretch", hide_index=True)
