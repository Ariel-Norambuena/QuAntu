# Reproducibilidad

Los comandos siguientes se ejecutan desde la raíz del repositorio. Los rangos
de `requirements*.txt` describen compatibilidad prevista; **no son archivos de
bloqueo de versiones**. Para comparar corridas, registrar sistema operativo,
versión de Python/MATLAB, parámetros y dependencias exactas.

## Entorno Python

Se recomienda Python 3.11 o posterior en un entorno virtual. En PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip freeze > environment-local.txt
python scripts/check_science.py
```

En Linux/macOS, la activación es `source .venv/bin/activate`; los demás comandos
son iguales. `environment-local.txt` registra la instalación local y no implica
que ese entorno haya sido comprobado en todas las plataformas.

`check_science.py` comprueba sintaxis Python y de celdas de los cuatro notebooks,
integridad de los CSV utilizados por modelos/notebooks y 36 combinaciones del
modelo Voigt. Ejecuta las funciones científicas existentes sin importar las
interfaces. Verifica finitud, positividad, normalización, acuerdo entre ambas
interfaces y dependencia térmica de la anchura. No valida el ajuste a datos ni
los cálculos completos de matriz densidad.

## Absorción con Python

Interfaz local con Matplotlib:

```powershell
python models/interactive/mod_interactivo.py
```

Dashboard opcional:

```powershell
python -m pip install -r requirements-dashboard.txt
python -m streamlit run models/interactive/dashboard_rb.py
```

Ambas interfaces cargan `Data_Rb_Gas.csv` junto al script y fallan explícitamente
si falta. El modelo agrupa transiciones hiperfinas en cuatro perfiles efectivos;
no sustituye el cálculo completo de subniveles de matriz densidad. En ambos exploradores `gamma_MHz` es HWHM Lorentziano; la FWHM es el doble. El valor inicial histórico se conserva y está rotulado con esta convención.

Los notebooks históricos conservan rutas relativas y sus salidas originales.
Abrirlos con su propia carpeta como directorio de trabajo:

```powershell
python -m jupyterlab --notebook-dir=notebooks/absorption
```

Ejecutar las celdas en orden. Su sintaxis se comprueba automáticamente; la
ejecución completa requiere las dependencias de `requirements.txt`. Los datos
digitalizados y las figuras de publicaciones requieren consultar su procedencia
en la documentación de datos.

## Matriz densidad con Python

La implementación principal es `models/density-matrix/rb_d2.py`, con NumPy y
SciPy sparse. Incluye todos los subniveles hiperfinos y Zeeman de ambos isótopos
(dimensiones 36 y 24), símbolos Wigner 3j/6j mediante Racah, Hamiltoniano,
emisión espontánea con branching normalizado, mezcla del estado fundamental y
dephasing opcional. Conserva la vectorización por columnas y los factores
`2*pi` de las fuentes MATLAB. No necesita MATLAB, GPU ni Parallel Toolbox.

Para comprobar ejecución con mallas deliberadamente gruesas:

```powershell
python -m pip install -r requirements-core.txt
python models/density-matrix/run_fast.py --quick
python models/density-matrix/run_direct.py --quick
python scripts/check_density_matrix.py
python -m unittest discover -s models/density-matrix -p 'test_*.py'
```

`--quick` usa siete frecuencias, cinco clases Doppler y, en fast, un paso de
respuesta de 250 MHz. **No resuelve resonancias estrechas y no es un espectro
convergido**. Sin `--quick`, fast usa 1001 frecuencias, 1001 clases Doppler y
paso 0.5 MHz; direct usa 301 frecuencias y 301 clases. La segunda estrategia
resuelve cada par frecuencia/velocidad y puede resultar considerablemente más
lenta. Los valores predeterminados reproducen diferencias de los scripts
originales: fast usa polarización `pi` y calibración horizontal activa;
direct usa `linear_x` y calibración desactivada. Para comparar ambos métodos,
igualar explícitamente estos parámetros:

```powershell
python models/density-matrix/run_fast.py --nomega 101 --nv 101 --response-step 1 --polarization pi --no-axis-calibration
python models/density-matrix/run_direct.py --nomega 101 --nv 101 --polarization pi --no-axis-calibration
```

Estos comandos sólo fijan un ejemplo común; también debe comprobarse
convergencia incrementando las mallas. `--help` enumera temperatura, Rabi,
anchuras, abundancia, promedio de polarizaciones y conversión Beer–Lambert o
lineal. Las salidas `spectrum.csv`, `metadata.json` y figuras PNG/SVG/PDF se
guardan en una carpeta nueva bajo `results/density-matrix/`. `--output` permite
elegir una carpeta nueva y rechaza una existente. `--no-plot` omite figuras.

La absorción máxima se escala por defecto a 0.42; la calibración afín opcional
del eje usa parámetros empíricos (`aCal=1.0434`, `bCal=0.0781 GHz`) y sólo cambia
la representación horizontal, no el Hamiltoniano. Las figuras no son una
predicción absoluta de amplitud independiente de esa escala. Los archivos de
referencia se buscan junto a los scripts.

### Verificación de la traducción

`check_density_matrix.py` comprueba 32 estados estacionarios para ambos isótopos
y las cuatro polarizaciones: traza, Hermiticidad, positividad y residual del
generador original. Comprueba además branching, conservación de traza, límite
sin drive, descomposición Beer–Lambert y coincidencia fast/direct cuando los
puntos consultados pertenecen a la malla de respuesta.

La fixture `tests/fixtures/matlab_density_matrix.json` se generó ejecutando
las funciones MATLAB originales con MATLAB R2025b Update 6: 16 matrices de
densidad y ocho espectros pequeños (fast/direct, ambos isótopos, `pi` y
`linear_x`). Registra las huellas SHA-256 de ambos archivos fuente. La
comparación Python/MATLAB obtuvo errores absolutos máximos de `7.8e-16` en las
matrices y `1.0e-17` en espectros; el registro completo está en
`validation/density-matrix-metrics.json`. Los tests requieren la fixture y no
requieren MATLAB.

Para regenerarla opcionalmente, pasar las dos fuentes MATLAB originales al
harness; se extraen sus funciones locales sin ejecutar la malla grande inicial:

```powershell
python scripts/generate_matlab_fixture.py --fast-source archive/theoretical-group/Rb_D2_density_matrix_fast_COHERENCE_ABS.m --direct-source archive/theoretical-group/Rb_D2_density_matrix_slow_direct.m
```

El harness y sus preferencias temporales quedan bajo `results/`; el comando
necesita una instalación MATLAB con licencia funcional. Las fuentes MATLAB
se conservan como referencia histórica. La paridad de muestras pequeñas no
demuestra convergencia de mallas de producción ni validación experimental.

## Taller Qiskit

```powershell
python -m pip install -r education/qiskit/requirements.txt
python education/qiskit/validate_notebook.py
```

El validador ejecuta todas las celdas sin Jupyter. El taller usa Statevector del
núcleo de Qiskit; no requiere credenciales, Aer o hardware. El README original
registra comprobaciones previas con Qiskit 1.4.5 y 2.5.1; esta preparación también ejecutó las 12 celdas con Qiskit 2.6.1 y completó todas las pruebas.

## Animación MOT

```powershell
python -m pip install -r requirements-video.txt
python education/mot/render_mot_workshop.py --stills results/mot-preview --times 3 32 72 --width 640 --height 360
```

El renderer usa los PNG de ecuaciones incluidos. Prioriza las fuentes de
Windows originales y busca alternativas comunes en Linux/macOS; como último
recurso usa la fuente predeterminada de Pillow. La tipografía puede variar por
sistema. Para regenerar las ecuaciones se requieren además `pdflatex`,
`pdftocairo` y los paquetes LaTeX utilizados por el script:

```powershell
python education/mot/make_latex_assets.py
python education/mot/render_mot_workshop.py --output results/MOT_Rb87_workshop_1080p.mp4
```

La animación es pedagógica y sus escalas representativas no constituyen una
medición de una MOT construida por el proyecto.

## Procedencia OQS y límites conocidos

Los materiales históricos de reuniones se retiraron del árbol publicado.
La [implementación Python OQS](open-quantum-systems.md) permanece como modelo
autónomo y ejecutable con sus pruebas. La referencia histórica de fluorescencia
invocaba `CorrelationTRG`, función ausente del material recibido; Python incorpora
una rutina QRT explícita verificada mediante controles analíticos. Las ecuaciones
y convenciones se documentan sin depender de los archivos retirados.

No se recibió un script que regenere automáticamente todos los CSV procesados
desde los datos brutos. Los archivos existentes documentan el trabajo recibido;
no implican trazabilidad completa del procesamiento ni validación experimental.

## Reproducción automática y registro

`python scripts/validate.py --with-notebooks --with-qiskit` ejecuta las comprobaciones estructurales, Voigt, D2, OQS y ambos grupos de notebooks. Las dependencias opcionales deben estar instaladas. Véanse los [resultados y límites registrados](validation.md) y el [procedimiento de publicación](publishing.md).
