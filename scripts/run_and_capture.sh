#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")"; pwd)"
ROOT="$(dirname "$HERE")"
source "$ROOT/.venv/bin/activate"
cd "$HERE"

LOG="$ROOT/report/experiment_outputs.txt"
mkdir -p "$ROOT/report" "$ROOT/results/data" "$ROOT/results/figures"
> "$LOG"

run_script() {
    echo "================================================================" | tee -a "$LOG"
    echo ">> $*" | tee -a "$LOG"
    echo "================================================================" | tee -a "$LOG"
    python "$@" 2>&1 | tee -a "$LOG"
    echo "" | tee -a "$LOG"
}

run_script 01_hf_integrals.py --molecule h2 --with-dft
run_script 02_second_quantization.py --molecule h2
run_script 03_mapper_comparison.py --molecule h2
run_script 04_vqe_exact_fci.py --molecule h2 --mapper parity --maxiter 250
run_script 05_pes_scan.py --molecule h2 --points 7 --maxiter 180
run_script 06_optimizer_benchmark.py --molecule h2 --maxiter 200
run_script 07_noise_and_adapt.py --molecule h2 --maxiter 150

echo "ALL_DONE" | tee -a "$LOG"
