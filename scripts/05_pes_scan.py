#!/usr/bin/env python
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd

from qchem_vqe.classical import run_casci_reference, run_rhf_and_fci
from qchem_vqe.io_utils import save_csv
from qchem_vqe.molecules import get_molecule
from qchem_vqe.plotting import plot_pes
from qchem_vqe.problem import build_electronic_problem
from qchem_vqe.solvers import run_vqe
from _common import RESULTS_DATA, RESULTS_FIGURES, add_molecule_args


def main() -> None:
    parser = argparse.ArgumentParser(description="5) Scan a molecular potential-energy curve")
    add_molecule_args(parser)
    parser.add_argument("--start", type=float, default=None)
    parser.add_argument("--stop", type=float, default=None)
    parser.add_argument("--points", type=int, default=7)
    parser.add_argument("--mapper", choices=["jw", "parity"], default="parity")
    parser.add_argument("--optimizer", choices=["slsqp", "cobyla", "l-bfgs-b"], default="slsqp")
    parser.add_argument("--maxiter", type=int, default=200)
    parser.add_argument("--skip-vqe", action="store_true")
    args = parser.parse_args()

    spec = get_molecule(args.molecule)
    if args.start is None:
        args.start = 0.4 if args.molecule == "h2" else 1.0
    if args.stop is None:
        args.stop = 2.2 if args.molecule == "h2" else 3.2

    rows = []
    for r in np.linspace(args.start, args.stop, args.points):
        classical = run_rhf_and_fci(spec, float(r), args.basis)
        if args.active_electrons is not None:
            reference_energy = run_casci_reference(
                spec, float(r), args.basis,
                args.active_electrons, args.active_orbitals
            )
            reference_label = "casci_energy"
        else:
            reference_energy = classical.fci_energy
            reference_label = "fci_energy"
        row = {
            "bond_length": float(r),
            "hf_energy": classical.hf_energy,
            "fci_energy": classical.fci_energy,
        }
        if reference_label == "casci_energy":
            row["casci_energy"] = reference_energy
        if not args.skip_vqe:
            problem = build_electronic_problem(
                spec, float(r), args.basis, args.active_electrons, args.active_orbitals
            )
            vqe = run_vqe(problem, args.mapper, args.optimizer, args.maxiter)
            row["vqe_energy"] = vqe.total_energy
            row["vqe_error_vs_reference_mHa"] = 1000.0 * (vqe.total_energy - reference_energy)
        rows.append(row)
        print(row)

    df = pd.DataFrame(rows)
    csv_path = RESULTS_DATA / f"05_{args.molecule}_pes.csv"
    fig_path = RESULTS_FIGURES / f"05_{args.molecule}_pes.png"
    save_csv(df, csv_path)
    plot_pes(df, fig_path)
    print(f"Saved: {csv_path}")
    print(f"Saved: {fig_path}")


if __name__ == "__main__":
    main()
