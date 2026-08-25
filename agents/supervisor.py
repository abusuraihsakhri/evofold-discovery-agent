"""
Discovery Supervisor coordinating Folding, Docking, ADMET, and AI Operations Chat.
"""
import uuid
from typing import Dict, Any, List, Optional
from .base import AuditLogger, ActionExecutor, PHIGuard
from .models import TargetProtein, LigandCandidate, BindingPocket, DockingScore, ADMETProfile, DiscoveryDossier
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
