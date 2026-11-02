# Mapa de la colección QuAntü

La importación inicial conserva **137 archivos** de la carpeta de trabajo. El
[inventario](inventory.csv) registra cada ruta original, su ruta en el repositorio,
el tamaño actual, el SHA256 actual y el SHA256 de origen. La columna
`modified_for_portability` identifica los cambios realizados para ejecutar los
materiales desde su nueva ubicación. Los documentos y herramientas de organización
añadidos al repositorio se suman a estos 137 archivos.

| Ruta | Archivos importados | Contenido y procedencia |
|---|---:|---|
| [models/density-matrix](../models/density-matrix/) | 12 | `Codes Absorption Spectrum Rb Vapor`: modelos MATLAB, tablas y espectros guardados. |
| [models/interactive](../models/interactive/) | 3 | `Experimental spectrum DATA/Modelo interactivo`: modelo Python, dashboard y tabla de transiciones. |
| [archive/theoretical-group](../archive/theoretical-group/) | 12 | `Codes Thoretical Group`: copia histórica y variantes de resultados. |
| [data/raw](../data/raw/) | 16 | `Data_BRUTA`: imágenes y CSV de referencia de la literatura. |
| [data/processed](../data/processed/) | 10 | `DATA_PROCESADA`: tablas procesadas de absorción. |
| [notebooks/absorption](../notebooks/absorption/) | 6 | `Codigo del Paper J. Ma 2017 Scientific Reports`: tres notebooks, tabla y presentación en dos formatos. |
| [references/papers](../references/papers/) | 8 | Artículos y datos atómicos consultados. |
| [references/atomic-data](../references/atomic-data/) | 2 | `Steck Notes`: tablas de datos de rubidio. |
| [references/hardware](../references/hardware/) | 2 | `Rb Cell Thorlabs`: documentación Thorlabs y SCHOTT. |
| [references/rubidium-theory](../references/rubidium-theory/) | 2 | `Theory of Rubidium atoms`: documentos teóricos de ambos isótopos. |
| [reports/technical-progress](../reports/technical-progress/) | 7 | `Technical_Progress_Report`: LaTeX, bibliografía, tres figuras y PDF existente. |
| [education/qiskit](../education/qiskit/) | 7 | Snapshot del taller Qiskit, incluido su archivo `.gitignore`. |
| [education/mot](../education/mot/) | 36 | Fuentes y video MOT, ecuaciones renderizadas y fotogramas de control. |
| [education/lectures](../education/lectures/) | 1 | Presentación de modelado dinámico de Ariel Norambuena. |
| [meetings/kickoff](../meetings/kickoff/) | 2 | Presentaciones general y técnica de la reunión inicial. |
| [meetings/2026-03-13-sas](../meetings/2026-03-13-sas/) | 1 | Presentación SAS. |
| [meetings/2026-04-10-oqs](../meetings/2026-04-10-oqs/) | 7 | Presentación OQS y seis archivos MATLAB. |
| [meetings/questions](../meetings/questions/) | 1 | Preguntas de teoría SAS. |
| [outreach/quantu-stem](../outreach/quantu-stem/) | 2 | Documento del evento y presentación de Alonso Recabarren. |

## Duplicados y versiones preservadas

En la colección de origen, ocho de los doce archivos de las dos carpetas de
espectros eran idénticos por SHA256: los dos programas MATLAB, los dos CSV y las
cuatro exportaciones de `Rb_absorption_spectrum_slow_direct`. Las cuatro
exportaciones de `Rb_absorption_spectrum` difieren entre carpetas y se conservan
como versiones distintas. `models/density-matrix/` es la entrada principal;
`archive/theoretical-group/` conserva la segunda colección para trazabilidad.

`Data_Rb_Gas.csv` tenía el mismo contenido en las dos carpetas MATLAB, los
notebooks de absorción y el modelo interactivo. Las copias se conservan junto a
sus consumidores. Los PDF Steck de `references/papers/` también tienen copias
idénticas en `references/atomic-data/`. No se eliminaron materiales por compartir
nombre; el inventario permite comparar los hashes de origen y actuales.

## Taller Qiskit e historia Git

El taller provenía de un repositorio Git anidado con origen
[Ariel-Norambuena/neutral-atoms-qiskit-workshop](https://github.com/Ariel-Norambuena/neutral-atoms-qiskit-workshop).
Se importa como **snapshot de archivos ordinarios** en `education/qiskit/`, con
su README y su cita originales. Este repositorio no contiene su directorio
`.git`, no registra un submódulo y no incorpora su historial de commits. El
repositorio y los archivos originales permanecen en la carpeta de trabajo.

## Exclusiones

La carpeta original `tmp/` contenía 91 imágenes renderizadas y extracciones de
texto usadas para revisar PDF, con 21,029,968 bytes. No forma parte de la
importación y no se borró de la carpeta de trabajo. También se excluyeron los
34 archivos internos del Git anidado, con 47,315 bytes. Las figuras científicas,
el PDF del reporte, los fotogramas de control y los recursos de la animación
sí están incluidos.

Los resultados de nuevas ejecuciones deben guardarse en `results/generated/`;
esa ubicación, los entornos y las cachés están excluidos mediante `.gitignore`.
El alcance de la atribución y los materiales externos se documentan en
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Comprobar la importación

Desde la raíz del repositorio:

```sh
python scripts/verify_repository.py
```

La herramienta usa sólo la biblioteca estándar de Python. Verifica los 137
registros, tamaños y hashes actuales, unicidad y seguridad de rutas, recursos
LaTeX, enlaces locales Markdown, sintaxis Python y las celdas de código de los
notebooks. No ejecuta los modelos, no recompila el PDF ni consulta enlaces
externos. `source_sha256` conserva la huella registrada en la importación; la
comprobación portable no necesita acceso a la carpeta original.
