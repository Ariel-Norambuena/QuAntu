# Hoja de ruta científica

Esta hoja de ruta reúne hitos de los componentes actualmente versionados de QuAntü (ATE250066). El proyecto integra los grupos de algoritmos, experimental y teórico; las tareas siguientes proceden de la revisión del informe y de los modelos y datos disponibles. Son trabajo pendiente, salvo que se indique evidencia de ejecución en la documentación de validación.

| Prioridad | Hito | Criterio de término |
| --- | --- | --- |
| Alta | Paridad MATLAB–Python | Comparar observables con los mismos parámetros, mallas y tolerancias; registrar discrepancias y coste |
| Alta | Convergencia del cálculo D2 | Barridos de malla espectral, Doppler e interpolación con tolerancias justificadas |
| Alta | Validación estacionaria | Residuo del Liouvilliano, traza, hermiticidad y positividad por isótopo y régimen |
| Alta | Comparación rápida/directa | Un conjunto común de desintonías y parámetros, con error y tiempos documentados |
| Alta | Pipeline de datos | Transformación ejecutable de cada conjunto bruto a su versión procesada, con unidades y procedencia |
| Media | Evaluación común de ajustes | Métricas de todos los modelos sobre los mismos datos y tratamiento de incertidumbre |
| Media | Calibración absoluta | Densidad de vapor, longitud de celda, dipolo y campo óptico físicamente calibrados |
| Media | Extensión magnética | Hamiltoniano Zeeman, campo y definición del eje de cuantización documentados |
| Media | Entorno reproducible | Congelar dependencias después de validar el flujo completo de cada componente |
| Media | Versiones citables | Acordar autores, licencia por componente y versión estable antes de publicar un release |

La animación MOT y los circuitos Qiskit son recursos docentes. Sus ilustraciones y simulaciones no acreditan la construcción ni la operación de un experimento del proyecto.
