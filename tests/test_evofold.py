"""
Unit & Integration Test Suite for EvoFold Molecular Discovery.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException
from agents.models import TargetProtein, LigandCandidate, BindingPocket
from agents.folding_worker import FoldingWorker
from agents.docking_worker import DockingWorker
from agents.admet_worker import ADMETWorker
from agents.supervisor import DiscoverySupervisor
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
