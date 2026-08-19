#!/usr/bin/env python
from __future__ import annotations

import argparse

from qchem_vqe.io_utils import save_json
from qchem_vqe.molecules import get_molecule
from qchem_vqe.problem import build_electronic_problem, fermionic_hamiltonian
from _common import RESULTS_DATA, add_molecule_args


def main() -> None:
    parser = argparse.ArgumentParser(description="2) Build the second-quantized electronic Hamiltonian")
    add_molecule_args(parser)
    parser.add_argument("--max-terms", type=int, default=40)
    args = parser.parse_args()

    spec = get_molecule(args.molecule)
    problem = build_electronic_problem(
        spec,
        args.bond,
        args.basis,
        args.active_electrons,
        args.active_orbitals,
    )
    op = fermionic_hamiltonian(problem)
    terms = list(op.items())
    payload = {
        "molecule": spec.name,
        "num_spatial_orbitals": problem.num_spatial_orbitals,
        "num_particles": list(problem.num_particles),
        "num_fermionic_terms": len(terms),
        "sample_terms": [{"label": label, "coefficient": complex(coeff)} for label, coeff in terms[: args.max_terms]],
    }
    out = RESULTS_DATA / f"02_{args.molecule}_second_quantized_hamiltonian.json"
    save_json(payload, out)

    print(f"Spatial orbitals: {problem.num_spatial_orbitals}")
    print(f"Particles (alpha, beta): {problem.num_particles}")
    print(f"Fermionic terms: {len(terms)}")
    print("\nFirst terms:")
    for label, coeff in terms[: args.max_terms]:
        print(f"  {coeff:+.10f}  {label}")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
