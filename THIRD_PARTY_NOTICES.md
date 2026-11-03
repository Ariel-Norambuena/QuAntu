# Procedencia y materiales de terceros

Este repositorio reúne código, datos, documentos y material docente utilizados
por QuAntü. Su inclusión en la colección no transfiere derechos de autor ni
establece una licencia nueva para los archivos originales. La colección se
publica con acceso público y conserva las atribuciones de sus componentes.

No se aplica una licencia general a toda la colección. Deben respetarse los
avisos, autores y condiciones que consten en cada documento y en sus fuentes.
La ausencia de un archivo de licencia junto a un material no equivale a una
concesión de derechos.

## Artículos y datos atómicos

Los PDF de [references/papers](references/papers/) y
[references/atomic-data](references/atomic-data/) son documentos de consulta de
sus respectivos autores y editores. La bibliografía del reporte se conserva en
[references.bib](reports/technical-progress/references.bib):

| Referencia | Identificador de la bibliografía |
|---|---|
| Jian Ma y colaboradores, *Optical Spin Noise Spectra of Rb Atomic Gas with Homogeneous and Inhomogeneous Broadening* (2017) | DOI `10.1038/s41598-017-08759-4` |
| V. Jacques y colaboradores, *Nonlinear Spectroscopy of Rubidium: An Undergraduate Experiment* (2009) | DOI `10.1088/0143-0807/30/5/001` |
| Paul Siddons y colaboradores, *Absolute Absorption on Rubidium D Lines: Comparison Between Theory and Experiment* (2008) | DOI `10.1088/0953-4075/41/15/155004` |
| Nicola Agnew y colaboradores, *Practical Doppler Broadening Thermometry* (2024) | DOI `10.1063/5.0234155` |
| Rajni Bala y colaboradores, *A Comprehensive Model for Doppler Spectra in Thermal Atomic Vapour* (2022) | DOI `10.1088/1361-6455/ac7e93` |
| H. Horn y colaboradores, *Spin-Noise Spectroscopy Under Resonant Optical Probing Conditions: Coherent and Nonlinear Effects* (2011) | DOI `10.1103/PhysRevA.84.043851` |
| Daniel A. Steck, *Rubidium 85 D Line Data* y *Rubidium 87 D Line Data* | [Fuente de datos atómicos](https://steck.us/alkalidata/) |

Las fechas, títulos e identificadores de esta tabla se transcriben de la
bibliografía local del reporte; no representan una nueva revisión bibliográfica.
Las copias de las tablas Steck en ambas carpetas se preservan por procedencia.

## Imágenes y tablas obtenidas de literatura

[data/raw](data/raw/) y [data/processed](data/processed/) contienen imágenes,
tablas digitalizadas y datos procesados asociados a Agnew, Bala, Horn, Jacques y
Siddons. Deben citarse sus fuentes al reutilizarlos. Estos materiales no deben
presentarse como mediciones propias del laboratorio QuAntü. La procedencia por
archivo y las limitaciones de reconstrucción deben consultarse en la
documentación de datos; la inclusión de un CSV no certifica su licencia ni la
exactitud de la digitalización.

[notebooks/absorption](notebooks/absorption/) proviene de una carpeta llamada
`Codigo del Paper J. Ma 2017 Scientific Reports`. Ese nombre relaciona el
material con una referencia científica; por sí solo no prueba que los notebooks
sean código publicado por los autores del artículo. Se conserva esa procedencia
en el inventario, sin atribuir autoría o licencia no acreditadas.

## Documentación de fabricantes y material teórico

[references/hardware](references/hardware/) contiene documentos de Thorlabs y
SCHOTT/BOROFLOAT. Los nombres comerciales y el contenido corresponden a sus
respectivos titulares. [references/rubidium-theory](references/rubidium-theory/)
conserva otros documentos de consulta de rubidio; su presencia no establece
autoría del equipo QuAntü ni una licencia de redistribución.

## Taller Qiskit y otros materiales docentes

[education/qiskit](education/qiskit/) conserva un snapshot del repositorio
[neutral-atoms-qiskit-workshop](https://github.com/Ariel-Norambuena/neutral-atoms-qiskit-workshop),
atribuido a Ariel Norambuena por su README y
[CITATION.cff](education/qiskit/CITATION.cff). Se preservan esos avisos. En los
archivos importados no se identificó una licencia independiente que autorice
aplicar una licencia general al taller.

Las presentaciones de clases y extensión mantienen los nombres y
créditos presentes en sus originales, entre ellos Ariel Norambuena y Alonso
Recabarren. Conservarlas en esta colección no implica permiso para
relicenciar sus imágenes, marcas u otros componentes externos.

Las bibliotecas de Python y MATLAB necesarias para ejecutar los programas no se
redistribuyen aquí; sus licencias y términos corresponden a sus distribuidores.
Los recursos generados para la animación MOT permanecen junto a sus fuentes y su
documentación. Los valores ilustrativos de la animación deben interpretarse
según las convenciones descritas en su README.

## Registro de procedencia

[docs/inventory.csv](docs/inventory.csv) relaciona las 126 rutas de origen con
sus destinos y hashes; [docs/repository-map.md](docs/repository-map.md) explica
las copias, exclusiones y el snapshot Git. Los 11 materiales de reuniones se
retiraron del árbol publicado y sus originales permanecen en la carpeta de
trabajo del proyecto. Los avisos y condiciones específicos de cada material
continúan aplicándose a su reutilización.
