#!/usr/bin/env python3
"""Rubidium D2 steady-state density-matrix models translated from MATLAB.

The two original scripts share the same Hamiltonian and Lindblad channels.
``direct`` solves every (laser detuning, Doppler shift) pair; ``fast`` solves
an effective-detuning grid and linearly interpolates before Doppler averaging.
All frequencies are MHz; Hamiltonians/rates acquire the original 2*pi factor.
Density matrices use column-major (MATLAB/Fortran) vectorization throughout.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from functools import lru_cache
import json
from math import ceil, floor, gamma, sqrt
from pathlib import Path
import platform
import warnings

import numpy as np
import scipy
from scipy import sparse
from scipy.sparse.linalg import MatrixRankWarning, spsolve


ROOT = Path(__file__).resolve().parents[2]
AMU = 1.66053906660e-27
KB = 1.380649e-23
POLARIZATIONS = ("pi", "sigma_plus", "sigma_minus", "linear_x")


@dataclass(frozen=True)
class Isotope:
    isotope: int
    I: float
    Fg: tuple[int, ...]
    Fe: tuple[int, ...]
    Ag: float
    Ae: float
    Be: float
    mass: float
    wavelength: float
    iso_center: float
    Jg: float = 0.5
    Je: float = 1.5
    Bg: float = 0.0


def make_isotope(number: int) -> Isotope:
    if number == 85:
        return Isotope(85, 2.5, (2, 3), (1, 2, 3, 4), 1011.9108130,
                       25.0354, 25.898, 84.911789732 * AMU, 780.241368271e-9, 0.0)
    if number == 87:
        return Isotope(87, 1.5, (1, 2), (0, 1, 2, 3), 3417.341305452145,
                       84.7185, 12.4965, 86.909180520 * AMU, 780.241209686e-9, 78.095)
    raise ValueError("Only isotopes 85 and 87 are supported")


@dataclass(frozen=True)
class State:
    manifold: str
    F: int
    m: int
    energy: float


def hyperfine_shift(I: float, J: float, A: float, B: float, F: int) -> float:
    K = F * (F + 1) - I * (I + 1) - J * (J + 1)
    energy = 0.5 * A * K
    if I > 0.5 and J > 0.5 and B != 0:
        energy += B * (1.5 * K * (K + 1) - 2 * I * (I + 1) * J * (J + 1)) / (
            4 * I * (2 * I - 1) * J * (2 * J - 1))
    return energy


def build_basis(rb: Isotope) -> tuple[State, ...]:
    states = []
    for manifold, values, J, A, B in (("g", rb.Fg, rb.Jg, rb.Ag, rb.Bg),
                                      ("e", rb.Fe, rb.Je, rb.Ae, rb.Be)):
        for F in values:
            energy = hyperfine_shift(rb.I, J, A, B, F)
            states.extend(State(manifold, F, m, energy) for m in range(-F, F + 1))
    return tuple(states)


def triangle(a: float, b: float, c: float) -> bool:
    return abs(a - b) <= c + 1e-12 and c <= a + b + 1e-12 and abs(a + b + c - round(a + b + c)) < 1e-12


def delta_tri(a: float, b: float, c: float) -> float:
    return sqrt(gamma(a + b - c + 1) * gamma(a - b + c + 1) *
                gamma(-a + b + c + 1) / gamma(a + b + c + 2))


@lru_cache(maxsize=None)
def wigner3j(j1: float, j2: float, j3: float, m1: float, m2: float, m3: float) -> float:
    """Racah formula, retaining the phases and selection rules of the source."""
    if abs(m1 + m2 + m3) > 1e-12 or any(abs(m) > j for m, j in ((m1, j1), (m2, j2), (m3, j3))) or not triangle(j1, j2, j3):
        return 0.0
    tri = gamma(j1 + j2 - j3 + 1) * gamma(j1 - j2 + j3 + 1) * gamma(-j1 + j2 + j3 + 1) / gamma(j1 + j2 + j3 + 2)
    norm = gamma(j1 + m1 + 1) * gamma(j1 - m1 + 1) * gamma(j2 + m2 + 1) * gamma(j2 - m2 + 1) * gamma(j3 + m3 + 1) * gamma(j3 - m3 + 1)
    pref = (-1) ** round(j1 - j2 - m3) * sqrt(tri * norm)
    lower = ceil(max(0, j2 - j3 - m1, j1 - j3 + m2) - 1e-12)
    upper = floor(min(j1 + j2 - j3, j1 - m1, j2 + m2) + 1e-12)
    total = 0.0
    for z in range(lower, upper + 1):
        denominator = (gamma(z + 1) * gamma(j1 + j2 - j3 - z + 1) * gamma(j1 - m1 - z + 1) *
                       gamma(j2 + m2 - z + 1) * gamma(j3 - j2 + m1 + z + 1) * gamma(j3 - j1 - m2 + z + 1))
        total += (-1) ** z / denominator
    return pref * total


@lru_cache(maxsize=None)
def wigner6j(a: float, b: float, c: float, d: float, e: float, f: float) -> float:
    if not all(triangle(*t) for t in ((a, b, c), (a, e, f), (d, b, f), (d, e, c))):
        return 0.0
    pref = delta_tri(a, b, c) * delta_tri(a, e, f) * delta_tri(d, b, f) * delta_tri(d, e, c)
    lower = ceil(max(a + b + c, a + e + f, d + b + f, d + e + c) - 1e-12)
    upper = floor(min(a + b + d + e, a + c + d + f, b + c + e + f) + 1e-12)
    total = 0.0
    for z in range(lower, upper + 1):
        denominator = (gamma(z - a - b - c + 1) * gamma(z - a - e - f + 1) *
                       gamma(z - d - b - f + 1) * gamma(z - d - e - c + 1) *
                       gamma(a + b + d + e - z + 1) * gamma(a + c + d + f - z + 1) * gamma(b + c + e + f - z + 1))
        total += (-1) ** z * gamma(z + 2) / denominator
    return pref * total


def dipole_amplitude(rb: Isotope, ground: State, excited: State) -> float:
    q = ground.m - excited.m
    if abs(q) > 1:
        return 0.0
    return ((-1) ** round(excited.F - 1 + ground.m) *
            sqrt((2 * ground.F + 1) * (2 * excited.F + 1) * (2 * rb.Jg + 1)) *
            wigner6j(rb.Jg, rb.Je, 1, excited.F, ground.F, rb.I) *
            wigner3j(excited.F, 1, ground.F, excited.m, q, -ground.m))


def polarization_components(mode: str) -> dict[int, float]:
    modes = {"pi": {0: 1.0}, "sigma_plus": {1: 1.0}, "sigma_minus": {-1: 1.0},
             "linear_x": {-1: 1 / sqrt(2), 1: 1 / sqrt(2)}}
    if mode not in modes:
        raise ValueError(f"Unknown polarization {mode!r}")
    return modes[mode]


def build_dipole(rb: Isotope, states: tuple[State, ...], mode: str) -> sparse.csc_matrix:
    n = len(states)
    dipole = sparse.lil_matrix((n, n), dtype=complex)
    pol = polarization_components(mode)
    for g, ground in enumerate(states):
        if ground.manifold != "g":
            continue
        for e, excited in enumerate(states):
            if excited.manifold == "e":
                dipole[e, g] = pol.get(excited.m - ground.m, 0) * dipole_amplitude(rb, ground, excited)
    return dipole.tocsc()


def branching_weights(rb: Isotope, states: tuple[State, ...]) -> np.ndarray:
    ground = [s for s in states if s.manifold == "g"]
    excited = [s for s in states if s.manifold == "e"]
    weights = np.array([[abs(dipole_amplitude(rb, g, e)) ** 2 for g in ground] for e in excited])
    sums = weights.sum(axis=1)
    if np.any(sums <= 0):
        raise ValueError("An excited state has no allowed spontaneous-decay channel")
    return weights / sums[:, None]


def hamiltonian_superoperator(H: sparse.spmatrix) -> sparse.csc_matrix:
    eye = sparse.eye(H.shape[0], format="csc")
    return (-1j * (sparse.kron(eye, H, format="csc") - sparse.kron(H.T, eye, format="csc"))).tocsc()


def build_dissipator(rb: Isotope, states: tuple[State, ...], linewidth: float,
                     ground_rate: float, extra_fwhm: float = 0.0) -> sparse.csc_matrix:
    """Same single-entry collapse operators as MATLAB, assembled sparsely.

    For C=sqrt(rate)|target><source|, C*rho*C^dagger contributes
    rate*rho[source,source] to target's population. The two anticommutator
    terms damp the source row and column by rate/2. This avoids constructing
    hundreds of Kronecker products without changing the Lindblad channels.
    """
    n = len(states)
    ground = [i for i, s in enumerate(states) if s.manifold == "g"]
    excited = [i for i, s in enumerate(states) if s.manifold == "e"]
    rows, cols, values = [], [], []

    def jump(target: int, source: int, rate: float) -> None:
        if rate <= 0:
            return
        rows.append(target + target * n)
        cols.append(source + source * n)
        values.append(rate)
        for j in range(n):
            for index in (source + j * n, j + source * n):
                rows.append(index)
                cols.append(index)
                values.append(-0.5 * rate)

    weights = branching_weights(rb, states)
    for ie, e in enumerate(excited):
        for ig, g in enumerate(ground):
            jump(g, e, 2 * np.pi * linewidth * weights[ie, ig])
    for source in ground:
        for target in ground:
            jump(target, source, 2 * np.pi * ground_rate / len(ground))
    for e in excited:
        jump(e, e, 2 * np.pi * extra_fwhm)
    return sparse.coo_matrix((values, (rows, cols)), shape=(n * n, n * n)).tocsc()


@dataclass
class Model:
    isotope: Isotope
    states: tuple[State, ...]
    dipole: sparse.csc_matrix
    generator: sparse.csc_matrix
    detuning_generator: sparse.csc_matrix
    L0: sparse.csc_matrix
    Ldet: sparse.csc_matrix
    rhs: np.ndarray
    absorption_vector: np.ndarray

    def steady_state(self, detuning: float) -> np.ndarray:
        with warnings.catch_warnings():
            warnings.simplefilter("error", MatrixRankWarning)
            vector = spsolve(self.L0 + detuning * self.Ldet, self.rhs)
        if not np.isfinite(vector).all():
            raise ArithmeticError("Nonfinite steady-state solution; check uniqueness and rates")
        return vector.reshape((len(self.states), len(self.states)), order="F")

    def response(self, detuning: float) -> float:
        rho = self.steady_state(detuning)
        # Transpose without conjugation matches absVec.' * rhoVec in MATLAB.
        return float(np.imag(self.absorption_vector @ rho.ravel(order="F")))


def prepare_model(number: int, polarization: str = "pi", rabi: float = 10.0,
                  linewidth: float = 6.0666, ground_rate: float = 0.05,
                  extra_fwhm: float = 0.0) -> Model:
    if not np.isfinite([rabi, linewidth, ground_rate, extra_fwhm]).all():
        raise ValueError("Model parameters must be finite")
    if rabi < 0 or linewidth <= 0 or ground_rate < 0 or extra_fwhm < 0:
        raise ValueError("Require rabi>=0, linewidth>0, ground_rate>=0, extra_fwhm>=0")
    rb = make_isotope(number)
    states = build_basis(rb)
    n = len(states)
    dipole = build_dipole(rb, states, polarization)
    energies = np.array([s.energy + (rb.iso_center if s.manifold == "e" else 0) for s in states])
    excited = np.array([s.manifold == "e" for s in states], dtype=float)
    H0 = sparse.diags(2 * np.pi * energies, format="csc") + np.pi * rabi * (dipole + dipole.conjugate().T)
    Hd = sparse.diags(2 * np.pi * excited, format="csc")
    generator = hamiltonian_superoperator(H0) + build_dissipator(rb, states, linewidth, ground_rate, extra_fwhm)
    detuning_generator = hamiltonian_superoperator(Hd)
    L0 = generator.tolil()
    Ldet = detuning_generator.tolil()
    L0[0, :] = 0
    L0[0, np.arange(n) * (n + 1)] = 1
    Ldet[0, :] = 0
    rhs = np.zeros(n * n, dtype=complex)
    rhs[0] = 1
    absorption = np.zeros(n * n, dtype=complex)
    for g, ground in enumerate(states):
        if ground.manifold == "g":
            for e, state in enumerate(states):
                if state.manifold == "e":
                    absorption[g + e * n] = np.conjugate(dipole[e, g])
    return Model(rb, states, dipole, generator.tocsc(), detuning_generator,
                 L0.tocsc(), Ldet.tocsc(), rhs, absorption)


def doppler_grid(rb: Isotope, temperature: float, nv: int) -> tuple[np.ndarray, np.ndarray, float]:
    if not np.isfinite(temperature) or temperature <= 0 or nv < 2:
        raise ValueError("Require temperature>0 and nv>=2")
    sigma = sqrt(KB * temperature / rb.mass) / rb.wavelength / 1e6
    shifts = np.linspace(-4 * sigma, 4 * sigma, nv)
    probability = np.exp(-shifts ** 2 / (2 * sigma ** 2))
    probability /= np.trapezoid(probability, shifts)
    return shifts, probability, sigma


def spectrum(model: Model, omega: np.ndarray, shifts: np.ndarray, probability: np.ndarray,
             method: str = "fast", response_step: float = 0.5,
             linewidth: float = 6.0666, response_grid: np.ndarray | None = None) -> np.ndarray:
    omega = np.asarray(omega, dtype=float)
    shifts = np.asarray(shifts, dtype=float)
    probability = np.asarray(probability, dtype=float)
    if (omega.ndim != 1 or omega.size == 0 or shifts.ndim != 1 or shifts.size < 2 or
            probability.shape != shifts.shape or not np.isfinite(omega).all() or
            not np.isfinite(shifts).all() or not np.isfinite(probability).all() or
            np.any(np.diff(shifts) <= 0) or np.any(probability < 0)):
        raise ValueError("Require finite 1D detunings, increasing Doppler shifts, and nonnegative matching weights")
    if method == "direct":
        values = np.array([[model.response(float(o - d)) for d in shifts] for o in omega])
    elif method == "fast":
        if not np.isfinite(response_step) or response_step <= 0:
            raise ValueError("response_step must be positive")
        if response_grid is None:
            lower = omega.min() - shifts.max() - 5 * linewidth
            upper = omega.max() - shifts.min() + 5 * linewidth
            # MATLAB lower:step:upper includes only points <= upper.
            count = int(np.floor((upper - lower) / response_step + 1e-12)) + 1
            response_grid = lower + np.arange(count) * response_step
        response_grid = np.asarray(response_grid, dtype=float)
        if len(response_grid) < 2 or not np.isfinite(response_grid).all() or np.any(np.diff(response_grid) <= 0):
            raise ValueError("Response grid must have at least two increasing points")
        responses = np.array([model.response(float(x)) for x in response_grid])
        values = np.interp(omega[:, None] - shifts[None, :], response_grid, responses, left=0, right=0)
    else:
        raise ValueError(f"Unknown method: {method}")
    alpha = np.trapezoid(values * probability[None, :], shifts, axis=1)
    if alpha.max() < abs(alpha.min()):
        alpha = -alpha
    return np.maximum(alpha, 0)


def absorption_mixture(alpha85: np.ndarray, alpha87: np.ndarray, fraction85: float = 0.72,
                       max_absorption: float = 0.42, beer_lambert: bool = True):
    if not 0 <= fraction85 <= 1 or not 0 < max_absorption < 1:
        raise ValueError("Invalid abundance or absorption scale")
    od85 = fraction85 * alpha85
    od87 = (1 - fraction85) * alpha87
    total = od85 + od87
    peak = total.max()
    if peak <= 0:
        # The zero-drive limit has zero absorption; avoid source's 0/0 scale.
        return np.zeros_like(total), np.zeros_like(total), np.zeros_like(total)
    if not beer_lambert:
        return total * max_absorption / peak, od85 * max_absorption / peak, od87 * max_absorption / peak
    od85 = od85 * (-np.log1p(-max_absorption) / peak)
    od87 = od87 * (-np.log1p(-max_absorption) / peak)
    od = od85 + od87
    absorption = -np.expm1(-od)
    a85 = np.divide(absorption * od85, od, out=np.zeros_like(od), where=od > 0)
    a87 = np.divide(absorption * od87, od, out=np.zeros_like(od), where=od > 0)
    return absorption, a85, a87


def transition_centers(rb: Isotope) -> list[dict]:
    strengths = {
        85: {(2, 1): 3/10, (2, 2): 7/18, (2, 3): 14/45,
             (3, 2): 5/63, (3, 3): 5/18, (3, 4): 9/14},
        87: {(1, 0): 1/6, (1, 1): 5/12, (1, 2): 5/12,
             (2, 1): 1/20, (2, 2): 1/4, (2, 3): 7/10},
    }
    result = []
    for (Fg, Fe), strength in strengths[rb.isotope].items():
        center = -(rb.iso_center + hyperfine_shift(rb.I, rb.Je, rb.Ae, rb.Be, Fe) -
                   hyperfine_shift(rb.I, rb.Jg, rb.Ag, rb.Bg, Fg))
        result.append({"Fg": Fg, "Fe": Fe, "center_MHz": center, "strength": strength})
    return result


def cli(default_method: str = "fast") -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("fast", "direct"), default=default_method)
    parser.add_argument("--quick", action="store_true", help="Tiny coarse smoke run, not a converged spectrum")
    parser.add_argument("--nomega", type=int)
    parser.add_argument("--nv", type=int)
    parser.add_argument("--response-step", type=float, default=None, help="MHz")
    parser.add_argument("--omega-min", type=float, default=-6000.0, help="MHz")
    parser.add_argument("--omega-max", type=float, default=6000.0, help="MHz")
    parser.add_argument("--temperature", type=float, default=293.0, help="K")
    parser.add_argument("--rabi", type=float, default=10.0, help="MHz")
    parser.add_argument("--linewidth", type=float, default=6.0666, help="MHz FWHM")
    parser.add_argument("--ground-rate", type=float, default=0.05, help="MHz")
    parser.add_argument("--extra-fwhm", type=float, default=0.0, help="MHz")
    parser.add_argument("--fraction85", type=float, default=0.72)
    parser.add_argument("--max-absorption", type=float, default=0.42)
    parser.add_argument("--polarization", choices=POLARIZATIONS)
    parser.add_argument("--polarization-average", action="store_true")
    parser.add_argument("--axis-calibration", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--a-cal", type=float, default=1.0434)
    parser.add_argument("--b-cal", type=float, default=0.0781, help="GHz; plotting only")
    parser.add_argument("--linear", action="store_true", help="Use linear absorption instead of Beer-Lambert")
    parser.add_argument("--output", type=Path, help="New output directory; refuses an existing directory")
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args()
    if args.omega_min >= args.omega_max:
        parser.error("omega-min must be smaller than omega-max")
    default_points = 1001 if args.method == "fast" else 301
    args.nomega = args.nomega if args.nomega is not None else (7 if args.quick else default_points)
    args.nv = args.nv if args.nv is not None else (5 if args.quick else default_points)
    args.response_step = args.response_step if args.response_step is not None else (250.0 if args.quick else 0.5)
    args.polarization = args.polarization or ("pi" if args.method == "fast" else "linear_x")
    args.axis_calibration = args.axis_calibration if args.axis_calibration is not None else args.method == "fast"
    if args.nomega < 2 or args.nv < 2:
        parser.error("nomega and nv must both be >=2")
    if args.quick:
        warnings.warn("Quick grids only check execution; they do not resolve narrow resonances.", stacklevel=1)
    omega = np.linspace(args.omega_min, args.omega_max, args.nomega)
    raw = []
    metadata = {"parameters": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                "vectorization": "column-major/Fortran", "isotopes": {}}
    for number in (85, 87):
        components = []
        modes = ("pi", "sigma_plus", "sigma_minus") if args.polarization_average else (args.polarization,)
        for mode in modes:
            model = prepare_model(number, mode, args.rabi, args.linewidth, args.ground_rate, args.extra_fwhm)
            shifts, probability, sigma = doppler_grid(model.isotope, args.temperature, args.nv)
            print(f"{number}Rb {mode}: N={len(model.states)}, sigma_D={sigma:.6f} MHz; {args.method}", flush=True)
            components.append(spectrum(model, omega, shifts, probability, args.method, args.response_step, args.linewidth))
        raw.append(np.mean(components, axis=0))
        metadata["isotopes"][str(number)] = {"constants": asdict(model.isotope), "sigma_D_MHz": sigma,
                                            "transitions": transition_centers(model.isotope)}
    absorption, a85, a87 = absorption_mixture(*raw, args.fraction85, args.max_absorption, not args.linear)
    axis = omega * 1e-3
    if args.axis_calibration:
        axis = args.a_cal * axis + args.b_cal
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = args.output or ROOT / "results" / "density-matrix" / f"{args.method}_{stamp}"
    output.mkdir(parents=True, exist_ok=False)
    np.savetxt(output / "spectrum.csv", np.column_stack((omega, axis, *raw, absorption, a85, a87)), delimiter=",",
               header="omega_MHz,plot_detuning_GHz,alpha85_raw,alpha87_raw,absorption,contribution85,contribution87", comments="")
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    if not args.no_plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(axis, absorption, color="black", label=f"Theory {args.method}")
        ax.plot(axis, a85, "--", label="85Rb contribution")
        ax.plot(axis, a87, "--", label="87Rb contribution")
        experimental = Path(__file__).resolve().parent / "DATA_ABS_Rb.csv"
        if experimental.is_file():
            data = np.loadtxt(experimental, delimiter=",", skiprows=1)
            ax.scatter(data[:, 0], data[:, 1], s=15, alpha=0.6, label="Reference data")
        else:
            warnings.warn(f"Reference data missing: {experimental}; plotting theory only", stacklevel=1)
        ax.set(xlabel="Detuning (GHz)", ylabel="Absorption", xlim=(-6, 6))
        ax.legend()
        fig.tight_layout()
        for extension in ("png", "svg", "pdf"):
            fig.savefig(output / f"spectrum.{extension}", dpi=180)
        plt.close(fig)
    print(f"Saved: {output.resolve()}")


if __name__ == "__main__":
    cli()
