"""Collect RSDFT outputs into the CSV files used by the article.

Usage:
  python collect_rsdft_outputs.py md <rsdft_output_dir> <out.csv.gz>
  python collect_rsdft_outputs.py harmonic <harmonic_dir> <out.csv>

md: reads DIPOLE.dat (total dipole), traj.dat (written with ALLTRAJ 1) and
info.dat, and writes one row per MD step.
harmonic: reads <harmonic_dir>/<mode>_<u>/output/rsdft.json made from the
inputs of make_harmonic_inputs.py.
"""
import csv
import gzip
import json
import sys
from pathlib import Path

import numpy as np

BOHR = 0.529177210903  # angstrom
NAT = 3  # C, O1, O2


def read_traj(path):
    """Positions (bohr) from traj.dat: a time line, then Z, R, V, F per atom."""
    rows = [line.split() for line in path.read_text().splitlines() if line.strip()]
    blocks = [rows[i:i + NAT + 1] for i in range(0, len(rows) - NAT, NAT + 1)]
    t = np.array([float(b[0][0]) for b in blocks])
    r = np.array([[[float(v) for v in a[1:4]] for a in b[1:]] for b in blocks])
    return t, r


def collect_md(outdir, dest):
    dip = np.loadtxt(outdir / "DIPOLE.dat")
    info = np.loadtxt(outdir / "info.dat")
    t, r = read_traj(outdir / "traj.dat")
    if not (len(t) == len(dip) == len(info)) or np.abs(t - dip[:, 0]).max() > 1e-6:
        raise SystemExit("DIPOLE.dat, traj.dat and info.dat do not share the same time steps")
    r = r * BOHR
    header = ["time_fs", "mu_x_au", "mu_y_au", "mu_z_au"]
    header += [f"{a}_{k}_A" for a in ("C", "O1", "O2") for k in "xyz"]
    header += ["dE_conserved_Ha", "fictitious_ke_Ha", "temperature_K"]
    with gzip.open(dest, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for i in range(len(t)):
            w.writerow([f"{t[i]:.2f}"] + [f"{v:.8f}" for v in dip[i, 1:4]]
                       + [f"{v:.10f}" for v in r[i].ravel()]
                       + [f"{info[i, 2]:.8f}", f"{info[i, 5]:.8f}", f"{info[i, 7]:.6f}"])


def collect_harmonic(hdir, dest):
    with open(dest, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode", "u_bohr", "etot_Ha"])
        for d in sorted(hdir.iterdir()):
            j = d / "output" / "rsdft.json"
            if j.exists():
                mode, u = d.name.split("_")
                w.writerow([mode, u, f"{json.loads(j.read_text())['etot']['value']:.10f}"])


if __name__ == "__main__":
    kind, src, dest = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    {"md": collect_md, "harmonic": collect_harmonic}[kind](src, dest)
