# Contribuir a QuAntü

Los cambios científicos deben permitir a otra persona reproducir el resultado y evaluar su alcance.

1. Describe el objetivo físico y vincula el cambio con una sección del informe o un asunto concreto.
2. Usa Python para nuevas implementaciones. Conserva unidades, convenciones de frecuencia y normalizaciones explícitas. Documenta cualquier diferencia con las implementaciones originales.
3. Separa datos de entrada, parámetros y resultados generados. Escribe las nuevas salidas en `results/generated/` y evita sobrescribir las figuras históricas importadas.
4. Aporta el comando ejecutado, versiones del entorno y controles numéricos relevantes: traza, hermiticidad, positividad, convergencia o límites analíticos según corresponda.
5. Ejecuta `python scripts/verify_repository.py` y `python scripts/check_science.py`. Las comprobaciones estructurales no prueban exactitud física.
6. Cuando cambies intencionalmente un archivo importado, revisa el diff y actualiza su tamaño y hash actual mediante `python scripts/update_inventory.py --write`. El hash de origen se conserva. Adjunta la razón del cambio.

## Datos y resultados

Identifica la publicación o el montaje de origen, unidades de ambas columnas, transformaciones aplicadas y responsable. Los datos digitalizados de literatura no se deben etiquetar como mediciones propias. Conserva los brutos y añade un procesamiento reproducible antes de regenerar los archivos procesados.

## Notebooks y reportes

Evita rutas absolutas de una máquina. Ejecuta los notebooks desde su directorio o usa rutas explícitas a datos. Un resultado guardado sin nueva ejecución debe marcarse como histórico. El reporte LaTeX usa rutas locales dentro de `reports/technical-progress/`; conserva sus fuentes junto con las figuras.

## Atribución

Mantén los créditos existentes. No apliques una nueva licencia a los artículos ni al material externo por estar incluidos en este repositorio. La publicación pública y una licencia del código propio requieren una decisión explícita del equipo.
