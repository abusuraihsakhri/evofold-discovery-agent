"""
FastAPI REST Server for EvoFold Molecular Discovery.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger
from .models import TargetProtein, LigandCandidate, BindingPocket
from .supervisor import DiscoverySupervisor

supervisor = DiscoverySupervisor(model_provider="mock")

app = FastAPI(
    title="EvoFold Discovery Agent API",
    description="Autonomous Protein Folding, Molecular Docking & ADMET Drug Screening",
    version="2.0.0-PRO",
)


class ScreenRequest(BaseModel):
    target: TargetProtein
    pocket: BindingPocket
    ligand: LigandCandidate


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "evofold-discovery-agent", "version": "2.0.0-PRO"}


@app.get("/metrics")
def metrics():
    return {
        "campaigns_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "status": "NOMINAL"
    }


@app.post("/api/screen")
def api_screen(req: ScreenRequest):
    dossier = supervisor.screen_lead(req.target, req.pocket, req.ligand)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_operations_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit():
    return {"audit_trail": AuditLogger.get_trail()}
