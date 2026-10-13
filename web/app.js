"use strict";

// Explicit, unsigned browser preview of the same generic rules in agents/workers.py.
// This is not a clinical calculator and never fabricates an audit hash.
const $ = (id) => document.getElementById(id);
let useBackend = false;

function evaluateLocally(payload) {
  const alerts = [];
  if (payload.primary_metric > 25) {
    alerts.push({
      origin_worker: "InvariantQCWorker",
      urgency: "ELEVATED_RISK",
      summary: "Primary Metric Threshold Exceeded"
    });
  }
  if (payload.is_critical_flag || payload.secondary_metric > 12) {
    alerts.push({
      origin_worker: "SafetyEscalationWorker",
      urgency: payload.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary: "Critical Safety Interlock Triggered"
    });
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"].some(
    (term) => payload.status_descriptor.toUpperCase().includes(term)
  )) {
    alerts.push({
      origin_worker: "ProtocolConformanceWorker",
      urgency: "ELEVATED_RISK",
      summary: "Protocol Conformance Discordance Detected"
    });
  }
  const critical = alerts.filter((a) => a.urgency === "CRITICAL_STAT_PANIC").length;
  const urgency = critical ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  return {
    result_type: "UNSIGNED_LOCAL_RULE_PREVIEW",
    clinical_validation: "NONE",
    task_id: payload.task_id,
    target_identifier: payload.target_identifier,
    overall_urgency: urgency,
    integrity_status: critical ? "RECALIBRATION_REQUIRED" :
      alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts: alerts.length,
    critical_alerts_count: critical,
    alerts,
    audit_hash: null,
    note: "No server-side audit was performed; no HMAC was generated."
  };
}

async function detectBackend() {
  if (location.protocol === "file:" || location.hostname.endsWith(".github.io")) return;
  try {
    const res = await fetch("./health", { cache: "no-store" });
    if (!res.ok) return;
    const status = await res.json();
    if (status.service === "ibd-flare-biomarker-agent") {
      useBackend = true;
      $("mode").textContent = "Local FastAPI mode";
    }
  } catch (_) {
    // Not a FastAPI instance; retain clearly labeled browser mode.
  }
}

function readPayload() {
  const primary = $("primary").value.trim();
  const secondary = $("secondary").value.trim();
  const task = $("task-id").value.trim();
  const target = $("target-id").value.trim();
  const p = Number(primary);
  const s = Number(secondary);
  if (!task || !target || !primary || !secondary || !Number.isFinite(p) || !Number.isFinite(s)) {
    throw new Error("Supply synthetic identifiers and finite numeric values.");
  }
  return {
    task_id: task,
    target_identifier: target,
    primary_metric: p,
    secondary_metric: s,
    status_descriptor: $("descriptor").value.trim(),
    is_critical_flag: $("critical").checked
  };
}

$("audit-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("submit").disabled = true;
  $("result-status").textContent = "Evaluating...";
  try {
    const payload = readPayload();
    let result;
    if (useBackend) {
      const response = await fetch("./api/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(typeof body.detail === "string" ? body.detail : "Server rejected the input.");
      }
      result = body;
      $("result-kind").textContent = "Server evaluation";
    } else {
      result = evaluateLocally(payload);
      $("result-kind").textContent = "Unsigned preview";
    }
    $("output").textContent = JSON.stringify(result, null, 2);
    $("result-status").textContent = "Completed · " + result.overall_urgency;
  } catch (error) {
    $("result-kind").textContent = "Error";
    $("result-status").textContent = error.message || "Evaluation failed.";
    $("output").textContent = "{}";
  } finally {
    $("submit").disabled = false;
  }
});

detectBackend();
