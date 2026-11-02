# Alcance científico

QuAntü desarrolla modelos progresivos del espectro de absorción D2 de vapor térmico de rubidio natural. Esta descripción se basa en la copia local del [reporte técnico](../reports/technical-progress/main.pdf), sus [fuentes LaTeX](../reports/technical-progress/main.tex) y el [desarrollo de matriz densidad](../reports/technical-progress/density_matrix_model.tex). El reporte declara como autor a Alexis R. Legón, Pontificia Universidad Católica de Chile, QuAntü Research Group, y cubre mayo–julio de 2026. Esa atribución corresponde al reporte; no establece por sí sola la autoría de todos los materiales del repositorio.

## Modelos progresivos

| Etapa | Descripción | Implementación |
| --- | --- | --- |
| 1 | Suma de perfiles gaussianos con anchura Doppler común y centros y amplitudes efectivos. | [Model_1.ipynb](../notebooks/absorption/Model_1.ipynb) |
| 2 | Modelo gaussiano con contribuciones de los dos isótopos y abundancia natural. Conserva correcciones efectivas de posiciones y pesos. | [Model_2.ipynb](../notebooks/absorption/Model_2.ipynb) |
| 3 | Respuesta de susceptibilidad óptica con ensanchamiento homogéneo y promedio térmico Doppler. El notebook conserva parámetros y normalizaciones efectivos. | [Model_3.ipynb](../notebooks/absorption/Model_3.ipynb) |
| 4 | Matriz densidad estacionaria con estructura hiperfina, subniveles magnéticos, acoplamiento coherente y relajación Lindblad. | [Módulo Python](../models/density-matrix/rb_d2.py), [ejecución rápida](../models/density-matrix/run_fast.py) y [ejecución directa](../models/density-matrix/run_direct.py) |

Las etapas ayudan a identificar qué mecanismos explican la envolvente Doppler, los cuatro grupos de resonancias, las coherencias y el bombeo óptico. Una mayor complejidad física no implica automáticamente menor error: el modelo de matriz densidad todavía no tiene métricas obtenidas bajo el mismo protocolo residual que las primeras tres etapas.

## Resultados históricos conservados

Las siguientes cifras se encuentran en las salidas guardadas de los notebooks y corresponden, con redondeo, a la tabla del reporte. Durante la preparación se ejecutaron de nuevo todas las celdas de los tres notebooks y se reprodujeron estas cifras dentro de su precisión de redondeo; el [registro numérico](../validation/notebook-metrics.json) conserva las versiones y huellas de los archivos. La reproducción usa los mismos datos y no constituye una validación experimental independiente.

| Modelo | MSE guardado | MAE guardado |
| --- | ---: | ---: |
| Gaussiano | 0.006772 | 0.054760 |
| Gaussiano isotópico | 0.004758 | 0.052138 |
| Susceptibilidad | 0.004004 | 0.048501 |
| Matriz densidad | Pendiente | Pendiente |

Los notebooks calculan los residuos después de interpolar la curva teórica en la grilla experimental. Algunas figuras multiplican el residuo por 100 para visualizarlo; ese factor gráfico no se aplica a MSE y MAE. Las métricas usan las escalas y calibraciones de cada notebook y no representan una medición absoluta del coeficiente de absorción.

## Cadena del modelo de matriz densidad

```mermaid
flowchart LR
    A[Datos atomicos e hiperfinos] --> B[Base F y mF]
    B --> C[Hamiltoniano y dipolos]
    C --> D[Lindblad estacionario]
    D --> E[Coherencia optica]
    E --> F[Promedio Doppler]
    F --> G[Mezcla isotopica]
    G --> H[Escala optica y Beer-Lambert]
```

La transición retenida es $5^2S_{1/2}\rightarrow5^2P_{3/2}$, cerca de 780 nm. Cada isótopo se resuelve por separado.

| Isótopo | Espín nuclear | Estados fundamentales | Estados excitados | Dimensión de Hilbert | Dimensión de Liouville |
| --- | ---: | ---: | ---: | ---: | ---: |
| $^{85}\mathrm{Rb}$ | $5/2$ | 12 | 24 | 36 | 1296 |
| $^{87}\mathrm{Rb}$ | $3/2$ | 8 | 16 | 24 | 576 |

La base contiene todos los $m_F$ de los manifolds D2 para calcular reglas de selección, bombeo y branching de emisión espontánea. El Hamiltoniano actual no incorpora energía Zeeman: los subniveles de un mismo $F$ permanecen degenerados. Resolver explícitamente $m_F$ no equivale a modelar un campo magnético aplicado.

La matriz estacionaria satisface $\mathcal{L}(x)\rho_{\mathrm{ss}}(x)=0$ y $\operatorname{Tr}\rho_{\mathrm{ss}}=1$. La observable de absorción procede de la parte imaginaria de las coherencias ópticas ponderadas por los dipolos, no de la población excitada total. Algunos comentarios históricos del código mencionan población excitada; la implementación y la derivación detallada usan coherencia óptica.

El solver rápido aprovecha la dependencia afín de la Liouvilliana con el detuning: calcula una respuesta estacionaria en una grilla, interpola y realiza el promedio Doppler. El solver directo conserva una formulación alternativa para comparar la solución sobre detuning y velocidad. Las implementaciones Python constituyen la vía de ejecución del repositorio. Los originales [MATLAB rápido](../models/density-matrix/Rb_D2_density_matrix_fast_COHERENCE_ABS.m) y [MATLAB directo](../models/density-matrix/Rb_D2_density_matrix_slow_direct.m) se preservan como respaldo y referencia de la derivación histórica del reporte.

## Parámetros predeterminados y calibraciones

Estos valores describen el script rápido histórico que fundamenta el reporte; no son parámetros medidos de un montaje completo. Consulte las opciones del ejecutable Python para su grilla de ejecución y sus parámetros efectivos.

| Parámetro | Valor |
| --- | --- |
| Temperatura | 293 K |
| Fracciones $^{85}\mathrm{Rb}$ / $^{87}\mathrm{Rb}$ | 0.72 / 0.28 |
| Anchura natural FWHM | 6.0666 MHz, común a ambos isótopos |
| Escala efectiva de Rabi | 10.0 MHz antes de factores angulares |
| Mezcla del estado fundamental | 0.05 MHz |
| Dephasing óptico adicional | 0 MHz |
| Polarización | $\pi$ |
| Grilla del láser | 1001 puntos entre −6 y +6 GHz |
| Grilla de velocidades | 1001 puntos; truncamiento de $\pm4\sigma_D$ |
| Espaciado de respuesta estacionaria | 0.5 MHz |
| Absorción máxima objetivo | 0.42 |
| Transformación de eje para comparación | $\Omega_{\mathrm{plot}}=1.0434\,\Omega_{\mathrm{theory}}+0.0781\,\mathrm{GHz}$ |

La convención teórica es $\Omega=\nu_{85,\mathrm{D2\,cog}}-\nu_L$, en frecuencias ordinarias. Aumentar la frecuencia del láser desplaza $\Omega$ en sentido negativo. El origen atómico y la transformación empírica del eje deben tratarse por separado.

La mezcla se realiza a nivel de profundidad óptica y la absorción se construye mediante $A=1-\exp(-\mathrm{OD})$. Un factor global fija la absorción máxima en 0.42. Las curvas isotópicas dibujadas son una descomposición aditiva de la absorción total; no representan dos pérdidas de transmisión independientes que puedan sumarse físicamente.

El modelo no predice todavía un coeficiente absoluto en unidades SI: la magnitud reducida del dipolo, la densidad de vapor, la longitud de celda y la división por el campo necesaria para una susceptibilidad absoluta no están incorporadas en esa normalización. La escala de Rabi predeterminada puede producir saturación y bombeo óptico; no debe describirse automáticamente como el límite de sonda débil.

## Validación pendiente y extensiones

El repositorio conserva implementaciones y figuras existentes. La disponibilidad de ambos solvers no demuestra por sí sola una comparación numérica completa. El resumen del reporte alude a verificaciones frente a la formulación directa, mientras que la sección de trabajo futuro todavía propone benchmarking y convergencia; faltan resultados sistemáticos documentados que cierren ese alcance.

1. Comprobar traza, hermiticidad, positividad y residuo de la ecuación estacionaria en detunings representativos.
2. Verificar branching normalizado, reglas de selección y centros de transición antes de calibrar el eje.
3. Comparar solvers rápido y directo con parámetros y grillas comunes.
4. Cuantificar convergencia respecto a espaciado de respuesta, grilla de velocidades y truncamiento Doppler.
5. Explorar drive cero y convergencia a respuesta lineal, separando saturación y bombeo.
6. Calcular MSE y MAE de matriz densidad con el mismo dataset y protocolo que los demás modelos.
7. Reemplazar escalas y relajaciones efectivas por intensidad, geometría, densidad, longitud y tasas medidas.
8. Incorporar términos Zeeman, ensanchamiento colisional e incertidumbres cuando existan parámetros experimentales suficientes.

El cálculo D2 es estacionario, monomodo y Markoviano; considera sólo D2 y clases de velocidad unidimensionales independientes. No simula escaneos temporales, pulsos, difusión, retroceso ni colisiones que cambien la velocidad. El [ejemplo Python de dos niveles](open-quantum-systems.md) cubre por separado dinámica temporal y fluorescencia de un sistema idealizado; no sustituye un modelo temporal completo de rubidio. Los materiales de [MOT](../education/mot/README.md), [Qiskit](../education/qiskit/README.md), reuniones y divulgación amplían el contexto formativo; su presencia no acredita una MOT experimental operativa ni experimentos de computación cuántica realizados en hardware.

Consulte la [trazabilidad del reporte](report-traceability.md), la [procedencia de datos](data-provenance.md) y la [bibliografía del reporte](../reports/technical-progress/references.bib).

## Convención de anchuras en los exploradores Voigt

En las interfaces históricas, `gamma_MHz` entra en el perfil Voigt como semiancho Lorentziano a media altura (HWHM); su FWHM es `2*gamma_MHz`. Se conserva el valor inicial histórico de 6 MHz para reproducir las curvas. En el modelo de matriz densidad, `linewidth=6.0666 MHz` representa FWHM: los parámetros no se deben igualar numéricamente sin convertir la convención. Los controles de las interfaces identifican explícitamente HWHM.
