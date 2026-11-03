#!/usr/bin/env python3
"""Check syntax, data integrity, and the existing Voigt functions without a UI.

These checks exercise numerical invariants. They do not establish agreement with
an experimental spectrum or validate the MATLAB density-matrix calculations.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
from scipy.special import wofz


ROOT = Path(__file__).resolve().parents[1]
CONSTANTS = {
    "c", "kB", "lambda0", "nu0", "eta_85", "m_85", "centers_85",
    "weights_85", "eta_87", "m_87", "centers_87", "weights_87", "shift_global",
}


def check_syntax() -> tuple[int, int]:
    python_files = [
        path for path in ROOT.rglob("*.py")
        if not any(part in {".venv", "venv", ".git", "__pycache__", ".cache", "build", "outputs", "results", "tmp"} for part in path.parts)
    ]
    for path in python_files:
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    notebooks = list((ROOT / "theory" / "notebooks").rglob("*.ipynb"))
    notebooks += list((ROOT / "algorithms" / "education" / "qiskit").glob("*.ipynb"))
    for path in notebooks:
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        if document.get("nbformat") != 4:
            raise AssertionError(f"Unsupported notebook format: {path}")
        for index, cell in enumerate(document["cells"]):
            if cell["cell_type"] == "code":
                compile("".join(cell["source"]), f"{path}:cell-{index}", "exec")
    return len(python_files), len(notebooks)


def scientific_function(path: Path):
    """Load actual constants and function definitions, without interface imports."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = {item.id for target in node.targets for item in ast.walk(target)
                     if isinstance(item, ast.Name)}
            if names and names <= CONSTANTS:
                nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name == "calculate_absorption":
            nodes.append(node)
    namespace = {"np": np, "wofz": wofz, "Omega": np.linspace(-7, 5, 3000)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace["calculate_absorption"]


def check_voigt() -> int:
    folder = ROOT / "theory" / "models" / "interactive"
    local_model = scientific_function(folder / "interactive_model.py")
    dashboard_model = scientific_function(folder / "dashboard_rb.py")
    cases = 0
    for temperature in (10.0, 293.0, 3000.0):
        for gamma in (0.0, 6.0, 300.0):
            for rb85, rb87 in ((False, False), (True, False), (False, True), (True, True)):
                local = local_model(temperature, gamma, rb85, rb87)
                dashboard, sigma = dashboard_model(temperature, gamma, rb85, rb87)
                if local.shape != (3000,) or not np.isfinite(local).all():
                    raise AssertionError("Invalid Voigt output shape or nonfinite value")
                if local.min() < -1e-12 or local.max() > 1.0 + 1e-12:
                    raise AssertionError("Absorption outside normalized bounds")
                if rb85 or rb87:
                    np.testing.assert_allclose(local.max(), 1.0, atol=1e-12)
                else:
                    np.testing.assert_array_equal(local, np.zeros_like(local))
                np.testing.assert_allclose(local, dashboard, rtol=1e-12, atol=1e-12)
                if not np.isfinite(sigma) or sigma <= 0:
                    raise AssertionError("Doppler width must be positive and finite")
                cases += 1
    _, sigma_low = dashboard_model(100.0, 6.0, True, True)
    _, sigma_high = dashboard_model(400.0, 6.0, True, True)
    np.testing.assert_allclose(sigma_high / sigma_low, 2.0, rtol=1e-12)
    return cases


def check_data() -> int:
    files = list((ROOT / "theory" / "models").rglob("*.csv"))
    files += list((ROOT / "theory" / "notebooks" / "absorption").glob("*.csv"))
    for path in files:
        data = np.loadtxt(path, delimiter=",", skiprows=1)
        if data.ndim != 2 or data.shape[1] != 2 or data.shape[0] < 2:
            raise AssertionError(f"Expected two-column spectrum: {path}")
        if not np.isfinite(data).all() or data[:, 1].max() <= 0:
            raise AssertionError(f"Invalid spectrum values: {path}")
    return len(files)


def main() -> None:
    python_count, notebook_count = check_syntax()
    case_count = check_voigt()
    data_count = check_data()
    print(f"PASS: syntax of {python_count} Python files and {notebook_count} notebooks")
    print(f"PASS: {case_count} Voigt cases, interface agreement, and thermal-width scaling")
    print(f"PASS: {data_count} model/notebook CSV files")
    print("Scope: numerical integrity only; no experimental fit or full MATLAB execution.")


if __name__ == "__main__":
    main()
