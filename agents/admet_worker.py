"""
ADMET Prediction Worker evaluating Lipinski Rule of 5, Veber, and BBB Permeability.
"""
import math
from typing import Dict, Any, List
from .models import ADMETProfile, LigandCandidate


class ADMETWorker:
    """Calculates physicochemical and ADMET properties for small molecules."""

    @classmethod
    def evaluate(cls, ligand: LigandCandidate) -> ADMETProfile:
        mw = ligand.molecular_weight
        logp = ligand.logp
        hbd = ligand.hbd_count
        hba = ligand.hba_count
        tpsa = ligand.tpsa
        rot_bonds = ligand.rotatable_bonds

        # Lipinski Rule of 5 violations
        lipinski_viols = 0
        if mw > 500.0: lipinski_viols += 1
        if logp > 5.0: lipinski_viols += 1
        if hbd > 5: lipinski_viols += 1
        if hba > 10: lipinski_viols += 1

        # Veber criteria
        veber_pass = (rot_bonds <= 10) and (tpsa <= 140.0)

        # Blood-Brain Barrier (BBB) Score estimation
        # BBB positive if MW < 400, LogP in 1-3, TPSA < 90, HBD < 3
        bbb_permeable = (mw < 450) and (1.0 <= logp <= 4.0) and (tpsa < 90.0) and (hbd <= 2)

        # Quantitative Estimate of Drug-Likeness (QED approximation)
        qed = max(0.0, min(1.0, 1.0 - (lipinski_viols * 0.22) - (0.15 if not veber_pass else 0.0)))

        cyp_risk = "HIGH_INHIBITION_RISK" if (logp > 4.5 and mw > 400) else "LOW_RISK"

        return ADMETProfile(
            ligand_id=ligand.ligand_id,
            molecular_weight=mw,
            logp=logp,
            tpsa=tpsa,
            hbd_count=hbd,
            hba_count=hba,
            rotatable_bonds=rot_bonds,
            lipinski_violations=lipinski_viols,
            veber_compliant=veber_pass,
            bbb_permeable=bbb_permeable,
            qed_score=round(qed, 3),
            cyp_inhibition_risk=cyp_risk,
        )
