from qchem_vqe.molecules import get_molecule


def test_h2_geometry():
    h2 = get_molecule("h2")
    assert h2.name == "H2"
    assert "H 0.0 0.0 0.0" in h2.atom_string()
    assert "0.7350000000" in h2.atom_string()


def test_lih_geometry_override():
    lih = get_molecule("lih")
    assert "2.0000000000" in lih.atom_string(2.0)
