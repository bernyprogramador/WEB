from datetime import datetime, timedelta
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from booking_conversion_agent_mvp.src.agent_engine import BookingConversionAgent, Lead


def mklead(i, **kwargs):
    base = Lead(
        lead_id=f"L{i:03d}",
        created_at=datetime.utcnow(),
        villa_id="VILLA001",
        channel="webhook",
        message="hola",
    )
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


def run():
    kb = {
        "VILLA001": {
            "min_budget": 1200,
            "policies_fully_defined": False,
        }
    }
    agent = BookingConversionAgent(kb)

    leads = []
    for i in range(1, 8):
        leads.append(
            mklead(
                i,
                checkin=datetime.utcnow() + timedelta(days=10),
                checkout=datetime.utcnow() + timedelta(days=14),
                guests=6,
                budget=1600,
                explicit_intent=True,
            )
        )
    for i in range(8, 15):
        leads.append(
            mklead(
                i,
                checkin=datetime.utcnow() + timedelta(days=45),
                checkout=datetime.utcnow() + timedelta(days=50),
                guests=4 if i % 2 == 0 else None,
                budget=None,
            )
        )
    for i in range(15, 21):
        leads.append(mklead(i, message="solo mirando opciones"))

    hot = warm = cold = 0
    for lead in leads:
        lead.score = agent.calculate_score(lead)
        if lead.score == "HOT":
            hot += 1
        elif lead.score == "WARM":
            warm += 1
        else:
            cold += 1

    assert hot == 7, f"Expected 7 HOT, got {hot}"
    assert warm == 7, f"Expected 7 WARM, got {warm}"
    assert cold == 6, f"Expected 6 COLD, got {cold}"

    no_hallucination_reply = agent.guarded_reply(leads[0], "¿precio exacto para 12-14 junio?")
    assert "manager" in no_hallucination_reply.lower() or "conecto" in no_hallucination_reply.lower()

    escalation_reason = agent.should_escalate("Need exact availability now", kb["VILLA001"])
    assert escalation_reason is not None

    followups = agent.schedule_followups(leads[1], datetime.utcnow())
    assert len(followups) == 3
    assert (followups[0] - datetime.utcnow()) < timedelta(minutes=31)

    brief = agent.generate_brief(leads[2], ["msg1", "obj: discount", "msg3"])
    assert all(k in brief for k in ["summary", "key_data", "objections", "next_step"])

    print("OK: 20 leads simulated, scoring and guardrails validated")


if __name__ == "__main__":
    run()
