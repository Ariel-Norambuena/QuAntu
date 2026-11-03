#!/usr/bin/env python3
"""Run structural and scientific checks; optional complete notebook execution."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-notebooks", action="store_true", help="Execute all three absorption notebooks; requires Plotly")
    parser.add_argument("--with-qiskit", action="store_true", help="Execute the Qiskit workshop; requires Qiskit")
    args = parser.parse_args()
    commands = [
        ["scripts/verify_repository.py"],
        ["scripts/check_science.py"],
        ["-m", "unittest", "discover", "-s", "theory/models/density-matrix", "-p", "test_*.py", "-v"],
        ["-m", "unittest", "discover", "-s", "theory/models/open-quantum-systems", "-p", "test_*.py", "-v"],
    ]
    if args.with_notebooks:
        commands.append(["scripts/run_absorption_notebooks.py"])
    if args.with_qiskit:
        commands.append(["algorithms/education/qiskit/validate_notebook.py"])
    for command in commands:
        print("Running: python " + " ".join(command), flush=True)
        result = subprocess.run([sys.executable, *command], cwd=ROOT)
        if result.returncode:
            return result.returncode
    print("All requested checks passed. Scope and remaining scientific work: docs/validation.md")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
