# Validation status

The repository was assembled against the current official APIs pinned in `requirements.txt`.

Validated during packaging:

- all Python files pass `compileall` / syntax compilation;
- Qiskit Nature 0.8 API usage follows the official `PySCFDriver`, `ParityMapper`, `UCCSD`, `GroundStateEigensolver` and ADAPT-VQE examples;
- Qiskit Algorithms 0.4 `VQE` is used with the V2 Estimator interface;
- Qiskit Aer `EstimatorV2` is paired with an explicit transpiler before noisy execution, since Aer executes the supplied circuit directly;
- PySCF FCI and AO-to-MO transformation usage follows the PySCF user/API documentation.

The packaging sandbox used to create this ZIP did not have Qiskit/PySCF installed and did not permit `pip` network access, so numerical runs were not fabricated. A GitHub Actions workflow is included to install the pinned stack and execute the tests after you publish the repository.
