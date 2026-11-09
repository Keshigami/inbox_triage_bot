# Ops inbox triage bot · carousel

Spec: film/specs/portfolio__inbox_triage_bot.json · 8 slides, 1080x1350.

## 1/8 Hook

- Offline mode: routed to CRM. Nothing sent.

## 2/8 The question

- Six emails. One is a fifty-seat lead.
- Can it route without sending anything?
- S1 enterprise plan: 50 · 50% of total

## 3/8 What it does

- Ops inbox triage bot
- Portfolio · Automation Engineer
- Email in, on-schema record out, routing simulated
- max@baluyot ~ $ uv run python -c "from triage import *; print(triage_email(SAMPLE_EMAILS[0]['body']))"

## 4/8 How it is built

- 1. 6 sample emails with a hand-labelled category in — pandas
- 2. pydantic EmailTriage — streamlit
- 3. common/llm.py complete_json — streamlit · pydantic · pandas
- 4. Streamlit with common/streamlit_theme.py — Streamlit
- 5. Dashboard — Streamlit
- Missing route? Derived from the category.

## 5/8 The result

- What the validators guarantee · tests/test_triage.py
- route slack:#support · → Slack #support
- route missing · → derived from category
- empty email · → rejected
- every routing line · [SIMULATED] (highlighted)

## 6/8 The proof

- Use sample, Triage, offline: Sales, route CRM
- screen: portfolio/inbox_triage_bot/demo/poster.png

## 7/8 The answer and the limit

- 0
- messages sent · every route line is [SIMULATED]
- Offline answers Sales every time: one of six.
- And it ships.

## 8/8 Try it

- Try it: Use sample, Triage, read the log.
- max@baluyot ~ $ git clone https://github.com/Keshigami/inbox_triage_bot.git
- max@baluyot ~ $ just inbox_triage_bot-setup
- max@baluyot ~ $ just inbox_triage_bot-up
- github.com/Keshigami/inbox_triage_bot
- Maximus Friedrich Baluyot
- AI & ML Specialist · Applied AI · ML Engineering · Automation

_Maximus Friedrich Baluyot · Caltech CTME · PGC AIML_
