#!/usr/bin/env python3
"""Execute historical absorption notebooks headlessly and check saved metrics.

Only display methods are suppressed. Model code, parameters and input CSVs are
unchanged. No output is written back into the source notebooks.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "Model_1.ipynb": {"MSE": 0.006772, "MAE": 0.054760},
    "Model_2.ipynb": {"MSE": 0.004758, "MAE": 0.052138},
    "Model_3.ipynb": {"MSE": 0.004004, "MAE": 0.048501},
}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON validation record")
    args = parser.parse_args()
    os.environ.setdefault("MPLBACKEND", "Agg")
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    import plotly
    from plotly.basedatatypes import BaseFigure
    import scipy
    original_show, original_plotly_show = plt.show, BaseFigure.show
    plt.show = lambda *args, **kwargs: plt.close("all")
    BaseFigure.show = lambda self, *args, **kwargs: None
    initial_directory = Path.cwd()
    results = {}
    try:
        for name, expected in EXPECTED.items():
            path = ROOT / "notebooks" / "absorption" / name
            document = json.loads(path.read_text(encoding="utf-8"))
            namespace = {"__name__": "__notebook_validation__"}
            os.chdir(path.parent)
            log = io.StringIO()
            cells = 0
            with contextlib.redirect_stdout(log):
                for index, cell in enumerate(document["cells"]):
                    if cell["cell_type"] != "code":
                        continue
                    source = "".join(cell["source"])
                    exec(compile(source, f"{name}:cell-{index}", "exec"), namespace)
                    cells += 1
            metrics = {key: float(namespace[key]) for key in expected}
            for key, value in expected.items():
                np.testing.assert_allclose(metrics[key], value, rtol=0, atol=5.01e-7,
                                           err_msg=f"Historical metric differs: {name} {key}")
            results[name] = {
                "code_cells_executed": cells,
                "metrics": metrics,
                "historical_metrics_rounded": expected,
                "absolute_tolerance": 5.01e-7,
                "notebook_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            print(f"PASS {name}: {cells} cells; MSE={metrics['MSE']:.9f}; MAE={metrics['MAE']:.9f}")
    finally:
        os.chdir(initial_directory)
        plt.show, BaseFigure.show = original_show, original_plotly_show
        plt.close("all")
    record = {
        "scope": "Historical notebook numerical reproduction; displays suppressed; not an independent experimental validation",
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__, "matplotlib": matplotlib.__version__,
                        "plotly": plotly.__version__},
        "data_sha256": hashlib.sha256((ROOT / "notebooks/absorption/Data_Rb_Gas.csv").read_bytes()).hexdigest(),
        "results": results,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
