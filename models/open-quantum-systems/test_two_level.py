"""Physical checks independent of the Liouvillian's Kronecker construction."""
import unittest

import numpy as np
from numpy.testing import assert_allclose
from scipy.linalg import expm

import two_level as tls


class TwoLevelPhysicsTests(unittest.TestCase):
    def test_liouvillian_matches_direct_master_equation(self):
        rho = np.array([[0.37, 0.13 + 0.17j], [0.13 - 0.17j, 0.63]])
        h = -0.7 * tls.SZ / 2 - 1.3 * tls.SX / 2
        gamma, nth = 0.8, 0.23
        expected = -1j * (h @ rho - rho @ h)
        for operator, rate in ((tls.SM, gamma * (nth + 1)), (tls.SP, gamma * nth)):
            product = operator.conj().T @ operator
            expected += rate * (operator @ rho @ operator.conj().T - (product @ rho + rho @ product) / 2)
        actual = (tls.build_liouvillian(h, gamma=gamma, nth=nth) @ rho.reshape(-1, order="F")).reshape((2, 2), order="F")
        assert_allclose(actual, expected, atol=2e-15)
        assert_allclose(np.trace(actual), 0, atol=2e-15)

    def test_steady_state_matches_optical_bloch_analytic_solution(self):
        for omega in (0.0, 0.03, 0.5, 4.0):
            for delta in (-3.1, 0.0, 2.4):
                for gamma in (0.2, 1.0):
                    liouvillian = tls.tls_liouvillian(omega, delta, gamma)
                    rho = tls.steady_state(liouvillian)
                    assert_allclose(rho, tls.analytic_steady_state(omega, delta, gamma), atol=3e-14)
                    assert_allclose(liouvillian @ rho.reshape(-1, order="F"), 0, atol=3e-14)
                    assert_allclose(np.trace(rho), 1, atol=1e-14)
                    self.assertGreaterEqual(np.linalg.eigvalsh(rho).min(), -1e-14)

    def test_zero_drive_thermal_equilibrium(self):
        for nth in (0, 0.1, 2.0):
            rho = tls.steady_state(tls.tls_liouvillian(0, 1.2, 0.7, nth))
            assert_allclose(rho[0, 0], nth / (2 * nth + 1), atol=2e-15)
            assert_allclose(rho[0, 1], 0, atol=2e-15)

    def test_no_drive_spontaneous_decay_dynamics(self):
        times = np.linspace(0, 15, 301)
        states = tls.propagate(tls.tls_liouvillian(0, 0.8, 0.7), tls.EXCITED, times)
        assert_allclose(states[:, 0, 0], np.exp(-0.7 * times), atol=3e-14)
        assert_allclose(np.trace(states, axis1=1, axis2=2), 1, atol=3e-14)
        self.assertGreaterEqual(np.linalg.eigvalsh(states).min(), -1e-13)

    def test_driven_dynamics_converges_to_steady_state(self):
        liouvillian = tls.tls_liouvillian(1.2, -0.6, 0.8)
        times = np.linspace(0, 100, 1001)
        states = tls.propagate(liouvillian, tls.GROUND, times)
        assert_allclose(states[0], tls.GROUND, atol=1e-15)
        assert_allclose(states[-1], tls.steady_state(liouvillian), atol=2e-13)
        assert_allclose(np.trace(states, axis1=1, axis2=2), 1, atol=2e-13)
        assert_allclose(states, states.conj().transpose(0, 2, 1), atol=2e-13)
        self.assertGreaterEqual(np.linalg.eigvalsh(states).min(), -1e-13)

    def test_irregular_elapsed_times(self):
        liouvillian = tls.tls_liouvillian(0.7, 0.5, 0.9)
        times = np.array([0.1, 0.2, 0.6, 1.8])
        states = tls.propagate(liouvillian, tls.GROUND, times)
        for time, actual in zip(times, states):
            expected = (expm(liouvillian * time) @ tls.GROUND.reshape(-1, order="F")).reshape((2, 2), order="F")
            assert_allclose(actual, expected, atol=3e-15)

    def test_doppler_integral_matches_numerical_liouvillian_solutions(self):
        detunings = np.array([-1.7, 0, 1.7])
        numerical, doppler = tls.steady_scan(detunings, 0.9, 0.6, 0.4, 101)
        shifts = np.linspace(-2, 2, 101)
        weights = np.exp(-shifts ** 2 / (2 * 0.4 ** 2))
        weights /= np.trapezoid(weights, shifts)
        for index, delta in enumerate(detunings):
            states = np.array([tls.steady_state(tls.tls_liouvillian(0.9, delta - shift, 0.6)) for shift in shifts])
            expected = np.trapezoid(weights[:, None, None] * states, shifts, axis=0)
            assert_allclose(doppler[index], expected, atol=3e-15)
        _, zero_width = tls.steady_scan(detunings, 0.9, 0.6, 0, 101)
        assert_allclose(zero_width, numerical, atol=1e-15)

    def test_qrt_initial_value_long_time_and_zero_drive(self):
        liouvillian = tls.tls_liouvillian(1.2, 0.4, 0.8)
        rho = tls.steady_state(liouvillian)
        times = np.linspace(0, 100, 1001)
        total = tls.correlation(liouvillian, rho, times, incoherent=False)
        connected = tls.correlation(liouvillian, rho, times)
        elastic = abs(rho[0, 1]) ** 2
        assert_allclose(total[0], rho[0, 0], atol=3e-15)
        assert_allclose(connected[0], rho[0, 0] - elastic, atol=3e-15)
        assert_allclose(total[-1], elastic, atol=3e-14)
        assert_allclose(connected[-1], 0, atol=3e-14)
        zero_l = tls.tls_liouvillian(0, 0, 1)
        assert_allclose(tls.correlation(zero_l, tls.steady_state(zero_l), times), 0, atol=1e-15)

    def test_fft_matches_exponential_lorentzian(self):
        times = np.linspace(0, 100, 32768)
        rate = 0.7
        frequency, spectrum = tls.fluorescence_spectrum(times, np.exp(-rate * times))
        expected = rate / (np.pi * (rate ** 2 + frequency ** 2))
        region = abs(frequency) < 5
        assert_allclose(spectrum[region], expected[region], atol=2e-7, rtol=3e-5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
