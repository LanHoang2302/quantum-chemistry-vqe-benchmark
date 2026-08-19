from __future__ import annotations

from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.transformers import ActiveSpaceTransformer
from qiskit_nature.units import DistanceUnit

from .molecules import MoleculeSpec


def build_electronic_problem(
    spec: MoleculeSpec,
    bond_length: float | None = None,
    basis: str = "sto3g",
    active_electrons: int | None = None,
    active_orbitals: int | None = None,
):
    """Build a Qiskit Nature ElectronicStructureProblem via the PySCF driver.

    If an active space is requested, both active_electrons and active_orbitals
    must be supplied. The transformer retains the inactive contribution as an
    effective energy/operator contribution as defined by Qiskit Nature.
    """
    driver = PySCFDriver(
        atom=spec.atom_string(bond_length),
        unit=DistanceUnit.ANGSTROM,
        charge=spec.charge,
        spin=spec.spin,
        basis=basis,
    )
    problem = driver.run()

    if (active_electrons is None) ^ (active_orbitals is None):
        raise ValueError("active_electrons and active_orbitals must be provided together")
    if active_electrons is not None and active_orbitals is not None:
        transformer = ActiveSpaceTransformer(
            num_electrons=int(active_electrons),
            num_spatial_orbitals=int(active_orbitals),
        )
        problem = transformer.transform(problem)
    return problem


def fermionic_hamiltonian(problem):
    """Return the electronic Hamiltonian as a FermionicOp in second quantization."""
    return problem.hamiltonian.second_q_op()
