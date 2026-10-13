#!/usr/bin/env python3
"""
IBD-Sentinel Demonstration Rule Engine
Demonstrates generic numerical rules; does not calculate validated IBD biomarkers, scores, or therapeutic drug levels.

Domain: Gastroenterology
Author: Dr. Abu Suraih Sakhri
License: MIT
"""

import argparse
import csv
import datetime
import json
import math
import sys
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional


class Severity(str, Enum):
    INFO = "INFO"
    ADVISORY = "ADVISORY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL_ACTION_REQUIRED"



# ==============================================================================
# GENERIC RULE DEMONSTRATION METADATA
# ==============================================================================

class DomainKnowledgeRegistry:
    """Demonstration rules; no guideline validation or HIPAA certification."""
    SYSTEM_VERSION = "2.0.0-DEMO"
    ZERO_PHI_COMPLIANCE = False
    HIPAA_SAFE_HARBOR = "NOT_ASSESSED"

    @staticmethod
    def audit_security_and_integrity(payload: Dict[str, Any]) -> List[str]:
        warnings = []
        for key in payload.keys():
            if any(phi_keyword in key.lower() for phi_keyword in ["patient_name", "ssn", "mrn_raw", "dob_raw"]):
                warnings.append(f"IDENTIFIER_WARNING: Field '{key}' requires removal before use.")
        return warnings

class AgentAlert:
    def __init__(self, alert_id: str, agent_name: str, severity: str, title: str, details: str, recommendation: str):
        self.alert_id = alert_id
        self.agent_name = agent_name
        self.severity = severity
        self.title = title
        self.details = details
        self.recommendation = recommendation
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "agent": self.agent_name,
            "severity": self.severity,
            "title": self.title,
            "details": self.details,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp,
        }


def parse_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ("1", "true", "yes"):
            return True
        if value in ("", "0", "false", "no"):
            return False
    raise ValueError("Boolean value must be true/false, yes/no, or 1/0")


def parse_finite_metric(value: Any, name: str) -> float:
    """Never silently substitute nominal values for invalid metrics."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


class CalprotectinKineticsAgent:
    """Specialized Sub-Agent 1 for ibd-flare-biomarker-agent"""
    def evaluate(self, payload: Dict[str, Any]) -> List[AgentAlert]:
        alerts = []
        val1 = parse_finite_metric(payload.get("metric_primary", 15.0), "metric_primary")
        if val1 > 20.0:
            alerts.append(
                AgentAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    agent_name="CalprotectinKineticsAgent",
                    severity=Severity.WARNING,
                    title="Primary Metric Threshold Discrepancy",
                    details=f"Primary metric value ({val1:.1f}) exceeded the configured demonstration boundary.",
                    recommendation="Review the demonstration rule and supplied synthetic measurement.",
                )
            )
        return alerts


class EndoscopicSeverityScorerAgent:
    """Specialized Sub-Agent 2 for ibd-flare-biomarker-agent"""
    def evaluate(self, payload: Dict[str, Any]) -> List[AgentAlert]:
        alerts = []
        is_critical = parse_boolean(payload.get("critical_flag", False))
        val2 = parse_finite_metric(payload.get("metric_secondary", 5.0), "metric_secondary")
        if is_critical or val2 > 12.0:
            alerts.append(
                AgentAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    agent_name="EndoscopicSeverityScorerAgent",
                    severity=Severity.CRITICAL,
                    title="Urgent Consensus Protocol Trigger",
                    details=f"Secondary parameter index ({val2:.1f}) triggered a demonstration alert; no escalation was sent.",
                    recommendation="This example triggers no real clinical notification.",
                )
            )
        return alerts


class BiologicTroughAuditorAgent:
    """Specialized Sub-Agent 3 for ibd-flare-biomarker-agent"""
    def evaluate(self, payload: Dict[str, Any]) -> List[AgentAlert]:
        alerts = []
        status_text = str(payload.get("status_text", "NORMAL")).upper()
        if "DISCORDANT" in status_text or "SUSPICIOUS" in status_text:
            alerts.append(
                AgentAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    agent_name="BiologicTroughAuditorAgent",
                    severity=Severity.ADVISORY,
                    title="Biomarker / Feature Discordance Flag",
                    details=f"Phenotypic discordance noted in observation status ({status_text}).",
                    recommendation="Review the demonstration status descriptor.",
                )
            )
        return alerts


class IBDCoordinator:
    """Executive Coordinator Agent for ibd-flare-biomarker-agent"""
    def __init__(self):
        self.sub_agent_1 = CalprotectinKineticsAgent()
        self.sub_agent_2 = EndoscopicSeverityScorerAgent()
        self.sub_agent_3 = BiologicTroughAuditorAgent()
        self.case_registry: Dict[str, Dict[str, Any]] = {}

    def audit_case(self, case_payload: Dict[str, Any]) -> Dict[str, Any]:
        case_id = str(case_payload.get("case_id", f"CASE-{uuid.uuid4().hex[:6].upper()}"))
        all_alerts: List[AgentAlert] = []

        all_alerts.extend(self.sub_agent_1.evaluate(case_payload))
        all_alerts.extend(self.sub_agent_2.evaluate(case_payload))
        all_alerts.extend(self.sub_agent_3.evaluate(case_payload))

        critical_count = sum(1 for a in all_alerts if a.severity == Severity.CRITICAL)
        warning_count = sum(1 for a in all_alerts if a.severity == Severity.WARNING)

        overall_status = "CRITICAL_ACTION_REQUIRED" if critical_count > 0 else ("WARNING_ACTIVE" if all_alerts else "CONCORDANT_NORMAL")

        dossier = {
            "system": "ibd-flare-biomarker-agent",
            "domain": "Gastroenterology",
            "case_id": case_id,
            "overall_status": overall_status,
            "total_alerts": len(all_alerts),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "alerts": [a.to_dict() for a in all_alerts],
            "consensus_summary": f"Audit completed across 3 specialized sub-agents with status [{overall_status}].",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        self.case_registry[case_id] = dossier
        return dossier

    def query_assistant(self, user_query: str) -> str:
        q = user_query.strip().lower()
        if "summary" in q or "status" in q:
            return f"IBD-Sentinel Demonstration Rule Engine currently tracking {len(self.case_registry)} cases in local in-process memory."
        elif "guidelines" in q or "protocol" in q:
            return "This software does not implement validated IBD clinical guidelines; its numerical limits are demonstration thresholds."
        else:
            return f"IBD-Sentinel demonstration is available for manual evaluations; continuous monitoring is not implemented."


coordinator = IBDCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field

        app = FastAPI(
            title="IBD-Sentinel Demonstration Rule Engine",
            description="Demonstrates generic numerical rules; does not calculate validated IBD biomarkers, scores, or therapeutic drug levels.",
            version="2.0.0",
        )

        class AuditRequest(BaseModel):
            case_id: Optional[str] = None
            metric_primary: float = Field(15.0, allow_inf_nan=False)
            metric_secondary: float = Field(5.0, allow_inf_nan=False)
            critical_flag: bool = False
            status_text: str = "NORMAL"

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "ibd-flare-biomarker-agent", "version": "2.0.0"}

        @app.post("/api/audit")
        def api_audit(req: AuditRequest):
            return coordinator.audit_case(req.model_dump())

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_assistant(req.query)}

        return app
    except ImportError:
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ibd-flare-biomarker-agent", description="IBD-Sentinel Demonstration Rule Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Audit
    audit_parser = subparsers.add_parser("audit", help="Audit single case")
    audit_parser.add_argument("--case-id", default="CASE-TEST-001")
    audit_parser.add_argument("--primary", type=float, default=24.5)
    audit_parser.add_argument("--secondary", type=float, default=14.0)
    audit_parser.add_argument("--critical", action="store_true")
    audit_parser.add_argument("--status", default="DISCORDANT")

    # Batch
    batch_parser = subparsers.add_parser("batch", help="Batch process CSV")
    batch_parser.add_argument("-i", "--input", required=True)
    batch_parser.add_argument("-o", "--output", default="results.csv")

    # Chat
    chat_parser = subparsers.add_parser("chat", help="Query air-gapped assistant")
    chat_parser.add_argument("query", nargs="+")

    # Serve
    serve_parser = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "audit":
        payload = {
            "case_id": args.case_id,
            "metric_primary": args.primary,
            "metric_secondary": args.secondary,
            "critical_flag": args.critical,
            "status_text": args.status,
        }
        dossier = coordinator.audit_case(payload)
        print("=" * 80)
        print(f"  IBD-SENTINEL: DEMONSTRATION RULE ENGINE")
        print(f"  Case: {dossier['case_id']} | Status: [{dossier['overall_status']}] | Alerts: {dossier['total_alerts']}")
        print("=" * 80)
        for a in dossier["alerts"]:
            print(f"\n  [{a['severity']}] from {a['agent']}:")
            print(f"  Title: {a['title']}")
            print(f"  Details: {a['details']}")
            print(f"  Recommendation: {a['recommendation']}")
        print("\n" + "=" * 80)
        return 0

    if args.command == "chat":
        ans = coordinator.query_assistant(" ".join(args.query))
        print(f"\n[{coordinator.__class__.__name__}]:\n{ans}\n")
        return 0

    if args.command == "batch":
        try:
            with open(args.input, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                fieldnames = list(reader.fieldnames or [])
                rows = list(reader)
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
            return 1

        out_fields = fieldnames + ["overall_status", "total_alerts", "critical_count", "consensus_summary"]
        out_rows = []
        for r in rows:
            try:
                data = dict(r)
                data["critical_flag"] = parse_boolean(data.get("critical_flag", False))
                dossier = coordinator.audit_case(data)
            except Exception as e:
                print(f"Warning: Skipping row due to error: {e}", file=sys.stderr)
                continue
            row_dict = dict(r)
            row_dict["overall_status"] = dossier["overall_status"]
            row_dict["total_alerts"] = dossier["total_alerts"]
            row_dict["critical_count"] = dossier["critical_count"]
            row_dict["consensus_summary"] = dossier["consensus_summary"]
            out_rows.append(row_dict)

        with open(args.output, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Processed {len(out_rows)} records -> {args.output}")
        return 0

    if args.command == "serve":
        try:
            import uvicorn
            app = create_app()
            if app:
                print(f"Starting IBD-Sentinel Demonstration Rule Engine on http://{args.host}:{args.port}")
                uvicorn.run(app, host=args.host, port=args.port)
        except ImportError:
            print("FastAPI / uvicorn not installed. Run 'pip install fastapi uvicorn'")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
