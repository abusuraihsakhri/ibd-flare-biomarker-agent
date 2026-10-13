"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const controls = new Map();
const context = {
  document: {
    getElementById(id) {
      if (!controls.has(id)) {
        controls.set(id, { textContent: "", addEventListener() {} });
      }
      return controls.get(id);
    },
  },
  location: { protocol: "file:", hostname: "" },
};
const script = fs.readFileSync("web/app.js", "utf8");
vm.runInNewContext(script + "\n globalThis.rulePreview = evaluateLocally;", context);

function evaluate(values) {
  return context.rulePreview(Object.assign({
    task_id: "SYNTH", target_identifier: "SPECIMEN",
    primary_metric: 1, secondary_metric: 1,
    status_descriptor: "NOMINAL", is_critical_flag: false,
  }, values));
}
assert.equal(evaluate({}).overall_urgency, "ROUTINE");
assert.equal(evaluate({ primary_metric: 26 }).overall_urgency, "ELEVATED_RISK");
assert.equal(evaluate({ secondary_metric: 13 }).overall_urgency, "ELEVATED_RISK");
assert.equal(evaluate({ is_critical_flag: true }).overall_urgency, "CRITICAL_STAT_PANIC");
assert.equal(evaluate({ status_descriptor: "DISCORDANT" }).total_alerts, 1);
const combined = evaluate({
  primary_metric: 30, secondary_metric: 15,
  status_descriptor: "DISCORDANT", is_critical_flag: true,
});
assert.equal(combined.total_alerts, 3);
assert.equal(combined.critical_alerts_count, 1);
assert.equal(combined.audit_hash, null);
assert.equal(combined.result_type, "UNSIGNED_LOCAL_RULE_PREVIEW");
console.log("Browser rule smoke checks passed");
