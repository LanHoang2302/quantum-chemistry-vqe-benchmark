from qchem_vqe.mapping import mapping_stats
from qchem_vqe.molecules import get_molecule
from qchem_vqe.problem import build_electronic_problem, fermionic_hamiltonian
from qchem_vqe.solvers import exact_ground_state


def test_h2_mapping_and_exact_energy():
    problem = build_electronic_problem(get_molecule("h2"), 0.735, "sto3g")
    fermion = fermionic_hamiltonian(problem)

    jw_stats, _ = mapping_stats(problem, fermion, "jw")
    parity_stats, _ = mapping_stats(problem, fermion, "parity")

    assert jw_stats.num_qubits == 4
    assert parity_stats.num_qubits == 2

    exact = exact_ground_state(problem, "parity")
    assert abs(exact.total_energy - (-1.137306)) < 5e-4
