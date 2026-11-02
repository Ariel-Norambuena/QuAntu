#!/usr/bin/env python3
"""Check the Python density-matrix physics and optional MATLAB reference data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "models" / "density-matrix"))
import rb_d2 as rb  # noqa: E402


def assert_density(model: rb.Model, detuning: float) -> dict[str, float]:
    rho = model.steady_state(detuning)
    trace_error = float(abs(np.trace(rho) - 1))
    hermiticity = float(np.linalg.norm(rho - rho.conjugate().T))
    minimum_eigenvalue = float(np.linalg.eigvalsh((rho + rho.conjugate().T) / 2).min())
    vector = rho.ravel(order="F")
    residual = float(np.linalg.norm((model.generator + detuning * model.detuning_generator) @ vector))
    if trace_error > 1e-10 or hermiticity > 1e-9 or minimum_eigenvalue < -1e-9 or residual > 1e-8:
        raise AssertionError((model.isotope.isotope, detuning, trace_error, hermiticity, minimum_eigenvalue, residual))
    return {"trace_error": trace_error, "hermiticity_error": hermiticity,
            "minimum_eigenvalue": minimum_eigenvalue, "stationarity_residual": residual}


def check_physics() -> dict:
    diagnostics = []
    largest_grid_error = 0.0
    for number, expected_dimension in ((85, 36), (87, 24)):
        for polarization in rb.POLARIZATIONS:
            model = rb.prepare_model(number, polarization)
            if len(model.states) != expected_dimension:
                raise AssertionError("Incorrect Hilbert-space dimension")
            weights = rb.branching_weights(model.isotope, model.states)
            np.testing.assert_allclose(weights.sum(axis=1), 1, atol=1e-13)
            if weights.min() < 0:
                raise AssertionError("Negative branching probability")
            n = len(model.states)
            trace_row = np.eye(n).ravel(order="F")
            np.testing.assert_allclose(trace_row @ model.generator.toarray(), 0, atol=1e-11)
            for detuning in (-4200.0, -1700.0, 1300.0, 2500.0):
                diagnostics.append(assert_density(model, detuning))
        zero = rb.prepare_model(number, rabi=0)
        rho = zero.steady_state(0)
        ground = [i for i, s in enumerate(zero.states) if s.manifold == "g"]
        target = np.zeros_like(rho)
        target[ground, ground] = 1 / len(ground)
        np.testing.assert_allclose(rho, target, atol=1e-11)
        np.testing.assert_allclose(zero.response(0), 0, atol=1e-13)
        # Put every requested (Omega-D) on the response grid: interpolation
        # must then recover the independent direct quadrature to roundoff.
        model = rb.prepare_model(number, "pi")
        shifts = np.array([-10.0, 0.0, 10.0])
        probability = np.exp(-shifts ** 2 / 200)
        probability /= np.trapezoid(probability, shifts)
        omega = np.array([-1700.0, -1690.0, -1680.0]) if number == 85 else np.array([-4200.0, -4190.0, -4180.0])
        grid = np.arange(omega.min() - 10, omega.max() + 11, 10)
        direct = rb.spectrum(model, omega, shifts, probability, "direct")
        fast = rb.spectrum(model, omega, shifts, probability, "fast", response_grid=grid)
        largest_grid_error = max(largest_grid_error, float(np.max(np.abs(fast - direct))))
        np.testing.assert_allclose(fast, direct, rtol=1e-11, atol=1e-13)
    a, a85, a87 = rb.absorption_mixture(np.array([0.1, 0.2]), np.array([0.3, 0.1]))
    np.testing.assert_allclose(a, a85 + a87, atol=1e-14)
    np.testing.assert_allclose(a.max(), 0.42, atol=1e-14)
    return {"density_states_checked": len(diagnostics),
            "max_trace_error": max(d["trace_error"] for d in diagnostics),
            "max_hermiticity_error": max(d["hermiticity_error"] for d in diagnostics),
            "minimum_eigenvalue": min(d["minimum_eigenvalue"] for d in diagnostics),
            "max_stationarity_residual": max(d["stationarity_residual"] for d in diagnostics),
            "fast_direct_common_grid_max_error": largest_grid_error}


def check_matlab(path: Path) -> dict:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    models = {}
    density_error = 0.0
    response_error = 0.0
    spectrum_error = 0.0
    for case in fixture["samples"]:
        key = (case["isotope"], case["polarization"])
        if key not in models:
            models[key] = rb.prepare_model(*key)
        model = models[key]
        actual = model.steady_state(case["detuning_MHz"])
        expected = np.array(case["rho_real"]) + 1j * np.array(case["rho_imag"])
        density_error = max(density_error, float(np.max(np.abs(actual - expected))))
        response = model.response(case["detuning_MHz"])
        response_error = max(response_error, abs(response - case["response"]))
        np.testing.assert_allclose(actual, expected, rtol=1e-7, atol=2e-10)
        np.testing.assert_allclose(response, case["response"], rtol=1e-8, atol=1e-12)
    for case in fixture["spectra"]:
        model = models[case["isotope"], case["polarization"]]
        shifts, probability, _ = rb.doppler_grid(model.isotope, 293, case["nv"])
        for method in ("fast", "direct"):
            actual = rb.spectrum(model, np.array(case["omega_MHz"]), shifts, probability, method,
                                 case["response_step_MHz"])
            expected = np.array(case[method])
            spectrum_error = max(spectrum_error, float(np.max(np.abs(actual - expected))))
            np.testing.assert_allclose(actual, expected, rtol=1e-8, atol=1e-12)
    return {"matlab_version": fixture["matlab_version"], "matlab_states_checked": len(fixture["samples"]),
            "matlab_spectra_checked": 2 * len(fixture["spectra"]),
            "matlab_density_max_absolute_error": density_error,
            "matlab_response_max_absolute_error": response_error,
            "matlab_spectrum_max_absolute_error": spectrum_error}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=ROOT / "tests/fixtures/matlab_density_matrix.json")
    parser.add_argument("--skip-matlab-fixture", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = check_physics()
    if not args.skip_matlab_fixture:
        result.update(check_matlab(args.fixture))
    result["scope"] = "Selected-state and coarse-grid parity; not production-grid convergence or experimental validation"
    print(json.dumps(result, indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
