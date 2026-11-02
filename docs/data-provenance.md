# Procedencia y uso de los datos

Los espectros reunidos proceden de reconstrucciones de curvas publicadas y de archivos de trabajo conservados. El [reporte local](../reports/technical-progress/main.tex) describe la digitalización y normalización de un espectro de Ma et al. (2017) como benchmark de los primeros modelos. Estos archivos no deben presentarse como mediciones experimentales originales de QuAntü.

La carpeta [data/raw](../data/raw/) conserva tablas e imágenes recibidas como extracciones de figuras. «Raw» designa aquí el estado de esos archivos en la carpeta original; no implica datos sin procesar de un detector ni acceso a las adquisiciones de los autores de los artículos. [data/processed](../data/processed/) conserva las versiones preparadas para comparación.

## Benchmarks de los modelos

| Archivo | Filas numéricas | Uso | Procedencia documentada |
| --- | ---: | --- | --- |
| [notebooks/absorption/Data_Rb_Gas.csv](../notebooks/absorption/Data_Rb_Gas.csv) | 89 | Referencia de los notebooks Model_1, Model_2 y Model_3. | El reporte atribuye el benchmark reconstruido a Ma et al. (2017). No se conserva un registro individual de digitalización. |
| [models/density-matrix/DATA_ABS_Rb.csv](../models/density-matrix/DATA_ABS_Rb.csv) | 61 | Overlay experimental leído por MATLAB. | El reporte documenta su formato y uso, pero no identifica de forma inequívoca figura, extracción o transformación de este archivo. |
| [models/density-matrix/Data_Rb_Gas.csv](../models/density-matrix/Data_Rb_Gas.csv) | 89 | Copia local preservada en el directorio MATLAB. | Idéntica por bytes al benchmark de notebooks en esta versión. El script rápido lee DATA_ABS_Rb.csv. |
| [models/interactive/Data_Rb_Gas.csv](../models/interactive/Data_Rb_Gas.csv) | 89 | Input de los scripts interactivos. | Idéntica por bytes al benchmark de notebooks en esta versión. |

Los tres archivos llamados `Data_Rb_Gas.csv` de las ubicaciones activas comparten SHA-256 `d7111753eb374721401fef1ef6f002141075da64510972e8bc8fa2bd7a0b5035`. `DATA_ABS_Rb.csv` tiene SHA-256 `58e3d51023c850e95561e1a958d821f3b649de3a7e816177bbbbb876ae05433b`. Son datasets diferentes y no deben intercambiarse silenciosamente al comparar errores.

Ambos nombres de input conservan el encabezado `x, y`. Los scripts y el reporte interpretan la primera columna como detuning en GHz y la segunda como absorción en unidades arbitrarias. Los CSV no contienen, por sí solos, metadatos suficientes para reconstruir la calibración, la incertidumbre o el montaje experimental. `DATA_ABS_Rb.csv` contiene puntos fuera del orden de frecuencia: para nuevos análisis debe ordenarse conjuntamente cada par $(x,y)$ antes de interpolar, manteniendo intacto el archivo fuente.

## Colección bibliográfica de curvas

La asociación siguiente se basa en nombres de archivos, imágenes acompañantes y entradas de la [bibliografía local](../reports/technical-progress/references.bib). No sustituye una ficha que identifique la figura y condiciones exactas de cada extracción. El número de filas excluye el encabezado y coincide en cada pareja raw/processed.

| Familia | CSV en raw | CSV en processed | Filas | Referencia local |
| --- | --- | --- | ---: | --- |
| Agnew | [Agnew.csv](../data/raw/Agnew.csv) | [Agnew__absorption_data_processed.csv](../data/processed/Agnew__absorption_data_processed.csv) | 48 | Agnew et al., 2024; DOI `10.1063/5.0234155`. |
| Bala, etiqueta I_sat0 | [Bala_I_sat0.csv](../data/raw/Bala_I_sat0.csv) | [Bala_I_sat0_absorption_data_processed.csv](../data/processed/Bala_I_sat0_absorption_data_processed.csv) | 50 | Bala et al., 2022; DOI `10.1088/1361-6455/ac7e93`. |
| Bala, etiqueta 0.3_I_sat0 | [Bala_0.3_I_sat0.csv](../data/raw/Bala_0.3_I_sat0.csv) | [Bala_0.3_I_sat0_absorption_data_processed.csv](../data/processed/Bala_0.3_I_sat0_absorption_data_processed.csv) | 53 | Misma familia bibliográfica; conservar la etiqueta sin inferir intensidad medida de QuAntü. |
| Bala, etiqueta 0.01_I_sat0 | [Bala_0.01_I_sat0.csv](../data/raw/Bala_0.01_I_sat0.csv) | [Bala_0.01_I_sat0_absorption_data_processed.csv](../data/processed/Bala_0.01_I_sat0_absorption_data_processed.csv) | 78 | Misma familia bibliográfica. |
| Horn | [HORN.csv](../data/raw/HORN.csv) | [HORN_absorption_data_processed.csv](../data/processed/HORN_absorption_data_processed.csv) | 42 | Horn et al., 2011; DOI `10.1103/PhysRevA.84.043851`. |
| Jacques | [Jacques.csv](../data/raw/Jacques.csv) | [Jacques_absorption_data_processed.csv](../data/processed/Jacques_absorption_data_processed.csv) | 55 | Jacques et al., 2009; DOI `10.1088/0143-0807/30/5/001`. |
| Siddons | [Siddons.csv](../data/raw/Siddons.csv) | [Siddons_absorption_data_processed.csv](../data/processed/Siddons_absorption_data_processed.csv) | 64 | Siddons et al., 2008; DOI `10.1088/0953-4075/41/15/155004`. |
| Siddons, etiqueta T_16.5 | [Siddons_T_16.5.csv](../data/raw/Siddons_T_16.5.csv) | [Siddons_T_16.5_absorption_data_processed.csv](../data/processed/Siddons_T_16.5_absorption_data_processed.csv) | 38 | Misma familia; la condición exacta y su unidad deben cotejarse con la figura de origen. |
| Siddons, etiqueta T_25.0 | [Siddons_T_25.0.csv](../data/raw/Siddons_T_25.0.csv) | [Siddons_T_25.0_absorption_data_processed.csv](../data/processed/Siddons_T_25.0_absorption_data_processed.csv) | 61 | Misma familia bibliográfica. |
| Siddons, etiqueta T_36.6 | [Siddons_T_36.6.csv](../data/raw/Siddons_T_36.6.csv) | [Siddons_T_36.6_absorption_data_processed.csv](../data/processed/Siddons_T_36.6_absorption_data_processed.csv) | 69 | Misma familia bibliográfica. |

Las imágenes acompañantes se conservan en [raw](../data/raw/) y los PDF de consulta en [references/papers](../references/papers/). Los datos atómicos usados por MATLAB se describen en el [desarrollo del reporte](../reports/technical-progress/density_matrix_model.tex); las compilaciones de Steck están en [references/atomic-data](../references/atomic-data/).

## Formatos y transformaciones

- Los CSV usan coma como separador y una línea de encabezado. Hay espacios en algunos encabezados y valores: los lectores deben tolerarlos.
- Los raw conservan nombres genéricos `x, y`. La mayoría de los procesados usan `x,absorption`; el procesado de Jacques conserva `x, y`. No todos comparten un esquema nominal uniforme.
- Las diferencias entre raw y processed incluyen cambios de eje y de ordenada; no debe suponerse una única transformación universal. En particular, los ejes no se deben mezclar sin revisar signo, origen y escala.
- Se conservan valores ligeramente negativos en algunos datos procesados. No se han truncado aquí ni deben eliminarse de forma implícita para mejorar métricas.
- La colección original no aporta un script general ni un registro por archivo que reproduzca todas las transformaciones raw → processed, la herramienta de digitalización, sus puntos de calibración o sus incertidumbres. Esa trazabilidad está pendiente.

Las calibraciones del modelo de matriz densidad son otra etapa: el eje afín y la normalización de profundidad óptica descritos en [science.md](science.md) pertenecen a la comparación del modelo y no documentan cómo se digitalizó cada CSV.

## Requisitos para futuras incorporaciones

Para cada nuevo dataset, registrar junto a su archivo: referencia y figura exactas; autor de la extracción y fecha; unidades y convención del eje; magnitud original de la ordenada; herramienta y puntos de calibración; transformaciones en orden; incertidumbres; licencia o condiciones de uso; y hash del archivo fuente. Conservar el original y generar derivados con un script versionado.

El [inventario](inventory.csv) permite identificar el origen local y la integridad de esta copia, pero un hash no prueba el origen bibliográfico ni los derechos de redistribución. Los artículos, figuras y tablas derivados conservan las atribuciones y condiciones de sus respectivos titulares. No se declara una licencia abierta global para esos materiales.
