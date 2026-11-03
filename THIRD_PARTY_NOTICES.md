# Provenance and third-party materials

This repository brings together code, data, documents, and educational materials used by QuAntü. Inclusion does not transfer copyright or establish a new license for original files. The collection is public and preserves its components' attributions.

No general license applies to the entire collection. Respect the notices, authors, and conditions stated in each document and its sources. The absence of a license file alongside a material does not grant rights.

## Papers and atomic data

The PDFs in [references/papers](references/papers/) and [references/atomic-data](references/atomic-data/) are reference documents by their respective authors and publishers. The report bibliography is preserved in [references.bib](reports/technical-progress/references.bib):

| Reference | Bibliographic identifier |
| --- | --- |
| Jian Ma et al., *Optical Spin Noise Spectra of Rb Atomic Gas with Homogeneous and Inhomogeneous Broadening* (2017) | DOI `10.1038/s41598-017-08759-4` |
| V. Jacques et al., *Nonlinear Spectroscopy of Rubidium: An Undergraduate Experiment* (2009) | DOI `10.1088/0143-0807/30/5/001` |
| Paul Siddons et al., *Absolute Absorption on Rubidium D Lines: Comparison Between Theory and Experiment* (2008) | DOI `10.1088/0953-4075/41/15/155004` |
| Nicola Agnew et al., *Practical Doppler Broadening Thermometry* (2024) | DOI `10.1063/5.0234155` |
| Rajni Bala et al., *A Comprehensive Model for Doppler Spectra in Thermal Atomic Vapour* (2022) | DOI `10.1088/1361-6455/ac7e93` |
| H. Horn et al., *Spin-Noise Spectroscopy Under Resonant Optical Probing Conditions: Coherent and Nonlinear Effects* (2011) | DOI `10.1103/PhysRevA.84.043851` |
| Daniel A. Steck, *Rubidium 85 D Line Data* and *Rubidium 87 D Line Data* | [Atomic data source](https://steck.us/alkalidata/) |

Dates, titles, and identifiers in this table are transcribed from the report's local bibliography; they are not a new bibliographic review. Copies of Steck's tables in both folders are preserved for provenance.

## Images and tables derived from literature

[data/raw](data/raw/) and [data/processed](data/processed/) contain images, digitized tables, and processed data associated with Agnew, Bala, Horn, Jacques, and Siddons. Cite their sources when reusing them. These materials must not be presented as original QuAntü laboratory measurements. Consult the data documentation for file-level provenance and reconstruction limitations; including a CSV does not certify its license or digitization accuracy.

[notebooks/absorption](notebooks/absorption/) originated in a folder named for code associated with J. Ma's 2017 Scientific Reports paper. That folder name connects the material with a scientific reference; it does not by itself establish that the notebooks were published by the paper's authors. The inventory preserves the exact historical source path without assigning unsupported authorship or licensing.

## Manufacturer documentation and theoretical materials

[references/hardware](references/hardware/) contains Thorlabs and SCHOTT/BOROFLOAT documents. Their trade names and content belong to their respective holders. [references/rubidium-theory](references/rubidium-theory/) preserves other rubidium reference documents; their inclusion does not establish QuAntü team authorship or a redistribution license.

## Qiskit workshop and other educational materials

[education/qiskit](education/qiskit/) preserves an English adaptation of the imported snapshot of [neutral-atoms-qiskit-workshop](https://github.com/Ariel-Norambuena/neutral-atoms-qiskit-workshop), attributed to Ariel Norambuena by its README and [CITATION.cff](education/qiskit/CITATION.cff). Those notices are preserved. No independent license allowing a collection-wide license to be applied to the workshop was identified in the imported files.

Lecture and outreach presentations preserve the names and credits in their originals, including Ariel Norambuena and Alonso Recabarren. Their inclusion does not authorize relicensing their images, brands, or other external components.

The Python and MATLAB libraries needed to run the programs are not redistributed here; their licenses and terms belong to their distributors. Generated MOT animation resources remain alongside their sources and documentation. Interpret the animation's illustrative values using the conventions in its README.

## Provenance record

[docs/inventory.csv](docs/inventory.csv) connects the 126 source paths with their destinations and hashes; [docs/repository-map.md](docs/repository-map.md) explains copies, exclusions, and the Git snapshot. The 11 meeting materials were removed from the published tree, and their originals remain in the project's working folder. Each material's specific notices and conditions continue to govern its reuse.
