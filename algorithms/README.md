# Algorithms Group

The Algorithms Group is part of **QuAntü**, the ANID Thematic Research Ring
project **“Neutral-atom-based quantum computing in Chile” (ATE250066)**.

**Group lead:** [Dardo Goyeneche](https://github.com/dardomg)<br>
**Project role:** Director

## Objectives and current scope

This area supports algorithm development and reproducible circuit simulations
in the context of neutral-atom quantum computing. Its repository objectives are
to:

- Explain the connection between quantum states, gates, and algorithmic
  primitives using examples that can be inspected and modified.
- Provide reproducible circuit implementations with explicit assumptions,
  expected outcomes, and numerical checks.
- Connect future algorithm requirements with the dynamical models and
  experimental constraints developed by the other groups.

The current material is an introductory Qiskit workshop. It includes one-qubit
and Bell-state examples, a manually constructed two-qubit Grover search, and a
conceptual introduction to Shor's algorithm. Execution uses classical
`Statevector` simulation and seeded sampling. The notebook does not implement
full Shor factorization or execute circuits on quantum hardware.

## Materials

| Material | Purpose |
| --- | --- |
| [Workshop guide](education/qiskit/README.md) | Teaching context, dependencies, and instructor preparation. |
| [Student notebook](education/qiskit/Neutral_Atom_Qiskit_Workshop_1h.ipynb) | Circuit examples, Grover search, an editable challenge, and automated checks. |
| [Notebook generator](education/qiskit/build_workshop_notebook.py) | Deterministic regeneration of the teaching notebook. |
| [Notebook validator](education/qiskit/validate_notebook.py) | Executes all 12 code cells without Jupyter. |
| [Component citation](education/qiskit/CITATION.cff) | Original workshop authorship and citation information. |

Group leadership and material authorship are distinct. The workshop retains its
credit to Ariel Norambuena and its original event context.

## Run the workshop

Use Python 3.11 or later. Run these commands from the **repository root**:

```sh
python -m pip install -r algorithms/education/qiskit/requirements.txt
python algorithms/education/qiskit/validate_notebook.py
```

Open the student notebook in the same Python environment for the interactive
exercise. The validator runs locally without credentials, Aer, or hardware
access. To regenerate the notebook intentionally:

```sh
python algorithms/education/qiskit/build_workshop_notebook.py
```

## Collaboration and contributions

Work with the [Theory Group](../theory/README.md) to state model and noise
assumptions, and with the [Experimental Group](../experimental/README.md) to
identify available controls, measurement observables, and physical constraints.
Distinguish ideal simulation, noisy simulation, and device execution in any
future result.

New algorithm examples should record circuit definitions, parameters, sampling
seeds, dependencies, and the checks needed to reproduce their outputs. Follow
the shared [contribution guide](../CONTRIBUTING.md),
[reproducibility guide](../docs/reproducibility.md), and
[validation record](../docs/validation.md). The [project overview](../README.md)
describes the three research groups and the wider collection.
