#!/usr/bin/env python3
"""Build the robust, dependency-light Qiskit workshop notebook."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Neutral_Atom_Qiskit_Workshop_1h.ipynb"


def markdown(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.strip() + "\n",
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip() + "\n",
    }


CELLS = [
    markdown(
        r"""
# From a trapped atom to a quantum algorithm

## Hands-on Qiskit workshop — 60 minutes

**Main idea:** *Shor provides the motivating promise; Grover provides a hands-on way to understand quantum algorithms.*

**Event:** Workshop Astro Physics<br>
**Author and instructor:** Prof. Ariel Norambuena — Universidad Técnica Federico Santa María · QSTATE · QuAntü

In the first part, we saw how a MOT captures rubidium atoms, how internal states can represent qubits, and how controlled interactions implement gates. We will now follow the final connection:

$$
\text{controlled atom}\longrightarrow\text{qubit}\longrightarrow
\text{interference}\longrightarrow\text{algorithm}.
$$

This notebook runs **locally and offline**. It does not use IBM Runtime, `qiskit-aer`, `qiskit_algorithms`, widgets, or external services.
"""
    ),
    markdown(
        r"""
## Learning objectives and outline

By the end, we will be able to:

1. Interpret superposition and measurement in a circuit.
2. Construct an entangled Bell state.
3. Explain which part of Shor's algorithm is quantum.
4. Build a two-qubit Grover search manually.
5. Verify that the algorithm finds any of the four possible answers.

### Suggested timing

- **3 min:** Shor, factorization, and cryptography.
- **5 min:** one qubit, Hadamard, and measurement.
- **5 min:** Bell entanglement.
- **15 min:** the oracle, phase, and interference in Grover.
- **7 min:** programming challenge and discussion.

> The remaining workshop time covers the physical motivation, the MOT, and neutral-atom qubits.
"""
    ),
    markdown(
        r"""
## Before you begin

1. Select a Python kernel with Qiskit installed.
2. Run **Restart Kernel and Run All**.
3. If the first cell reports that Qiskit is missing, run this command in a terminal using the same Python environment:

```text
python -m pip install "qiskit>=1.4,<3"
```

Aer, Matplotlib, pylatexenc, and an IBM Quantum account are not required. Earlier versions were validated with Qiskit 1.4.5 and 2.5.1; this repository was also validated with Qiskit 2.6.1.
"""
    ),
    code(
        r'''
# Minimal environment check: fail early with a clear message.
import sys
from importlib.metadata import PackageNotFoundError, version

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
except ImportError as exc:
    raise RuntimeError(
        "Qiskit is unavailable in this kernel. Open a terminal in the same "
        "environment and run: python -m pip install qiskit"
    ) from exc

try:
    QISKIT_VERSION = version("qiskit")
except PackageNotFoundError:
    QISKIT_VERSION = "unknown"

print(f"Python : {sys.version.split()[0]}")
print(f"Qiskit : {QISKIT_VERSION}")
print("Environment ready: only the Qiskit core will be used.")
'''
    ),
    code(
        r'''
# Self-contained tools for simulation and displaying results.
# Use HTML bars when supported, with text as a fallback.
from collections import Counter
from html import escape
import random


def statevector_of(circuit):
    """Return the exact state of a circuit without measurement instructions."""
    return Statevector.from_instruction(circuit)


def probabilities_of(circuit, cutoff=1e-12):
    """Exact computational-basis probabilities."""
    probabilities = statevector_of(circuit).probabilities_dict()
    return {
        str(label): float(probability)
        for label, probability in probabilities.items()
        if float(probability) > cutoff
    }


def simulate_counts(circuit, shots=1024, seed=2026):
    """Reproducible local sampling without Aer or hardware access."""
    probabilities = probabilities_of(circuit)
    labels = list(probabilities)
    weights = [probabilities[label] for label in labels]
    rng = random.Random(seed)
    samples = rng.choices(labels, weights=weights, k=shots)
    return dict(Counter(samples))


def show_counts(counts, title="Results", color="#36d9ff"):
    """Display an HTML histogram in Jupyter, with an ASCII fallback."""
    total = sum(counts.values())
    ordered = sorted(counts.items())
    try:
        from IPython.display import HTML, display

        rows = []
        for label, count in ordered:
            fraction = count / total if total else 0.0
            rows.append(
                "<div style='display:grid;grid-template-columns:52px 1fr 105px;"
                "gap:10px;align-items:center;margin:7px 0'>"
                f"<code style='font-size:16px'>{escape(label)}</code>"
                "<div style='background:#17233f;border-radius:6px;height:22px'>"
                f"<div style='width:{100*fraction:.3f}%;height:22px;"
                f"background:{color};border-radius:6px'></div></div>"
                f"<span>{count} ({100*fraction:5.1f}%)</span></div>"
            )
        display(HTML(
            f"<h4 style='margin-bottom:8px'>{escape(title)}</h4>" + "".join(rows)
        ))
    except Exception:
        print(title)
        for label, count in ordered:
            fraction = count / total if total else 0.0
            bar = "#" * int(round(40 * fraction))
            print(f"  {label}: {count:4d} |{bar:<40}| {100*fraction:5.1f}%")


def show_amplitudes(circuit, title="Amplitudes"):
    """Show signs and phases, which are invisible in a histogram."""
    state = statevector_of(circuit)
    width = circuit.num_qubits
    print(title)
    for index, amplitude in enumerate(state.data):
        if abs(amplitude) > 1e-10:
            label = format(index, f"0{width}b")
            print(f"  |{label}> : {amplitude.real:+.3f}{amplitude.imag:+.3f}j")


def show_circuit(circuit, title="Circuit"):
    print(title)
    print(circuit.draw(output="text"))
'''
    ),
    code(
        r'''
# Smoke test: OK means the main workshop cells can run.
_smoke = QuantumCircuit(1)
_smoke.h(0)
_p = probabilities_of(_smoke)
assert abs(_p["0"] - 0.5) < 1e-10
assert abs(_p["1"] - 0.5) < 1e-10
print("OK — Qiskit and the statevector simulator work correctly.")
'''
    ),
    markdown(
        r"""
# 1. Shor: the promise

Factorization asks which primes multiply to give a number:

$$N=pq.$$

For (N=15), the answer (15=3\times5) is obvious. A real RSA key uses an (N) with hundreds or thousands of bits, making recovery of (p) and (q) extremely difficult.

Shor's insight was to transform factorization into **period finding**. Choose an integer (a) coprime to (N) and study

$$f(x)=a^x\bmod N.$$

There are only (N) possible remainders, so the sequence eventually repeats. The quantum computer estimates this period (r) efficiently; converting (r) into factors through greatest common divisors is a classical calculation.

> **Scope:** we will not implement a compiled circuit that factors 15. We will examine the mathematical idea and use the hands-on session to build a complete, transparent quantum algorithm: Grover.
"""
    ),
    code(
        r'''
# The outline of Shor for N=15, using only the Python standard library.
from math import gcd


def multiplicative_order(a, N):
    """Smallest r>0 such that a**r = 1 (mod N), assuming gcd(a,N)=1."""
    if gcd(a, N) != 1:
        raise ValueError("a and N must be coprime")
    value = 1
    for r in range(1, N + 1):
        value = (value * a) % N
        if value == 1:
            return r
    raise RuntimeError("Period not found; check the inputs.")


N = 15
a = 2
r = multiplicative_order(a, N)
sequence = [pow(a, x, N) for x in range(r + 1)]

print(f"Sequence a^x mod N: {sequence}")
print(f"Period found: r = {r}")

if r % 2 != 0:
    raise RuntimeError("This value of a produced an odd period; try another a.")

x = pow(a, r // 2, N)
factor_1 = gcd(x - 1, N)
factor_2 = gcd(x + 1, N)

print(f"gcd(a^(r/2)-1, N) = {factor_1}")
print(f"gcd(a^(r/2)+1, N) = {factor_2}")
print(f"Result: {N} = {factor_1} × {factor_2}")

assert {factor_1, factor_2} == {3, 5}
'''
    ),
    markdown(
        r"""
## Where was the quantum part?

The previous cell calculated (r) classically so that we could follow the entire logic. In Shor's algorithm, the difficult step—estimating the period—uses:

1. A superposition of many values of (x).
2. Reversible modular exponentiation.
3. Phase estimation and the quantum Fourier transform.
4. Measurement and classical postprocessing.

Shor is a useful motivation, but implementing it in a first 20-minute exercise would hide too many ingredients. We will now build an algorithm whose interference can be followed gate by gate.
"""
    ),
    markdown(
        r"""
# 2. One qubit: superposition and measurement

We identify two internal atomic levels with

$$|0\rangle\quad\text{and}\quad |1\rangle.$$

A Hadamard gate prepares

$$H|0\rangle=|+\rangle=\frac{|0\rangle+|1\rangle}{\sqrt2}.$$

The state contains amplitudes; measurement produces random classical outcomes.
"""
    ),
    code(
        r'''
one_qubit = QuantumCircuit(1, name="superposition")
one_qubit.h(0)

show_circuit(one_qubit, "One-qubit circuit")
show_amplitudes(one_qubit)
counts_one = simulate_counts(one_qubit, shots=1000, seed=7)
show_counts(counts_one, "1000 simulated measurements")
'''
    ),
    markdown(
        r"""
Superposition does **not** mean that we see both 0 and 1 in a single run. Each measurement produces one bit; the distribution emerges after repeating the experiment.

A quantum algorithm organizes the amplitudes before measurement. Interference will perform this task in Grover's algorithm.
"""
    ),
    markdown(
        r"""
# 3. Two qubits: entanglement

Apply (H) to the first qubit and then a controlled (CX) gate:

$$
|00\rangle\longrightarrow
\frac{|00\rangle+|10\rangle}{\sqrt2}
\longrightarrow
|\Phi^+\rangle=\frac{|00\rangle+|11\rangle}{\sqrt2}.
$$

The measurements are correlated: 00 and 11 appear, while 01 and 10 do not.
"""
    ),
    code(
        r'''
bell = QuantumCircuit(2, name="Bell")
bell.h(0)
bell.cx(0, 1)

show_circuit(bell, "Preparation of |Φ+>")
show_amplitudes(bell)
counts_bell = simulate_counts(bell, shots=1000, seed=11)
show_counts(counts_bell, "Bell-state measurements", color="#a85cff")
'''
    ),
    markdown(
        r"""
# 4. Grover: finding an answer through interference

Imagine four possible experimental configurations, encoded as

$$|00\rangle,\ |01\rangle,\ |10\rangle,\ |11\rangle.$$

Exactly one configuration satisfies the desired condition. A classical search can check the candidates one at a time. Grover uses:

1. **Superposition:** prepare all candidates with equal amplitude.
2. **Oracle:** mark the answer by changing only its phase.
3. **Diffuser:** convert the phase difference into probability amplification.
4. **Measurement:** reveal the amplified answer.

With four candidates and one solution, one ideal iteration is sufficient.

> The experimental configuration is a teaching analogy. The oracle is a coherent function that recognizes the answer, rather than a classical measurement of the MOT.
"""
    ),
    code(
        r'''
def phase_oracle_2q(target):
    """Phase oracle for target in {'00','01','10','11'}.

    The bit string uses the conventional measurement order |q1 q0>.
    """
    if target not in {"00", "01", "10", "11"}:
        raise ValueError("target must be '00', '01', '10', or '11'")

    oracle = QuantumCircuit(2, name=f"O_{target}")
    # Temporarily map target to |11>, apply CZ, then undo the X gates.
    for qubit, bit in enumerate(reversed(target)):
        if bit == "0":
            oracle.x(qubit)
    oracle.cz(0, 1)
    for qubit, bit in enumerate(reversed(target)):
        if bit == "0":
            oracle.x(qubit)
    return oracle


TARGET = "10"  # Change to 00, 01, 10, or 11.
oracle = phase_oracle_2q(TARGET)
show_circuit(oracle, f"Oracle marking |{TARGET}>")
'''
    ),
    markdown(
        r"""
The oracle does not yet increase the probability of the answer. It changes

$$|x_*\rangle\longrightarrow-|x_*\rangle.$$

This sign is invisible if we measure immediately, but it changes how the amplitudes interfere in the next step.
"""
    ),
    code(
        r'''
def diffuser_2q():
    """Inversion about the mean, up to an irrelevant global phase."""
    diffuser = QuantumCircuit(2, name="D")
    for qubit in range(2):
        diffuser.h(qubit)
        diffuser.x(qubit)
    diffuser.cz(0, 1)
    for qubit in range(2):
        diffuser.x(qubit)
        diffuser.h(qubit)
    return diffuser


diffuser = diffuser_2q()
show_circuit(diffuser, "Two-qubit diffuser")
'''
    ),
    code(
        r'''
def grover_search_2q(target):
    """Complete one-iteration Grover circuit for four candidates."""
    circuit = QuantumCircuit(2, name=f"Grover_{target}")
    for qubit in range(2):
        circuit.h(qubit)
    circuit.compose(phase_oracle_2q(target), inplace=True)
    circuit.compose(diffuser_2q(), inplace=True)
    return circuit


# Keep all three stages to observe what changes.
initial = QuantumCircuit(2)
for qubit in range(2):
    initial.h(qubit)

after_oracle = initial.copy()
after_oracle.compose(phase_oracle_2q(TARGET), inplace=True)

grover = grover_search_2q(TARGET)

show_circuit(grover, f"Complete Grover circuit: search for |{TARGET}>")
'''
    ),
    code(
        r'''
show_amplitudes(initial, "1) Uniform superposition")
print()
show_amplitudes(after_oracle, "2) After the oracle: one phase changed")
print()
show_amplitudes(grover, "3) After the diffuser: the answer was amplified")

counts_grover = simulate_counts(grover, shots=1000, seed=19)
show_counts(counts_grover, f"Grover: marked state |{TARGET}>", color="#57e7a6")
'''
    ),
    markdown(
        r"""
## The key conceptual step

- Before the oracle: four equal amplitudes.
- After the oracle: four equal probabilities, but one amplitude has the opposite sign.
- After the diffuser: destructive interference cancels incorrect answers, while constructive interference amplifies the correct answer.

Grover's speedup comes from designing an evolution that **cancels incorrect answers before measurement**.
"""
    ),
    markdown(
        r"""
## Student challenge

Change only `MY_ANSWER` and run the cell again. Before looking at the result, predict which bar will dominate.
"""
    ),
    code(
        r'''
MY_ANSWER = "01"  # Try 00, 01, 10, or 11.

my_circuit = grover_search_2q(MY_ANSWER)
my_results = simulate_counts(my_circuit, shots=1000, seed=23)

show_circuit(my_circuit, f"My search: |{MY_ANSWER}>")
show_counts(my_results, "Challenge result", color="#ffcc5c")
'''
    ),
    markdown(
        r"""
## From four candidates to (N) candidates

For one solution among (N=2^n) candidates:

$$
\text{classical queries}=O(N),
\qquad
\text{Grover queries}=O(\sqrt N).
$$

The difference is small for four candidates; our goal is to see the complete mechanism. The advantage appears at larger sizes, although oracles and multicontrolled gates are costly on current noisy computers.

Grover is independent of the physical platform: the same logical circuit can be compiled for superconducting devices, ions, or neutral atoms. The physical implementation of the gates changes, for example through Rydberg interactions.
"""
    ),
    markdown(
        r"""
# 5. Automated validation

This cell tests all four oracles and the properties used throughout the workshop. It must finish with `ALL TESTS PASSED`.
"""
    ),
    code(
        r'''
def validate_workshop():
    # One-qubit superposition.
    p_one = probabilities_of(one_qubit)
    assert abs(p_one["0"] - 0.5) < 1e-10
    assert abs(p_one["1"] - 0.5) < 1e-10

    # Bell: only 00 and 11.
    p_bell = probabilities_of(bell)
    assert set(p_bell) == {"00", "11"}
    assert all(abs(value - 0.5) < 1e-10 for value in p_bell.values())

    # Grover must amplify each two-qubit target exactly.
    for target in ("00", "01", "10", "11"):
        probabilities = probabilities_of(grover_search_2q(target))
        assert set(probabilities) == {target}
        assert abs(probabilities[target] - 1.0) < 1e-10

    # Shor example used in the introduction.
    assert multiplicative_order(2, 15) == 4
    assert {gcd(2**2 - 1, 15), gcd(2**2 + 1, 15)} == {3, 5}

    return True


assert validate_workshop()
print("ALL TESTS PASSED ✓")
'''
    ),
    markdown(
        r"""
# Closing discussion

1. **The MOT supplies cold, controllable atoms.**
2. **Atomic levels encode qubits, and interactions implement gates.**
3. **Shor illustrates the potential impact on problems such as factorization.**
4. **Grover lets us see directly how phase and interference carry out a computation.**

The main lesson is more than memorizing a circuit:

> A quantum algorithm programs amplitudes and phases so that the desired answer is the most likely measurement outcome.

## Troubleshooting

- Run the cells from the beginning; functions are defined progressively.
- Confirm that the notebook uses the Python environment where Qiskit is installed.
- `qiskit-aer` is not required for this workshop.
- Use the local simulator during the main session.
- If the graphical histogram does not appear, its text fallback contains exactly the same information.

---

*Author: Prof. Ariel Norambuena. Material prepared for Workshop Astro Physics.*
"""
    ),
]


NOTEBOOK = {
    "cells": CELLS,
    "metadata": {
        "authors": [{"name": "Ariel Norambuena"}],
        "event": "Workshop Astro Physics",
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
        "title": "From a trapped atom to a quantum algorithm",
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(NOTEBOOK, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(OUTPUT)
    print(f"Cells: {len(CELLS)}")


if __name__ == "__main__":
    main()
