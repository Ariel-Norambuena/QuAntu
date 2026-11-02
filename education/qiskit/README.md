# Taller Qiskit: del átomo atrapado al algoritmo cuántico

Notebook autónomo para la sección práctica de un taller introductorio de una
hora sobre computación cuántica con átomos neutros.

**Evento:** Workshop Astro Physics  
**Autor y relator:** Prof. Ariel Norambuena — Universidad Técnica Federico
Santa María · QSTATE · QuAntü

## Archivo para entregar

- `Taller_Qiskit_Atomos_Neutros_1h.ipynb`

El notebook conecta una introducción conceptual a Shor con una implementación
completa y manual de Grover para dos qubits. También incluye un circuito de un
qubit, un estado de Bell, un reto editable y pruebas automáticas.

## Dependencia obligatoria

```text
qiskit>=1.4,<3
```

No necesita:

- `qiskit-aer`
- `qiskit-algorithms`
- `qiskit-ibm-runtime`
- Matplotlib
- pylatexenc
- credenciales, red o acceso a hardware

La simulación usa `qiskit.quantum_info.Statevector`, parte del núcleo de Qiskit.
Los shots se generan con el módulo `random` de Python y una semilla fija.

La ejecución completa fue validada con Qiskit 1.4.5 y Qiskit 2.5.1.

## Preparación del instructor

1. Abrir el notebook con el mismo entorno donde está instalado Qiskit.
2. Ejecutar **Restart Kernel and Run All**.
3. Confirmar que la última celda imprime `TODAS LAS PRUEBAS PASARON`.
4. Durante el taller, pedir a los estudiantes que cambien únicamente
   `MI_RESPUESTA` en el reto.

Se recomienda usar simulación local durante la sesión. El acceso a hardware
introduce cuentas, colas, cambios de API y ruido que distraen del objetivo de una
primera práctica.

## Por qué se reemplazó el notebook de 2023

El material anterior dependía de APIs eliminadas o separadas del paquete base,
incluyendo `from qiskit import Aer`, `qiskit.providers.aer`, `qiskit.ignis` y
mitigación basada en Ignis. También guardaba widgets y salidas que aumentaban su
tamaño a más de 500 KB. Esta versión contiene sólo APIs estables del núcleo y no
guarda resultados precomputados.

## Regeneración

El notebook se genera de forma determinista mediante:

```text
python build_workshop_notebook.py
```

Puede validarse sin instalar Jupyter o nbconvert:

```text
python validate_notebook.py
```

## Referencias oficiales

- Grover: <https://qiskit.qotlabs.org/docs/tutorials/grovers-algorithm>
- Shor: <https://quantum.cloud.ibm.com/docs/en/tutorials/shors-algorithm>

## Cómo citar

La información bibliográfica está disponible en `CITATION.cff`. En GitHub,
puede utilizarse directamente la opción **Cite this repository**.
