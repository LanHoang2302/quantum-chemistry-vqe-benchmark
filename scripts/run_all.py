#!/usr/bin/env python
"""Run a practical CV-sized suite on H2.

This intentionally uses modest settings so a laptop can finish. For LiH, run
individual scripts with an active space, for example --active-electrons 2
--active-orbitals 3.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent

COMMANDS = [
    ["01_hf_integrals.py", "--molecule", "h2", "--with-dft"],
    ["02_second_quantization.py", "--molecule", "h2"],
    ["03_mapper_comparison.py", "--molecule", "h2"],
    ["04_vqe_exact_fci.py", "--molecule", "h2", "--mapper", "parity", "--maxiter", "250"],
    ["05_pes_scan.py", "--molecule", "h2", "--points", "7", "--maxiter", "180"],
    ["06_optimizer_benchmark.py", "--molecule", "h2", "--maxiter", "200"],
    ["07_noise_and_adapt.py", "--molecule", "h2", "--maxiter", "150"],
]


def main() -> None:
    for command in COMMANDS:
        script = HERE / command[0]
        cmd = [sys.executable, str(script), *command[1:]]
        print("\n$", " ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
