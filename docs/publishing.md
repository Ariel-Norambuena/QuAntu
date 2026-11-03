# Publishing the repository

Authorized destination: **Ariel-Norambuena/QuAntu**, with public visibility. The checkout root is the directory containing the main README, `algorithms/`, `experimental/`, `theory/`, and the shared `docs/`, `scripts/`, and `.github/` directories. Run publishing commands from this root.

The [publish_repository.py](../scripts/publish_repository.py) publisher uses Git and GitHub CLI. It checks the 124 preserved imported files, authenticated account, `main` branch, clean working tree, and public visibility before pushing. It creates a public repository if none exists; it does not force history or automatically change an existing repository's visibility.

```sh
gh auth login --hostname github.com --git-protocol https --web
python scripts/publish_repository.py
```

If an existing remote is still private, the publisher stops without changing it. Visibility is changed separately using the authorized account; publishing can then be retried.

The `meetings/` folder was removed from the tree and history of the published branch. All commit trees and the absence of its 11 files as reachable objects were checked. Earlier history is preserved in a local backup outside the repository; original files remain in the working folder. The Python OQS models remain available and independent of those files.

After publishing, check [GitHub Actions](https://github.com/Ariel-Norambuena/QuAntu/actions) to verify execution on Linux. Publishing preserves each component's attributions and does not assign a new license to third-party materials.
