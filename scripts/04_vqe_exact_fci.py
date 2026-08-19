#!/usr/bin/env python
from __future__ import annotations

import argparse

from qchem_vqe.classical import run_casci_reference, run_rhf_and_fci
from qchem_vqe.io_utils import save_json
from qchem_vqe.molecules import get_molecule
from qchem_vqe.problem import build_electronic_problem
from qchem_vqe.solvers import exact_ground_state, run_vqe
from _common import RESULTS_DATA, add_molecule_args


def main() -> None:
    parser = argparse.ArgumentParser(description="4) VQE/UCCSD benchmark against exact diagonalization and PySCF FCI")
    add_molecule_args(parser)
    parser.add_argument("--mapper", choices=["jw", "parity"], default="parity")
    parser.add_argument("--optimizer", choices=["slsqp", "cobyla", "l-bfgs-b", "spsa"], default="slsqp")
    parser.add_argument("--maxiter", type=int, default=300)
    args = parser.parse_args()

    spec = get_molecule(args.molecule)
    bond = spec.default_bond if args.bond is None else args.bond

    classical = run_rhf_and_fci(spec, bond, args.basis)
    problem = build_electronic_problem(
        spec, bond, args.basis, args.active_electrons, args.active_orbitals
    )
    exact = exact_ground_state(problem, args.mapper)
    vqe = run_vqe(problem, args.mapper, args.optimizer, args.maxiter)
    if args.active_electrons is not None:
        matched_reference = run_casci_reference(
            spec, bond, args.basis,
            args.active_electrons, args.active_orbitals
        )
        reference_method = "PySCF CASCI (FCI within matched active space)"
    else:
        matched_reference = classical.fci_energy
        reference_method = "PySCF full-space FCI"

    payload = {
        "molecule": spec.name,
        "bond_length": bond,
        "mapper": args.mapper,
        "optimizer": args.optimizer,
        "hf_total_energy": classical.hf_energy,
        "pyscf_full_fci_total_energy": classical.fci_energy,
        "pyscf_matched_reference_method": reference_method,
        "pyscf_matched_reference_total_energy": matched_reference,
        "qiskit_exact_total_energy": exact.total_energy,
        "vqe_total_energy": vqe.total_energy,
        "vqe_minus_qiskit_exact_mHa": 1000.0 * (vqe.total_energy - exact.total_energy),
        "matched_reference_minus_qiskit_exact_mHa": 1000.0 * (matched_reference - exact.total_energy),
        "vqe_elapsed_seconds": vqe.elapsed_seconds,
        "vqe_evaluations": vqe.evaluations,
        "vqe_num_parameters": vqe.num_parameters,
        "convergence": vqe.convergence,
        "note": "When an active space is requested, the matched PySCF reference is CASCI (FCI inside that active space); full-space PySCF FCI is also retained separately.",
    }
    out = RESULTS_DATA / f"04_{args.molecule}_vqe_exact_fci.json"
    save_json(payload, out)

    print(f"RHF:          {classical.hf_energy:.12f} Ha")
    print(f"PySCF FCI:    {classical.fci_energy:.12f} Ha")
    if args.active_electrons is not None:
        print(f"PySCF CASCI:  {matched_reference:.12f} Ha")
    print(f"Qiskit exact: {exact.total_energy:.12f} Ha")
    print(f"VQE-UCCSD:    {vqe.total_energy:.12f} Ha")
    print(f"VQE error:    {1000*(vqe.total_energy-exact.total_energy):+.6f} mHa")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
