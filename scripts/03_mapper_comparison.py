#!/usr/bin/env python
from __future__ import annotations

import argparse

from qchem_vqe.io_utils import save_json
from qchem_vqe.mapping import mapping_stats
from qchem_vqe.molecules import get_molecule
from qchem_vqe.problem import build_electronic_problem, fermionic_hamiltonian
from _common import RESULTS_DATA, add_molecule_args


def main() -> None:
    parser = argparse.ArgumentParser(description="3) Compare Jordan-Wigner and Parity mappings")
    add_molecule_args(parser)
    parser.add_argument("--max-pauli-terms", type=int, default=20)
    args = parser.parse_args()

    spec = get_molecule(args.molecule)
    problem = build_electronic_problem(
        spec, args.bond, args.basis, args.active_electrons, args.active_orbitals
    )
    fermionic_op = fermionic_hamiltonian(problem)

    rows = []
    paulis = {}
    for mapper_name in ("jw", "parity"):
        stats, qubit_op = mapping_stats(problem, fermionic_op, mapper_name)
        rows.append(stats.__dict__)
        paulis[mapper_name] = [
            {"pauli": label, "coefficient": complex(coeff)}
            for label, coeff in qubit_op.to_list()[: args.max_pauli_terms]
        ]

    out = RESULTS_DATA / f"03_{args.molecule}_mapping_comparison.json"
    save_json({"stats": rows, "sample_pauli_terms": paulis}, out)
    for row in rows:
        print(
            f"{row['mapper']:>7}: qubits={row['num_qubits']:>2}, "
            f"Pauli terms={row['num_pauli_terms']}"
        )
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
