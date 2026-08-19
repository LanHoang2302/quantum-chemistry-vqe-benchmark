from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MoleculeSpec:
    name: str
    symbols: tuple[str, str]
    default_bond: float
    charge: int = 0
    spin: int = 0  # PySCF convention: 2S = N_alpha - N_beta

    def atom_string(self, bond_length: float | None = None) -> str:
        r = self.default_bond if bond_length is None else float(bond_length)
        return f"{self.symbols[0]} 0.0 0.0 0.0; {self.symbols[1]} 0.0 0.0 {r:.10f}"


MOLECULES: dict[str, MoleculeSpec] = {
    "h2": MoleculeSpec("H2", ("H", "H"), 0.735),
    "lih": MoleculeSpec("LiH", ("Li", "H"), 1.60),
}


def get_molecule(name: str) -> MoleculeSpec:
    key = name.strip().lower()
    if key not in MOLECULES:
        raise ValueError(f"Unsupported molecule {name!r}. Choose from: {', '.join(MOLECULES)}")
    return MOLECULES[key]
