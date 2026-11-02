#!/usr/bin/env python3
"""Regenerate a small cross-language fixture using the original MATLAB code.

MATLAB is optional for everyday Python use. This script extracts the original
local functions into a temporary harness, without executing its large default
grid or modifying the source. The fixture records the source SHA-256.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
HEADER = r"""
amu = 1.66053906660e-27;
Gamma = 6.0666; drive = 10.0; groundRate = 0.05;
detunings = [-4200, -1700, 1300, 2500];
omega = [-4200, -1700, 1300, 2500];
samples = struct([]); spectra = struct([]); count = 0; k = 0;
for number = [85, 87]
    if number == 85
        rb = make_rb85(amu, 780.241368271e-9);
        rb.isoCenter_MHz = 0;
    else
        rb = make_rb87(amu, 780.241209686e-9);
        rb.isoCenter_MHz = 78.095;
    end
    sigma = sqrt(1.380649e-23*293/rb.mass)/rb.lambda/1e6;
    for modeCell = {'pi', 'linear_x'}
        mode = modeCell{1};
        states = build_basis(rb); N = numel(states);
        Dip = build_dipole_operator(rb, states, mode);
        Ldiss = build_dissipator(rb, states, 2*pi*Gamma, 2*pi*groundRate, 0);
        [L0,Ldet,b,absVec] = prepare_affine_liouvillian(rb, states, Dip, Ldiss, drive);
        for detuning = detunings
            vec = (L0 + detuning*Ldet)\b;
            rho = reshape(vec,N,N);
            count = count+1;
            samples(count).isotope = number;
            samples(count).polarization = mode;
            samples(count).detuning_MHz = detuning;
            samples(count).response = imag(absVec.'*vec);
            samples(count).rho_real = real(rho);
            samples(count).rho_imag = imag(rho);
        end
        k = k+1;
        spectra(k).isotope = number;
        spectra(k).polarization = mode;
        spectra(k).omega_MHz = omega;
        spectra(k).nv = 5;
        spectra(k).response_step_MHz = 250;
        spectra(k).direct = density_matrix_spectrum_direct_pairs(rb,omega,sigma,5,Gamma,drive,groundRate,mode,false);
        spectra(k).fast = density_matrix_spectrum_fast(rb,omega,sigma,5,Gamma,drive,groundRate,mode,250,false,false);
    end
end
document.matlab_version = version;
document.samples = samples;
document.spectra = spectra;
fid = fopen('__OUTPUT__','w');
fprintf(fid,'%s',jsonencode(document));
fclose(fid);
"""


def local_functions(source: str) -> str:
    match = re.search(r"^function\s", source, flags=re.MULTILINE)
    if match is None:
        raise ValueError("MATLAB source has no local functions")
    return source[match.start():]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fast-source", required=True, type=Path)
    parser.add_argument("--direct-source", required=True, type=Path)
    parser.add_argument("--matlab", default="matlab")
    parser.add_argument("--output", type=Path, default=ROOT / "tests/fixtures/matlab_density_matrix.json")
    args = parser.parse_args()
    fast = args.fast_source.read_text(encoding="utf-8-sig")
    direct = args.direct_source.read_text(encoding="utf-8-sig")
    # Shared helpers come exclusively from the fast MATLAB source. Add only
    # the independently implemented direct quadrature routine from direct.
    direct_functions = local_functions(direct)
    next_function = re.search(r"^function\s", direct_functions[1:], flags=re.MULTILINE)
    direct_function = direct_functions if next_function is None else direct_functions[:next_function.start() + 1]
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    directory = ROOT / "results" / f"matlab-fixture-{stamp}"
    directory.mkdir(parents=True, exist_ok=False)
    harness = directory / "quantu_fixture.m"
    header = HEADER.replace("__OUTPUT__", output.as_posix().replace("'", "''"))
    harness.write_text(header + "\n" + local_functions(fast) + "\n" + direct_function, encoding="utf-8")
    preferences = directory / "preferences"
    preferences.mkdir()
    environment = dict(os.environ, MATLAB_PREFDIR=str(preferences))
    subprocess.run([args.matlab, "-batch", "run('" + harness.as_posix().replace("'", "''") + "')"],
                   env=environment, check=True)
    document = json.loads(output.read_text(encoding="utf-8"))
    document["source_sha256"] = {
        "fast": hashlib.sha256(args.fast_source.read_bytes()).hexdigest(),
        "direct": hashlib.sha256(args.direct_source.read_bytes()).hexdigest(),
    }
    document["parameters"] = {"rabi_MHz": 10.0, "linewidth_MHz": 6.0666,
                              "ground_rate_MHz": 0.05, "temperature_K": 293.0}
    output.write_text(json.dumps(document, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Saved {len(document['samples'])} MATLAB states and {len(document['spectra'])} spectrum cases: {output}")


if __name__ == "__main__":
    main()
