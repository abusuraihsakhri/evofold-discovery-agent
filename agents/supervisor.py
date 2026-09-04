"""
Discovery Supervisor coordinating Folding, Docking, ADMET, and AI Operations Chat.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .base import AuditLogger, ActionExecutor, PHIGuard
from .models import (
    TargetProtein, LigandCandidate, BindingPocket, DockingScore, ADMETProfile,
    DiscoveryDossier, SystemTaskPayload, SystemDossier, UrgencyLevel
)
from .folding_worker import FoldingWorker
from .docking_worker import DockingWorker
from .admet_worker import ADMETWorker
from .llm_factory import LLMFactory


class DiscoverySupervisor:
    """Master orchestrator for AI molecular drug discovery campaigns."""

    def __init__(self, model_provider: str = "mock"):
        self.folding_worker = FoldingWorker()
        self.docking_worker = DockingWorker()
        self.admet_worker = ADMETWorker()
        self.llm = LLMFactory.create(model_provider)
        self.dossier_registry: Dict[str, DiscoveryDossier] = {}

    def screen_lead(
        self,
        target: TargetProtein,
        pocket: BindingPocket,
        ligand: LigandCandidate,
        actor: str = "DiscoverySupervisor"
    ) -> DiscoveryDossier:
        # Step 1: Fold / Generate 3D Coordinates
        coords_3d = self.folding_worker.fold_backbone(target)

        # Step 2: Molecular Docking Score
        dock_score = self.docking_worker.dock(target, pocket, ligand, coords_3d)

        # Step 3: ADMET Drug-Likeness Profile
        admet_prof = self.admet_worker.evaluate(ligand)

        # Step 4: Overall Triage Assessment
        is_lead = (dock_score.affinity_kcal_mol <= -7.5) and (admet_prof.lipinski_violations <= 1) and admet_prof.veber_compliant
        triage_status = "ADVANCE_TO_LEAD_OPTIMIZATION" if is_lead else "REVISE_OR_REJECT"

        audit_entry = AuditLogger.log(
            actor=actor,
            actor_tier="supervisor",
            event_type="LEAD_SCREENING_COMPLETED",
            details={
                "target_id": target.target_id,
                "ligand_id": ligand.ligand_id,
                "affinity_kcal_mol": dock_score.affinity_kcal_mol,
                "qed_score": admet_prof.qed_score,
                "triage_status": triage_status,
            }
        )

        dossier = DiscoveryDossier(
            campaign_id=f"CAMP-{uuid.uuid4().hex[:8].upper()}",
            target=target,
            pocket=pocket,
            ligand=ligand,
            docking=dock_score,
            admet=admet_prof,
            triage_status=triage_status,
            audit_hash=audit_entry["current_hash"],
        )

        self.dossier_registry[dossier.campaign_id] = dossier
        return dossier

    def query_operations_chat(self, query: str) -> str:
        # Enforce zero PHI
        PHIGuard.assert_no_phi(query)
        prompt = f"You are EvoFold-Discovery Supervisor. Answer the medicinal chemistry question: {query}"
        return self.llm.invoke(prompt)


class SystemSupervisor:
    """System-level supervisor for processing task payloads with urgency classification."""

    # Thresholds for urgency classification
    ELEVATED_THRESHOLD = 25.0
    CRITICAL_THRESHOLD = 35.0

    def __init__(self, model_provider: str = "mock"):
        self.dossier_registry: Dict[str, SystemDossier] = {}

    def _classify_urgency(self, payload: SystemTaskPayload) -> UrgencyLevel:
        """Classify task urgency based on metrics and flags."""
        if payload.is_critical_flag:
            return UrgencyLevel.CRITICAL_STAT_PANIC

        primary = payload.primary_metric
        secondary = payload.secondary_metric

        if primary >= self.CRITICAL_THRESHOLD or secondary >= self.CRITICAL_THRESHOLD:
            return UrgencyLevel.CRITICAL_STAT_PANIC
        elif primary >= self.ELEVATED_THRESHOLD or secondary >= self.ELEVATED_THRESHOLD:
            return UrgencyLevel.ELEVATED_RISK
        else:
            return UrgencyLevel.ROUTINE

    def _determine_integrity(self, payload: SystemTaskPayload) -> str:
        """Determine integrity status based on payload characteristics."""
        if payload.status_descriptor == "DISCORDANT_ANOMALY":
            return "DISCORDANT_ANOMALY"
        elif payload.is_critical_flag:
            return "RECALIBRATION_REQUIRED"
        else:
            return "VALIDATED_OPTIMAL"

    def process_task(self, payload: SystemTaskPayload) -> SystemDossier:
        """Process a system task payload and return a dossier."""
        urgency = self._classify_urgency(payload)
        integrity = self._determine_integrity(payload)

        alerts = []
        if payload.primary_metric >= self.CRITICAL_THRESHOLD:
            alerts.append({
                "worker": "InvariantQCWorker",
                "alert": "Primary metric exceeds critical threshold"
            })
        if payload.secondary_metric >= self.CRITICAL_THRESHOLD:
            alerts.append({
                "worker": "SafetyEscalationWorker",
                "alert": "Secondary metric exceeds critical threshold"
            })
        if payload.is_critical_flag:
            alerts.append({
                "worker": "ProtocolConformanceWorker",
                "alert": "Critical emergency interlock flag active"
            })

        audit_entry = AuditLogger.log(
            actor="SystemSupervisor",
            actor_tier="system",
            event_type="TASK_PROCESSED",
            details={
                "task_id": payload.task_id,
                "urgency": urgency.value,
                "integrity": integrity,
            }
        )

        dossier = SystemDossier(
            dossier_id=f"SYS-{uuid.uuid4().hex[:8].upper()}",
            task_id=payload.task_id,
            target_identifier=payload.target_identifier,
            overall_urgency=urgency,
            integrity_status=integrity,
            alerts=alerts,
            audit_hash=audit_entry["current_hash"],
            processed_at=datetime.now(timezone.utc).isoformat(),
        )

        self.dossier_registry[dossier.dossier_id] = dossier
        return dossier
