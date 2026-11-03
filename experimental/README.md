# Experimental Group

The Experimental Group is part of **QuAntü**, the ANID Thematic Research Ring
project **“Neutral-atom-based quantum computing in Chile” (ATE250066)**.

**Group lead:** Jerónimo Maze<br>
**Project role:** Alternate Director

## Objectives and current scope

This area connects rubidium spectroscopy and laser-cooling concepts with the
data, hardware references, and documentation needed for experimental work. Its
repository objectives are to:

- Curate reference spectra with explicit sources, units, and processing history
  for comparison with theoretical models.
- Organize vapor-cell documentation and the physical conventions used when
  discussing spectroscopy, laser locking, and magneto-optical trapping.
- Support shared understanding of cooling and trapping through reproducible
  educational material.
- Establish reproducible acquisition, calibration, and uncertainty records as
  measurements from the project become available.

The current datasets are digitized or processed **literature reference data**.
They must retain their source attribution and must not be described as local
laboratory measurements. The MOT animation is a schematic teaching resource
with representative scales. This collection does not establish that a project
MOT has been built or operated, and it currently includes no instrument-control
or complete raw-to-processed data pipeline.

## Materials

| Material | Purpose |
| --- | --- |
| [Raw reference data](data/raw/) | Literature figures and associated digitized CSVs. |
| [Processed reference data](data/processed/) | Existing processed absorption curves. |
| [Hardware references](references/hardware/) | Rubidium-cell and window-material documentation. |
| [MOT animation guide](education/mot/README.md) | Conventions, representative operating scales, and regeneration instructions. |
| [MOT video](education/mot/MOT_Rb87_workshop_1080p.mp4) | English-captioned explanation of SAS, Doppler cooling, quadrupole fields, and trapping. |
| [Animation source](education/mot/render_mot_workshop.py) | Reproducible renderer with included equation assets. |

Consult the shared [data-provenance guide](../docs/data-provenance.md) before
using the spectra, and preserve the [third-party notices](../THIRD_PARTY_NOTICES.md).

## Reproduce an animation preview

Use Python 3.11 or later. Run these commands from the **repository root**:

```sh
python -m pip install -r requirements-video.txt
python experimental/education/mot/render_mot_workshop.py --stills results/generated/mot-preview --times 3 32 72 --width 640 --height 360
```

The included equation images support rendering without regenerating LaTeX
assets. The component guide explains full-video rendering and the additional
LaTeX tools needed to regenerate equations. New review outputs belong under
`results/generated/`, outside the versioned reference collection.

## Collaboration and contributions

Work with the [Theory Group](../theory/README.md) to agree on frequency
conventions, calibration, and comparison observables. Share control and
measurement constraints with the [Algorithms Group](../algorithms/README.md)
when connecting circuit proposals to experimental capabilities.

For new measurements, record the setup, temperature, relevant laser parameters,
units, calibration, uncertainties, and processing commands alongside the raw
data. Follow the shared [contribution guide](../CONTRIBUTING.md),
[reproducibility guide](../docs/reproducibility.md), and
[validation record](../docs/validation.md). The [project overview](../README.md)
describes the three research groups.
