# Data provenance and use

The collected spectra come from reconstructed published curves and preserved working files. The [local report](../reports/technical-progress/main.tex) describes digitizing and normalizing a spectrum from Ma et al. (2017) as a benchmark for the first models. These files must not be presented as original QuAntü experimental measurements.

[data/raw](../data/raw/) preserves tables and images received as figure extractions. “Raw” refers to their state in the original folder; it does not imply unprocessed detector data or access to the paper authors' acquisitions. [data/processed](../data/processed/) preserves versions prepared for comparison.

## Model benchmarks

| File | Numeric rows | Use | Documented provenance |
| --- | ---: | --- | --- |
| [notebooks/absorption/Data_Rb_Gas.csv](../notebooks/absorption/Data_Rb_Gas.csv) | 89 | Reference for Model_1, Model_2, and Model_3 notebooks. | The report attributes the reconstructed benchmark to Ma et al. (2017). No individual digitization record is preserved. |
| [models/density-matrix/DATA_ABS_Rb.csv](../models/density-matrix/DATA_ABS_Rb.csv) | 61 | Experimental overlay read by MATLAB. | The report documents its format and use but does not unambiguously identify the source figure, extraction, or transformation. |
| [models/density-matrix/Data_Rb_Gas.csv](../models/density-matrix/Data_Rb_Gas.csv) | 89 | Local copy preserved in the MATLAB directory. | Byte-identical to the notebook benchmark in this version. The fast script reads DATA_ABS_Rb.csv. |
| [models/interactive/Data_Rb_Gas.csv](../models/interactive/Data_Rb_Gas.csv) | 89 | Interactive-script input. | Byte-identical to the notebook benchmark in this version. |

The three active copies named `Data_Rb_Gas.csv` share SHA-256 `d7111753eb374721401fef1ef6f002141075da64510972e8bc8fa2bd7a0b5035`. `DATA_ABS_Rb.csv` has SHA-256 `58e3d51023c850e95561e1a958d821f3b649de3a7e816177bbbbb876ae05433b`. These are different datasets and must not be silently interchanged when comparing errors.

Both input filenames retain the `x, y` header. Scripts and the report interpret column 1 as detuning in GHz and column 2 as absorption in arbitrary units. The CSVs alone do not provide enough metadata to reconstruct calibration, uncertainty, or the experimental setup. `DATA_ABS_Rb.csv` contains points out of frequency order: new analyses should sort each $(x,y)$ pair together before interpolation, preserving the source file unchanged.

## Literature curve collection

The associations below use filenames, accompanying images, and entries in the [local bibliography](../reports/technical-progress/references.bib). They do not replace a record identifying the exact figure and conditions for each extraction. Row counts exclude the header and match within each raw/processed pair.

| Family | Raw CSV | Processed CSV | Rows | Local reference |
| --- | --- | --- | ---: | --- |
| Agnew | [Agnew.csv](../data/raw/Agnew.csv) | [Agnew__absorption_data_processed.csv](../data/processed/Agnew__absorption_data_processed.csv) | 48 | Agnew et al., 2024; DOI `10.1063/5.0234155`. |
| Bala, I_sat0 label | [Bala_I_sat0.csv](../data/raw/Bala_I_sat0.csv) | [Bala_I_sat0_absorption_data_processed.csv](../data/processed/Bala_I_sat0_absorption_data_processed.csv) | 50 | Bala et al., 2022; DOI `10.1088/1361-6455/ac7e93`. |
| Bala, 0.3_I_sat0 label | [Bala_0.3_I_sat0.csv](../data/raw/Bala_0.3_I_sat0.csv) | [Bala_0.3_I_sat0_absorption_data_processed.csv](../data/processed/Bala_0.3_I_sat0_absorption_data_processed.csv) | 53 | Same literature family; retain the label without inferring a QuAntü intensity measurement. |
| Bala, 0.01_I_sat0 label | [Bala_0.01_I_sat0.csv](../data/raw/Bala_0.01_I_sat0.csv) | [Bala_0.01_I_sat0_absorption_data_processed.csv](../data/processed/Bala_0.01_I_sat0_absorption_data_processed.csv) | 78 | Same literature family. |
| Horn | [HORN.csv](../data/raw/HORN.csv) | [HORN_absorption_data_processed.csv](../data/processed/HORN_absorption_data_processed.csv) | 42 | Horn et al., 2011; DOI `10.1103/PhysRevA.84.043851`. |
| Jacques | [Jacques.csv](../data/raw/Jacques.csv) | [Jacques_absorption_data_processed.csv](../data/processed/Jacques_absorption_data_processed.csv) | 55 | Jacques et al., 2009; DOI `10.1088/0143-0807/30/5/001`. |
| Siddons | [Siddons.csv](../data/raw/Siddons.csv) | [Siddons_absorption_data_processed.csv](../data/processed/Siddons_absorption_data_processed.csv) | 64 | Siddons et al., 2008; DOI `10.1088/0953-4075/41/15/155004`. |
| Siddons, T_16.5 label | [Siddons_T_16.5.csv](../data/raw/Siddons_T_16.5.csv) | [Siddons_T_16.5_absorption_data_processed.csv](../data/processed/Siddons_T_16.5_absorption_data_processed.csv) | 38 | Same family; verify the exact condition and its unit against the source figure. |
| Siddons, T_25.0 label | [Siddons_T_25.0.csv](../data/raw/Siddons_T_25.0.csv) | [Siddons_T_25.0_absorption_data_processed.csv](../data/processed/Siddons_T_25.0_absorption_data_processed.csv) | 61 | Same literature family. |
| Siddons, T_36.6 label | [Siddons_T_36.6.csv](../data/raw/Siddons_T_36.6.csv) | [Siddons_T_36.6_absorption_data_processed.csv](../data/processed/Siddons_T_36.6_absorption_data_processed.csv) | 69 | Same literature family. |

Accompanying images remain in [raw](../data/raw/), and reference PDFs in [references/papers](../references/papers/). Atomic data used by MATLAB are described in the [report derivation](../reports/technical-progress/density_matrix_model.tex); Steck compilations are in [references/atomic-data](../references/atomic-data/).

## Formats and transformations

- CSVs use comma delimiters and one header line. Some headers and values contain spaces, which readers should tolerate.
- Raw files retain generic `x, y` names. Most processed files use `x,absorption`; the processed Jacques file retains `x, y`. They do not all share a uniform naming schema.
- Differences between raw and processed files include axis and ordinate transformations; do not assume one universal transformation. In particular, do not combine axes without checking sign, origin, and scale.
- Slightly negative values are preserved in some processed data. They have not been clipped here and should not be implicitly removed to improve metrics.
- The original collection provides no general script or per-file record reproducing every raw → processed transformation, digitization tool, calibration point, or uncertainty. That traceability remains pending.

Density-matrix model calibrations are a separate stage: the affine axis and optical-depth normalization described in [science.md](science.md) belong to the model comparison and do not document how each CSV was digitized.

## Requirements for future additions

For each new dataset, record alongside the file: exact reference and figure; extraction author and date; axis units and convention; original ordinate quantity; tool and calibration points; ordered transformations; uncertainties; license or usage conditions; and source-file hash. Preserve the original and generate derivatives with a versioned script.

The [inventory](inventory.csv) identifies local origin and copy integrity, but a hash does not establish bibliographic provenance or redistribution rights. Derived papers, figures, and tables retain their respective holders' attributions and conditions. No collection-wide open license is declared for those materials.
