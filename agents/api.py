"""FastAPI interface for EvoFold's deterministic screening demonstration."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .base import AuditLogger, SecurityException
from .models import TargetProtein, LigandCandidate, BindingPocket, SystemTaskPayload
from .supervisor import DiscoverySupervisor, SystemSupervisor

discovery_supervisor = DiscoverySupervisor(model_provider="mock")
system_supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="EvoFold Discovery Agent API",
    description="Illustrative molecular descriptor screening and system task classification; not validated molecular modeling.",
    version="2.1.0",
)

class ScreenRequest(BaseModel):
    target: TargetProtein
    pocket: BindingPocket
    ligand: LigandCandidate

class ChatRequest(BaseModel):
    query: str

@app.get("/")
def index():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")

@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "evofold-discovery-agent", "version": "2.1.0"}

@app.get("/metrics")
def metrics():
    return {
        "campaigns_total": len(discovery_supervisor.dossier_registry),
        "tasks_total": len(system_supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "audit_integrity_valid": AuditLogger.verify_integrity(),
    }

@app.post("/api/screen")
def api_screen(req: ScreenRequest):
    try:
        return discovery_supervisor.screen_lead(req.target, req.pocket, req.ligand).to_dict()
    except SecurityException:
        raise HTTPException(status_code=400, detail="Potential personal identifier detected")

@app.post("/api/audit")
def api_audit(req: SystemTaskPayload):
    try:
        return system_supervisor.process_task(req).model_dump(mode="json")
    except SecurityException:
        raise HTTPException(status_code=400, detail="Potential personal identifier detected")

@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        return {"response": discovery_supervisor.query_operations_chat(req.query)}
    except SecurityException:
        raise HTTPException(status_code=400, detail="Potential personal identifier detected")

@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "integrity_valid": AuditLogger.verify_integrity()}
