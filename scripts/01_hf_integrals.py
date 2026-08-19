#!/usr/bin/env python
from __future__ import annotations

import argparse
import numpy as np

from qchem_vqe.classical import run_dft_reference, run_rhf_and_fci
from qchem_vqe.io_utils import save_json
from qchem_vqe.molecules import get_molecule
from _common import RESULTS_DATA, add_molecule_args


def main() -> None:
    parser = argparse.ArgumentParser(description="1) RHF + molecular integrals + FCI with PySCF")
    add_molecule_args(parser)
    parser.add_argument("--with-dft", action="store_true", help="Also calculate a PBE DFT reference")
    args = parser.parse_args()

    spec = get_molecule(args.molecule)
    result = run_rhf_and_fci(spec, args.bond, args.basis)
    payload = {
        "molecule": spec.name,
        "bond_length": spec.default_bond if args.bond is None else args.bond,
        "basis": args.basis,
        "hf_energy": result.hf_energy,
        "fci_energy": result.fci_energy,
        "nuclear_repulsion": result.nuclear_repulsion,
        "num_ao": result.num_ao,
        "num_mo": result.num_mo,
        "num_electrons": result.num_electrons,
        "orbital_energies": result.orbital_energies,
        "h1_mo": result.h1_mo,
        "eri_mo_shape": list(result.eri_mo.shape),
        "eri_mo_frobenius_norm": float(np.linalg.norm(result.eri_mo)),
        "elapsed_seconds": result.elapsed_seconds,
    }
    if args.with_dft:
        payload["pbe_dft_energy"] = run_dft_reference(
            spec, args.bond, args.basis, functional="pbe"
        )

    out = RESULTS_DATA / f"01_{args.molecule}_hf_integrals.json"
    save_json(payload, out)
    print(f"RHF total energy: {result.hf_energy:.12f} Ha")
    print(f"FCI total energy: {result.fci_energy:.12f} Ha")
    print(f"h1(MO) shape: {result.h1_mo.shape}; eri(MO) shape: {result.eri_mo.shape}")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
