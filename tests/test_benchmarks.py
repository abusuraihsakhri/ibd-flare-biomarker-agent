"""Exercise the repository's synthetic golden fixtures against the real supervisor."""
import json
from pathlib import Path

import pytest

from agents.base import PHIGuard, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor


FIXTURES = json.loads(
    (Path(__file__).resolve().parents[1] / "benchmark_dataset.json").read_text(encoding="utf-8")
)["test_cases"]


@pytest.mark.parametrize("case", FIXTURES, ids=lambda x: x["case_id"])
def test_synthetic_fixture(case):
    if case.get("expected_security_exception"):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi(case["adversarial_prompt"])
        return

    dossier = SystemSupervisor().process_task(SystemTaskPayload(**case["payload"]))
    assert dossier.overall_urgency.value == case["expected_urgency"]
    assert dossier.integrity_status.value == case["expected_integrity"]
