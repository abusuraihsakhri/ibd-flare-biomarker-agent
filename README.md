# IBD Flare Biomarker Agent

A local, reproducible demonstration of simple numeric and status-flag rules, with Python CLI, FastAPI endpoints, and an accessible browser rule explorer.

**Important:** This repository does **not** calculate or validate fecal calprotectin activity, endoscopic Mayo/SES-CD scores, Harvey–Bradshaw scores, or biologic therapeutic drug monitoring. Its generic thresholds are not guideline-derived clinical cutoffs. **Do not use this software to diagnose, triage, or manage IBD or other clinical conditions.**

## What is implemented

- Three rule workers: a primary metric above **25**, secondary metric above **12** or an explicit critical flag, and descriptor-based anomaly detection.
- An aggregate demonstration urgency (routine, elevated, critical) and detailed worker alerts.
- Per-process HMAC-SHA256 chained audit entries; verification recomputes signatures and checks chain pointers.
- Heuristic screening for *some* common identifiers, including MRN patterns, phone numbers and email addresses. **This is not full PHI detection, HIPAA de-identification, or an authorization system.**
- Local FastAPI API, CSV batch CLI, an optional local server, and a static browser preview.

These are generic software rules with unitless inputs; nothing here establishes biomarker-specific performance or clinical validity. Separate older entry points (`ibd_sentinel.py` and `ibd_flare_biomarker_agent.cli`) remain available for compatibility, but also use demonstration logic.

## Browser demonstration

Open `web/index.html` directly or serve the directory:

```bash
python -m http.server 8080 --directory web
```

The standalone browser explorer runs JavaScript equivalents of the three generic rules. It does not contact the API, generate signed audit hashes, persist input, or send data to a remote calculation service. The result is explicitly marked **UNSIGNED_LOCAL_RULE_PREVIEW**. Enter only synthetic identifiers.

The `web/` directory is also suitable for GitHub Pages. The repository includes a Pages publishing workflow; **do not assume a live deployment exists until the Pages build and URL have been verified**.

## Local Python installation and API

Python 3.10–3.12 is exercised by the CI matrix (package metadata supports Python 3.9+).

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[api,test]"
python cli.py audit --task-id TASK-001 --target SYNTH-01 --primary 28.5 --secondary 14.2 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` to use the same browser interface with server-side evaluation. The API exposes `POST /api/audit`, `POST /api/chat` (a **mock response, not real language-model inference**), `GET /api/audit/logs`, `GET /health`, `GET /metrics` (Prometheus text) and OpenAPI documentation at `/docs`.

The top-level CLI accepts `task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor` CSV fields, with the first three required by convention. `sample.csv` follows this format. Older alternative CLIs use a different schema; `sample_legacy.csv` provides a matching example.

## Tests

```bash
python -m pytest -q
node --check web/app.js
node tests/browser_smoke.cjs
python simulator.py 100
```

CI runs Python tests on 3.10, 3.11 and 3.12, CLI smoke tests, Python compilation, and browser JavaScript checks. No real-world clinical performance has been established by these tests.

## Configuration, security and limitations

`AUDIT_SECRET_KEY` sets the in-memory ledger's HMAC secret. Generate a random value for each deployment. Without it, the server creates an ephemeral key that cannot verify prior sessions. Audit records and evaluated dossiers reside **only in process memory**; there is no persistent evidence store or longitudinal review. The verifier can detect tampering with retained signed records, but not the removal of the entire in-memory ledger or data changed before hashing.

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
docker compose up --build
```

Docker Compose requires the secret and publishes the service only on `127.0.0.1:8000`. **Do not publish the API on the open internet:** it has no authentication, rate limiting, production access controls, or verified PHI handling. Do not submit real patient identifiers or sensitive health information.

The adapter for `MODEL_PROVIDER=mock` is intentionally deterministic. External hosted/local model integrations are not implemented. The rule explorer does not run Python or Pyodide in the browser; JavaScript implements the small, explicitly identified preview only. No browser persistence is used. Interface code targets current standards-based browsers; cross-browser certification has not been performed.

## Technology and license

Python, Pydantic v2, optional FastAPI/Uvicorn, pytest, vanilla JavaScript, CSS, Docker and GitHub Actions. See [MIT license](LICENSE).
