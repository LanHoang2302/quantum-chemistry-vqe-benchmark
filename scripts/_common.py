from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DATA = ROOT / "results" / "data"
RESULTS_FIGURES = ROOT / "results" / "figures"


def add_molecule_args(parser: argparse.ArgumentParser, default_molecule: str = "h2") -> None:
    parser.add_argument("--molecule", choices=["h2", "lih"], default=default_molecule)
    parser.add_argument("--bond", type=float, default=None, help="Bond length in Angstrom")
    parser.add_argument("--basis", default="sto3g", help="Qiskit/PySCF basis, e.g. sto3g")
    parser.add_argument("--active-electrons", type=int, default=None)
    parser.add_argument("--active-orbitals", type=int, default=None)
