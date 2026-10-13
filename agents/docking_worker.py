"""
Illustrative descriptor-based docking-score surrogate; does not execute AutoDock Vina.
"""
import math
from typing import List
from .models import TargetProtein, LigandCandidate, BindingPocket, DockingScore, Residue3DCoordinate


class DockingWorker:
    """Returns a deterministic score derived from descriptors, not a physical docking simulation."""

    @classmethod
    def dock(
        cls,
        target: TargetProtein,
        pocket: BindingPocket,
        ligand: LigandCandidate,
        coords: List[Residue3DCoordinate]
    ) -> DockingScore:
        # Vina scoring potential estimation:
        # Based on molecular weight, logP, polar surface area, and pocket proximity
        mw = ligand.molecular_weight
        logp = ligand.logp
        hbd = ligand.hbd_count
        hba = ligand.hba_count

        # Estimate binding affinity (more negative = stronger binding)
        base_affinity = -4.0
        lipophilic_term = -0.5 * max(0.0, min(5.0, logp))
        size_term = -0.008 * mw
        hbond_term = -0.35 * (hbd + hba * 0.5)

        total_affinity = round(base_affinity + lipophilic_term + size_term + hbond_term, 2)
        hbond_contacts = min(8, max(1, hbd + (1 if hba > 2 else 0)))

        return DockingScore(
            target_id=target.target_id,
            pocket_id=pocket.pocket_id,
            ligand_id=ligand.ligand_id,
            affinity_kcal_mol=total_affinity,
            rmsd_angstrom=1.2,
            hbond_count=hbond_contacts,
            buried_surface_area_angstrom2=round(mw * 1.8, 1),
        )
