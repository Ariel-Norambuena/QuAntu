# Reproducibility

Run the following commands from the repository root. The ranges in `requirements*.txt` describe intended compatibility; **they are not dependency lock files**. To compare runs, record the operating system, Python/MATLAB version, parameters, and exact dependencies.

## Python environment

Python 3.11 or later in a virtual environment is recommended. In PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip freeze > environment-local.txt
python scripts/check_science.py
```

On Linux/macOS, activate with `source .venv/bin/activate`; the remaining commands are the same. `environment-local.txt` records the local installation and does not imply that the environment has been tested on every platform.

`check_science.py` checks Python and notebook-cell syntax for all four notebooks, the integrity of CSVs used by models and notebooks, and 36 Voigt-model combinations. It executes existing scientific functions without importing the interfaces. It checks finiteness, positivity, normalization, agreement between both interfaces, and the linewidth's temperature dependence. It does not validate data fitting or full density-matrix calculations.

## Absorption with Python

Local Matplotlib interface:

```powershell
python theory/models/interactive/interactive_model.py
```

Optional dashboard:

```powershell
python -m pip install -r requirements-dashboard.txt
python -m streamlit run theory/models/interactive/dashboard_rb.py
```

Both interfaces load `Data_Rb_Gas.csv` alongside the script and fail explicitly if it is missing. The model groups hyperfine transitions into four effective profiles; it does not replace the full density-matrix sublevel calculation. In both explorers, `gamma_MHz` is the Lorentzian HWHM; FWHM is twice that value. The historical initial value is retained and labeled using this convention.

The notebooks preserve relative paths and numerical results, with English teaching text and displayed output. Open them with their own folder as the working directory:

```powershell
python -m jupyterlab --notebook-dir=theory/notebooks/absorption
```

Execute cells in order. Their syntax is checked automatically; complete execution requires the dependencies in `requirements.txt`. Consult the data documentation for the provenance of digitized data and published figures.

## Density matrices with Python

The primary implementation is `theory/models/density-matrix/rb_d2.py`, using NumPy and SciPy sparse matrices. It includes all hyperfine and Zeeman sublevels of both isotopes (dimensions 36 and 24), Wigner 3j/6j symbols evaluated through Racah formulas, the Hamiltonian, spontaneous emission with normalized branching, ground-state mixing, and optional dephasing. It retains column-major vectorization and the MATLAB sources' `2*pi` factors. MATLAB, a GPU, and the Parallel Computing Toolbox are not required.

To check execution using deliberately coarse grids:

```powershell
python -m pip install -r requirements-core.txt
python theory/models/density-matrix/run_fast.py --quick
python theory/models/density-matrix/run_direct.py --quick
python scripts/check_density_matrix.py
python -m unittest discover -s theory/models/density-matrix -p 'test_*.py'
```

`--quick` uses seven frequencies, five Doppler classes, and, in fast mode, a response spacing of 250 MHz. **It does not resolve narrow resonances and is not a converged spectrum**. Without `--quick`, fast mode uses 1001 frequencies, 1001 Doppler classes, and 0.5 MHz spacing; direct mode uses 301 frequencies and 301 classes. The latter solves every frequency/velocity pair and can be substantially slower. Defaults reproduce differences between the original scripts: fast uses `pi` polarization with horizontal calibration enabled; direct uses `linear_x` with calibration disabled. To compare the methods, explicitly match those parameters:

```powershell
python theory/models/density-matrix/run_fast.py --nomega 101 --nv 101 --response-step 1 --polarization pi --no-axis-calibration
python theory/models/density-matrix/run_direct.py --nomega 101 --nv 101 --polarization pi --no-axis-calibration
```

These commands only establish a common example; convergence must also be checked by refining the grids. `--help` lists temperature, Rabi frequency, linewidths, abundance, polarization averaging, and Beer–Lambert or linear conversion. Outputs `spectrum.csv`, `metadata.json`, and PNG/SVG/PDF figures are saved in a new directory under `results/density-matrix/`. `--output` selects a new directory and rejects an existing one. `--no-plot` skips figures.

Maximum absorption is scaled to 0.42 by default; the optional affine axis calibration uses empirical parameters (`aCal=1.0434`, `bCal=0.0781 GHz`) and changes only the horizontal representation, not the Hamiltonian. The figures are not absolute amplitude predictions independent of that scale. Reference files are located alongside the scripts.

### Port verification

`check_density_matrix.py` checks 32 steady states for both isotopes and all four polarizations: trace, Hermiticity, positivity, and the original generator's residual. It also checks branching, trace preservation, the zero-drive limit, the Beer–Lambert decomposition, and fast/direct agreement when queried points lie on the response grid.

The `tests/fixtures/matlab_density_matrix.json` fixture was generated by executing original MATLAB functions with MATLAB R2025b Update 6: 16 density matrices and eight small spectra (fast/direct, both isotopes, `pi` and `linear_x`). It records SHA-256 hashes of the source revisions executed during the original parity validation, before later comment-only English translation. The imported source hashes remain in the inventory. The Python/MATLAB comparison produced maximum absolute errors of `7.8e-16` in matrices and `1.0e-17` in spectra; the complete record is in `validation/density-matrix-metrics.json`. Tests require the fixture and do not require MATLAB.

To regenerate it optionally, pass both original MATLAB sources to the harness; it extracts their local functions without executing the large initial grid:

```powershell
python scripts/generate_matlab_fixture.py --fast-source theory/archive/theoretical-group/Rb_D2_density_matrix_fast_COHERENCE_ABS.m --direct-source theory/archive/theoretical-group/Rb_D2_density_matrix_slow_direct.m
```

The harness and its temporary preferences remain under `results/`; the command needs a MATLAB installation with a working license. MATLAB sources are preserved as historical references. Small-sample parity does not establish production-grid convergence or experimental validation.

## Qiskit workshop

```powershell
python -m pip install -r algorithms/education/qiskit/requirements.txt
python algorithms/education/qiskit/validate_notebook.py
```

The validator executes all cells without Jupyter. The workshop uses Statevector from Qiskit core; it requires no credentials, Aer, or hardware. The English README retains the original credits and records earlier checks with Qiskit 1.4.5 and 2.5.1; this preparation also executed all 12 cells with Qiskit 2.6.1 and completed all tests.

## MOT animation

```powershell
python -m pip install -r requirements-video.txt
python experimental/education/mot/render_mot_workshop.py --stills results/mot-preview --times 3 32 72 --width 640 --height 360
```

The renderer uses the included equation PNGs. It prioritizes the original Windows fonts and searches for common alternatives on Linux/macOS; Pillow's default font is the final fallback. Typography may vary by system. Regenerating equations additionally requires `pdflatex`, `pdftocairo`, and the LaTeX packages used by the script:

```powershell
python experimental/education/mot/make_latex_assets.py
python experimental/education/mot/render_mot_workshop.py --output results/MOT_Rb87_workshop_1080p.mp4
```

The animation is educational, and its representative scales are not measurements of a MOT built by the project.

## OQS provenance and known limitations

Historical meeting materials were removed from the published tree. The [Python OQS implementation](open-quantum-systems.md) remains a standalone, executable model with tests. The historical fluorescence reference called `CorrelationTRG`, a function absent from the supplied materials; Python includes an explicit QRT routine verified using analytical checks. Equations and conventions are documented independently of the removed files.

No script was supplied to automatically regenerate all processed CSVs from raw data. Existing files document the materials received; they do not imply complete processing traceability or experimental validation.

## Automated reproduction and records

`python scripts/validate.py --with-notebooks --with-qiskit` runs structural, Voigt, D2, OQS, and both notebook-group checks. Optional dependencies must be installed. See the [recorded results and limitations](validation.md) and [publishing procedure](publishing.md).
