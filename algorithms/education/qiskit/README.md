# Qiskit workshop: from a trapped atom to a quantum algorithm

A self-contained notebook for the practical section of a one-hour introductory
workshop on quantum computing with neutral atoms.

**Event:** Workshop Astro Physics<br>
**Author and instructor:** Prof. Ariel Norambuena — Universidad Técnica Federico
Santa María · QSTATE · QuAntü

## Student notebook

[`Neutral_Atom_Qiskit_Workshop_1h.ipynb`](Neutral_Atom_Qiskit_Workshop_1h.ipynb)
connects a conceptual introduction to Shor with a complete, manually constructed
two-qubit Grover algorithm. It also includes a one-qubit circuit, a Bell state,
an editable programming challenge, and automated checks. All teaching text,
comments, and displayed messages are in English.

## Required dependency

```text
qiskit>=1.4,<3
```

The workshop does not require `qiskit-aer`, `qiskit-algorithms`,
`qiskit-ibm-runtime`, Matplotlib, pylatexenc, credentials, network access, or
quantum hardware. Simulation uses `qiskit.quantum_info.Statevector` from the
Qiskit core. Python's `random` module generates shots with a fixed seed.

Earlier complete executions were validated with Qiskit 1.4.5 and 2.5.1. The
English edition was also validated with Qiskit 2.6.1.

## Instructor preparation

1. Open the notebook in the Python environment where Qiskit is installed.
2. Run **Restart Kernel and Run All**.
3. Confirm that the final code cell prints `ALL TESTS PASSED`.
4. During the workshop, ask students to change only `MY_ANSWER` in the challenge.

Use local simulation during the session. Hardware access introduces accounts,
queues, API changes, and noise that distract from a first hands-on exercise.

## Background

The earlier 2023 material depended on APIs that were removed or split from the
base package, including `from qiskit import Aer`, `qiskit.providers.aer`,
`qiskit.ignis`, and Ignis-based mitigation. Stored widgets and outputs increased
its size beyond 500 KB. The current notebook uses core APIs and does not store
precomputed results.

## Regeneration and validation

From the repository root:

```text
python algorithms/education/qiskit/build_workshop_notebook.py
python algorithms/education/qiskit/validate_notebook.py
```

Generation is deterministic. Validation executes all 12 code cells without
requiring Jupyter or nbconvert.

## Official references

- [Grover's algorithm](https://qiskit.qotlabs.org/docs/tutorials/grovers-algorithm)
- [Shor's algorithm](https://quantum.cloud.ibm.com/docs/en/tutorials/shors-algorithm)

## Citation

Bibliographic information is provided in [`CITATION.cff`](CITATION.cff).
