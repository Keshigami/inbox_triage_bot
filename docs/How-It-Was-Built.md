# How it was built

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

## Tech stack
| Layer | Choice | Why |
|---|---|---|
| Language and runtime | Python 3.11 via uv | same as the rest of the portfolio |
| Model or core logic | `common/llm.py` `complete_json` + pydantic `EmailTriage` | provider by env, validation in code not in the prompt |
| Interface | Streamlit with `common/streamlit_theme.py` | two columns: email in, metrics and log out; `key="input"`, `key="run"` for scripted demos |
| Data | 6 sample emails with a hand-labelled category in `triage.py` | one-click batch demo and a visible match count |
| Tests | pytest (6) incl. `AppTest` smoke | logic, validation, simulated routing, UI happy path |

## Libraries
`streamlit` (UI), `pydantic` (schema validation, alias normalisation, route derivation), `pandas` (sample table),
`anthropic` / `openai` / `google-genai` (providers behind the shared door), `pytest`, `ruff`.
