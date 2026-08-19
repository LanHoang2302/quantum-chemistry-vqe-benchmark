from __future__ import annotations

from dataclasses import dataclass

from qiskit_nature.second_q.mappers import JordanWignerMapper, ParityMapper


@dataclass
class MappingStats:
    mapper: str
    num_qubits: int
    num_pauli_terms: int


def make_mapper(name: str, problem):
    key = name.strip().lower().replace("_", "-")
    if key in {"jw", "jordan-wigner", "jordanwigner"}:
        return JordanWignerMapper()
    if key in {"parity", "p"}:
        # Providing particle counts enables Qiskit Nature's two-qubit reduction
        # when the parity symmetries allow it.
        return ParityMapper(num_particles=problem.num_particles)
    raise ValueError("mapper must be 'jw' or 'parity'")


def map_hamiltonian(fermionic_op, mapper):
    return mapper.map(fermionic_op)


def mapping_stats(problem, fermionic_op, mapper_name: str) -> tuple[MappingStats, object]:
    mapper = make_mapper(mapper_name, problem)
    qubit_op = map_hamiltonian(fermionic_op, mapper)
    stats = MappingStats(
        mapper=mapper_name,
        num_qubits=int(qubit_op.num_qubits),
        num_pauli_terms=int(len(qubit_op.paulis)),
    )
    return stats, qubit_op
