"""Regression tests for audit integrity, input validation, and API transparency."""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from agents.api import app
from agents.base import (
    AuditTrail, PHIGuard, ResourceLimitExceededException, SecurityException,
    MAX_PHI_SCAN_LENGTH,
)
from agents.llm_factory import LLMFactory
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor


def test_audit_signature_verifies_with_correct_key():
    audit = AuditTrail(secret_key="test-key-not-for-production")
    audit.log("unit-test", "test", "EVENT", {"sample": 1})
    audit.log("unit-test", "test", "EVENT", {"sample": 2})
    assert audit.verify_integrity()
    assert audit.get_trail()[1]["prev_hash"] == audit.get_trail()[0]["current_hash"]


@pytest.mark.parametrize("field", [
    "audit_id", "timestamp", "actor", "actor_tier",
    "event_type", "payload_hash", "prev_hash", "current_hash",
])
def test_audit_detects_tampered_signed_fields(field):
    audit = AuditTrail(secret_key="test-key")
    audit.log("unit", "test", "EVENT", {"synthetic": True})
    audit.logs[0][field] += "X"
    assert audit.verify_integrity() is False


def test_external_audit_snapshot_cannot_mutate_ledger():
    audit = AuditTrail(secret_key="test-key")
    audit.log("unit", "test", "EVENT", {"synthetic": True})
    snapshot = audit.get_trail()
    snapshot[0]["actor"] = "tampered"
    assert audit.get_trail()[0]["actor"] == "unit"
    assert audit.verify_integrity()


def test_phi_scan_does_not_ignore_identifiers_beyond_scan_limit():
    with pytest.raises(ResourceLimitExceededException):
        PHIGuard.assert_no_phi("X" * MAX_PHI_SCAN_LENGTH + " MRN 123456")
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("synthetic context MRN 123456")


def test_supervisor_checks_nested_attributes_for_obvious_identifiers():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="SYNTHETIC", target_identifier="KEY-01", primary_metric=1,
        attributes={"notes": {"contact": "patient@example.com"}},
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_metrics_rejected(bad_value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(
            task_id="SYNTHETIC", target_identifier="KEY-01",
            primary_metric=bad_value,
        )


def test_mock_does_not_claim_real_inference():
    assert "No clinical evaluation" in LLMFactory.create("mock").invoke("System status?")
    with pytest.raises(NotImplementedError):
        LLMFactory.create("openai")
    with pytest.raises(ValueError):
        LLMFactory.create("unsupported-provider")


def test_api_serves_dashboard_and_assets():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert "not validated IBD clinical thresholds" in client.get("/").text
    assert client.get("/app.js").status_code == 200
    assert client.get("/styles.css").status_code == 200


def test_api_audit_and_phi_error_handling():
    client = TestClient(app)
    clean = {
        "task_id": "SYNTHETIC-1",
        "target_identifier": "KEY-01",
        "primary_metric": 10,
        "secondary_metric": 1,
    }
    response = client.post("/api/audit", json=clean)
    assert response.status_code == 200
    assert response.json()["overall_urgency"] == "ROUTINE"
    assert len(response.json()["audit_hash"]) == 64
    dangerous = dict(clean, target_identifier="MRN-123456")
    blocked = client.post("/api/audit", json=dangerous)
    assert blocked.status_code == 400
    assert "MRN-123456" not in blocked.text
    assert client.post("/api/audit", json=dict(clean, primary_metric="nan")).status_code == 422
    assert client.get("/api/audit/logs").json()["verified"] is True
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "system_tasks_total" in metrics.text


def test_csv_boolean_parsing_and_batch(tmp_path):
    import csv
    from cli import main, parse_boolean

    assert parse_boolean("False") is False
    assert parse_boolean("YES") is True
    with pytest.raises(ValueError):
        parse_boolean("not-a-boolean")
    source = tmp_path / "cases.csv"
    target = tmp_path / "results.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "A,SYNTH-1,1,1,false,NOMINAL\n"
        "B,SYNTH-2,1,1,true,NOMINAL\n",
        encoding="utf-8",
    )
    assert main(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(encoding="utf-8", newline="") as stream:
        records = list(csv.DictReader(stream))
    assert len(records) == 2
    assert records[0]["overall_urgency"] == "ROUTINE"
    assert records[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"


def test_legacy_interfaces_reject_nonfinite_or_invalid_metrics():
    from ibd_sentinel import (
        CalprotectinKineticsAgent, EndoscopicSeverityScorerAgent,
    )
    from ibd_flare_biomarker_agent.engine import ClinicalDomainEngine

    assert EndoscopicSeverityScorerAgent().evaluate(
        {"critical_flag": "False", "metric_secondary": 1}
    ) == []
    with pytest.raises(ValueError):
        CalprotectinKineticsAgent().evaluate({"metric_primary": "not-a-number"})
    with pytest.raises(ValueError):
        CalprotectinKineticsAgent().evaluate({"metric_primary": float("nan")})
    with pytest.raises(ValueError):
        ClinicalDomainEngine.evaluate_secondary_kinetics(float("inf"), False)


def test_concurrent_audit_writes_preserve_valid_chain():
    from concurrent.futures import ThreadPoolExecutor

    audit = AuditTrail(secret_key="synthetic-test-key")
    with ThreadPoolExecutor(max_workers=12) as pool:
        entries = list(pool.map(
            lambda number: audit.log("test", "worker", "EVENT", {"id": number}),
            range(120),
        ))
    assert len(entries) == 120
    assert len(audit.get_trail()) == 120
    assert len({entry["current_hash"] for entry in entries}) == 120
    assert audit.verify_integrity()
