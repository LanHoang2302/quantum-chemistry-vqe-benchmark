from __future__ import annotations

import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit_aer.primitives import EstimatorV2
from qiskit.transpiler import generate_preset_pass_manager


def build_depolarizing_noise_model(
    one_qubit_error: float = 1e-3,
    two_qubit_error: float = 1e-2,
) -> NoiseModel:
    """Construct a small gate-depolarizing model suitable for Aer experiments."""
    if not (0 <= one_qubit_error <= 1):
        raise ValueError("one_qubit_error must be between 0 and 1")
    if not (0 <= two_qubit_error <= 1):
        raise ValueError("two_qubit_error must be between 0 and 1")

    model = NoiseModel()
    err1 = depolarizing_error(one_qubit_error, 1)
    err2 = depolarizing_error(two_qubit_error, 2)

    # Cover common single-qubit gates emitted by decomposition/transpilation.
    model.add_all_qubit_quantum_error(err1, ["x", "sx", "rz", "rx", "ry", "h"])
    model.add_all_qubit_quantum_error(err2, ["cx", "cz", "swap"])
    return model


def make_noisy_estimator(
    one_qubit_error: float = 1e-3,
    two_qubit_error: float = 1e-2,
    shots: int = 4096,
    seed: int = 7,
) -> EstimatorV2:
    """Aer EstimatorV2 using density-matrix simulation plus depolarizing noise.

    EstimatorV2's `default_precision` controls normal-distribution sampling of
    expectation values. 1/sqrt(shots) gives a transparent shot-like precision
    scale while the density-matrix backend applies the gate noise model.
    """
    model = build_depolarizing_noise_model(one_qubit_error, two_qubit_error)
    precision = 1.0 / np.sqrt(float(shots))
    return EstimatorV2(
        options={
            "default_precision": precision,
            "backend_options": {
                "method": "density_matrix",
                "noise_model": model,
                "seed_simulator": seed,
            },
            "run_options": {
                "seed_simulator": seed,
            },
        }
    )


def make_noise_transpiler(seed: int = 7):
    """Compile high-level ansatz operations to the noisy simulator basis.

    Aer EstimatorV2 executes the supplied circuit directly, so VQE must provide
    a transpiler when its ansatz contains high-level/evolved operations.
    """
    return generate_preset_pass_manager(
        optimization_level=1,
        basis_gates=["rz", "sx", "x", "cx"],
        seed_transpiler=seed,
    )
