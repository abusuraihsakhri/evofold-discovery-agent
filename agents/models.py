"""
Data models for EvoFold Molecular Discovery.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TargetProtein(BaseModel):
    target_id: str = Field(..., min_length=1, max_length=200)
    protein_name: str = Field(..., min_length=1, max_length=200)
    amino_acid_sequence: str = Field(..., min_length=1, max_length=5000)
    organism: str = "Homo sapiens"


class Residue3DCoordinate(BaseModel):
    residue_index: int
    amino_acid: str
    x: float
    y: float
    z: float
    b_factor: float = 20.0


class BindingPocket(BaseModel):
    pocket_id: str
    center_x: float = Field(..., allow_inf_nan=False)
    center_y: float = Field(..., allow_inf_nan=False)
    center_z: float = Field(..., allow_inf_nan=False)
    radius_angstrom: float = Field(default=10.0, gt=0, le=1000, allow_inf_nan=False)


class LigandCandidate(BaseModel):
    ligand_id: str = Field(..., min_length=1, max_length=200)
    smiles: str = Field(..., min_length=1, max_length=4096)
    molecular_weight: float = Field(..., gt=0, le=100000, allow_inf_nan=False)
    logp: float = Field(..., ge=-100, le=100, allow_inf_nan=False)
    tpsa: float = Field(..., ge=0, le=10000, allow_inf_nan=False)
    hbd_count: int = Field(default=2, ge=0, le=1000)
    hba_count: int = Field(default=4, ge=0, le=1000)
    rotatable_bonds: int = Field(default=4, ge=0, le=1000)


class DockingScore(BaseModel):
    target_id: str
    pocket_id: str
    ligand_id: str
    affinity_kcal_mol: float
    rmsd_angstrom: float
    hbond_count: int
    buried_surface_area_angstrom2: float


class ADMETProfile(BaseModel):
    ligand_id: str
    molecular_weight: float
    logp: float
    tpsa: float
    hbd_count: int
    hba_count: int
    rotatable_bonds: int
    lipinski_violations: int
    veber_compliant: bool
    bbb_permeable: bool
    qed_score: float
    cyp_inhibition_risk: str


class DiscoveryDossier(BaseModel):
    campaign_id: str
    target: TargetProtein
    pocket: BindingPocket
    ligand: LigandCandidate
    docking: DockingScore
    admet: ADMETProfile
    triage_status: str
    audit_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED_RISK = "ELEVATED_RISK"
    CRITICAL_STAT_PANIC = "CRITICAL_STAT_PANIC"


class SystemTaskPayload(BaseModel):
    """Payload for system-level task processing."""
    task_id: str = Field(..., min_length=1, max_length=100)
    target_identifier: str = Field(..., min_length=1, max_length=200)
    primary_metric: float = Field(..., ge=0.0, le=1000.0, allow_inf_nan=False)
    secondary_metric: float = Field(..., ge=0.0, le=1000.0, allow_inf_nan=False)
    status_descriptor: str = Field(default="NOMINAL", max_length=50)
    is_critical_flag: bool = False

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("task_id cannot be empty or whitespace")
        return v.strip()

    @field_validator("target_identifier")
    @classmethod
    def validate_target_identifier(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("target_identifier cannot be empty or whitespace")
        return v.strip()


class SystemDossier(BaseModel):
    """Result dossier from system-level task processing."""
    dossier_id: str
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: str
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    audit_hash: str
    processed_at: str
