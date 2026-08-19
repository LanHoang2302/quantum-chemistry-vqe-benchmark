#!/usr/bin/env python
from __future__ import annotations

import argparse
import pandas as pd

from qchem_vqe.io_utils import save_csv, save_json
from qchem_vqe.molecules import get_molecule
from qchem_vqe.plotting import plot_optimizer_convergence
from qchem_vqe.problem import build_electronic_problem
from qchem_vqe.solvers import exact_ground_state, run_vqe
from _common import RESULTS_DATA, RESULTS_FIGURES, add_molecule_args


def main() -> None:
    parser = argparse.ArgumentParser(description="6) Benchmark VQE classical optimizers")
    add_molecule_args(parser)
    parser.add_argument("--mapper", choices=["jw", "parity"], default="parity")
    parser.add_argument("--maxiter", type=int, default=250)
    parser.add_argument(
        "--optimizers",
        nargs="+",
        default=["slsqp", "cobyla", "l-bfgs-b", "spsa"],
        choices=["slsqp", "cobyla", "l-bfgs-b", "spsa"],
    )
    args = parser.parse_args()

    spec = get_molecule(args.molecule)
    problem = build_electronic_problem(
        spec, args.bond, args.basis, args.active_electrons, args.active_orbitals
    )
    exact = exact_ground_state(problem, args.mapper)

    rows = []
    histories = {}
    for optimizer in args.optimizers:
        result = run_vqe(problem, args.mapper, optimizer, args.maxiter)
        rows.append(
            {
                "optimizer": optimizer,
                "vqe_total_energy": result.total_energy,
                "error_vs_exact_mHa": 1000.0 * (result.total_energy - exact.total_energy),
                "evaluations": result.evaluations,
                "elapsed_seconds": result.elapsed_seconds,
                "num_parameters": result.num_parameters,
            }
        )
        histories[optimizer] = result.convergence or []
        print(rows[-1])

    df = pd.DataFrame(rows).sort_values(["error_vs_exact_mHa", "elapsed_seconds"])
    csv_path = RESULTS_DATA / f"06_{args.molecule}_optimizer_benchmark.csv"
    hist_path = RESULTS_DATA / f"06_{args.molecule}_optimizer_histories.json"
    fig_path = RESULTS_FIGURES / f"06_{args.molecule}_optimizer_convergence.png"
    save_csv(df, csv_path)
    save_json(histories, hist_path)
    plot_optimizer_convergence(histories, fig_path)
    print(f"Exact total energy: {exact.total_energy:.12f} Ha")
    print(f"Saved: {csv_path}")
    print(f"Saved: {hist_path}")
    print(f"Saved: {fig_path}")


if __name__ == "__main__":
    main()
