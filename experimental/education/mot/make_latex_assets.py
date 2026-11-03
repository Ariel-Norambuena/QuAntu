#!/usr/bin/env python3
"""Typeset the equations used by the MOT workshop video as transparent PNGs."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "equations"

EQUATIONS = {
    "nu_lock": r"\nu_L\longrightarrow\nu_0",
    "detuning_axis": r"\Delta/\Gamma",
    "nu_laser": r"\nu_L",
    "red_detuning": r"\delta=\omega_L-\omega_0<0",
    "photon_red": r"\hbar\omega_L<\hbar\omega_0",
    "velocity_axis": r"v_x",
    "doppler_force": r"\mathbf F_{\!D}\simeq-\alpha\,\mathbf v",
    "doppler_temp": r"T_D=\frac{\hbar\Gamma}{2k_B}=146\,\mu\mathrm K",
    "div_b": r"\boldsymbol\nabla\!\cdot\!\mathbf B=0",
    "linear_field": r"B_z\simeq b' z",
    "gradient_value": r"b'=12\,\mathrm{G/cm}",
    "mf_minus": r"m_F=-1",
    "mf_zero": r"m_F=0",
    "mf_plus": r"m_F=+1",
    "mot_detuning": r"\delta=-2.5\,\Gamma",
    "mot_force": r"\mathbf F_{\!\mathrm{MOT}}\simeq-\alpha\,\mathbf v-\kappa\,\mathbf r",
    "cloud_size": r"\sigma_r\simeq0.5\text{--}1\,\mathrm{mm}",
    "cloud_temp": r"T\simeq100\text{--}300\,\mu\mathrm K",
    "delta_negative": r"\delta<0",
    "grad_b": r"\boldsymbol\nabla B",
    "loading_model": r"\frac{dN}{dt}=R-\frac{N}{\tau}\quad\Longrightarrow\quad N(t)=N_{\mathrm{ss}}\!\left(1-e^{-t/\tau}\right)",
    "cooling_time": r"\tau_{\mathrm{cool}}\sim1\text{--}10\,\mathrm{ms}",
    "loading_time": r"t_{\mathrm{load}}\sim1\,\mathrm{s}",
    "atom_number": r"N_{\mathrm{MOT}}\sim5\times10^{7}",
}


TEMPLATE = r"""\documentclass[border=5pt]{standalone}
\usepackage{amsmath,amssymb,bm}
\usepackage{xcolor}
\begin{document}
\color{white}
$\displaystyle %s$
\end{document}
"""


def trim_transparency(path: Path) -> None:
    image = Image.open(path).convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    if bbox:
        image = image.crop(bbox)
    image.save(path)


def main() -> None:
    pdflatex = shutil.which("pdflatex")
    pdftocairo = shutil.which("pdftocairo")
    if not pdflatex or not pdftocairo:
        raise SystemExit("pdflatex and pdftocairo are required.")
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mot_latex_") as tmp_name:
        tmp = Path(tmp_name)
        for name, equation in EQUATIONS.items():
            tex = tmp / f"{name}.tex"
            tex.write_text(TEMPLATE % equation, encoding="utf-8")
            subprocess.run(
                [pdflatex, "-interaction=batchmode", "-halt-on-error", tex.name],
                cwd=tmp,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            target = OUT / name
            subprocess.run(
                [pdftocairo, "-png", "-singlefile", "-transp", "-r", "420", str(tmp / f"{name}.pdf"), str(target)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            trim_transparency(target.with_suffix(".png"))
            print(target.with_suffix(".png"))


if __name__ == "__main__":
    main()
