"""Scientific integrity checks, including independently generated MATLAB data."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from check_density_matrix import check_matlab, check_physics  # noqa: E402


class DensityMatrixTests(unittest.TestCase):
    def test_density_physics_and_quadrature(self):
        result = check_physics()
        self.assertEqual(result["density_states_checked"], 32)

    def test_matlab_reference(self):
        fixture = ROOT / "tests" / "fixtures" / "matlab_density_matrix.json"
        self.assertTrue(fixture.is_file(), "The independently generated MATLAB reference must be included")
        result = check_matlab(fixture)
        self.assertEqual(result["matlab_states_checked"], 16)


if __name__ == "__main__":
    unittest.main()
