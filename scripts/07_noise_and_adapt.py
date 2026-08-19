#!/usr/bin/env python
from __future__ import annotations

import argparse

from qchem_vqe.io_utils import save_json
from qchem_vqe.molecules import get_molecule
from qchem_vqe.noise import make_noise_transpiler, make_noisy_estimator
from qchem_vqe.problem import build_electronic_problem
from qchem_vqe.solvers import exact_ground_state, run_adapt_vqe, run_vqe
from _common import RESULTS_DATA, add_molecule_args


def main() -> None:
    parser = argparse.ArgumentParser(description="7) Noisy VQE and ADAPT-VQE extension")
    add_molecule_args(parser)
    parser.add_argument("--mapper", choices=["jw", "parity"], default="parity")
    parser.add_argument("--maxiter", type=int, default=200)
    parser.add_argument("--one-qubit-error", type=float, default=1e-3)
    parser.add_argument("--two-qubit-error", type=float, default=1e-2)
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--skip-noise", action="store_true")
    parser.add_argument("--skip-adapt", action="store_true")
    args = parser.parse_args()

    spec = get_molecule(args.molecule)
    problem = build_electronic_problem(
        spec, args.bond, args.basis, args.active_electrons, args.active_orbitals
    )
    exact = exact_ground_state(problem, args.mapper)
    ideal = run_vqe(problem, args.mapper, "slsqp", args.maxiter)

    payload = {
        "molecule": spec.name,
        "exact_total_energy": exact.total_energy,
        "ideal_vqe_total_energy": ideal.total_energy,
        "ideal_vqe_error_mHa": 1000 * (ideal.total_energy - exact.total_energy),
    }

    if not args.skip_noise:
        estimator = make_noisy_estimator(
            args.one_qubit_error, args.two_qubit_error, args.shots
        )
        noisy = run_vqe(
            problem,
            args.mapper,
            "spsa",
            args.maxiter,
            estimator=estimator,
            transpiler=make_noise_transpiler(),
        )
        payload["noisy_vqe"] = {
            "total_energy": noisy.total_energy,
            "error_vs_exact_mHa": 1000 * (noisy.total_energy - exact.total_energy),
            "one_qubit_error": args.one_qubit_error,
            "two_qubit_error": args.two_qubit_error,
            "shots_precision_proxy": args.shots,
            "optimizer": "SPSA",
            "evaluations": noisy.evaluations,
            "elapsed_seconds": noisy.elapsed_seconds,
        }

    if not args.skip_adapt:
        adapt = run_adapt_vqe(problem, args.mapper, args.maxiter)
        payload["adapt_vqe"] = {
            "total_energy": adapt.total_energy,
            "error_vs_exact_mHa": 1000 * (adapt.total_energy - exact.total_energy),
            "elapsed_seconds": adapt.elapsed_seconds,
            "extra": adapt.extra,
        }

    out = RESULTS_DATA / f"07_{args.molecule}_noise_and_adapt.json"
    save_json(payload, out)
    print(payload)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
