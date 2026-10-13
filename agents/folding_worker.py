"""
Deterministic illustrative C-alpha helix generator; not a protein folding predictor.
"""
import math
from typing import List
from .models import TargetProtein, Residue3DCoordinate


class FoldingWorker:
    """Generates fixed helical C-alpha coordinates, independent of sequence chemistry."""

    @classmethod
    def fold_backbone(cls, target: TargetProtein) -> List[Residue3DCoordinate]:
        seq = target.amino_acid_sequence
        coords = []
        # Simulate alpha-helix & beta-sheet folding dynamics (3.8 Angstrom C-alpha distance)
        r = 5.0
        pitch = 1.5
        for i, aa in enumerate(seq):
            angle = i * (2.0 * math.pi / 3.6)
            x = round(r * math.cos(angle), 3)
            y = round(r * math.sin(angle), 3)
            z = round(i * pitch, 3)
            coords.append(Residue3DCoordinate(
                residue_index=i + 1,
                amino_acid=aa,
                x=x,
                y=y,
                z=z,
                b_factor=20.0 + (i % 5) * 2.0,
            ))
        return coords
