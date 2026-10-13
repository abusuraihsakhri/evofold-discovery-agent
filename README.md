# EvoFold Discovery Agent

A reproducible **demonstration** of molecular-descriptor screening and system-task triage. The source code is authoritative: it uses simple numerical rules rather than pretrained protein-folding models, physical docking software, or validated ADMET/QED predictors.

## Features

- Deterministic alpha-carbon helix coordinates from input sequence length (illustrative geometry, **not predicted structure**).
- Descriptor-based affinity surrogate, Lipinski and Veber rule checks, simplified BBB/CYP flags, and a heuristic drug-likeness score.
- Molecular dossier CLI and FastAPI endpoints, plus a rule-based task classifier.
- HMAC-SHA256 chained in-memory audit ledger and a pattern-based identifier guard.
- Self-contained browser sandbox in `web/index.html` with JSON export; no Python, backend, or external models required.

**Scientific limitations:** The surrogate docking score does not evaluate a protein pocket or ligand pose. Its numeric value is **not an experimentally meaningful binding energy**. The heuristic labeled QED is not the published QED algorithm. SMILES is a label, not a parsed molecule. Escalation thresholds have no established clinical units or validation. Outputs must not inform clinical care, medicinal chemistry decisions, or safety evaluation.

## Browser demo

Open `web/index.html` in a modern browser. All computations and JSON exports are local to the page; no data is uploaded. This browser interface uses JavaScript implementations of the basic deterministic rules and does not execute Python via WebAssembly or Pyodide.

The production GitHub Pages URL will be added only after deployment is verified.

## Python setup

Requires Python 3.10 or newer.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python cli.py screen
python cli.py screen --target KRAS --sequence MTEYKLVVVG --ligand EXAMPLE --smiles CCO --mw 46.07 --logp -0.3 --tpsa 20.2
python cli.py chat "Explain the mock workflow"
python cli.py audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The CLI requires a subcommand; run `python cli.py --help` for options. The `chat` command is a deterministic placeholder, not a live language-model integration. The `audit` command shows entries written **within that process only**.

When serving, open `http://127.0.0.1:8000/` for the standalone browser demo and `http://127.0.0.1:8000/docs` for interactive API documentation.

## API

| Endpoint | Description |
| --- | --- |
| `GET /` | Static browser sandbox |
| `GET /health` | Service health |
| `GET /metrics` | In-memory JSON counters (not Prometheus text) |
| `POST /api/screen` | Demonstrative molecular screening |
| `POST /api/audit` | Rule-based task classification |
| `POST /api/chat` | Local mock response |
| `GET /api/audit/logs` | Current-process HMAC chain and integrity status |

The API is not authenticated and should **not** be exposed directly to untrusted networks. FastAPI provides request validation and OpenAPI documentation automatically.

## Container

```bash
docker compose up --build
```

Compose binds only to `127.0.0.1:8000` on the host. To use a stable HMAC signing key across process restarts, export `AUDIT_SECRET_KEY` in the shell before starting. Without it, a random in-memory key is created. **Audit entries are not persisted** across restarts, regardless of whether the key is stable.

## Privacy and security

Browser inputs remain in browser memory unless explicitly exported. In Python, request fields are processed in memory and some identifier values can be included in API responses. The regex-based guard checks certain common patterns but **does not guarantee PHI detection or anonymization**. Do not submit patient-identifiable or other sensitive data. Do not treat audit logging as a durable, compliance-grade audit system.

## Quality checks

```bash
python -m pytest -q
python -m compileall -q agents cli.py enrichment.py simulator.py
python simulator.py 100
```

GitHub Actions tests Python 3.10–3.12. The browser app needs a modern JavaScript-enabled browser.

## License

No license file is currently present in the repository; no specific reuse license is asserted.
