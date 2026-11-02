#!/usr/bin/env python3
"""Execute every code cell in order without requiring Jupyter or nbconvert."""

from __future__ import annotations

import json
import traceback
from pathlib import Path


NOTEBOOK = Path(__file__).resolve().parent / "Taller_Qiskit_Atomos_Neutros_1h.ipynb"


def main() -> None:
    document = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace = {"__name__": "__workshop_validation__"}
    code_cells = [cell for cell in document["cells"] if cell["cell_type"] == "code"]
    for index, cell in enumerate(code_cells, start=1):
        source = "".join(cell["source"])
        try:
            exec(compile(source, f"{NOTEBOOK.name}:code-cell-{index}", "exec"), namespace)
        except Exception:
            print(f"FAILED in code cell {index}")
            traceback.print_exc()
            raise SystemExit(1)
    print(f"VALIDATION COMPLETE — {len(code_cells)} code cells executed")


if __name__ == "__main__":
    main()
