"""HTTP regression tests for the user-facing backend."""
from fastapi.testclient import TestClient

from agents.api import app

client = TestClient(app)


def test_health_and_static_console():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "HEALTHY"
    page = client.get("/")
    assert page.status_code == 200
    assert "EvoFold" in page.text


def test_screen_and_validation():
    payload = {
        "target": {"target_id": "KRAS", "protein_name": "KRAS", "amino_acid_sequence": "MTEYKLVVVG"},
        "pocket": {"pocket_id": "SITE", "center_x": 0, "center_y": 0, "center_z": 0},
        "ligand": {"ligand_id": "EXAMPLE", "smiles": "CCO", "molecular_weight": 46.07,
                   "logp": -0.3, "tpsa": 20.2},
    }
    response = client.post("/api/screen", json=payload)
    assert response.status_code == 200
    assert response.json()["ligand"]["ligand_id"] == "EXAMPLE"
    payload["ligand"]["molecular_weight"] = -1
    assert client.post("/api/screen", json=payload).status_code == 422


def test_system_audit_and_metrics():
    data = {"task_id": "TASK-1", "target_identifier": "SAMPLE-1",
            "primary_metric": 36, "secondary_metric": 4}
    r = client.post("/api/audit", json=data)
    assert r.status_code == 200
    assert r.json()["overall_urgency"] == "CRITICAL_STAT_PANIC"
    metrics = client.get("/metrics").json()
    assert metrics["tasks_total"] >= 1
    assert metrics["audit_integrity_valid"] is True
    logs = client.get("/api/audit/logs").json()
    assert logs["integrity_valid"] is True
    assert isinstance(logs["audit_trail"], list)


def test_sensitive_input_guard():
    r = client.post("/api/chat", json={"query": "Patient John Doe MRN-123456"})
    assert r.status_code == 400
    assert "MRN-123456" not in r.text
