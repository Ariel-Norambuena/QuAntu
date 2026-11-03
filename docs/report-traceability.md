# Trazabilidad del reporte y los materiales

Este documento relaciona el reporte de espectroscopia de rubidio y sus materiales de apoyo con los archivos disponibles de QuAntü, proyecto «Neutral-atom-based quantum computing in Chile» (Anillo Temático ANID ATE250066).

La referencia documental de esta versión es la copia local de [Technical Progress Report](../reports/technical-progress/main.pdf), titulada *Development of Progressive Theoretical Models for the Rubidium Absorption Spectrum*, junto con [main.tex](../reports/technical-progress/main.tex), [density_matrix_model.tex](../reports/technical-progress/density_matrix_model.tex) y [references.bib](../reports/technical-progress/references.bib).

El reporte declara a Alexis R. Legón, Pontificia Universidad Católica de Chile, QuAntü Research Group, y un período de mayo–julio de 2026. El [proyecto Overleaf proporcionado](https://www.overleaf.com/project/6a679a4b0c07d40f5ac1dd88) no pudo leerse durante la preparación. Por ello, esta versión conserva la copia local y no afirma que esté sincronizada con Overleaf ni que refleje su revisión más reciente.

## Correspondencia científica

| Declaración o componente | Archivos del repositorio | Evidencia y límite |
| --- | --- | --- |
| Objetivos y evolución de modelos | [Fuente principal del reporte](../reports/technical-progress/main.tex) | Describe objetivos, actividades, resultados y trabajo futuro. |
| Gaussiano fenomenológico | [Model_1.ipynb](../notebooks/absorption/Model_1.ipynb), [figura 1](../reports/technical-progress/figure_1.png) | Código y salidas históricas; MSE 0.006772, MAE 0.054760. |
| Gaussiano con mezcla isotópica | [Model_2.ipynb](../notebooks/absorption/Model_2.ipynb), [figura 2](../reports/technical-progress/figure_2.png) | Código y salidas históricas; MSE 0.004758, MAE 0.052138. |
| Susceptibilidad con promedio Doppler | [Model_3.ipynb](../notebooks/absorption/Model_3.ipynb), [figura 3](../reports/technical-progress/figure_3.png) | Código y salidas históricas; MSE 0.004004, MAE 0.048501. |
| Datos reconstruidos para notebooks | [Data_Rb_Gas.csv](../notebooks/absorption/Data_Rb_Gas.csv) | El reporte atribuye el benchmark a Ma et al. (2017); no equivale a adquisición propia. |
| Derivación de matriz densidad | [Desarrollo LaTeX](../reports/technical-progress/density_matrix_model.tex) | Detalla estados, dipolos, Lindblad, observable, calibraciones y supuestos. |
| Solver estacionario rápido | [Ejecutable Python](../models/density-matrix/run_fast.py), [módulo común](../models/density-matrix/rb_d2.py) y [original MATLAB](../models/density-matrix/Rb_D2_density_matrix_fast_COHERENCE_ABS.m) | Versión Python para ejecutar; el original y las figuras históricas se conservan en [su directorio](../models/density-matrix/). |
| Solver directo alternativo | [Ejecutable Python](../models/density-matrix/run_direct.py) y [original MATLAB](../models/density-matrix/Rb_D2_density_matrix_slow_direct.m) | Formulación alternativa para evaluar diferencias de interpolación y convergencia. |
| Overlay experimental MATLAB | [DATA_ABS_Rb.csv](../models/density-matrix/DATA_ABS_Rb.csv) | Input de dos columnas; su origen exacto y transformaciones no están registrados en un manifiesto individual. No es idéntico a Data_Rb_Gas.csv. |
| Comparación rápida/directa y métricas comunes | [Pruebas propuestas en la derivación](../reports/technical-progress/density_matrix_model.tex) y [trabajo futuro](../reports/technical-progress/main.tex) | Validación sistemática y MSE/MAE comparables de matriz densidad pendientes. |
| Otros espectros bibliográficos | [Extracciones conservadas](../data/raw/), [tablas procesadas](../data/processed/) y [artículos locales](../references/papers/) | Disponibilidad de archivos; no acredita que cada dataset se haya validado con el solver. |
| Datos atómicos | [Compilaciones de Steck](../references/atomic-data/), [bibliografía](../reports/technical-progress/references.bib) | Fuentes de constantes y formalismo angular; se conservan distintas revisiones locales. |
| Escala absoluta y extensiones experimentales | [Trabajo futuro del reporte](../reports/technical-progress/main.tex) | Densidad, geometría, intensidad y relajaciones medidas, incertidumbres y término Zeeman son tareas pendientes. |

Las cifras de los tres primeros modelos se conservaron de las salidas históricas y además se reprodujeron ejecutando los notebooks durante esta preparación; véase el [registro de reproducción](../validation/notebook-metrics.json). La sección de resultados del reporte evita asignar métricas a la matriz densidad hasta disponer de un protocolo común. Véanse los [supuestos científicos](science.md) y la [procedencia de los datos](data-provenance.md).

## Materiales adicionales de QuAntü

Estos elementos forman parte de la carpeta de trabajo, aunque no son resultados de espectroscopia cuantitativa establecidos por el reporte.

| Área | Ubicación | Función documental |
| --- | --- | --- |
| Exploración interactiva | [models/interactive](../models/interactive/) | Scripts Python y datos locales para visualizar modelos. |
| Copia histórica del grupo teórico | [archive/theoretical-group](../archive/theoretical-group/) | Preserva la carpeta original separada de los puntos de entrada principales en Python. |
| Taller Qiskit | [education/qiskit](../education/qiskit/README.md) | Notebook, requisitos, constructor y validador del taller. Conserva su propia información de citación. |
| Material MOT | [education/mot](../education/mot/README.md) | Video, generador, ecuaciones y vistas previas educativas. |
| Clases | [education/lectures](../education/lectures/) | Presentación de modelamiento dinámico. |
| Sistemas cuánticos abiertos | [Modelo Python](../models/open-quantum-systems/two_level.py) | Implementación autónoma de dos niveles; la [documentación OQS](open-quantum-systems.md) explica su procedencia y la rutina QRT nueva. Los materiales originales de reuniones se retiraron del árbol publicado. |
| Divulgación STEM | [outreach/quantu-stem](../outreach/quantu-stem/) | Documento del evento y presentación de Alonso Recabarren. |
| Teoría atómica de consulta | [references/rubidium-theory](../references/rubidium-theory/) | Documentos sobre ambos isótopos. |
| Celda y materiales | [references/hardware](../references/hardware/) | Documentación de celda Thorlabs y vidrio Borofloat; no acredita adquisición ni caracterización del montaje. |

## Conservación y revisión

El [inventario](inventory.csv) relaciona rutas originales con rutas del repositorio e incluye tamaños y hashes. Los cambios de portabilidad, si los hay, deben reflejarse en sus campos correspondientes. Este mapa permite revisar la incorporación de materiales sin confundir su organización con una validación física nueva.

Los 11 materiales de reuniones se retiraron del árbol publicado por solicitud del responsable del proyecto; sus originales permanecen en la carpeta de trabajo. La colección mantiene 126 archivos importados en su inventario.

La publicación pública no atribuye una licencia abierta global a artículos, figuras, documentos de fabricantes ni presentaciones de terceros. Se conservan las atribuciones y condiciones de sus respectivos titulares.
