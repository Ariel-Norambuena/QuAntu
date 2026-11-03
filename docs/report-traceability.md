# Report and material traceability

This document connects the rubidium spectroscopy report and its supporting materials to available files in QuAntü, the ANID Thematic Research Ring project “Neutral-atom-based quantum computing in Chile” (ATE250066).

The report and scientific implementations are organized under [Theory](../theory/README.md), literature-derived reference datasets and apparatus materials under [Experimental](../experimental/README.md), and the Qiskit workshop under [Algorithms](../algorithms/README.md). Group placement preserves the existing component credits and validation scope.

The documentary reference for this version is the local [Technical Progress Report](../theory/reports/technical-progress/main.pdf), titled *Development of Progressive Theoretical Models for the Rubidium Absorption Spectrum*, together with [main.tex](../theory/reports/technical-progress/main.tex), [density_matrix_model.tex](../theory/reports/technical-progress/density_matrix_model.tex), and [references.bib](../theory/reports/technical-progress/references.bib).

The report identifies Alexis R. Legón, Pontificia Universidad Católica de Chile, QuAntü Research Group, and a reporting period of May–July 2026. The supplied [Overleaf project](https://www.overleaf.com/project/6a679a4b0c07d40f5ac1dd88) could not be read during preparation. This version therefore preserves the local copy without asserting that it is synchronized with Overleaf or reflects its latest revision.

## Scientific correspondence

| Claim or component | Repository files | Evidence and limitation |
| --- | --- | --- |
| Objectives and model progression | [Main report source](../theory/reports/technical-progress/main.tex) | Describes objectives, activities, results, and future work. |
| Phenomenological Gaussian | [Model_1.ipynb](../theory/notebooks/absorption/Model_1.ipynb), [figure 1](../theory/reports/technical-progress/figure_1.png) | Code and historical outputs; MSE 0.006772, MAE 0.054760. |
| Gaussian with isotope mixture | [Model_2.ipynb](../theory/notebooks/absorption/Model_2.ipynb), [figure 2](../theory/reports/technical-progress/figure_2.png) | Code and historical outputs; MSE 0.004758, MAE 0.052138. |
| Susceptibility with Doppler averaging | [Model_3.ipynb](../theory/notebooks/absorption/Model_3.ipynb), [figure 3](../theory/reports/technical-progress/figure_3.png) | Code and historical outputs; MSE 0.004004, MAE 0.048501. |
| Reconstructed notebook data | [Data_Rb_Gas.csv](../theory/notebooks/absorption/Data_Rb_Gas.csv) | The report attributes the benchmark to Ma et al. (2017); it is not original data acquisition. |
| Density-matrix derivation | [LaTeX derivation](../theory/reports/technical-progress/density_matrix_model.tex) | Details states, dipoles, Lindblad dynamics, the observable, calibrations, and assumptions. |
| Fast steady-state solver | [Python executable](../theory/models/density-matrix/run_fast.py), [shared module](../theory/models/density-matrix/rb_d2.py), and [MATLAB original](../theory/models/density-matrix/Rb_D2_density_matrix_fast_COHERENCE_ABS.m) | Python execution path; the original and historical figures remain in [its directory](../theory/models/density-matrix/). |
| Alternative direct solver | [Python executable](../theory/models/density-matrix/run_direct.py) and [MATLAB original](../theory/models/density-matrix/Rb_D2_density_matrix_slow_direct.m) | Alternative formulation for assessing interpolation differences and convergence. |
| MATLAB experimental overlay | [DATA_ABS_Rb.csv](../theory/models/density-matrix/DATA_ABS_Rb.csv) | Two-column input; exact origin and transformations are not recorded in an individual manifest. It differs from Data_Rb_Gas.csv. |
| Fast/direct comparison and common metrics | [Proposed derivation checks](../theory/reports/technical-progress/density_matrix_model.tex) and [future work](../theory/reports/technical-progress/main.tex) | Systematic validation and comparable density-matrix MSE/MAE remain pending. |
| Other literature spectra | [Preserved extractions](../experimental/data/raw/), [processed tables](../experimental/data/processed/), and [local papers](../theory/references/papers/) | File availability does not establish solver validation against every dataset. |
| Atomic data | [Steck compilations](../theory/references/atomic-data/), [bibliography](../theory/reports/technical-progress/references.bib) | Sources for constants and angular-momentum formalism; different local revisions are preserved. |
| Absolute scale and experimental extensions | [Report future work](../theory/reports/technical-progress/main.tex) | Measured density, geometry, intensity and relaxation, uncertainties, and a Zeeman term remain pending. |

The first three models' values were preserved from historical outputs and also reproduced by executing the notebooks during preparation; see the [reproduction record](../validation/notebook-metrics.json). The report results section leaves density-matrix metrics unassigned until a common protocol is available. See the [scientific assumptions](science.md) and [data provenance](data-provenance.md).

## Additional QuAntü materials

These items belong to the working collection, although the report does not establish them as quantitative spectroscopy results.

| Area | Location | Documentary role |
| --- | --- | --- |
| Interactive exploration | [theory/models/interactive](../theory/models/interactive/) | Python scripts and local data for model visualization. |
| Historical theory-group copy | [theory/archive/theoretical-group](../theory/archive/theoretical-group/) | Preserves the original folder separately from the primary Python entry points. |
| Qiskit workshop | [algorithms/education/qiskit](../algorithms/education/qiskit/README.md) | Notebook, requirements, builder, and validator. Retains its own citation information. |
| MOT materials | [experimental/education/mot](../experimental/education/mot/README.md) | Video, generator, equations, and educational previews. |
| Lectures | [theory/education/lectures](../theory/education/lectures/) | Dynamical-modeling presentation. |
| Open quantum systems | [Python model](../theory/models/open-quantum-systems/two_level.py) | Standalone two-level implementation; [OQS documentation](open-quantum-systems.md) explains provenance and the new QRT routine. Original meeting materials were removed from the published tree. |
| Atomic theory references | [theory/references/rubidium-theory](../theory/references/rubidium-theory/) | Documents about both isotopes. |
| Cell and materials | [experimental/references/hardware](../experimental/references/hardware/) | Thorlabs cell and Borofloat glass documentation; does not establish setup acquisition or characterization. |

## Preservation and review

The [inventory](inventory.csv) connects original paths with repository paths and includes sizes and hashes. Portability changes, if any, should be reflected in the corresponding fields. This mapping supports incorporation review without confusing organization with new physical validation.

The 11 meeting materials and two outreach files were removed from the current tree at the project owner's request; their originals remain in the working folder. The inventory retains 124 imported files.

Public access does not assign a collection-wide open license to papers, figures, manufacturer documents, or third-party presentations. Their respective holders' attributions and conditions are preserved.
