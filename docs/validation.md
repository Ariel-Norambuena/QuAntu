# Verificaciones de esta preparación

Fecha local: **2 de noviembre de 2026**. El [entorno registrado](../validation/environment.json) documenta Python y las dependencias efectivamente usadas. La ejecución local usó Windows y Python 3.13.12 en un entorno virtual que comparte las bibliotecas científicas existentes; no equivale a un entorno aislado congelado.

## Resultados ejecutados

| Componente | Evidencia | Resultado y alcance |
| --- | --- | --- |
| Inventario, referencias y sintaxis | `python scripts/verify_repository.py` | Integridad de los 137 archivos importados, rutas locales, recursos LaTeX, fuentes Python y cuatro notebooks. |
| Exploradores Voigt | `python scripts/check_science.py` | 36 combinaciones de temperatura, anchura e isótopos; valores finitos, no negativos, normalizados, acuerdo entre interfaces y escalado térmico. |
| Matriz densidad Python | [Pruebas](../models/density-matrix/test_rb_d2.py), [registro](../validation/density-matrix-metrics.json) | Dos pruebas automatizadas, con 32 estados físicos, canales de decaimiento, drive cero y comparación rápida/directa en una malla común. |
| Comparación D2 contra MATLAB | [Fixture independiente](../tests/fixtures/matlab_density_matrix.json) | MATLAB R2025b Update 6 ejecutó funciones originales: 16 matrices y ocho espectros pequeños. Error máximo en rho: `7.79e-16`; en espectros: `9.97e-18`. |
| Sistemas abiertos | [Nueve pruebas](../models/open-quantum-systems/test_two_level.py) | Liouvilliana frente a ecuación directa, solución de Bloch, equilibrio térmico, decaimiento, dinámica, Doppler, QRT y espectro frente a Lorentziana. |
| Notebooks de absorción | [Registro de métricas](../validation/notebook-metrics.json) | Se ejecutaron las 15 celdas de código de los tres notebooks. MSE y MAE coinciden con los valores guardados dentro de `5.01e-7`. Sólo se suprimió la presentación de gráficos. |
| Taller Qiskit | `python education/qiskit/validate_notebook.py` | Las 12 celdas ejecutadas completaron las pruebas con Qiskit 2.6.1; simulación local sin credenciales. |
| Dashboard | Streamlit `AppTest` | La aplicación cargó sin excepciones y presentó dos controles deslizantes; esta comprobación no cubre toda interacción visual. |
| Interfaz Matplotlib | Backend Agg | Carga de datos y ejecución sin ventana interactiva; se mantiene pendiente una revisión manual completa de los controles. |
| Animación MOT | Tres fotogramas de 640 × 360 | Render a 3, 32 y 72 segundos con assets incluidos; no se regeneró el video completo. |
| Informe técnico | `latexmk -pdf` con shell escape desactivado | Las fuentes y la bibliografía compilaron correctamente en una carpeta de salida separada; el PDF histórico incluido no se reemplazó. |

La comprobación estacionaria D2 obtuvo error máximo de traza `5.6e-16`, hermiticidad `7.9e-16`, autovalor mínimo `-2.1e-17` y residuo `3.5e-15`. El autovalor negativo indicado es compatible con redondeo. Los valores completos y el alcance están en el registro JSON.

La prueba adicional independiente incluyó las cuatro polarizaciones de ambos isótopos con dephasing adicional, y controles térmicos y de suma del espectro OQS. La suite versionada cubre los casos enumerados en sus archivos de prueba; los controles exploratorios adicionales no se presentan como una nueva certificación general.

## Repetir las comprobaciones

Desde la raíz del repositorio:

```sh
python -m pip install -r requirements.txt
python scripts/validate.py --with-notebooks
python -m pip install -r education/qiskit/requirements.txt
python scripts/validate.py --with-qiskit
```

El comando sin opciones requiere sólo `requirements-core.txt`. Las opciones añaden la ejecución de notebooks y del taller; la validación siempre se detiene con código no cero ante un fallo. La configuración de [GitHub Actions](../.github/workflows/validate.yml) repite los controles principales en Python 3.11 y 3.13 y ejecuta el taller por separado. Su ejecución remota debe comprobarse después del primer push.

## Límites prácticos

La paridad D2 usa muestras y mallas pequeñas; no verifica convergencia de las mallas de producción. La reproducción de notebooks conserva los datos y calibraciones originales y no mide generalización ni adquisición propia. La regresión cuántica OQS reemplaza una rutina ausente y tiene controles analíticos, sin comparación completa con esa función histórica.

La versión en línea de Overleaf no pudo verificarse. No existe todavía un pipeline documentado para regenerar todos los CSV procesados desde los brutos. La calibración absoluta, las incertidumbres experimentales y la extensión Zeeman figuran en la [hoja de ruta](../ROADMAP.md).

Durante la ejecución de los notebooks apareció una advertencia de ajuste de layout de Matplotlib; no afectó las métricas. Streamlit emitió una advertencia de obsolescencia de `use_container_width`; la aplicación pasó la prueba en la versión registrada. Estos puntos no se interpretan como fallos numéricos.
