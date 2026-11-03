# Publicación del repositorio

Destino autorizado: **Ariel-Norambuena/QuAntu**, con visibilidad pública. La raíz del checkout es la carpeta que contiene el README principal, `models/`, `reports/` y `.github/`.

El publicador [publish_repository.py](../scripts/publish_repository.py) usa Git y GitHub CLI. Comprueba los 126 archivos importados conservados, la cuenta autenticada, la rama `main`, la ausencia de cambios pendientes y la visibilidad pública antes de subir. Crea un repositorio público si todavía no existe; no fuerza el historial ni cambia automáticamente la visibilidad de uno existente.

```sh
gh auth login --hostname github.com --git-protocol https --web
python scripts/publish_repository.py
```

Si un remoto existente todavía es privado, el publicador se detiene sin cambiarlo. El cambio de visibilidad se realiza por separado con la cuenta autorizada; después puede repetirse la publicación.

La carpeta `meetings/` se retiró del árbol publicado; los archivos originales permanecen en la carpeta de trabajo. Esta descripción no afirma una eliminación de commits anteriores. Los modelos Python OQS siguen disponibles y son independientes de esos archivos.

Después de publicar, revisar [GitHub Actions](https://github.com/Ariel-Norambuena/QuAntu/actions) para comprobar la ejecución en Linux. La publicación conserva las atribuciones de cada componente y no asigna una licencia nueva a los materiales de terceros.
