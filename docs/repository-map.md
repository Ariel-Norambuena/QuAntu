# QuAntü collection map

The published collection preserves **126 files** from the working folder. The [inventory](inventory.csv) records each original path, repository path, current size, current SHA256, and source SHA256. The `modified_for_portability` column marks any difference from the imported source, including portability adjustments and English translation. Documentation and organizational tools added to the repository are additional to these 126 files. Historical source paths remain unchanged in the inventory's `original_path` field.

## Research groups

| Group | Project lead | Imported files | Group guide |
| --- | --- | ---: | --- |
| Algorithms | Dardo Goyeneche, Director | 7 | [Algorithms README](../algorithms/README.md) |
| Experimental | Jerónimo Maze, Alternate Director | 64 | [Experimental README](../experimental/README.md) |
| Theory | Ariel Norambuena, Principal Investigator | 53 | [Theory README](../theory/README.md) |
| Shared outreach | Existing component credits | 2 | [QuAntü-STEM materials](../outreach/quantu-stem/) |
| **Total** | | **126** | [Inventory](inventory.csv) |

Group placement organizes the current collection; it does not change component authorship or establish new scientific results. Group READMEs and shared tools are additional files, outside the imported-file counts.

### Algorithms: 7 imported files

| Path | Imported files | Content and provenance |
| --- | ---: | --- |
| [algorithms/education/qiskit](../algorithms/education/qiskit/) | 7 | English adaptation of the Qiskit workshop snapshot, including its `.gitignore` and original credits. |

### Experimental: 64 imported files

| Path | Imported files | Content and provenance |
| --- | ---: | --- |
| [experimental/data/raw](../experimental/data/raw/) | 16 | Original raw-data collection: literature reference images and CSVs. |
| [experimental/data/processed](../experimental/data/processed/) | 10 | Original processed-data collection: processed absorption tables. |
| [experimental/references/hardware](../experimental/references/hardware/) | 2 | Rubidium-cell documentation from Thorlabs and SCHOTT. |
| [experimental/education/mot](../experimental/education/mot/) | 36 | MOT sources and video, rendered equations, and review frames. |

### Theory: 53 imported files

| Path | Imported files | Content and provenance |
| --- | ---: | --- |
| [theory/models/density-matrix](../theory/models/density-matrix/) | 12 | Original rubidium-vapor absorption collection: MATLAB models, tables, and saved spectra. |
| [theory/models/interactive](../theory/models/interactive/) | 3 | Original interactive-model collection: Python model, dashboard, and transition table. |
| [theory/archive/theoretical-group](../theory/archive/theoretical-group/) | 12 | Original theory-group collection: historical copy and result variants. |
| [theory/notebooks/absorption](../theory/notebooks/absorption/) | 6 | Collection associated with J. Ma's 2017 Scientific Reports paper: three notebooks, a table, and a presentation in two formats. |
| [theory/references/papers](../theory/references/papers/) | 8 | Consulted papers and atomic data. |
| [theory/references/atomic-data](../theory/references/atomic-data/) | 2 | Steck notes: rubidium data tables. |
| [theory/references/rubidium-theory](../theory/references/rubidium-theory/) | 2 | Theoretical documents about both rubidium isotopes. |
| [theory/reports/technical-progress](../theory/reports/technical-progress/) | 7 | Technical progress report: LaTeX, bibliography, three figures, and existing PDF. |
| [theory/education/lectures](../theory/education/lectures/) | 1 | Dynamical-modeling presentation by Ariel Norambuena. |

### Shared materials and tools

[outreach/quantu-stem](../outreach/quantu-stem/) preserves the two imported event files, including Alonso Recabarren's presentation. The root-level [docs](../docs/), [scripts](../scripts/), [tests](../tests/), and [validation](../validation/) directories support all three groups. Dependency manifests and repository configuration also remain at the root.

## Preserved duplicates and versions

In the original collection, eight of the twelve files in the two spectrum folders were identical by SHA256: both MATLAB programs, both CSVs, and all four `Rb_absorption_spectrum_slow_direct` exports. The four `Rb_absorption_spectrum` exports differ between folders and are preserved as distinct versions. `theory/models/density-matrix/` is the primary entry point; `theory/archive/theoretical-group/` preserves the second collection for traceability.

`Data_Rb_Gas.csv` had identical content in both MATLAB folders, the absorption notebooks, and the interactive model. Copies are preserved alongside their consumers. Steck PDFs in `theory/references/papers/` also have identical copies in `theory/references/atomic-data/`. Materials were not removed merely because they shared a name; the inventory supports comparing source and current hashes.

## Qiskit workshop and Git history

The workshop came from a nested Git repository with origin [Ariel-Norambuena/neutral-atoms-qiskit-workshop](https://github.com/Ariel-Norambuena/neutral-atoms-qiskit-workshop). It is imported as a **snapshot of ordinary files** in `algorithms/education/qiskit/`, with an English README and citation that preserve the original authorship credits. This repository does not contain the workshop's `.git` directory, register a submodule, or import its commit history. The original repository and files remain in the working folder.

## Exclusions

The `meetings/` folder, containing 11 meeting files and historical examples, was removed from the tree and history of the published branch at the project owner's request. The original files remain outside this checkout, in the working folder. The [Python two-level model](../theory/models/open-quantum-systems/) remains a standalone implementation with its tests and documentation.

The original `tmp/` folder contained 91 rendered images and text extractions used for PDF review, totaling 21,029,968 bytes. It was not imported and was not deleted from the working folder. The nested Git repository's 34 internal files, totaling 47,315 bytes, were also excluded. Scientific figures, the report PDF, review frames, and animation resources are included.

New execution results are stored under `results/` (D2 and checks), `outputs/oqs/` (two-level examples), or an explicit directory; both output roots are excluded from Git. Selected evidence is versioned in `validation/`. Output locations, environments, and caches are excluded through `.gitignore`. Attribution scope and external materials are documented in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Checking the import

From the repository root:

```sh
python scripts/verify_repository.py
```

The tool uses only the Python standard library. It checks the 126 records, current sizes and hashes, path uniqueness and safety, LaTeX resources, local Markdown links, Python syntax, and notebook code cells. It does not execute models, recompile the PDF, or fetch external links. `source_sha256` preserves the hash recorded at import; the portable check does not require access to the original folder.
