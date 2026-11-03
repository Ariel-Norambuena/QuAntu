# Theory Group

The Theory Group is part of **QuAntü**, the ANID Thematic Research Ring project
**“Neutral-atom-based quantum computing in Chile” (ATE250066)**.

**Group lead:** [Ariel Norambuena](https://github.com/Ariel-Norambuena)<br>
**Project role:** Principal Investigator

## Objectives and current scope

This area develops models of rubidium spectroscopy and open quantum dynamics
that support neutral-atom quantum computing. Its repository objectives are to:

- Build progressively more microscopic descriptions of thermal-rubidium D2
  absorption, including isotope composition and Doppler broadening.
- Model driven populations and coherences, spontaneous emission, relaxation,
  and optical response with explicit units and conventions.
- Provide tested numerical implementations and traceable comparisons with
  analytical limits, historical models, and reference data.
- Connect model assumptions and predicted observables with algorithm design,
  experimental calibration, and future quantum-control studies.

Python is the primary execution path. The current collection includes
phenomenological and susceptibility notebooks, full hyperfine-sublevel
density-matrix calculations, interactive Voigt explorers, and two-level
Lindblad dynamics and fluorescence. The D2 bases contain 36 states for `85Rb`
and 24 for `87Rb`. Magnetic sublevels are explicit, while a Zeeman Hamiltonian
remains future work.

## Materials

| Material | Purpose |
| --- | --- |
| [D2 density-matrix models](models/density-matrix/) | Direct and interpolated steady-state response with Doppler averaging. |
| [Interactive explorers](models/interactive/) | Local Matplotlib and Streamlit interfaces for effective Voigt profiles. |
| [Open quantum systems](models/open-quantum-systems/) | Two-level dynamics, Doppler scans, quantum regression, and fluorescence. |
| [Absorption notebooks](notebooks/absorption/) | Three historical models and their reproduced fit metrics. |
| [Technical report](reports/technical-progress/main.pdf) | Scientific account with accompanying LaTeX sources and bibliography. |
| [Historical model archive](archive/theoretical-group/) | Original MATLAB implementations and preserved figure variants. |
| [Lectures](education/lectures/) | Teaching material on dynamical modeling and open systems. |
| [Scientific references](references/) | Papers, atomic data, and rubidium reference documents. |

## Run the models and checks

Use Python 3.11 or later. Run these commands from the **repository root**:

```sh
python -m pip install -r requirements-core.txt
python theory/models/density-matrix/run_fast.py --quick --no-plot
python theory/models/open-quantum-systems/two_level.py check
python scripts/check_density_matrix.py
```

The quick D2 grid checks execution and does not resolve narrow resonances.
The shared [reproducibility guide](../docs/reproducibility.md) explains matched
fast/direct parameters, grid refinement, interactive interfaces, and notebook
execution. The [validation record](../docs/validation.md) states the numerical
checks performed and their limits.

Absorption amplitudes and optional affine frequency calibration are empirical.
Current outputs are not absolute predictions in SI units. Selected-state
agreement with MATLAB and analytical checks do not establish production-grid
convergence or complete experimental validation. The
[scientific roadmap](../ROADMAP.md) tracks those remaining tasks.

## Collaboration and contributions

Work with the [Experimental Group](../experimental/README.md) to compare models
against correctly attributed spectra and documented calibration. Work with the
[Algorithms Group](../algorithms/README.md) to connect dynamical assumptions,
noise channels, and control requirements with circuit-level studies.

Preserve source attribution and distinguish reproduced historical results from
new calculations. Follow the shared [contribution guide](../CONTRIBUTING.md),
[scientific background](../docs/science.md), and
[report-traceability matrix](../docs/report-traceability.md). The
[project overview](../README.md) describes the three research groups.
