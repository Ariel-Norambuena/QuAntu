# Contributing to QuAntü

Scientific changes should let another person reproduce the result and assess its scope.

1. Identify the research area—Algorithms, Experimental, Theory, or cross-cutting—explain the scientific or computational objective, and connect the change to documentation or a specific issue.
2. Use Python for new implementations. State units, frequency conventions, and normalizations explicitly. Document differences from the original implementations.
3. Keep input data, parameters, and generated results separate. Write new outputs to `results/generated/` and avoid overwriting imported historical figures.
4. Provide the command executed, environment versions, and relevant numerical checks: trace, Hermiticity, positivity, convergence, or analytical limits, as appropriate.
5. Run `python scripts/verify_repository.py` and `python scripts/check_science.py`. Structural checks do not establish physical accuracy.
6. When intentionally changing an imported file, review its diff and update its current size and hash with `python scripts/update_inventory.py --write`. Preserve the source hash and explain the change.

## Data and results

Identify the source publication or setup, units of both columns, applied transformations, and the person responsible. Do not label digitized literature data as original measurements. Preserve raw files and add reproducible processing before regenerating processed datasets.

## Notebooks and reports

Avoid machine-specific absolute paths. Run notebooks from their own directories or use explicit data paths. Label a saved result as historical if it has not been rerun. The LaTeX report uses local paths within `reports/technical-progress/`; keep its sources together with its figures.

## Attribution

Preserve existing credits. Inclusion in this repository does not authorize applying a new license to papers or external materials. Public distribution and licensing of original code require an explicit team decision.
