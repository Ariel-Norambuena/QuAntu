"""Driven two-level Lindblad model, dynamics and resonance fluorescence.

Python implementation of the local April 2026 OQS MATLAB examples. Basis:
(excited, ground), hbar=1, column-major vectorization. Quantum regression is
implemented explicitly here because CorrelationTRG.m was not supplied.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[3]

SP = np.array([[0, 1], [0, 0]], dtype=complex)
SM = SP.conj().T
SZ = np.diag([1.0, -1.0]).astype(complex)
SX = SP + SM
GROUND = np.diag([0.0, 1.0]).astype(complex)
EXCITED = np.diag([1.0, 0.0]).astype(complex)


def build_liouvillian(hamiltonian, sm=SM, sp=SP, gamma=1.0, nth=0.0):
    """Build -i[H,rho]+gamma(n+1)D[sm]rho+gamma*n*D[sp]rho.

    The ordering and Kronecker products match BuildLiouvillianTLS.m.
    All rates and H must use consistent angular-frequency/time units.
    """
    if not np.isfinite(gamma) or gamma <= 0:
        raise ValueError("gamma must be positive and finite")
    if not np.isfinite(nth) or nth < 0:
        raise ValueError("nth must be nonnegative and finite")
    h = np.asarray(hamiltonian, dtype=complex)
    if h.ndim != 2 or h.shape[0] != h.shape[1] or not np.isfinite(h).all():
        raise ValueError("Hamiltonian must be a finite square matrix")
    if not np.allclose(h, h.conj().T):
        raise ValueError("Hamiltonian must be Hermitian")
    identity = np.eye(h.shape[0], dtype=complex)
    result = -1j * np.kron(identity, h) + 1j * np.kron(h.T, identity)
    for operator, rate in ((sm, gamma * (nth + 1)), (sp, gamma * nth)):
        operator = np.asarray(operator, dtype=complex)
        if operator.shape != h.shape or not np.isfinite(operator).all():
            raise ValueError("Collapse operators must match the Hamiltonian")
        product = operator.conj().T @ operator
        result += rate * (np.kron(operator.conj(), operator)
                          - 0.5 * np.kron(identity, product)
                          - 0.5 * np.kron(product.T, identity))
    return result


def tls_liouvillian(omega=1.0, delta=0.0, gamma=1.0, nth=0.0):
    """Real drive convention H=-delta*sz/2-omega*sx/2."""
    if not np.isfinite([omega, delta]).all():
        raise ValueError("omega and delta must be finite real numbers")
    return build_liouvillian(-0.5 * delta * SZ - 0.5 * omega * SX,
                             gamma=gamma, nth=nth)


def steady_state(liouvillian):
    """Solve the trace-constrained linear system; do not clip eigenvalues."""
    liouvillian = np.asarray(liouvillian, dtype=complex)
    dim = int(round(np.sqrt(len(liouvillian))))
    if liouvillian.shape != (dim * dim, dim * dim):
        raise ValueError("Liouvillian dimension must be a square")
    matrix = liouvillian.copy()
    matrix[-1] = np.eye(dim).reshape(-1, order="F")
    rhs = np.zeros(dim * dim, dtype=complex)
    rhs[-1] = 1
    rho = np.linalg.solve(matrix, rhs).reshape((dim, dim), order="F")
    rho = 0.5 * (rho + rho.conj().T)
    return rho / np.trace(rho)


def propagate(liouvillian, initial_matrix, times):
    """Propagate any matrix linearly, including non-density QRT matrices.

    times are nonnegative elapsed times, not absolute timestamps. Uniform
    grids reuse one matrix exponential; irregular grids use each interval.
    No normalization or Hermitian cleanup is applied to propagated states.
    """
    times = np.asarray(times, dtype=float)
    if (times.ndim != 1 or not len(times) or not np.isfinite(times).all()
            or times[0] < 0 or np.any(np.diff(times) <= 0)):
        raise ValueError("times must be finite, nonnegative and increasing")
    initial = np.asarray(initial_matrix, dtype=complex)
    if initial.ndim != 2 or initial.shape[0] != initial.shape[1]:
        raise ValueError("initial_matrix must be square")
    liouvillian = np.asarray(liouvillian, dtype=complex)
    if liouvillian.shape != (initial.size, initial.size):
        raise ValueError("Liouvillian and matrix dimensions disagree")
    vector = expm(liouvillian * times[0]) @ initial.reshape(-1, order="F")
    output = np.empty((len(times),) + initial.shape, dtype=complex)
    output[0] = vector.reshape(initial.shape, order="F")
    intervals = np.diff(times)
    uniform = len(intervals) and np.allclose(intervals, intervals[0], rtol=1e-10, atol=1e-14)
    step = expm(liouvillian * intervals[0]) if uniform else None
    for index, interval in enumerate(intervals, start=1):
        propagator = step if uniform else expm(liouvillian * interval)
        vector = propagator @ vector
        output[index] = vector.reshape(initial.shape, order="F")
    return output


def analytic_steady_state(omega, delta, gamma):
    """Zero-temperature optical Bloch steady state for this H convention."""
    if gamma <= 0 or not np.isfinite([omega, delta, gamma]).all():
        raise ValueError("Expected finite parameters and gamma > 0")
    saturation = (omega * omega / 2) / (delta * delta + (gamma / 2) ** 2)
    population = saturation / (2 * (1 + saturation))
    coherence = 1j * omega / (2 * (1 + saturation) * (gamma / 2 - 1j * delta))
    return np.array([[population, coherence], [coherence.conjugate(), 1 - population]])


def steady_scan(detunings, omega=1.0, gamma=0.5, sigma_d=1.0, velocity_points=161):
    """Numerical stationary scan, including a Gaussian Doppler convolution.

    Each no-Doppler point solves the Liouvillian. The Doppler integral uses
    the equivalent analytic zero-temperature steady state for efficiency.
    This equivalence is checked independently in test_two_level.py.
    """
    detunings = np.asarray(detunings, dtype=float)
    if detunings.ndim != 1 or not np.isfinite(detunings).all():
        raise ValueError("detunings must be a finite 1D array")
    if not np.isfinite(sigma_d) or sigma_d < 0 or velocity_points < 3:
        raise ValueError("sigma_d >= 0 and velocity_points >= 3 required")
    numerical = np.array([steady_state(tls_liouvillian(omega, d, gamma)) for d in detunings])
    if sigma_d == 0:
        return numerical, numerical.copy()
    shifts = np.linspace(-5 * sigma_d, 5 * sigma_d, velocity_points)
    weights = np.exp(-0.5 * (shifts / sigma_d) ** 2)
    weights /= np.trapezoid(weights, shifts)
    effective = detunings[:, None] - shifts[None, :]
    saturation = (omega * omega / 2) / (effective ** 2 + (gamma / 2) ** 2)
    populations = saturation / (2 * (1 + saturation))
    coherences = 1j * omega / (2 * (1 + saturation) * (gamma / 2 - 1j * effective))
    averaged = np.empty_like(numerical)
    averaged[:, 0, 0] = np.trapezoid(weights * populations, shifts, axis=1)
    averaged[:, 1, 1] = 1 - averaged[:, 0, 0]
    averaged[:, 0, 1] = np.trapezoid(weights * coherences, shifts, axis=1)
    averaged[:, 1, 0] = averaged[:, 0, 1].conj()
    return numerical, averaged


def correlation(liouvillian, rho_ss, times, a=SP, b=SM, incoherent=True):
    """C(tau)=Tr[A exp(L*tau)(B rho_ss)], optionally connected.

    The connected part subtracts Tr(A rho_ss)*Tr(B rho_ss). This is a new
    explicit QRT implementation, not a recovered CorrelationTRG.m routine.
    """
    states = propagate(liouvillian, b @ rho_ss, times)
    values = np.einsum("ij,tji->t", a, states)
    if incoherent:
        values -= np.trace(a @ rho_ss) * np.trace(b @ rho_ss)
    return values


def fluorescence_spectrum(times, values):
    """One-sided FFT: Re integral C(tau) exp(-i*nu*tau) d tau / pi.

    Endpoints receive trapezoidal half weights. Output nu is angular
    frequency relative to the pump. A finite time window broadens the
    elastic delta peak of the total correlation. Values are never clipped.
    """
    times = np.asarray(times, dtype=float)
    values = np.asarray(values, dtype=complex)
    if len(times) < 2 or values.shape != times.shape:
        raise ValueError("Matching 1D arrays with at least two points required")
    dt = times[1] - times[0]
    if (not np.isfinite(times).all() or not np.isfinite(values).all()
            or dt <= 0 or not np.isclose(times[0], 0)
            or not np.allclose(np.diff(times), dt, rtol=1e-9, atol=1e-14)):
        raise ValueError("FFT requires a finite uniform grid starting at zero")
    weighted = values.copy()
    weighted[[0, -1]] *= 0.5
    frequency = 2 * np.pi * np.fft.fftshift(np.fft.fftfreq(len(times), dt))
    spectrum = np.fft.fftshift(np.fft.fft(weighted)).real * dt / np.pi
    return frequency, spectrum


def run_self_checks():
    """Run the adjacent physical/numerical unittest suite."""
    import unittest
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), "test_two_level.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


def _save_csv(path, header, columns):
    np.savetxt(path, np.column_stack(columns), delimiter=",", header=header, comments="")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="Run physical and numerical self-checks")
    dynamics = subparsers.add_parser("dynamics", help="Ground-state initial dynamics")
    scan = subparsers.add_parser("scan", help="Stationary detuning scan with Doppler average")
    fluorescence = subparsers.add_parser("fluorescence", help="QRT fluorescence at resonance")
    for command in (dynamics, scan, fluorescence):
        command.add_argument("--output", type=Path, default=ROOT / "outputs" / "oqs")
        command.add_argument("--points", type=int, default=60000 if command is fluorescence else 2000 if command is dynamics else 500)
    for command in (dynamics, scan):
        command.add_argument("--omega", type=float, default=1.0)
        command.add_argument("--gamma", type=float, default=0.5)
    dynamics.add_argument("--delta", type=float, default=1.0)
    dynamics.add_argument("--tmax", type=float, default=50.0)
    scan.add_argument("--span", type=float, default=7.0, help="Detuning range in units of omega")
    scan.add_argument("--sigma-d", type=float, default=1.0)
    scan.add_argument("--velocity-points", type=int, default=161)
    fluorescence.add_argument("--gamma", type=float, default=1.0)
    fluorescence.add_argument("--ratios", type=float, nargs="+", default=[2, 8, 16], help="Values of 4*omega/gamma")
    fluorescence.add_argument("--tmax", type=float, default=100.0)
    fluorescence.add_argument("--total", action="store_true", help="Include the elastic coherent component")
    args = parser.parse_args(argv)
    if args.command == "check":
        run_self_checks()
        return
    if args.points < 3 or not np.isfinite(args.gamma) or args.gamma <= 0:
        parser.error("points >= 3 and finite gamma > 0 required")
    if args.command in ("dynamics", "scan") and (not np.isfinite(args.omega) or args.omega <= 0):
        parser.error("CLI requires finite omega > 0; API supports omega=0")
    if args.command in ("dynamics", "fluorescence") and (not np.isfinite(args.tmax) or args.tmax <= 0):
        parser.error("tmax must be positive and finite")
    if args.command == "scan" and (not np.isfinite(args.span) or args.span <= 0):
        parser.error("span must be positive and finite")
    if args.command == "fluorescence" and (not np.isfinite(args.ratios).all() or min(args.ratios) < 0):
        parser.error("ratios must be finite and nonnegative")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    args.output.mkdir(parents=True, exist_ok=True)
    metadata = {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()}
    metadata.update({"basis": ["excited", "ground"], "hbar": 1, "implementation": "Python two_level.py; stationary thermal occupation zero"})
    if args.command == "dynamics":
        times = np.linspace(0, args.tmax, args.points)
        states = propagate(tls_liouvillian(args.omega, args.delta, args.gamma), GROUND, times)
        population = states[:, 0, 0].real
        coherence = states[:, 0, 1]
        _save_csv(args.output / "dynamics.csv", "time,rho_ee,rho_gg,re_rho_eg,im_rho_eg", [times, population, states[:, 1, 1].real, coherence.real, coherence.imag])
        figure, axis = plt.subplots(figsize=(8, 5))
        axis.plot(times * args.omega, population, color="red", label="rho_ee")
        axis.plot(times * args.omega, states[:, 1, 1].real, color="blue", label="rho_gg")
        axis.plot(times * args.omega, 2 * abs(coherence), color="darkgreen", label="2 |rho_eg|")
        axis.set(xlabel="Omega t", ylabel="Population / coherence")
    elif args.command == "scan":
        detunings = np.linspace(-args.span * args.omega, args.span * args.omega, args.points)
        states, doppler = steady_scan(detunings, args.omega, args.gamma, args.sigma_d, args.velocity_points)
        _save_csv(args.output / "scan.csv", "delta,rho_ee,re_rho_eg,im_rho_eg,rho_ee_doppler,re_rho_eg_doppler,im_rho_eg_doppler", [detunings, states[:, 0, 0].real, states[:, 0, 1].real, states[:, 0, 1].imag, doppler[:, 0, 0].real, doppler[:, 0, 1].real, doppler[:, 0, 1].imag])
        figure, axes = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
        axes[0].plot(detunings / args.omega, states[:, 0, 0].real, label="rho_ee")
        axes[0].plot(detunings / args.omega, doppler[:, 0, 0].real, "--", label="rho_ee Doppler")
        axes[0].set(ylabel="Excited population")
        for part, label in ((np.real, "Re"), (np.imag, "Im")):
            axes[1].plot(detunings / args.omega, part(states[:, 0, 1]), label=label + " rho_eg")
            axes[1].plot(detunings / args.omega, part(doppler[:, 0, 1]), "--", label=label + " rho_eg Doppler")
        axes[1].set(xlabel="delta / Omega", ylabel="Optical coherence")
        axes[0].legend()
        axis = axes[1]
    else:
        times = np.linspace(0, args.tmax / args.gamma, args.points)
        figure, axes = plt.subplots(2, 1, figsize=(8, 8))
        for index, ratio in enumerate(args.ratios):
            omega = ratio * args.gamma / 4
            liouvillian = tls_liouvillian(omega, 0, args.gamma)
            rho_ss = steady_state(liouvillian)
            values = correlation(liouvillian, rho_ss, times, incoherent=not args.total)
            frequency, spectrum = fluorescence_spectrum(times, values)
            _save_csv(args.output / f"correlation_{index}.csv", "tau,re_c,im_c", [times, values.real, values.imag])
            _save_csv(args.output / f"fluorescence_{index}.csv", "nu,spectrum", [frequency, spectrum])
            axes[0].plot(times * args.gamma, values.real, label=f"4 Omega/gamma={ratio:g}")
            axes[1].plot(frequency / args.gamma, spectrum, label=f"4 Omega/gamma={ratio:g}")
        axes[0].set(xlabel="gamma tau", ylabel="Re C(tau)", xlim=(0, min(20, args.tmax)))
        axes[1].set(xlabel="nu / gamma (relative to pump)", ylabel="S(nu)", xlim=(-6, 6))
        axes[0].legend()
        axis = axes[1]
        metadata.update({"qrt": "Tr[sp exp(L*tau)(sm rho_ss)]", "incoherent": not args.total, "fft": "negative exponent, trapezoidal endpoints, 1/pi normalization"})
    axis.legend()
    figure.tight_layout()
    figure.savefig(args.output / f"{args.command}.png", dpi=180)
    plt.close(figure)
    (args.output / f"{args.command}_parameters.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {args.command} outputs to {args.output.resolve()}")


if __name__ == "__main__":
    main()
