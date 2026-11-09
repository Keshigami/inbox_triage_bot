import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import triage  # noqa: E402


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "offline")
    for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(k, raising=False)


def test_triage_offline_deterministic():
    a = triage.triage_email(triage.SAMPLE_EMAILS[0]["body"])
    b = triage.triage_email(triage.SAMPLE_EMAILS[0]["body"])
    assert a == b
    assert a.category in triage.CATEGORIES and a.urgency in triage.URGENCIES and a.route in triage.ROUTES
    assert a.provider == "offline"


def test_empty_rejected():
    with pytest.raises(ValueError):
        triage.triage_email("")


def test_validation_normalises_and_derives_route():
    r = triage.EmailTriage(category="billing", urgency="URGENT", summary="  a   b ", route="")
    assert r.category == "Billing" and r.urgency == "High" and r.summary == "a b"
    assert r.route == "Slack #finance"  # derived from category
    r2 = triage.EmailTriage(category="nonsense", urgency="??", route="slack:#support")
    assert r2.category == "Support" and r2.urgency == "Medium" and r2.route == "Slack #support"
    r3 = triage.EmailTriage(category="Spam", route="made up")
    assert r3.route == "Ignore"


def test_simulated_routing_is_labelled():
    r = triage.EmailTriage(category="Sales", urgency="High", summary="Lead wants 50 seats", route="CRM")
    lines = triage.simulate_routing(r, "S1")
    assert all("[SIMULATED]" in line for line in lines)
    assert any("CRM" in line for line in lines) and any("pager" in line for line in lines)


def test_triage_many_rows():
    rows = triage.triage_many(triage.SAMPLE_EMAILS)
    assert len(rows) == 6 and {"id", "category", "urgency", "route", "summary", "match"} <= set(rows[0])


def test_app_smoke():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(HERE / "app.py"), default_timeout=60)
    at.run()
    assert not at.exception
    at.button(key="use_sample").click().run()
    assert at.session_state["input"].startswith("Hi team")
    at.button(key="run").click().run()
    assert not at.exception
    assert any("[SIMULATED]" in c.value for c in at.code)
    labels = [m.label for m in at.metric]
    assert "Category" in labels and "Urgency" in labels and "Route" in labels
