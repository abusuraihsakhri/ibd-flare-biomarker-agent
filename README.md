# Ibd Flare Biomarker Agent

> **Domain:** Gastroenterology, Hepatology & Clinical Nutrition
> **Reference Guidelines & Standards:** `AASLD & ACG Clinical Practice Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Ibd Flare Biomarker Agent** is an advanced analytical and computational platform implementing Fecal Calprotectin, Mayo Endoscopic Score & Biologic TDM Agent. It evaluates clinical measurements across specialized sub-agents and produces consensus dossiers with cryptographic audit trails.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`CalprotectinKineticsAgent`**: Specialized Sub-Agent 1 for ibd-flare-biomarker-agent
- **`EndoscopicSeverityScorerAgent`**: Specialized Sub-Agent 2 for ibd-flare-biomarker-agent
- **`BiologicTroughAuditorAgent`**: Specialized Sub-Agent 3 for ibd-flare-biomarker-agent

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/ibd-flare-biomarker-agent.git
cd ibd-flare-biomarker-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Optional: Set a persistent audit key (recommended for production)
export AUDIT_SECRET_KEY="your-secure-random-key-here"
```

---

## 💻 CLI Quickstart & Usage

The CLI uses subcommands. Run `python cli.py --help` for full usage.

### 1. Run a Single Audit
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --status DISCORDANT
```

### 2. Query the Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task / case identifier
- `--target`: Entity, patient key, or target identifier
- `--primary`: Primary domain measurement or score (float)
- `--secondary`: Secondary kinetic or confidence score (float)
- `--status`: Status code or phenotype descriptor (e.g., NOMINAL, DISCORDANT)
- `--critical`: Flag to trigger emergency escalation

### Input Data Schema (for batch CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Entity or patient key | Required |
| `primary_metric` | Primary measurement (float) | Required |
| `secondary_metric` | Secondary measurement (float) | Optional |
| `is_critical_flag` | Emergency escalation flag | Optional |
| `status_descriptor` | Status code or phenotype | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t ibd-flare-biomarker-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-secure-key" ibd-flare-biomarker-agent
```

Or using Docker Compose:

```bash
AUDIT_SECRET_KEY="your-secure-key" docker-compose up -d
```

---

## 📁 Project Structure

```
ibd-flare-biomarker-agent/
├── agents/                  # Core agent package (supervisor, workers, models, security)
│   ├── base.py             # PHI guard, HMAC audit trail, security exceptions
│   ├── models.py           # Pydantic schemas and data definitions
│   ├── supervisor.py       # Master orchestrator
│   ├── workers.py          # Specialized domain worker agents
│   ├── api.py              # FastAPI REST server
│   ├── metrics.py          # Prometheus metrics exporter
│   ├── learning.py         # Bayesian calibration engine
│   ├── llm_factory.py      # LLM provider factory
│   └── streamer.py         # WebSocket telemetry broadcaster
├── tests/                  # Test suite
│   ├── test_ibd_flare_biomarker_agent.py
│   ├── test_enrichment.py
│   └── test_ibd_sentinel.py
├── cli.py                  # Command-line interface entry point
├── ibd_sentinel.py         # Standalone IBD-Sentinel module
├── enrichment.py           # Enrichment feature engines
├── simulator.py            # High-throughput simulation benchmark
├── web/index.html          # Operations console web UI
├── Dockerfile              # Container build definition
├── docker-compose.yml      # Multi-container orchestration
└── pyproject.toml          # Project metadata and build configuration
```
