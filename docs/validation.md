# Validation performed during preparation

Local date: **November 2, 2026**. The [recorded environment](../validation/environment.json) documents the Python version and dependencies actually used. Local execution used Windows and Python 3.13.12 in a virtual environment sharing existing scientific libraries; this is not an isolated, frozen environment.

Historical structural update on **November 3, 2026**: the 11 meeting files were removed from the published tree, and the then-current 126-file inventory and local links were checked. A later removal of two outreach files leaves the current inventory at 124 files. These structural changes do not change the recorded scientific results.

## Executed checks

| Component | Evidence | Result and scope |
| --- | --- | --- |
| Inventory, references, and syntax | `python scripts/verify_repository.py` | Integrity of the current 124 imported files, local paths, LaTeX resources, Python sources, and four notebooks. Meeting and outreach materials are excluded from the current tree. |
| Voigt explorers | `python scripts/check_science.py` | 36 temperature, linewidth, and isotope combinations; finite, nonnegative, normalized values, interface agreement, and temperature scaling. |
| Python density matrix | [Tests](../theory/models/density-matrix/test_rb_d2.py), [record](../validation/density-matrix-metrics.json) | Two automated tests covering 32 physical states, decay channels, zero drive, and fast/direct comparison on a common grid. |
| D2 comparison against MATLAB | [Independent fixture](../tests/fixtures/matlab_density_matrix.json) | MATLAB R2025b Update 6 executed original functions: 16 matrices and eight small spectra. Maximum error in rho: `7.79e-16`; in spectra: `9.97e-18`. |
| Open systems | [Nine tests](../theory/models/open-quantum-systems/test_two_level.py) | Liouvillian against the direct equation, Bloch solution, thermal equilibrium, decay, dynamics, Doppler averaging, QRT, and spectrum against a Lorentzian. |
| Absorption notebooks | [Metrics record](../validation/notebook-metrics.json) | All 15 code cells of the three notebooks executed. MSE and MAE agree with saved values within `5.01e-7`. Only plot display was suppressed. |
| Qiskit workshop | `python algorithms/education/qiskit/validate_notebook.py` | All 12 executed cells completed their tests with Qiskit 2.6.1; local simulation without credentials. |
| Dashboard | Streamlit `AppTest` | The application loaded without exceptions and displayed two sliders; this check does not cover every visual interaction. |
| Matplotlib interface | Agg backend | Data loading and execution without an interactive window; complete manual control review remains pending. |
| MOT animation | Full English video and review frames | Regenerated all 98 seconds at 1920 × 1080, 30 fps, H.264/AAC. All 63 captions are English; 98 sampled frames were checked for text outside the canvas. |
| Technical report | `latexmk -pdf` with shell escape disabled | Sources and bibliography compiled successfully in a separate output directory; the included historical PDF was not replaced. |

The D2 steady-state check produced maximum trace error `5.6e-16`, Hermiticity error `7.9e-16`, minimum eigenvalue `-2.1e-17`, and residual `3.5e-15`. The negative eigenvalue is consistent with rounding. Full values and scope appear in the JSON record.

An additional independent check covered all four polarizations of both isotopes with additional dephasing, plus OQS thermal and spectral-sum checks. The versioned suite covers the cases listed in its test files; additional exploratory checks are not presented as a new general certification.

## Repeating the checks

From the repository root:

```sh
python -m pip install -r requirements.txt
python scripts/validate.py --with-notebooks
python -m pip install -r algorithms/education/qiskit/requirements.txt
python scripts/validate.py --with-qiskit
```

The command without options requires only `requirements-core.txt`. Options add notebook and workshop execution; validation always exits with a nonzero code on failure. The [GitHub Actions configuration](../.github/workflows/validate.yml) repeats the main checks on Python 3.11 and 3.13 and runs the workshop separately. Check its remote execution after the first push.

## Practical limitations

D2 parity uses small samples and grids; it does not verify production-grid convergence. Notebook reproduction preserves the original data and calibrations and does not assess generalization or original data acquisition. OQS quantum regression replaces a missing routine and has analytical checks, without a complete comparison against that historical function.

The online Overleaf version could not be verified. A documented pipeline to regenerate every processed CSV from raw data is still unavailable. Absolute calibration, experimental uncertainties, and the Zeeman extension appear in the [roadmap](../ROADMAP.md).

Notebook execution produced a Matplotlib layout warning that did not affect metrics. Streamlit emitted a deprecation warning for `use_container_width`; the application passed its test with the recorded version. These are not treated as numerical failures.

## English edition checked on November 3, 2026

The English edition includes repository documentation and templates, source comments,
notebook teaching text and displayed output, both absorption interfaces, editable
Office text, and all MOT captions. Proper names, official logos, original citation
titles, and historical `original_path` identifiers retain their original spelling.
The original files outside the checkout are unchanged.

During that English-edition check, before the later outreach removal, all 51 slides
were rendered. The six slides with visible changes and both event-document pages
were visually reviewed; the other 45 slides were pixel-identical to their source
renders. This historical scope includes the two outreach files no longer in the
current tree. The reference PDFs and report were already in English.
The complete 98-second MOT video was regenerated, and review images cover every scene.
Numerical checks, all three absorption notebooks and all 12 Qiskit code cells passed
again with unchanged scientific results. The [English-edition record](../validation/english-localization.json)
records the scope and renamed paths. Current and original source hashes remain in
the inventory.

## Group organization checked on November 3, 2026

The collection was organized under `algorithms/`, `experimental/`, and `theory/`, each with its own English README. At that stage, the inventory placed 7 imported files in Algorithms, 64 in Experimental, and 53 in Theory, with 2 shared outreach imports at the root. Those two outreach files were later removed; the current three-group inventory totals 124 files. Shared validation tools, fixtures, requirements, and evidence remain at the root.

After relocation, the full validation command passed again, including all numerical tests, three absorption notebooks, and the Qiskit workshop. Model entry points and GitHub Actions use the new paths. Imported documents, data, notebooks, and media retain their bytes; imported changes are limited to active MATLAB output paths and the Qiskit guide commands. Original source files outside this checkout remain unchanged.

## Current collection after outreach removal

The current tree contains 124 imported files: 7 in Algorithms, 64 in Experimental, and 53 in Theory. The two outreach files were removed without rewriting earlier commits. Their removal does not change model inputs, numerical results, or the dated validation records above.
