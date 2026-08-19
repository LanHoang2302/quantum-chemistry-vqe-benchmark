from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import numpy as np
from pyscf import ao2mo, dft, fci, gto, mcscf, scf

from .molecules import MoleculeSpec


@dataclass
class ClassicalResult:
    hf_energy: float
    fci_energy: float
    nuclear_repulsion: float
    num_ao: int
    num_mo: int
    num_electrons: int
    h1_mo: np.ndarray
    eri_mo: np.ndarray
    orbital_energies: np.ndarray
    mo_coeff: np.ndarray
    elapsed_seconds: float


def build_pyscf_molecule(
    spec: MoleculeSpec,
    bond_length: float | None = None,
    basis: str = "sto-3g",
) -> gto.Mole:
    return gto.M(
        atom=spec.atom_string(bond_length),
        basis=basis,
        unit="Angstrom",
        charge=spec.charge,
        spin=spec.spin,
        verbose=0,
    )


def run_rhf_and_fci(
    spec: MoleculeSpec,
    bond_length: float | None = None,
    basis: str = "sto-3g",
    conv_tol: float = 1e-10,
) -> ClassicalResult:
    """Run RHF, transform one-/two-electron integrals to the MO basis, then run FCI.

    PySCF's fci.FCI(mf).kernel()[0] includes the nuclear repulsion term because
    the FCI object is constructed from the SCF object with ecore=energy_nuc().
    """
    t0 = perf_counter()
    mol = build_pyscf_molecule(spec, bond_length, basis)
    mf = scf.RHF(mol)
    mf.conv_tol = conv_tol
    hf_energy = float(mf.kernel())
    if not mf.converged:
        raise RuntimeError("PySCF RHF did not converge")

    coeff = np.asarray(mf.mo_coeff)
    h1_ao = np.asarray(mf.get_hcore())
    h1_mo = coeff.T @ h1_ao @ coeff

    eri_compact = ao2mo.kernel(mol, coeff)
    nmo = coeff.shape[1]
    eri_mo = np.asarray(ao2mo.restore(1, eri_compact, nmo))

    fci_solver = fci.FCI(mf)
    fci_solver.conv_tol = conv_tol
    fci_energy = float(fci_solver.kernel()[0])

    return ClassicalResult(
        hf_energy=hf_energy,
        fci_energy=fci_energy,
        nuclear_repulsion=float(mol.energy_nuc()),
        num_ao=int(mol.nao_nr()),
        num_mo=int(nmo),
        num_electrons=int(mol.nelectron),
        h1_mo=h1_mo,
        eri_mo=eri_mo,
        orbital_energies=np.asarray(mf.mo_energy),
        mo_coeff=coeff,
        elapsed_seconds=perf_counter() - t0,
    )


def run_casci_reference(
    spec: MoleculeSpec,
    bond_length: float | None = None,
    basis: str = "sto-3g",
    active_electrons: int = 2,
    active_orbitals: int = 2,
    conv_tol: float = 1e-10,
) -> float:
    """Return a CASCI/FCI-in-active-space total energy using canonical RHF orbitals.

    For the simple closed-shell H2/LiH examples in this repository, PySCF's
    default CASCI orbital partition (core + contiguous active orbitals) matches
    the usual Qiskit Nature ActiveSpaceTransformer setup when only counts are
    provided.
    """
    mol = build_pyscf_molecule(spec, bond_length, basis)
    mf = scf.RHF(mol)
    mf.conv_tol = conv_tol
    mf.kernel()
    if not mf.converged:
        raise RuntimeError("PySCF RHF did not converge")
    cas = mcscf.CASCI(mf, int(active_orbitals), int(active_electrons))
    cas.conv_tol = conv_tol
    energy = float(cas.kernel()[0])
    return energy


def run_dft_reference(
    spec: MoleculeSpec,
    bond_length: float | None = None,
    basis: str = "sto-3g",
    functional: str = "pbe",
) -> float:
    """Optional DFT reference (not used as the exact benchmark)."""
    mol = build_pyscf_molecule(spec, bond_length, basis)
    ks = dft.RKS(mol)
    ks.xc = functional
    ks.verbose = 0
    energy = float(ks.kernel())
    if not ks.converged:
        raise RuntimeError("PySCF DFT did not converge")
    return energy
