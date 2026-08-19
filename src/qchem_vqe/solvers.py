from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import numpy as np
from qiskit.primitives import StatevectorEstimator
from qiskit_algorithms import AdaptVQE, NumPyMinimumEigensolver, VQE
from qiskit_algorithms.optimizers import COBYLA, L_BFGS_B, SLSQP, SPSA
from qiskit_algorithms.utils import algorithm_globals
from qiskit_nature.second_q.algorithms import GroundStateEigensolver
from qiskit_nature.second_q.circuit.library import HartreeFock, UCCSD

from .mapping import make_mapper


@dataclass
class SolverResult:
    method: str
    mapper: str
    total_energy: float
    elapsed_seconds: float
    evaluations: int | None = None
    num_parameters: int | None = None
    convergence: list[dict[str, float]] | None = None
    extra: dict[str, Any] | None = None


def make_optimizer(name: str, maxiter: int = 300):
    key = name.strip().lower().replace("_", "-")
    if key == "slsqp":
        return SLSQP(maxiter=maxiter)
    if key == "cobyla":
        return COBYLA(maxiter=maxiter)
    if key in {"l-bfgs-b", "lbfgsb", "l_bfgs_b"}:
        return L_BFGS_B(maxiter=maxiter, maxfun=max(5 * maxiter, maxiter))
    if key == "spsa":
        return SPSA(maxiter=maxiter)
    raise ValueError("optimizer must be one of: SLSQP, COBYLA, L_BFGS_B, SPSA")


def exact_ground_state(problem, mapper_name: str = "jw") -> SolverResult:
    mapper = make_mapper(mapper_name, problem)
    solver = GroundStateEigensolver(mapper, NumPyMinimumEigensolver())
    t0 = perf_counter()
    result = solver.solve(problem)
    elapsed = perf_counter() - t0
    return SolverResult(
        method="NumPy exact diagonalization",
        mapper=mapper_name,
        total_energy=float(np.real(result.total_energies[0])),
        elapsed_seconds=elapsed,
    )


def run_vqe(
    problem,
    mapper_name: str = "jw",
    optimizer_name: str = "slsqp",
    maxiter: int = 300,
    seed: int = 7,
    estimator=None,
    transpiler=None,
) -> SolverResult:
    algorithm_globals.random_seed = seed
    mapper = make_mapper(mapper_name, problem)
    hf_state = HartreeFock(
        problem.num_spatial_orbitals,
        problem.num_particles,
        mapper,
    )
    ansatz = UCCSD(
        problem.num_spatial_orbitals,
        problem.num_particles,
        mapper,
        initial_state=hf_state,
    )

    history: list[dict[str, float]] = []

    def callback(eval_count, params, mean, metadata):
        history.append({"eval": float(eval_count), "energy": float(np.real(mean))})

    estimator = StatevectorEstimator() if estimator is None else estimator
    vqe = VQE(
        estimator,
        ansatz,
        make_optimizer(optimizer_name, maxiter=maxiter),
        callback=callback,
        transpiler=transpiler,
    )
    # UCCSD with all-zero amplitudes prepares exactly the Hartree-Fock initial state.
    vqe.initial_point = np.zeros(ansatz.num_parameters)

    t0 = perf_counter()
    result = GroundStateEigensolver(mapper, vqe).solve(problem)
    elapsed = perf_counter() - t0

    return SolverResult(
        method=f"VQE-UCCSD/{optimizer_name.upper()}",
        mapper=mapper_name,
        total_energy=float(np.real(result.total_energies[0])),
        elapsed_seconds=elapsed,
        evaluations=len(history),
        num_parameters=int(ansatz.num_parameters),
        convergence=history,
        extra={
            "num_qubits": int(ansatz.num_qubits),
        },
    )


def run_adapt_vqe(
    problem,
    mapper_name: str = "jw",
    maxiter: int = 200,
    gradient_threshold: float = 1e-5,
    eigenvalue_threshold: float = 1e-5,
    seed: int = 7,
) -> SolverResult:
    """Run ADAPT-VQE using a chemistry UCCSD excitation pool.

    Qiskit Nature 0.8's current how-to constructs an ordinary UCCSD-based VQE,
    wraps it in AdaptVQE, and then wraps that in GroundStateEigensolver. This
    implementation follows that documented integration path.
    """
    algorithm_globals.random_seed = seed
    mapper = make_mapper(mapper_name, problem)
    hf_state = HartreeFock(problem.num_spatial_orbitals, problem.num_particles, mapper)
    ansatz = UCCSD(
        problem.num_spatial_orbitals,
        problem.num_particles,
        mapper,
        initial_state=hf_state,
    )

    base_vqe = VQE(StatevectorEstimator(), ansatz, SLSQP(maxiter=maxiter))
    base_vqe.initial_point = np.zeros(ansatz.num_parameters)
    adapt = AdaptVQE(
        base_vqe,
        gradient_threshold=gradient_threshold,
        eigenvalue_threshold=eigenvalue_threshold,
        max_iterations=maxiter,
    )
    # Work around the integration gap explicitly documented by Qiskit Nature 0.8.
    adapt.supports_aux_operators = lambda: True

    t0 = perf_counter()
    result = GroundStateEigensolver(mapper, adapt).solve(problem)
    elapsed = perf_counter() - t0

    raw = result.raw_result
    extra: dict[str, Any] = {}
    for attr in ("num_iterations", "final_max_gradient", "termination_criterion"):
        if hasattr(raw, attr):
            value = getattr(raw, attr)
            extra[attr] = value.value if hasattr(value, "value") else value

    return SolverResult(
        method="ADAPT-VQE/UCCSD-pool",
        mapper=mapper_name,
        total_energy=float(np.real(result.total_energies[0])),
        elapsed_seconds=elapsed,
        evaluations=None,
        num_parameters=None,
        extra=extra,
    )
