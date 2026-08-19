# Quantum Chemistry VQE Benchmark

## What this project implements

1. **PySCF RHF + molecular integrals** — compute Hartree–Fock energy, one-electron integrals and two-electron repulsion integrals in the MO basis. An optional PBE/DFT reference is included.
2. **Electronic Hamiltonian in second quantization** — build a Qiskit Nature `ElectronicStructureProblem` and inspect the resulting fermionic Hamiltonian.
3. **Jordan–Wigner vs Parity mapping** — compare qubit count and Pauli-term count. The Parity mapper is constructed with particle counts so Qiskit Nature can apply its documented two-qubit reduction when allowed.
4. **VQE + UCCSD vs exact/FCI** — run VQE with a Hartree–Fock initial state and UCCSD ansatz; compare against Qiskit exact diagonalization and PySCF FCI.
5. **Potential Energy Surface (PES)** — scan bond lengths for H2 or LiH and export CSV + PNG curves for RHF, FCI and VQE.
6. **Optimizer benchmark** — compare SLSQP, COBYLA, L-BFGS-B and SPSA by final energy error, objective evaluations and runtime.
7. **Noise + ADAPT-VQE** — run a depolarizing-noise experiment using Qiskit Aer `EstimatorV2`, and an ADAPT-VQE extension using a UCCSD chemistry excitation pool.

## Stack

- Python 3.10+
- Qiskit 2.5.1
- Qiskit Nature 0.8.0
- Qiskit Algorithms 0.4.0
- Qiskit Aer 0.17.2
- PySCF 2.14.0
- NumPy / SciPy / pandas / Matplotlib

These versions are intentionally pinned because Qiskit's primitives and algorithm APIs evolve quickly.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Run the seven experiments

```bash
python scripts/01_hf_integrals.py --molecule h2 --with-dft
python scripts/02_second_quantization.py --molecule h2
python scripts/03_mapper_comparison.py --molecule h2
python scripts/04_vqe_exact_fci.py --molecule h2 --mapper parity --maxiter 250
python scripts/05_pes_scan.py --molecule h2 --points 7 --maxiter 180
python scripts/06_optimizer_benchmark.py --molecule h2 --maxiter 200
python scripts/07_noise_and_adapt.py --molecule h2 --maxiter 150
```

Or run the practical H2 suite:

```bash
python scripts/run_all.py
```

Outputs are written under:

- `results/data/` — JSON/CSV numerical results
- `results/figures/` — PES and convergence plots

## LiH active-space example

Full-space LiH/UCCSD is considerably more expensive than H2. For a laptop-friendly research demo, use an explicit active space and report that choice:

```bash
python scripts/04_vqe_exact_fci.py \
  --molecule lih \
  --mapper parity \
  --active-electrons 2 \
  --active-orbitals 3 \
  --maxiter 300
```

When an active space is requested, the scripts compute a matched PySCF CASCI reference (FCI within the chosen active space) and also keep the full-space PySCF FCI energy as a separate reference.

## Experiment details

### 1. RHF and MO integrals

`src/qchem_vqe/classical.py` uses PySCF to:

- construct H2 or LiH,
- solve restricted Hartree–Fock,
- transform the one-electron core Hamiltonian from AO to MO basis,
- transform electron-repulsion integrals `(ij|kl)` to the MO basis,
- solve full configuration interaction (FCI) as a classical exact reference for the chosen finite basis.

### 2. Second quantization

Qiskit Nature's `PySCFDriver` generates an `ElectronicStructureProblem`. The electronic Hamiltonian is accessed through `problem.hamiltonian.second_q_op()` and saved as fermionic creation/annihilation terms.

### 3. Fermion-to-qubit mappings

The project compares:

- `JordanWignerMapper()`
- `ParityMapper(num_particles=problem.num_particles)`

Metrics include the resulting number of qubits and number of Pauli terms.

### 4. VQE/UCCSD benchmark

The VQE implementation follows the current Qiskit Nature 0.8 workflow:

- Hartree–Fock initial state,
- UCCSD ansatz,
- all-zero initial amplitudes (therefore starting from the HF state),
- a `StatevectorEstimator`,
- selected classical optimizer,
- `GroundStateEigensolver` for end-to-end electronic-structure interpretation.

For small systems, `NumPyMinimumEigensolver` supplies an exact qubit-space reference.

### 5. Potential-energy curve

For each bond distance, the project calculates RHF and full-space FCI. With an active space it also calculates a matched CASCI reference. Unless `--skip-vqe` is set, it calculates VQE and saves an energy-error column in milli-Hartree against the matched reference.

### 6. Optimizer benchmark

The benchmark records:

- final VQE energy,
- error against exact diagonalization (mHa),
- objective-evaluation count,
- elapsed wall-clock time,
- convergence history.

This makes the result more useful than reporting only the final energy.

### 7. Noise and ADAPT-VQE

The noise experiment builds a custom depolarizing model and passes it into Qiskit Aer `EstimatorV2` through `backend_options`. Because Aer `EstimatorV2` executes the supplied circuit directly, the VQE path also supplies a preset pass manager that decomposes the UCCSD circuit to `rz/sx/x/cx` before execution. The density-matrix simulator applies channel noise; `default_precision = 1/sqrt(shots)` adds a transparent shot-like precision scale to estimator values. SPSA is used for the noisy optimization because it is designed for stochastic objective functions.

The ADAPT-VQE path follows Qiskit Nature 0.8's documented integration with UCCSD and `GroundStateEigensolver`, including the documented temporary `supports_aux_operators` workaround.

## Suggested GitHub screenshots

After running the suite, include these in the repository description or README:

1. `results/figures/05_h2_pes.png`
2. `results/figures/06_h2_optimizer_convergence.png`
3. a terminal screenshot from `04_vqe_exact_fci.py` showing RHF/FCI/exact/VQE energies and mHa error
4. a compact table from `06_h2_optimizer_benchmark.csv`

## Testing

```bash
python -m pip install pytest
pytest -q
```

## Reproducibility note

The repository is source-complete, but generated numerical results are intentionally not committed. Run the scripts in the pinned environment to generate your own measurements. That is important if you want to discuss the project in an interview or quote benchmark numbers on a CV.

## Official documentation used as API references

- Qiskit Nature 0.8 getting started: https://qiskit-community.github.io/qiskit-nature/getting_started.html
- Qiskit Nature qubit mappers: https://qiskit-community.github.io/qiskit-nature/tutorials/06_qubit_mappers.html
- Qiskit Nature ADAPT-VQE how-to: https://qiskit-community.github.io/qiskit-nature/howtos/adapt_vqe.html
- Qiskit Algorithms VQE: https://qiskit-community.github.io/qiskit-algorithms/stubs/qiskit_algorithms.VQE.html
- Qiskit Aer EstimatorV2: https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.EstimatorV2.html
- PySCF FCI guide: https://pyscf.org/user/ci.html
- PySCF AO-to-MO integral transformation: https://pyscf.org/pyscf_api_docs/pyscf.ao2mo.html

## License

MIT
