---
title: Ops Inbox Triage Bot
group: portfolio
role: Automation Engineer
port: 8114
status: working
one_liner: Paste an email and get category, urgency, a one-line summary and a suggested route, validated by pydantic, with the routing shown as simulated log lines.
---
# Ops Inbox Triage Bot

## Demo
<!-- demo:auto -->
![demo](demo/demo.gif)

Full walkthrough with captions: [demo/demo.mp4](demo/demo.mp4) (59 s, 1280x800, animated intro and end card). Run it yourself: `just setup && just up`, then open http://localhost:8114/.

Two-minute walkthrough:
1. Ops inbox triage: use a sample email
2. Triage: category, urgency and the route it would take
3. The summary and the simulated routing log; nothing is sent
4. Six sample emails, one click
5. Triage all six: category, expected label, match, urgency, route
6. The batch routing log
<!-- /demo:auto -->

## Brief
A shared ops inbox mixes sales leads, outages, invoice disputes, press requests and spam, and the lead that matters
waits behind the noise. This bot reads one email and returns a structured record (category, urgency, summary, route)
that a router can act on. Solved means every email is pre-sorted in seconds and the record is always on-schema, so
downstream automation never sees a malformed answer.

## Tech stack
| Layer | Choice | Why |
|---|---|---|
| Language and runtime | Python 3.11 via uv | same as the rest of the portfolio |
| Model or core logic | `common/llm.py` `complete_json` + pydantic `EmailTriage` | provider by env, validation in code not in the prompt |
| Interface | Streamlit with `common/streamlit_theme.py` | two columns: email in, metrics and log out; `key="input"`, `key="run"` for scripted demos |
| Data | 6 sample emails with a hand-labelled category in `triage.py` | one-click batch demo and a visible match count |
| Tests | pytest (6) incl. `AppTest` smoke | logic, validation, simulated routing, UI happy path |

## Libraries used
`streamlit` (UI), `pydantic` (schema validation, alias normalisation, route derivation), `pandas` (sample table),
`anthropic` / `openai` / `google-genai` (providers behind the shared door), `pytest`, `ruff`.

## How it was built
1. Read the original `triage_bot.py` and `app.py`: OpenAI JSON mode, a fixed mock when no key, a success banner that
   claimed the email was "routed" with no routing code.
2. Replaced the OpenAI call with `common.llm.complete_json` and a schema hint; renamed `priority` to `urgency` and
   added a `Billing` category and explicit route names (`CRM`, `Slack #support`, `Slack #finance`,
   `Slack #partnerships`, `Ignore`).
3. Wrote `EmailTriage` validators: category and urgency aliases, route parsing, and a before-model validator that
   derives the route from the category when the model's route is missing or unknown.
4. Added `simulate_routing`, which returns timestamped `[SIMULATED]` log lines instead of pretending to send.
5. Built the Streamlit page: provider badge, Use sample, Triage, metrics, log, JSON, and a one-click table for all
   six samples with a match count.
6. Tests (pure functions plus an `AppTest` run through sample -> Triage), ruff, just recipes with a pid file.

## Results
No metrics file; the measurable part is the six-sample table. Offline (no key in the build environment) the match
count is 1/6 because the door answers the first option (`Sales`) every time; it is the floor. With a key, 6/6 is
expected on these clear cases. The tests prove: deterministic output, empty input rejected, `URGENT` -> `High`,
`slack:#support` -> `Slack #support`, unknown route -> derived from category, every routing line labelled
`[SIMULATED]`, and the UI reaching a result from one click.

## Demo details
- Run: `just inbox_triage_bot-setup && just inbox_triage_bot-up`, open `http://localhost:8114/`.
- Two-minute walkthrough: (1) badge in the header; (2) Use sample -> Triage, read the three metrics and the
  `[SIMULATED]` log; (3) Triage all 6 samples, compare category with the label column; (4) paste a two-word email and
  show the record is still on-schema.
- Video clip: `demo/clips/portfolio__inbox_triage_bot.webm`.
- Sample inputs: `SAMPLE_EMAILS` in `triage.py` (S1 sales lead, S2 outage, S3 duplicate invoice, S4 partnership, S5
  spam, S6 API question). Offline every row is `Sales / Low / CRM`.

## Limits and next steps
- Routing is simulated by design; a production version adds real Slack and CRM clients behind an approval step.
- Offline mode is a placeholder, not a classifier.
- Six emails demonstrate the loop; a labelled set of a few hundred emails is needed to claim the 95% routing target.
- No mailbox connector yet (Gmail/Outlook webhooks were the original next step and still are).
