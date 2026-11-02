#!/usr/bin/env python3
"""Build the robust, dependency-light Qiskit workshop notebook."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Taller_Qiskit_Atomos_Neutros_1h.ipynb"


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
# Del átomo atrapado al algoritmo cuántico

## Taller práctico de Qiskit — 60 minutos

**Idea central:** *Shor como la promesa que captura la imaginación; Grover como la experiencia práctica que permite entenderla.*

**Evento:** Workshop Astro Physics  
**Autor y relator:** Prof. Ariel Norambuena — Universidad Técnica Federico Santa María · QSTATE · QuAntü

En la primera parte vimos cómo una MOT captura átomos de rubidio, cómo los estados internos pueden representar qubits y cómo las interacciones controladas producen compuertas. Ahora recorreremos el último puente:

$$
\text{átomo controlado}\longrightarrow\text{qubit}\longrightarrow
\text{interferencia}\longrightarrow\text{algoritmo}.
$$

Este notebook funciona **localmente y sin conexión a internet**. No utiliza IBM Runtime, `qiskit-aer`, `qiskit_algorithms`, widgets ni servicios externos.
"""
    ),
    markdown(
        r"""
## Objetivos y ruta

Al terminar podremos:

1. Interpretar superposición y medición en un circuito.
2. Construir un estado entrelazado de Bell.
3. Explicar qué parte de Shor es verdaderamente cuántica.
4. Construir manualmente una búsqueda de Grover de dos qubits.
5. Verificar que el algoritmo encuentra cualquiera de cuatro respuestas posibles.

### Distribución sugerida

- **3 min:** Shor, factorización y criptografía.
- **5 min:** un qubit, Hadamard y medición.
- **5 min:** entrelazamiento de Bell.
- **15 min:** oráculo, fase e interferencia en Grover.
- **7 min:** reto de programación y discusión.

> El resto de la hora corresponde a la motivación física, la MOT y los qubits de átomos neutros.
"""
    ),
    markdown(
        r"""
## Antes de comenzar

1. Seleccionar un kernel de Python que tenga Qiskit instalado.
2. Ejecutar **Restart Kernel and Run All**.
3. Si la primera celda informa que Qiskit no está instalado, ejecutar en una terminal asociada al mismo Python:

```text
python -m pip install "qiskit>=1.4,<3"
```

No es necesario instalar Aer, Matplotlib, pylatexenc ni configurar una cuenta de IBM Quantum. El notebook fue validado con Qiskit 1.4.5 y 2.5.1.
"""
    ),
    code(
        r'''
# Diagnóstico mínimo del entorno. Esta celda falla temprano y con un mensaje claro.
import sys
from importlib.metadata import PackageNotFoundError, version

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
except ImportError as exc:
    raise RuntimeError(
        "Qiskit no está disponible en este kernel. Abra una terminal del mismo "
        "entorno y ejecute: python -m pip install qiskit"
    ) from exc

try:
    QISKIT_VERSION = version("qiskit")
except PackageNotFoundError:
    QISKIT_VERSION = "desconocida"

print(f"Python : {sys.version.split()[0]}")
print(f"Qiskit : {QISKIT_VERSION}")
print("Entorno listo: sólo se usará el núcleo de Qiskit.")
'''
    ),
    code(
        r'''
# Herramientas autocontenidas para simular y mostrar resultados.
# Se usan barras HTML cuando el notebook lo permite y texto como alternativa.
from collections import Counter
from html import escape
import random


def statevector_of(circuit):
    """Devuelve el estado exacto producido por un circuito sin mediciones."""
    return Statevector.from_instruction(circuit)


def probabilities_of(circuit, cutoff=1e-12):
    """Probabilidades exactas en la base computacional."""
    probabilities = statevector_of(circuit).probabilities_dict()
    return {
        str(label): float(probability)
        for label, probability in probabilities.items()
        if float(probability) > cutoff
    }


def simulate_counts(circuit, shots=1024, seed=2026):
    """Muestreo local reproducible, sin Aer ni acceso a hardware."""
    probabilities = probabilities_of(circuit)
    labels = list(probabilities)
    weights = [probabilities[label] for label in labels]
    rng = random.Random(seed)
    samples = rng.choices(labels, weights=weights, k=shots)
    return dict(Counter(samples))


def show_counts(counts, title="Resultados", color="#36d9ff"):
    """Histograma robusto: HTML en Jupyter y ASCII como respaldo."""
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
    """Muestra signo y fase, información invisible en un histograma."""
    state = statevector_of(circuit)
    width = circuit.num_qubits
    print(title)
    for index, amplitude in enumerate(state.data):
        if abs(amplitude) > 1e-10:
            label = format(index, f"0{width}b")
            print(f"  |{label}> : {amplitude.real:+.3f}{amplitude.imag:+.3f}j")


def show_circuit(circuit, title="Circuito"):
    print(title)
    print(circuit.draw(output="text"))
'''
    ),
    code(
        r'''
# Prueba de humo: si aparece OK, las celdas centrales del taller pueden ejecutarse.
_smoke = QuantumCircuit(1)
_smoke.h(0)
_p = probabilities_of(_smoke)
assert abs(_p["0"] - 0.5) < 1e-10
assert abs(_p["1"] - 0.5) < 1e-10
print("OK — Qiskit y el simulador de estado funcionan correctamente.")
'''
    ),
    markdown(
        r"""
# 1. Shor: la promesa

La factorización pregunta por los primos cuyo producto forma un número:

$$N=pq.$$

Para (N=15), la respuesta (15=3\times5) es evidente. Para una clave RSA real, (N) contiene cientos o miles de bits y recuperar (p) y (q) es extremadamente difícil.

La intuición de Shor fue transformar la factorización en una **búsqueda de período**. Elegimos un entero (a) coprimo con (N) y estudiamos

$$f(x)=a^x\bmod N.$$

Como sólo existen (N) residuos posibles, la secuencia eventualmente se repite. El computador cuántico se utiliza para estimar eficientemente ese período (r); convertir (r) en factores mediante máximos comunes divisores es nuevamente un cálculo clásico.

> **Mensaje honesto:** aquí no implementaremos un circuito compilado para factorizar 15. Entenderemos el corazón matemático y reservaremos el tiempo práctico para un algoritmo cuántico completo y transparente: Grover.
"""
    ),
    code(
        r'''
# El esqueleto de Shor para N=15. Esta celda usa únicamente Python estándar.
from math import gcd


def multiplicative_order(a, N):
    """Menor r>0 tal que a**r = 1 (mod N), si gcd(a,N)=1."""
    if gcd(a, N) != 1:
        raise ValueError("a y N deben ser coprimos")
    value = 1
    for r in range(1, N + 1):
        value = (value * a) % N
        if value == 1:
            return r
    raise RuntimeError("No se encontró el período; revise las entradas.")


N = 15
a = 2
r = multiplicative_order(a, N)
sequence = [pow(a, x, N) for x in range(r + 1)]

print(f"Secuencia a^x mod N: {sequence}")
print(f"Período encontrado: r = {r}")

if r % 2 != 0:
    raise RuntimeError("Este valor de a produjo un período impar; pruebe otro a.")

x = pow(a, r // 2, N)
factor_1 = gcd(x - 1, N)
factor_2 = gcd(x + 1, N)

print(f"gcd(a^(r/2)-1, N) = {factor_1}")
print(f"gcd(a^(r/2)+1, N) = {factor_2}")
print(f"Resultado: {N} = {factor_1} × {factor_2}")

assert {factor_1, factor_2} == {3, 5}
'''
    ),
    markdown(
        r"""
## ¿Dónde estuvo la parte cuántica?

En la celda anterior calculamos (r) clásicamente para poder ver toda la lógica. En Shor, la parte difícil —estimar el período— se resuelve mediante:

1. Superposición de muchos valores de (x).
2. Exponenciación modular reversible.
3. Estimación de fase y transformada cuántica de Fourier.
4. Medición y postprocesamiento clásico.

Esto convierte a Shor en una motivación excelente, pero en una primera práctica de 20 minutos ocultaría demasiados ingredientes. Ahora construiremos un algoritmo cuya interferencia pueda seguirse puerta por puerta.
"""
    ),
    markdown(
        r"""
# 2. Un qubit: superposición y medición

Identificamos dos niveles internos del átomo con

$$|0\rangle\quad\text{y}\quad |1\rangle.$$

Una compuerta Hadamard prepara

$$H|0\rangle=|+\rangle=\frac{|0\rangle+|1\rangle}{\sqrt2}.$$

El estado contiene amplitudes; la medición entrega resultados clásicos aleatorios.
"""
    ),
    code(
        r'''
one_qubit = QuantumCircuit(1, name="superposición")
one_qubit.h(0)

show_circuit(one_qubit, "Circuito de un qubit")
show_amplitudes(one_qubit)
counts_one = simulate_counts(one_qubit, shots=1000, seed=7)
show_counts(counts_one, "1000 mediciones simuladas")
'''
    ),
    markdown(
        r"""
La superposición **no** significa que veremos simultáneamente 0 y 1 en una ejecución. Cada medición produce un bit; la distribución aparece al repetir el experimento.

El algoritmo cuántico debe organizar las amplitudes antes de medir. Ésa será la función de la interferencia en Grover.
"""
    ),
    markdown(
        r"""
# 3. Dos qubits: entrelazamiento

Aplicamos (H) al primer qubit y después una compuerta controlada (CX):

$$
|00\rangle\longrightarrow
\frac{|00\rangle+|10\rangle}{\sqrt2}
\longrightarrow
|\Phi^+\rangle=\frac{|00\rangle+|11\rangle}{\sqrt2}.
$$

Las mediciones están correlacionadas: aparecen 00 y 11, pero no 01 ni 10.
"""
    ),
    code(
        r'''
bell = QuantumCircuit(2, name="Bell")
bell.h(0)
bell.cx(0, 1)

show_circuit(bell, "Preparación de |Φ+>")
show_amplitudes(bell)
counts_bell = simulate_counts(bell, shots=1000, seed=11)
show_counts(counts_bell, "Mediciones del estado de Bell", color="#a85cff")
'''
    ),
    markdown(
        r"""
# 4. Grover: encontrar una respuesta mediante interferencia

Imaginemos cuatro configuraciones posibles de un experimento, codificadas como

$$|00\rangle,\ |01\rangle,\ |10\rangle,\ |11\rangle.$$

Una única configuración satisface la condición buscada. Clásicamente podemos consultar las opciones una a una. Grover utiliza:

1. **Superposición:** prepara todas las candidatas con igual amplitud.
2. **Oráculo:** marca la respuesta cambiando sólo su fase.
3. **Difusor:** convierte la diferencia de fase en amplificación de probabilidad.
4. **Medición:** revela la respuesta amplificada.

Con cuatro opciones y una solución, una iteración ideal es suficiente.

> La configuración experimental es una analogía pedagógica. El oráculo representa una función coherente capaz de reconocer la respuesta, no una medición clásica de la MOT.
"""
    ),
    code(
        r'''
def phase_oracle_2q(target):
    """Oráculo de fase para target en {'00','01','10','11'}.

    La cadena se escribe en el orden convencional de medición |q1 q0>.
    """
    if target not in {"00", "01", "10", "11"}:
        raise ValueError("target debe ser '00', '01', '10' o '11'")

    oracle = QuantumCircuit(2, name=f"O_{target}")
    # Convertimos temporalmente target en |11>, aplicamos CZ y deshacemos X.
    for qubit, bit in enumerate(reversed(target)):
        if bit == "0":
            oracle.x(qubit)
    oracle.cz(0, 1)
    for qubit, bit in enumerate(reversed(target)):
        if bit == "0":
            oracle.x(qubit)
    return oracle


TARGET = "10"  # Cambiar por 00, 01, 10 o 11.
oracle = phase_oracle_2q(TARGET)
show_circuit(oracle, f"Oráculo que marca |{TARGET}>")
'''
    ),
    markdown(
        r"""
El oráculo no aumenta todavía la probabilidad de la respuesta. Cambia

$$|x_*\rangle\longrightarrow-|x_*\rangle.$$

Ese signo es invisible si medimos inmediatamente, pero cambia cómo las amplitudes interfieren en el siguiente paso.
"""
    ),
    code(
        r'''
def diffuser_2q():
    """Inversión respecto del promedio, salvo una fase global irrelevante."""
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
show_circuit(diffuser, "Difusor de dos qubits")
'''
    ),
    code(
        r'''
def grover_search_2q(target):
    """Circuito completo de una iteración de Grover para cuatro opciones."""
    circuit = QuantumCircuit(2, name=f"Grover_{target}")
    for qubit in range(2):
        circuit.h(qubit)
    circuit.compose(phase_oracle_2q(target), inplace=True)
    circuit.compose(diffuser_2q(), inplace=True)
    return circuit


# Guardamos las tres etapas para observar lo que cambia.
initial = QuantumCircuit(2)
for qubit in range(2):
    initial.h(qubit)

after_oracle = initial.copy()
after_oracle.compose(phase_oracle_2q(TARGET), inplace=True)

grover = grover_search_2q(TARGET)

show_circuit(grover, f"Grover completo: buscar |{TARGET}>")
'''
    ),
    code(
        r'''
show_amplitudes(initial, "1) Superposición uniforme")
print()
show_amplitudes(after_oracle, "2) Después del oráculo: una fase cambió")
print()
show_amplitudes(grover, "3) Después del difusor: la respuesta fue amplificada")

counts_grover = simulate_counts(grover, shots=1000, seed=19)
show_counts(counts_grover, f"Grover: estado marcado |{TARGET}>", color="#57e7a6")
'''
    ),
    markdown(
        r"""
## El momento conceptual importante

- Antes del oráculo: cuatro amplitudes iguales.
- Después del oráculo: cuatro probabilidades iguales, pero una amplitud tiene signo opuesto.
- Después del difusor: la interferencia destructiva cancela las respuestas incorrectas y la interferencia constructiva amplifica la correcta.

La aceleración de Grover no proviene de “probar todas las respuestas y leerlas”. Proviene de diseñar una evolución que **cancele lo incorrecto antes de medir**.
"""
    ),
    markdown(
        r"""
## Reto para estudiantes

Cambiar solamente `MI_RESPUESTA` y volver a ejecutar la celda. Antes de mirar el resultado, predecir qué barra dominará.
"""
    ),
    code(
        r'''
MI_RESPUESTA = "01"  # Pruebe 00, 01, 10 o 11.

mi_circuito = grover_search_2q(MI_RESPUESTA)
mis_resultados = simulate_counts(mi_circuito, shots=1000, seed=23)

show_circuit(mi_circuito, f"Mi búsqueda: |{MI_RESPUESTA}>")
show_counts(mis_resultados, "Resultado del reto", color="#ffcc5c")
'''
    ),
    markdown(
        r"""
## De cuatro opciones a (N) opciones

Para una única solución entre (N=2^n) candidatas:

$$
\text{consultas clásicas}=O(N),
\qquad
\text{consultas de Grover}=O(\sqrt N).
$$

En cuatro opciones, la diferencia es pequeña; el objetivo es ver el mecanismo completo. La ventaja aparece al escalar, aunque los oráculos y las compuertas multicontroladas son costosos en computadores ruidosos actuales.

Grover es independiente de la plataforma física: el mismo circuito lógico puede compilarse para superconductores, iones o átomos neutros. Lo que cambia es cómo se implementan físicamente las compuertas, por ejemplo mediante interacciones de Rydberg.
"""
    ),
    markdown(
        r"""
# 5. Validación automática

Esta celda prueba los cuatro oráculos y las propiedades usadas durante el taller. Debe terminar con `TODAS LAS PRUEBAS PASARON`.
"""
    ),
    code(
        r'''
def validate_workshop():
    # Superposición de un qubit.
    p_one = probabilities_of(one_qubit)
    assert abs(p_one["0"] - 0.5) < 1e-10
    assert abs(p_one["1"] - 0.5) < 1e-10

    # Bell: sólo 00 y 11.
    p_bell = probabilities_of(bell)
    assert set(p_bell) == {"00", "11"}
    assert all(abs(value - 0.5) < 1e-10 for value in p_bell.values())

    # Grover debe amplificar exactamente cada objetivo de dos qubits.
    for target in ("00", "01", "10", "11"):
        probabilities = probabilities_of(grover_search_2q(target))
        assert set(probabilities) == {target}
        assert abs(probabilities[target] - 1.0) < 1e-10

    # Ejemplo de Shor usado en la introducción.
    assert multiplicative_order(2, 15) == 4
    assert {gcd(2**2 - 1, 15), gcd(2**2 + 1, 15)} == {3, 5}

    return True


assert validate_workshop()
print("TODAS LAS PRUEBAS PASARON ✓")
'''
    ),
    markdown(
        r"""
# Cierre

1. **La MOT entrega átomos fríos y controlables.**
2. **Los niveles atómicos codifican qubits y las interacciones producen compuertas.**
3. **Shor muestra el impacto potencial sobre problemas como la factorización.**
4. **Grover permite observar directamente cómo fase e interferencia realizan un cálculo.**

La lección más importante no es memorizar un circuito:

> Un algoritmo cuántico programa amplitudes y fases para que, al medir, la respuesta deseada sea la más probable.

## Si algo falla

- Ejecutar las celdas desde el principio; las funciones se definen progresivamente.
- Confirmar que el notebook usa el mismo Python donde está instalado Qiskit.
- No instalar `qiskit-aer` para este taller: no es necesario.
- No reemplazar el simulador local por hardware durante la sesión principal.
- Si el histograma gráfico no aparece, la versión textual contiene exactamente la misma información.

---

*Autor: Prof. Ariel Norambuena. Material preparado para Workshop Astro Physics.*
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
        "title": "Del átomo atrapado al algoritmo cuántico",
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(NOTEBOOK, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)
    print(f"Cells: {len(CELLS)}")


if __name__ == "__main__":
    main()
