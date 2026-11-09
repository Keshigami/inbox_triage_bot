<!-- public-top -->
# Ops Inbox Triage Bot

Paste an email and get category, urgency, a one-line summary and a suggested route, validated by pydantic, with the routing shown as simulated log lines. Portfolio, Automation Engineer.

**Watch it first:** [the 90-second film](demo/film.mp4) (what it does, how it is built, the proof, the answer) or the [60-second cut](demo/film-60s.mp4). The plain walkthrough with captions is [demo/demo.mp4](demo/demo.mp4).

## Try it in three commands

```bash
git clone https://github.com/Keshigami/inbox_triage_bot.git && cd inbox_triage_bot
just setup        # creates the venv with uv (Python 3.11)
just up           # http://127.0.0.1:8114/  (just down to stop)
```

You need [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just) (`brew install uv just` on a Mac). Everything the app needs is in the repo (synthetic sample data where a dataset is used). No API key is required: without one the app runs in a deterministic offline mode and says so on screen. Set `ANTHROPIC_API_KEY` (or `LLM_PROVIDER=openai` with `OPENAI_API_KEY`, or `gemini` with `GOOGLE_API_KEY`) in your shell for real model answers. `just test` runs the lint and the offline tests.

Step by step: [docs/Getting-Started.md](docs/Getting-Started.md), then [how it was built](docs/How-It-Was-Built.md), [results](docs/Results.md), [limits](docs/Limits-and-Next-Steps.md) and [the film](docs/The-Film.md). The same pages are on the [wiki](https://github.com/Keshigami/inbox_triage_bot/wiki).
<!-- /public-top -->
# Ops Inbox Triage Bot

## Demo walkthrough
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

Port 8114. Streamlit. LLM calls go through the repo's shared door (`common/llm.py`): Anthropic by default, OpenAI or
Gemini via env, and a deterministic offline mode when no key is set. Routing is simulated: the app prints the log
lines a router would emit; nothing is sent to Slack, a CRM or a pager.

## 1. Problem Statement & Business Impact

- **The Problem**: Operations teams are overwhelmed by generic inboxes, resulting in slow response times to high-value leads.
- **Goal**: Automatically classify, summarize, and route emails to reduce manual triaging by 70%.
- **Metric of Success**: Correct routing > 95%, Triage time < 5s per email.

## 2. Technical Solution

- **Approach**: One LLM call per email returns `category`, `urgency`, `summary` and `route` as JSON against a schema
  hint; pydantic validates it, normalises aliases (`URGENT` -> `High`, `slack:#support` -> `Slack #support`) and
  derives the route from the category when the model's route is missing or unknown.
- **Stack**: Python 3.11 (uv), Streamlit, pydantic v2, pandas (the sample table), `common/llm.py`, pytest with
  `streamlit.testing.v1.AppTest`, ruff.
- **Diagram**: [Incoming Email] -> [common.llm.complete_json] -> [pydantic EmailTriage] -> [simulate_routing: log lines]

Categories: `Sales, Support, Billing, Partnerships, Spam`. Urgency: `Low, Medium, High`.
Routes: `CRM, Slack #support, Slack #finance, Slack #partnerships, Ignore`.

## 3. Evaluation & Results

The six sample emails in `triage.py` carry a hand-labelled category; "Triage all 6 samples" shows a table with the
model's category next to the label and a match count. Offline, the door returns the first option (`Sales`), so the
match is 1/6: that is the floor, not a result. With a key, all six should match (they are deliberately clear cases;
the original README notes sarcastic or very short emails are the known failure mode).

What the tests prove (offline, 6 tests): deterministic triage, empty input rejected, alias normalisation and route
derivation, every routing line carries `[SIMULATED]`, the batch table has one row per email, and the Streamlit page
runs through sample -> Triage -> metrics and log without an exception.

- **Tradeoffs**: Validation lives in pydantic, not in the prompt, so a model that answers off-schema still produces a
  safe, routable record instead of a crash.

## 4. How to run

```bash
just inbox_triage_bot-setup
just inbox_triage_bot-test                # ruff + 6 pytest tests, offline
just inbox_triage_bot-up                  # background on :8114, pid in .pid, log in app.log
curl -s localhost:8114/_stcore/health     # ok
just inbox_triage_bot-down
```

Set `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY` / `GOOGLE_API_KEY`) in the shell before `-up` for real triage.

## 5. Two-minute interviewer walkthrough

1. Open `http://localhost:8114/`. The badge shows `offline · deterministic` or the provider and model.
2. Press **Use sample** (the Acme 50-seat enquiry) then **Triage**: three metrics (category, urgency, route), the
   one-line summary, the simulated routing log and the validated JSON.
3. Press **Triage all 6 samples**: a table with the model's category beside the hand label and a match count, plus
   the combined routing log; point at the `[SIMULATED]` prefix on every line.
4. Paste a short or sarcastic email of your own and watch the validation keep the output on-schema.

## 6. What is real vs mocked

- Real: the LLM call when a key is set, pydantic validation and alias handling, route derivation from category, the
  batch table and match count.
- Simulated: CRM lead creation, Slack posts and pager flags are log lines labelled `[SIMULATED]`; no network call is
  made for routing in any mode.
- Offline (no key): every email comes back `Sales / Low / CRM` with a placeholder summary; the sidebar says so.

## 7. Case Study Narrative

- **Context**: Highlights AI's role in workflow automation and decision-making.
- **Implementation**: A script that validates LLM output against a strict schema before any downstream action.
- **Limitations**: Sarcastic or extremely short emails can lead to misclassification; six samples is a demo, not an eval.
- **Next Steps**: Connect to a live Gmail/Outlook API via webhooks; replace the simulated router with real Slack and
  CRM calls behind an approval step.

## Standalone repo

Exported from Max's `caltech-capstone` workspace. `common/` is vendored (LLM door, UI tokens). Run: `just setup && just test && just up`.
LLM-backed features read `ANTHROPIC_API_KEY` (or `LLM_PROVIDER` + `OPENAI_API_KEY` / `GOOGLE_API_KEY`); with no key they run in a deterministic offline mode.
Film: `demo/film.mp4` (90 s, what it does, how it is built, the proof, the answer) and `demo/film-60s.mp4` (60 s cut); `demo/demo.mp4` is the plain walkthrough.
