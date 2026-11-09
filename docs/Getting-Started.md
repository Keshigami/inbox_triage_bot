# Getting started

## What you need
- [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just). On a Mac: `brew install uv just`.
- Python 3.11 is installed by uv.
- No API key is required: without one the app runs in a deterministic offline mode and says so on screen. Set `ANTHROPIC_API_KEY` (or `LLM_PROVIDER=openai` with `OPENAI_API_KEY`, or `gemini` with `GOOGLE_API_KEY`) in your shell for real model answers.

## Three commands
```bash
git clone https://github.com/Keshigami/inbox_triage_bot.git && cd inbox_triage_bot
just setup
just up           # http://127.0.0.1:8114/  (just down to stop)
```
Everything the app needs is in the repo (synthetic sample data where a dataset is used).

## Commands
`just setup`, `just train` where a model is trained, `just up` / `just down`, `just test`, `just demo`.

## What you see
- Run: `just inbox_triage_bot-setup && just inbox_triage_bot-up`, open `http://localhost:8114/`.
- Two-minute walkthrough: (1) badge in the header; (2) Use sample -> Triage, read the three metrics and the
  `[SIMULATED]` log; (3) Triage all 6 samples, compare category with the label column; (4) paste a two-word email and
  show the record is still on-schema.
- Video clip: `demo/clips/portfolio__inbox_triage_bot.webm`.
- Sample inputs: `SAMPLE_EMAILS` in `triage.py` (S1 sales lead, S2 outage, S3 duplicate invoice, S4 partnership, S5
  spam, S6 API question). Offline every row is `Sales / Low / CRM`.

## Try this
Try it: Use sample, Triage, read the log.
