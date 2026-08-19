import pytest

from qchem_vqe.noise import build_depolarizing_noise_model


def test_noise_probability_validation():
    with pytest.raises(ValueError):
        build_depolarizing_noise_model(-0.1, 0.01)
    with pytest.raises(ValueError):
        build_depolarizing_noise_model(0.001, 1.1)
