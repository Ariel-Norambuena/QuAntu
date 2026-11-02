# Publicación del repositorio privado

Destino autorizado: **Ariel-Norambuena/QuAntu**, privado. La raíz del checkout es la carpeta que contiene este README, `models/`, `reports/` y `.github/`.

El publicador [publish_repository.py](../scripts/publish_repository.py) usa Git y GitHub CLI. Comprueba los archivos importados, la cuenta autenticada, la rama `main`, la ausencia de cambios pendientes y la visibilidad privada antes de subir. Crea el repositorio si todavía no existe; no fuerza el historial ni cambia la visibilidad de uno existente.

```sh
gh auth login --hostname github.com --git-protocol https --web
python scripts/publish_repository.py
```

Después de publicar, revisar [GitHub Actions](https://github.com/Ariel-Norambuena/QuAntu/actions) para comprobar la ejecución en Linux. Una futura publicación pública requiere revisar derechos por componente, datos, autores y licencia; la copia privada no asigna derechos nuevos al material recibido.
