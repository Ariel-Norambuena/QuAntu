# Open quantum system examples in Python

The standalone [two_level.py](../models/open-quantum-systems/two_level.py) module implements a two-level system. It includes a Liouvillian, steady state, dynamics, detuning scans with Doppler averaging, and a quantum-regression fluorescence spectrum. It uses NumPy, SciPy, and Matplotlib; MATLAB and QuTiP are not required. Its development used examples from the April 10, 2026 meeting, whose original files were removed from the published tree.

## Conventions and correspondence

The basis is `(excited, ground)`, $\hbar=1$, $\sigma_+=|e\rangle\langle g|$, and $\sigma_-=|g\rangle\langle e|$. The Hamiltonian retains the original convention:

$$
H=-\frac{\delta}{2}\sigma_z-\frac{\Omega}{2}\sigma_x.
$$

The master equation is

$$
\dot\rho=-i[H,\rho]+\gamma(n_{\mathrm{th}}+1)\mathcal{D}[\sigma_-]\rho
+\gamma n_{\mathrm{th}}\mathcal{D}[\sigma_+]\rho,
\qquad
\mathcal{D}[c]\rho=c\rho c^\dagger-\frac12\{c^\dagger c,\rho\}.
$$

Frequencies in this example use angular units consistent with time; they are not the GHz detunings in the rubidium CSVs. The API supports thermal occupation through `nth`; CLI examples use `nth=0`.

| Historical original | Python implementation | Notes |
| --- | --- | --- |
| `BuildLiouvillianTLS.m` | `build_liouvillian`, `tls_liouvillian` | Retains column-major vectorization and Kronecker products. |
| `SteadyStateLiouvillian.m` | `steady_state` | Replaces one row with the trace constraint and symmetrizes at the end; does not clip eigenvalues. |
| `SolvesMasterEquation.m` | `propagate` | Solves the same constant generator using matrix exponentials rather than `ode45`. Does not renormalize states during propagation. |
| `MainSpectrumTLS.m` | CLI `dynamics` and `scan` | Reproduces the computed quantities: populations, coherences, and their Doppler averages. |
| `FlurescenceSpectrumOnResonanceTLS.m` | CLI `fluorescence`, `correlation`, `fluorescence_spectrum` | Retains drive parameters and explicitly implements the previously absent quantum-regression routine. |
| `rgb.m` | Matplotlib named colors | Replaces the color helper without attempting to reproduce its historical RGB rounding. |

The originals listed in this table are not part of the current publication and remain in the project's working folder. The Python module and its tests do not depend on them. The OQS comparison relies on equations and analytical solutions; MATLAB was not executed to certify end-to-end numerical equivalence of this example.

## Execution

From the repository root, with dependencies installed:

```sh
python models/open-quantum-systems/two_level.py check
python models/open-quantum-systems/two_level.py dynamics
python models/open-quantum-systems/two_level.py scan
python models/open-quantum-systems/two_level.py fluorescence
```

Commands save CSVs, PNGs, and a parameter JSON under `outputs/oqs/`. Use `--output` to select another directory. Each command uses distinct filenames; repeating the same command in the same directory replaces its previous results.

- `dynamics`: $\Omega=1$, $\delta=1$, $\gamma=0.5$, initial ground state, and 2000 points from $t=0$ to 50. Exports `dynamics.csv`, `dynamics.png`, and `dynamics_parameters.json`.
- `scan`: 500 detunings between $-7\Omega$ and $+7\Omega$, $\Omega=1$, $\gamma=0.5$, Doppler width $\sigma_D=1$, and 161 classes between $-5\sigma_D$ and $+5\sigma_D$. Exports `scan.csv`, `scan.png`, and `scan_parameters.json`.
- `fluorescence`: exact resonance, $\gamma=1$, $4\Omega/\gamma=2,8,16$, and 60000 delays up to $100/\gamma$. Exports a correlation CSV and spectrum CSV per drive, plus a shared figure and parameter JSON. `--points 4096` provides an exploratory run with lower temporal resolution; check the bandwidth before interpreting high frequencies.

Examples with explicit parameters:

```sh
python models/open-quantum-systems/two_level.py dynamics --omega 1 --delta 0 --gamma 0.5 --tmax 40 --output outputs/oqs-resonant
python models/open-quantum-systems/two_level.py scan --sigma-d 0.5 --velocity-points 321 --output outputs/oqs-doppler
python models/open-quantum-systems/two_level.py fluorescence --ratios 2 8 16 --total --output outputs/oqs-total
```

The scan without Doppler broadening solves each Liouvillian numerically. To accelerate the Doppler integral, it uses the equivalent analytical steady state at zero bath temperature; tests compare that integral with independent numerical Liouvillian solutions. The thermal distribution is normalized within the truncated interval.

## Quantum regression and spectrum

The original fluorescence example calls `CorrelationTRG`, but that routine was absent from the supplied files. Therefore, `correlation` is a new explicit implementation of the quantum regression theorem; it is not presented as a verified copy of an unavailable original function.

The definition is

$$
C(\tau)=\operatorname{Tr}\!\left[\sigma_+e^{\mathcal{L}\tau}(\sigma_-\rho_{\mathrm{ss}})\right].
$$

For the incoherent component, subtract
$\operatorname{Tr}(\sigma_+\rho_{\mathrm{ss}})\operatorname{Tr}(\sigma_-\rho_{\mathrm{ss}})$.
The initial operator $\sigma_-\rho_{\mathrm{ss}}$ is not a density matrix and must not be normalized or symmetrized during propagation.

The spectrum implements

$$
S(\nu)=\frac{1}{\pi}\operatorname{Re}\int_0^T C(\tau)e^{-i\nu\tau}\,d\tau,
$$

using an FFT on a uniform grid. $\nu$ is angular frequency relative to the pump. Endpoints use trapezoidal weights, unlike the MATLAB example's rectangular sum. Negative spectral values are not clipped; the finite window and sampling can produce errors or small oscillations requiring a convergence study.

The default mode returns the incoherent component. With `--total`, the elastic component is represented with the width imposed by the finite observation interval; that width is not a physical prediction for the ideal elastic line. CSV values retain the integral normalization without normalizing each spectrum to its maximum.

## Verification and limitations

The [test_two_level.py](../models/open-quantum-systems/test_two_level.py) suite contains nine tests and can also be run with:

```sh
python -m unittest discover -s models/open-quantum-systems -p "test_*.py" -v
```

Tests check the Liouvillian against the direct matrix equation; the steady-state Bloch solution over several drives, detunings, and rates; trace, positivity, and residuals; thermal equilibrium at zero drive; exponential population decay; driven dynamics and convergence; propagation at irregular times; Doppler averaging against numerical solutions; initial and asymptotic QRT limits; and FFT output against an analytical Lorentzian. During preparation, all nine tests passed and all three commands ran with their default parameters.

`MainSpectrumTLS.m` allocates matrices named `ChiMap`, `AbsMap`, `DispMap`, and fluorescence maps, but the supplied code does not compute them. This port reproduces its actually computed observables and adds the resonant example's explicit fluorescence; it does not claim to implement a full retarded susceptibility, absorption/gain, or additional-probe response map. Two-level fluorescence and multihyperfine D2 absorption are distinct observables and models.
