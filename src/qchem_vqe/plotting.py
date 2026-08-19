from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .io_utils import ensure_parent


def plot_pes(df: pd.DataFrame, path: str | Path) -> Path:
    p = ensure_parent(path)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["bond_length"], df["hf_energy"], marker="o", label="RHF")
    ax.plot(df["bond_length"], df["fci_energy"], marker="o", label="Full-space FCI")
    if "casci_energy" in df.columns:
        ax.plot(df["bond_length"], df["casci_energy"], marker="o", label="Active-space CASCI")
    if "vqe_energy" in df.columns:
        ax.plot(df["bond_length"], df["vqe_energy"], marker="o", label="VQE-UCCSD")
    ax.set_xlabel("Bond length (Å)")
    ax.set_ylabel("Total energy (Hartree)")
    ax.set_title("Potential Energy Curve")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(p, dpi=180)
    plt.close(fig)
    return p


def plot_optimizer_convergence(histories: dict[str, list[dict[str, float]]], path: str | Path) -> Path:
    p = ensure_parent(path)
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, history in histories.items():
        if not history:
            continue
        xs = [row["eval"] for row in history]
        ys = [row["energy"] for row in history]
        ax.plot(xs, ys, label=name)
    ax.set_xlabel("Objective evaluation")
    ax.set_ylabel("Electronic objective value (Hartree)")
    ax.set_title("VQE Optimizer Convergence")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(p, dpi=180)
    plt.close(fig)
    return p
