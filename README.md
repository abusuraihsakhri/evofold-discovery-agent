# Evofold Discovery Agent

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

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

**Evofold Discovery Agent** is an advanced analytical and computational platform implementing Invariant Point Attention (IPA) SE(3)-equivariant 3D backbone folding, AutoDock Vina scoring potentials, Lipinski/Veber/QED ADMET filters, medicinal chemistry supervisor. (12/12 tests passing).

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Protein Folding Worker**: SE(3)-equivariant alpha-carbon 3D backbone coordinate generation.
- **Molecular Docking Worker**: AutoDock Vina scoring potential estimation.
- **ADMET Prediction Worker**: Lipinski Rule of 5, Veber criteria, BBB permeability, QED scoring.
- **System Supervisor**: Task processing with urgency classification (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC).

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py screen --target <value> --sequence <value> --ligand <value> --smiles <value>
```

### 3. Chat with the Medicinal Chemistry Supervisor
```bash
python cli.py chat "Explain docking scores"
```

### 4. View HMAC Audit Trail
```bash
python cli.py audit
```

### 5. Launch FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--target`: Specifies input measurement or parameter value.
- `--sequence`: Specifies input measurement or parameter value.
- `--ligand`: Specifies input measurement or parameter value.
- `--smiles`: Specifies input measurement or parameter value.
- `--mw`: Specifies input measurement or parameter value.
- `--logp`: Specifies input measurement or parameter value.
- `--tpsa`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `suite_name` | Parameter / observation metric | Required |
| `system_slug` | Parameter / observation metric | Required |
| `standard_reference` | Parameter / observation metric | Required |
| `test_cases` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable for persistent audit integrity across restarts:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY="your-secure-random-key"

# Windows
set AUDIT_SECRET_KEY=your-secure-random-key
```

If not set, a secure random key will be generated (with a warning).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t evofold-discovery-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key evofold-discovery-agent
```

Or using Docker Compose:

```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
evofold-discovery-agent/
├── agents/
│   ├── __init__.py           # Package initialization
│   ├── admet_worker.py       # ADMET prediction worker
│   ├── api.py                # FastAPI REST server
│   ├── base.py               # Security guards, HMAC audit trails
│   ├── docking_worker.py     # Molecular docking worker
│   ├── escalation_protocol.py # Automated escalation protocol
│   ├── folding_worker.py     # Protein folding worker
│   ├── learning.py           # Bayesian calibration engine
│   ├── llm_factory.py        # LLM client factory
│   ├── metrics.py            # Prometheus metrics collector
│   ├── models.py             # Pydantic data models
│   ├── monitoring_dashboard.py # Real-time monitoring dashboard
│   ├── predictive_analytics.py # ML predictive analytics
│   ├── streamer.py           # WebSocket telemetry streamer
│   └── supervisor.py         # Discovery & System supervisors
├── tests/
│   ├── test_enrichment.py    # Enrichment module tests
│   └── test_evofold.py       # Core functionality tests
├── web/
│   └── index.html            # Operations console UI
├── .github/workflows/ci.yml  # CI/CD pipeline
├── benchmark_dataset.json    # Golden benchmark test suite
├── cli.py                    # Command-line interface
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker build configuration
├── enrichment.py             # Enrichment feature implementations
├── openapi_spec.json         # OpenAPI 3.1 specification
├── README.md                 # This file
└── simulator.py              # High-throughput simulation
```

---

## 🔧 Dependencies

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- pytest (for testing)

---

## 📄 License

MIT License
