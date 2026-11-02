# Ejemplos de sistemas cuánticos abiertos en Python

El módulo [two_level.py](../models/open-quantum-systems/two_level.py) implementa el sistema de dos niveles de la reunión del 10 de abril de 2026. Incluye Liouvilliana, estado estacionario, dinámica, barrido de detuning con promedio Doppler y espectro de fluorescencia por regresión cuántica. Usa NumPy, SciPy y Matplotlib; no requiere MATLAB ni QuTiP.

## Convenciones y correspondencia

La base es `(excitado, fundamental)`, $\hbar=1$, $\sigma_+=|e\rangle\langle g|$ y $\sigma_-=|g\rangle\langle e|$. El Hamiltoniano conserva la convención original:

$$
H=-\frac{\delta}{2}\sigma_z-\frac{\Omega}{2}\sigma_x.
$$

La ecuación maestra es

$$
\dot\rho=-i[H,\rho]+\gamma(n_{\mathrm{th}}+1)\mathcal{D}[\sigma_-]\rho
+\gamma n_{\mathrm{th}}\mathcal{D}[\sigma_+]\rho,
\qquad
\mathcal{D}[c]\rho=c\rho c^\dagger-\frac12\{c^\dagger c,\rho\}.
$$

Las frecuencias de este ejemplo están en unidades angulares consistentes con el tiempo; no son el detuning en GHz de los CSV de rubidio. La API admite ocupación térmica mediante `nth`; los ejemplos CLI usan `nth=0`.

| Original histórico | Implementación Python | Observación |
| --- | --- | --- |
| [BuildLiouvillianTLS.m](../meetings/2026-04-10-oqs/Codes/BuildLiouvillianTLS.m) | `build_liouvillian`, `tls_liouvillian` | Conserva vectorización por columnas y productos de Kronecker. |
| [SteadyStateLiouvillian.m](../meetings/2026-04-10-oqs/Codes/SteadyStateLiouvillian.m) | `steady_state` | Sustituye una fila por la restricción de traza y simetriza al final; no recorta autovalores. |
| [SolvesMasterEquation.m](../meetings/2026-04-10-oqs/Codes/SolvesMasterEquation.m) | `propagate` | Resuelve el mismo generador constante mediante exponenciales matriciales en lugar de `ode45`. No renormaliza estados durante la propagación. |
| [MainSpectrumTLS.m](../meetings/2026-04-10-oqs/Codes/MainSpectrumTLS.m) | CLI `dynamics` y `scan` | Reproduce las cantidades calculadas: poblaciones, coherencias y su promedio Doppler. |
| [FlurescenceSpectrumOnResonanceTLS.m](../meetings/2026-04-10-oqs/Codes/FlurescenceSpectrumOnResonanceTLS.m) | CLI `fluorescence`, `correlation`, `fluorescence_spectrum` | Conserva parámetros de drive y desarrolla explícitamente la regresión cuántica antes ausente. |
| [rgb.m](../meetings/2026-04-10-oqs/Codes/rgb.m) | Colores por nombre de Matplotlib | Sustituye la función auxiliar de color; no pretende reproducir su redondeo RGB histórico. |

Los originales se conservan como respaldo. La comparación se apoya en ecuaciones y soluciones analíticas; no se ejecutó MATLAB para certificar equivalencia numérica de extremo a extremo.

## Ejecución

Desde la raíz del repositorio, con las dependencias instaladas:

```sh
python models/open-quantum-systems/two_level.py check
python models/open-quantum-systems/two_level.py dynamics
python models/open-quantum-systems/two_level.py scan
python models/open-quantum-systems/two_level.py fluorescence
```

Los comandos guardan CSV, PNG y un JSON de parámetros en `outputs/oqs/`. `--output` permite elegir otro directorio. Los nombres de archivo de cada comando son distintos; repetir el mismo comando en el mismo directorio reemplaza sus resultados anteriores.

- `dynamics`: $\Omega=1$, $\delta=1$, $\gamma=0.5$, estado inicial fundamental, 2000 puntos entre $t=0$ y 50. Exporta `dynamics.csv`, `dynamics.png` y `dynamics_parameters.json`.
- `scan`: 500 detunings entre $-7\Omega$ y $+7\Omega$, $\Omega=1$, $\gamma=0.5$, anchura Doppler $\sigma_D=1$ y 161 clases entre $-5\sigma_D$ y $+5\sigma_D$. Exporta `scan.csv`, `scan.png` y `scan_parameters.json`.
- `fluorescence`: resonancia exacta, $\gamma=1$, $4\Omega/\gamma=2,8,16$, 60000 retardos hasta $100/\gamma$. Exporta un CSV de correlación y uno de espectro por drive, además de una figura común y parámetros JSON. `--points 4096` permite una ejecución exploratoria con menor resolución temporal; debe revisarse el ancho de banda antes de interpretar frecuencias altas.

Ejemplos con parámetros explícitos:

```sh
python models/open-quantum-systems/two_level.py dynamics --omega 1 --delta 0 --gamma 0.5 --tmax 40 --output outputs/oqs-resonant
python models/open-quantum-systems/two_level.py scan --sigma-d 0.5 --velocity-points 321 --output outputs/oqs-doppler
python models/open-quantum-systems/two_level.py fluorescence --ratios 2 8 16 --total --output outputs/oqs-total
```

El barrido sin Doppler resuelve numéricamente cada Liouvilliana. Para acelerar la integral Doppler usa la solución analítica estacionaria equivalente a temperatura del baño cero; las pruebas contrastan esa integral con soluciones numéricas independientes de la Liouvilliana. La distribución térmica se normaliza dentro del intervalo truncado.

## Regresión cuántica y espectro

El original de fluorescencia invoca `CorrelationTRG`, pero esa rutina no estaba en los archivos recibidos. Por tanto, `correlation` es una implementación nueva y explícita del teorema de regresión cuántica; no se presenta como copia verificada de una función original ausente.

Se define

$$
C(\tau)=\operatorname{Tr}\!\left[\sigma_+e^{\mathcal{L}\tau}(\sigma_-\rho_{\mathrm{ss}})\right].
$$

Para la componente incoherente se resta
$\operatorname{Tr}(\sigma_+\rho_{\mathrm{ss}})\operatorname{Tr}(\sigma_-\rho_{\mathrm{ss}})$.
El operador inicial $\sigma_-\rho_{\mathrm{ss}}$ no es una matriz densidad y no debe normalizarse ni simetrizarse durante la propagación.

El espectro implementa

$$
S(\nu)=\frac{1}{\pi}\operatorname{Re}\int_0^T C(\tau)e^{-i\nu\tau}\,d\tau,
$$

mediante FFT sobre una grilla uniforme. $\nu$ es frecuencia angular respecto al bombeo. Se usan pesos trapezoidales en los extremos, a diferencia de la suma rectangular del ejemplo MATLAB. No se recortan valores negativos del espectro; la ventana finita y el muestreo pueden producir errores o pequeñas oscilaciones que requieren un estudio de convergencia.

El modo predeterminado devuelve la componente incoherente. Con `--total`, el componente elástico se representa con el ancho impuesto por el intervalo finito de observación; esa anchura no es una predicción física de la línea elástica ideal. El CSV mantiene la normalización de la integral, sin normalizar cada espectro a su máximo.

## Verificación y límites

La suite [test_two_level.py](../models/open-quantum-systems/test_two_level.py) contiene nueve pruebas y puede ejecutarse también con:

```sh
python -m unittest discover -s models/open-quantum-systems -p "test_*.py" -v
```

Las pruebas verifican la Liouvilliana contra la ecuación matricial directa; la solución de Bloch estacionaria en varios drives, detunings y tasas; traza, positividad y residuo; equilibrio térmico sin drive; decaimiento exponencial de población; dinámica forzada y convergencia; propagación en tiempos irregulares; promedio Doppler frente a soluciones numéricas; límites inicial y asintótico de QRT; y FFT frente a una Lorentziana analítica. Durante la preparación pasaron las nueve pruebas y se ejecutaron los tres comandos con sus parámetros predeterminados.

`MainSpectrumTLS.m` reserva matrices llamadas `ChiMap`, `AbsMap`, `DispMap` y mapas de fluorescencia, pero su código recibido no las calcula. Este port reproduce sus observables efectivamente calculadas y añade la fluorescencia explícita del ejemplo resonante; no afirma implementar un mapa completo de susceptibilidad retardada, absorción/ganancia o respuesta de una sonda adicional. La fluorescencia de dos niveles y la absorción D2 multihiperfina son observables y modelos distintos.
