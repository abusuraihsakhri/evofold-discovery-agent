"""
Unit & Integration Test Suite for EvoFold Molecular Discovery.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException
from agents.models import TargetProtein, LigandCandidate, BindingPocket, SystemTaskPayload, UrgencyLevel
from agents.folding_worker import FoldingWorker
from agents.docking_worker import DockingWorker
from agents.admet_worker import ADMETWorker
from agents.supervisor import DiscoverySupervisor, SystemSupervisor
from cli import main


def test_phi_guard():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient John Doe MRN-994827 is taking Osimertinib")

    # Safe text passes
    PHIGuard.assert_no_phi("Target EGFR kinase domain mutant T790M")


def test_folding_and_docking():
    target = TargetProtein(
        target_id="KRAS",
        protein_name="KRAS_G12D",
        amino_acid_sequence="MTEYKLVVVGADGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAGQ"
    )
    pocket = BindingPocket(pocket_id="SWITCH_II_POCKET", center_x=10.0, center_y=10.0, center_z=10.0, radius_angstrom=8.0)
    ligand = LigandCandidate(ligand_id="MRTX1133", smiles="C1CC1...", molecular_weight=480.5, logp=2.8, tpsa=72.0)

    folder = FoldingWorker()
    coords = folder.fold_backbone(target)
    assert len(coords) == len(target.amino_acid_sequence)

    docker = DockingWorker()
    dock_score = docker.dock(target, pocket, ligand, coords)
    assert dock_score.affinity_kcal_mol < 0.0


def test_admet():
    ligand = LigandCandidate(
        ligand_id="LIG-01",
        smiles="CC...",
        molecular_weight=420.0,
        logp=2.5,
        tpsa=65.0,
        hbd_count=2,
        hba_count=4,
        rotatable_bonds=4
    )
    prof = ADMETWorker.evaluate(ligand)
    assert prof.lipinski_violations == 0
    assert prof.veber_compliant is True
    assert prof.qed_score > 0.8


def test_supervisor_and_cli():
    supervisor = DiscoverySupervisor(model_provider="mock")
    target = TargetProtein(target_id="BRAF", protein_name="BRAF_V600E", amino_acid_sequence="MKHHHHHHASMAL...")
    pocket = BindingPocket(pocket_id="DFG_OUT", center_x=0.0, center_y=0.0, center_z=0.0, radius_angstrom=10.0)
    ligand = LigandCandidate(ligand_id="VEMURAFENIB", smiles="CC...", molecular_weight=489.9, logp=3.5, tpsa=88.0)

    dossier = supervisor.screen_lead(target, pocket, ligand)
    assert dossier.campaign_id.startswith("CAMP-")
    assert dossier.audit_hash != ""

    assert main(["screen", "--target", "BRAF"]) == 0
    assert main(["chat", "Explain", "docking", "scores"]) == 0
    assert main(["audit"]) == 0


def test_audit_integrity_verification():
    """Test that audit trail integrity verification works correctly."""
    # Log some entries
    AuditLogger.log("test_actor", "test", "TEST_EVENT", {"data": "test1"})
    AuditLogger.log("test_actor", "test", "TEST_EVENT", {"data": "test2"})

    # Verify integrity
    assert AuditLogger.verify_integrity() is True


def test_system_supervisor_routine():
    """Test system supervisor classifies routine tasks correctly."""
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TEST-001",
        target_identifier="TARGET-ROUTINE",
        primary_metric=10.0,
        secondary_metric=5.0,
        status_descriptor="NOMINAL",
        is_critical_flag=False
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == "VALIDATED_OPTIMAL"
    assert dossier.audit_hash != ""


def test_system_supervisor_elevated():
    """Test system supervisor classifies elevated risk tasks correctly."""
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TEST-002",
        target_identifier="TARGET-ELEVATED",
        primary_metric=30.0,
        secondary_metric=5.0,
        status_descriptor="NOMINAL",
        is_critical_flag=False
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ELEVATED_RISK


def test_system_supervisor_critical():
    """Test system supervisor classifies critical tasks correctly."""
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TEST-003",
        target_identifier="TARGET-CRITICAL",
        primary_metric=10.0,
        secondary_metric=5.0,
        status_descriptor="DISCORDANT_ANOMALY",
        is_critical_flag=True
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.CRITICAL_STAT_PANIC
    # DISCORDANT_ANOMALY takes precedence in integrity determination
    assert dossier.integrity_status in ("DISCORDANT_ANOMALY", "RECALIBRATION_REQUIRED")
    assert len(dossier.alerts) > 0


def test_system_task_payload_validation():
    """Test SystemTaskPayload input validation."""
    # Valid payload
    payload = SystemTaskPayload(
        task_id="VALID-001",
        target_identifier="TARGET-VALID",
        primary_metric=50.0,
        secondary_metric=25.0
    )
    assert payload.task_id == "VALID-001"
    assert payload.primary_metric == 50.0

    # Test metric bounds
    with pytest.raises(Exception):
        SystemTaskPayload(
            task_id="INVALID",
            target_identifier="TARGET",
            primary_metric=-1.0,  # Below minimum
            secondary_metric=5.0
        )

    with pytest.raises(Exception):
        SystemTaskPayload(
            task_id="INVALID",
            target_identifier="TARGET",
            primary_metric=5.0,
            secondary_metric=1001.0  # Above maximum
        )


def test_system_task_payload_whitespace_validation():
    """Test that whitespace-only IDs are rejected."""
    with pytest.raises(Exception):
        SystemTaskPayload(
            task_id="   ",
            target_identifier="TARGET",
            primary_metric=5.0,
            secondary_metric=5.0
        )
