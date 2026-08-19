from __future__ import annotations

import argparse

from .molecules import MOLECULES


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quantum chemistry VQE benchmark. See scripts/ for the seven experiments."
    )
    parser.add_argument("--list-molecules", action="store_true")
    args = parser.parse_args()
    if args.list_molecules:
        for key, spec in MOLECULES.items():
            print(f"{key}: {spec.name}, default bond={spec.default_bond} Å")
    else:
        parser.print_help()
