"""
Command Line Interface for EvoFold Molecular Discovery.
"""
import argparse
import json
import sys
from agents.models import TargetProtein, LigandCandidate, BindingPocket
from agents.supervisor import DiscoverySupervisor
from agents.base import AuditLogger

supervisor = DiscoverySupervisor(model_provider="mock")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="evofold-discovery-agent", description="Autonomous Molecular Drug Discovery Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Screen
    p_screen = subparsers.add_parser("screen", help="Screen a small-molecule ligand against a target protein pocket")
    p_screen.add_argument("--target", default="EGFR_TKD", help="Protein target ID")
    p_screen.add_argument("--sequence", default="MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAGQ", help="Amino acid sequence")
    p_screen.add_argument("--ligand", default="OSIMERTINIB_DERIV", help="Ligand ID")
    p_screen.add_argument("--smiles", default="CN1CCN(CC1)C2=CC(=C(C=C2)NC3=NC=CC(=N3)C4=CN(C5=CC=CC=C54)C)NC(=O)C=C", help="SMILES string")
    p_screen.add_argument("--mw", type=float, default=499.6)
    p_screen.add_argument("--logp", type=float, default=3.2)
    p_screen.add_argument("--tpsa", type=float, default=85.2)

    # Chat
    p_chat = subparsers.add_parser("chat", help="Ask medicinal chemistry questions")
    p_chat.add_argument("query", nargs="+")

    # Audit
    subparsers.add_parser("audit", help="Display cryptographic HMAC audit trail")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "screen":
        target = TargetProtein(target_id=args.target, protein_name=args.target, amino_acid_sequence=args.sequence)
        pocket = BindingPocket(pocket_id="ATP_BINDING_SITE", center_x=12.5, center_y=-4.2, center_z=18.0, radius_angstrom=10.0)
        ligand = LigandCandidate(ligand_id=args.ligand, smiles=args.smiles, molecular_weight=args.mw, logp=args.logp, tpsa=args.tpsa)

        dossier = supervisor.screen_lead(target, pocket, ligand)
        print("=" * 80)
        print(f"  EVOFOLD DRUG DISCOVERY DOSSIER: {dossier.campaign_id}")
        print("=" * 80)
        print(f"  Target: {target.target_id} ({len(target.amino_acid_sequence)} AA)")
        print(f"  Ligand: {ligand.ligand_id} (MW: {ligand.molecular_weight:.1f}, LogP: {ligand.logp:.2f})")
        print(f"  Docking Affinity: {dossier.docking.affinity_kcal_mol:.2f} kcal/mol (H-Bonds: {dossier.docking.hbond_count})")
        print(f"  ADMET Profile:    QED={dossier.admet.qed_score:.3f} | Lipinski Viols={dossier.admet.lipinski_violations} | BBB={dossier.admet.bbb_permeable}")
        print(f"  Triage Decision:  [{dossier.triage_status}]")
        print(f"  HMAC Audit Hash:  {dossier.audit_hash}")
        print("=" * 80)
        return 0

    if args.command == "chat":
        query_text = " ".join(args.query)
        ans = supervisor.query_operations_chat(query_text)
        print(f"\n[EvoFold-Discovery Supervisor]:\n{ans}\n")
        return 0

    if args.command == "audit":
        trail = AuditLogger.get_trail()
        print(f"HMAC-SHA256 Audit Trail ({len(trail)} blocks):")
        for b in trail:
            print(f"  [{b['timestamp']}] {b['event_type']} by {b['actor']} (hash={b['current_hash'][:16]}...)")
        return 0

    if args.command == "serve":
        import uvicorn
        from agents.api import app
        uvicorn.run(app, host=args.host, port=args.port)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
