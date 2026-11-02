"""Analyze the Cu lattice-constant example from Quantum ESPRESSO jobs downloaded from Quloud.

Pass the ZIP files downloaded from the job pages of Quloud ("一括ダウンロード" of
the output files), folders holding them, or their extracted contents. A job is
an output of pw.x (a file holding "Program PWSCF") with the copy of its input
in the same folder (a file holding "K_POINTS"). The file names do not matter;
each job is recognized from its contents:

* calculation: an SCF at a fixed cell ('scf') or a cell optimization ('vc-relax'),
* lattice constant: the cubic lattice constant "lattice parameter (alat)" of an
  fcc cell written with ibrav = 2 (for vc-relax, the starting value),
* plane-wave cutoff "kinetic-energy cutoff".

The script prints the numbers quoted in the article and writes the figures for
the jobs it finds; parts that need missing jobs are skipped.

Usage: python analyze_cu_lattice.py <zip or folder> [...] [--figures DIR]
"""
import argparse
import re
import zipfile
from pathlib import Path, PurePosixPath

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RY_MEV = 13605.693122994  # Ry -> meV
BOHR = 0.529177210903  # angstrom
RY_A3_GPA = 2179.8723611  # Ry/angstrom^3 -> GPa (1 GPa = 10 kbar)

BLUE, AQUA, YELLOW = "#2a78d6", "#1baf7a", "#eda100"
START_COL = {3.56: "#86b6ef", 3.64: "#2a78d6", 3.72: "#0d366b"}
INK, MUTED, GRAY = "#0b0b0b", "#52514e", "#898781"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "lines.linewidth": 1.4,
})


# --- finding and reading jobs ------------------------------------------------------

def find_jobs(paths):
    """(label, input text, output text) of every pw.x job in the ZIP files and folders."""
    jobs = []

    def add_group(label, texts):
        outs = [t for t in texts if "Program PWSCF" in t]
        ins = [t for t in texts if "K_POINTS" in t and "Program PWSCF" not in t]
        for out in outs:
            jobs.append((label, ins[0] if len(ins) == 1 else None, out))

    def add_zip(zpath):
        zf = zipfile.ZipFile(zpath)
        folders = {}
        for n in zf.namelist():
            if n.endswith("/") or n.lower().endswith((".upf", ".dat", ".xml")):
                continue
            folders.setdefault(PurePosixPath(n).parent, []).append(n)
        for parent, members in sorted(folders.items()):
            texts = [zf.read(m).decode(errors="replace") for m in members]
            add_group(f"{zpath}" + ("" if str(parent) == "." else f":{parent}"), texts)

    for p in map(Path, paths):
        if p.is_file() and p.suffix.lower() == ".zip":
            add_zip(p)
        elif p.is_dir():
            for z in sorted(p.rglob("*.zip")):
                add_zip(z)
            for d in sorted({f.parent for f in p.rglob("*") if f.is_file() and f.suffix.lower() != ".zip"}):
                texts = [f.read_text(errors="replace") for f in d.iterdir()
                         if f.is_file() and f.stat().st_size < 50_000_000
                         and f.suffix.lower() not in (".zip", ".upf", ".dat", ".xml")]
                add_group(str(d), texts)
        else:
            raise SystemExit(f"Not a ZIP file or a folder: {p}")
    return jobs


def last(pattern, text, conv=float):
    m = re.findall(pattern, text, re.M)
    return conv(m[-1]) if m else None


def cubic_a(alat_bohr, first_row_x):
    """Cubic lattice constant (angstrom) of an ibrav = 2 cell: the first fcc vector is a(-1/2, 0, 1/2)."""
    return 2 * abs(first_row_x) * alat_bohr * BOHR


def parse_job(inp, out):
    """The quantities of one finished job of an fcc cell (ibrav = 2), or None."""
    if "JOB DONE." not in out or "convergence has been achieved" not in out:
        return None
    if last(r"bravais-lattice index\s*=\s*(-?\d+)", out, int) != 2:
        return None
    calc = re.search(r"calculation\s*=\s*'([\w-]+)'", inp or "")
    calc = calc.group(1) if calc else "scf"
    if calc not in ("scf", "vc-relax"):
        return None
    alat = float(re.search(r"lattice parameter \(alat\)\s*=\s*([\d.]+)", out).group(1))
    j = {
        "calc": calc,
        "a": round(alat * BOHR, 3),  # starting lattice constant for vc-relax
        "ecut": float(re.search(r"kinetic-energy cutoff\s*=\s*([\d.]+)", out).group(1)),
        "E": last(r"^!\s+total energy\s+=\s+([-\d.]+)\s+Ry", out),
        "P": last(r"P=\s*([-\d.]+)", out),
        "nat": last(r"number of atoms/cell\s*=\s*(\d+)", out, int),
    }
    if calc == "vc-relax":
        if "bfgs converged" not in out:
            return None
        relax, _, final = out.partition("Begin final coordinates")
        cells = [cubic_a(float(al), float(x)) for al, x in
                 re.findall(r"CELL_PARAMETERS \(alat=\s*([\d.]+)\)\n\s*([-\d.]+)", relax)]
        P = [float(x) for x in re.findall(r"P=\s*([-\d.]+)", relax)]
        fa = re.search(r"CELL_PARAMETERS \(alat=\s*([\d.]+)\)\n\s*([-\d.]+)", final)
        j["a_start"] = alat * BOHR
        j["traj_a"] = [alat * BOHR] + cells  # cell of each SCF during the relaxation
        j["traj_P"] = P
        j["a_final"] = cubic_a(float(fa.group(1)), float(fa.group(2)))
        j["P_final_scf"] = j["P"] if "G-vectors are recalculated" in final else None
    return j


def load_jobs(paths):
    data, seen = {}, set()
    print("Jobs found:")
    for label, inp, out in find_jobs(paths):
        j = parse_job(inp, out)
        if j is None:
            print(f"  {label}: not a finished scf / vc-relax of an fcc cell (ibrav = 2), skipped")
            continue
        key = (j["calc"], j["ecut"], j["a"])
        if key in seen:
            print(f"  {label}: same conditions as a job above, skipped")
            continue
        seen.add(key)
        cell = (f"a = {j['a_start']:.4f} -> {j['a_final']:.4f} A" if j["calc"] == "vc-relax"
                else f"a = {j['a']:.2f} A")
        print(f"  {label}: {j['calc']}, {j['ecut']:g} Ry, {cell}")
        data[key] = j
    print(f"{len(data)} jobs\n")
    return data


def scan(data, ecut):
    """Arrays (a, V per atom, E per atom in Ry, P in kbar) of the scf jobs at one cutoff, sorted by a."""
    js = sorted((j for (c, e, _), j in data.items() if c == "scf" and e == ecut), key=lambda j: j["a"])
    a = np.array([j["a"] for j in js])
    return a, a ** 3 / 4, np.array([j["E"] / j["nat"] for j in js]), np.array([j["P"] for j in js])


def cutoffs(data):
    return sorted({e for (c, e, _) in data if c == "scf"})


# --- equations of state -------------------------------------------------------------

def murnaghan(V, E0, V0, B0, B1):
    return E0 + B0 * V / B1 * ((V0 / V) ** B1 / (B1 - 1) + 1) - B0 * V0 / (B1 - 1)


def nelder_mead(f, x0, step, maxiter=4000):
    """Minimal Nelder-Mead minimizer (NumPy only)."""
    pts = [x0] + [x0 + np.eye(len(x0))[i] * step[i] for i in range(len(x0))]
    vals = [f(p) for p in pts]
    for _ in range(maxiter):
        order = np.argsort(vals)
        pts, vals = [pts[i] for i in order], [vals[i] for i in order]
        if np.ptp(np.array(pts), axis=0).max() < 1e-12:
            break
        c = np.mean(pts[:-1], axis=0)
        xr = c + (c - pts[-1])
        fr = f(xr)
        if fr < vals[0]:
            xe = c + 2 * (c - pts[-1])
            fe = f(xe)
            pts[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = xr, fr
        else:
            xc = c + 0.5 * (pts[-1] - c)
            fc = f(xc)
            if fc < vals[-1]:
                pts[-1], vals[-1] = xc, fc
            else:
                pts = [pts[0]] + [pts[0] + 0.5 * (p - pts[0]) for p in pts[1:]]
                vals = [vals[0]] + [f(p) for p in pts[1:]]
    return pts[int(np.argmin(vals))]


def fit_murnaghan(V, E):
    """Least squares fit. For fixed (V0, B0') E is linear in (E0, B0), so only (V0, B0') are searched."""
    def lin(V0, B1):
        g = V / B1 * ((V0 / V) ** B1 / (B1 - 1) + 1) - V0 / (B1 - 1)
        A = np.column_stack([np.ones_like(V), g])
        c, *_ = np.linalg.lstsq(A, E, rcond=None)
        r = E - A @ c
        return r @ r, c
    grid = [(lin(V0, B1)[0], V0, B1) for V0 in np.linspace(V.min(), V.max(), 61)
            for B1 in np.linspace(2.0, 8.0, 31)]
    _, V0, B1 = min(grid)
    V0, B1 = nelder_mead(lambda q: lin(q[0], q[1])[0], np.array([V0, B1]),
                         np.array([(V.max() - V.min()) / 50, 0.2]))
    _, (E0, B0) = lin(V0, B1)
    return {"E0": E0, "V0": V0, "B0": B0, "B1": B1, "E": lambda v: murnaghan(v, E0, V0, B0, B1)}


def fit_bm3(V, E):
    """Third-order Birch-Murnaghan: E is a cubic polynomial in x = V^(-2/3) (linear least squares)."""
    p = np.polyfit(V ** (-2.0 / 3.0), E, 3)
    f = lambda v: np.polyval(p, np.asarray(v) ** (-2.0 / 3.0))
    roots = [z.real for z in np.roots(np.polyder(p)) if abs(z.imag) < 1e-12 and z.real > 0]
    V0 = min(roots, key=lambda z: abs(z - np.mean(V ** (-2.0 / 3.0)))) ** -1.5
    h = V0 * 1e-4
    P = lambda v: -(f(v + h) - f(v - h)) / (2 * h)
    B = lambda v: v * (f(v + h) - 2 * f(v) + f(v - h)) / h ** 2
    B1 = (B(V0 + 10 * h) - B(V0 - 10 * h)) / (P(V0 + 10 * h) - P(V0 - 10 * h))
    return {"E0": float(f(V0)), "V0": V0, "B0": B(V0), "B1": B1, "E": f, "P": P}


def a_of(V):
    return (4 * V) ** (1 / 3)


def p_zero(a, P):
    """Lattice constant where the SCF pressure is zero (cubic fit of P(a))."""
    c = np.polyfit(a, P, min(3, len(a) - 1))
    r = [z.real for z in np.roots(c) if abs(z.imag) < 1e-9 and a.min() <= z.real <= a.max()]
    return r[0] if r else None


def window(a, lo, hi):
    return (np.round(a, 3) >= lo - 1e-6) & (np.round(a, 3) <= hi + 1e-6)


# --- tables ------------------------------------------------------------------------

def table_scan(data):
    if 60.0 not in cutoffs(data):
        return
    a, V, E, P = scan(data, 60.0)
    print("E(a) scan at 60 Ry: E - min(E) (meV/atom), P (kbar)")
    for ai, Ei, Pi in zip(a, E, P):
        print(f"  a = {ai:.2f} A   V = {ai ** 3 / 4:7.4f} A^3   {(Ei - E.min()) * RY_MEV:8.3f}   {Pi:9.2f}")
    print()


def table_eos(data):
    if 60.0 not in cutoffs(data):
        return
    a, V, E, P = scan(data, 60.0)
    if len(a) < 5:
        return
    print(f"Equation-of-state fits at 60 Ry ({len(a)} points, {a.min():.2f}-{a.max():.2f} A):")
    for name, fit in (("Birch-Murnaghan (3rd)", fit_bm3), ("Murnaghan", fit_murnaghan)):
        f = fit(V, E)
        res = (E - f["E"](V)) * RY_MEV
        print(f"  {name:22s} a0 = {a_of(f['V0']):.4f} A  B0 = {f['B0'] * RY_A3_GPA:6.1f} GPa"
              f"  B0' = {f['B1']:.2f}  max |residual| = {abs(res).max():.4f} meV")
    sel = window(a, 3.58, 3.70)
    if sel.sum() >= 5:
        f = fit_bm3(V[sel], E[sel])
        print(f"  BM3, 3.58-3.70 A ({sel.sum()} points): a0 = {a_of(f['V0']):.4f} A"
              f"  B0 = {f['B0'] * RY_A3_GPA:.1f} GPa  B0' = {f['B1']:.2f}")
    print("\nQuadratic fit E = c0 + c1 a + c2 a^2 on windows centred at 3.63 A:")
    for lo, hi in ((3.60, 3.66), (3.58, 3.68), (3.56, 3.70), (3.54, 3.72), (3.52, 3.74)):
        sel = window(a, lo, hi)
        if sel.sum() < 3:
            continue
        c = np.polyfit(a[sel], E[sel], 2)
        print(f"  {lo:.2f}-{hi:.2f} A ({sel.sum():2d} points): a0 = {-c[1] / (2 * c[0]):.4f} A")
    f = fit_bm3(V, E)
    print("\nPressure: SCF value and -dE/dV of the BM3 fit (kbar)")
    for ai, Vi, Pi in zip(a, V, P):
        Pf = f["P"](Vi) * RY_A3_GPA * 10
        print(f"  a = {ai:.2f} A   P_scf = {Pi:8.2f}   -dE/dV = {Pf:8.2f}   difference = {Pi - Pf:6.2f}")
    print(f"  P_scf = 0 at a = {p_zero(a, P):.4f} A\n")


def cutoff_rows(data):
    """Per cutoff: (ecut, E(3.64) in Ry, a0 of BM3 on 3.60-3.68, a at P_scf = 0, P_scf - P_fit at 3.64,
    vc-relax from 3.64: final a and final-SCF pressure)."""
    rows = []
    for ec in cutoffs(data):
        a, V, E, P = scan(data, ec)
        sel = window(a, 3.60, 3.68)
        if sel.sum() < 5:
            continue
        a, V, E, P = a[sel], V[sel], E[sel], P[sel]
        f = fit_bm3(V, E)
        i = int(np.argmin(abs(a - 3.64)))
        vc = data.get(("vc-relax", ec, 3.64))
        rows.append((ec, E[i], a_of(f["V0"]), f["B0"] * RY_A3_GPA, p_zero(a, P),
                     P[i] - f["P"](V[i]) * RY_A3_GPA * 10,
                     vc["a_final"] if vc else None, vc["P_final_scf"] if vc else None))
    return rows


def table_cutoff(data):
    rows = cutoff_rows(data)
    if not rows:
        return
    eref = rows[-1][1]
    print(f"Cutoff dependence (BM3 on 3.60-3.68 A; energy relative to {rows[-1][0]:g} Ry at 3.64 A)")
    print("  ecut  E(3.64)-ref   a0(energy)  B0     a(P_scf=0)  P_scf-P_fit(3.64)  vc-relax a  final P")
    for ec, e, a0, b0, ap, dp, avc, pvc in rows:
        vc = f"{avc:.4f}   {pvc:6.2f}" if avc is not None else "   -"
        print(f"  {ec:4g}  {(e - eref) * RY_MEV:8.2f} meV  {a0:.4f}  {b0:6.1f}  {ap:.4f}      {dp:7.2f} kbar"
              f"        {vc}")
    print()


def table_vcrelax(data):
    vcs = sorted((j for (c, _, _), j in data.items() if c == "vc-relax"), key=lambda j: (j["ecut"], j["a"]))
    if not vcs:
        return
    print("vc-relax: lattice constant and pressure of each SCF; final SCF with recalculated G-vectors")
    for j in vcs:
        steps = "  ".join(f"{ai:.4f}({pi:+.2f})" for ai, pi in zip(j["traj_a"], j["traj_P"]))
        fin = f"{j['P_final_scf']:.2f}" if j["P_final_scf"] is not None else "-"
        print(f"  {j['ecut']:4g} Ry from {j['a_start']:.4f} A: {steps}")
        print(f"            final a = {j['a_final']:.4f} A, final SCF P = {fin} kbar")
    print()


# --- figures -----------------------------------------------------------------------

def fig_eos(data, figdir):
    if 60.0 not in cutoffs(data):
        return
    a, V, E, P = scan(data, 60.0)
    if len(a) < 5:
        return
    f = fit_bm3(V, E)
    aa = np.linspace(a.min() - 0.01, a.max() + 0.01, 300)
    fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.3))
    ax = axs[0]
    ax.plot(aa, (f["E"](aa ** 3 / 4) - f["E0"]) * RY_MEV, color=GRAY, lw=1.0, label="Birch–Murnaghan fit")
    ax.scatter(a, (E - f["E0"]) * RY_MEV, color=BLUE, s=20, zorder=3, label="SCF")
    ax.axvline(a_of(f["V0"]), color=MUTED, ls=":", lw=0.8)
    ax.set_xlabel("lattice constant a (Å)")
    ax.set_ylabel("E − E0 (meV/atom)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8)
    ax = axs[1]
    ax.plot(aa, f["P"](aa ** 3 / 4) * RY_A3_GPA * 10, color=GRAY, lw=1.0, label="−dE/dV of the fit")
    ax.scatter(a, P, color=BLUE, s=20, zorder=3, label="SCF (stress)")
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_xlabel("lattice constant a (Å)")
    ax.set_ylabel("pressure (kbar)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(figdir / "energy_pressure.png", dpi=200)
    plt.close(fig)


def fig_quadratic(data, figdir):
    if 60.0 not in cutoffs(data):
        return
    a, V, E, P = scan(data, 60.0)
    if len(a) < 12:
        return
    f = fit_bm3(V, E)
    wins = [(3.60, 3.66), (3.58, 3.68), (3.56, 3.70), (3.54, 3.72), (3.52, 3.74)]
    fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.3))
    ax = axs[0]
    aa = np.linspace(3.51, 3.77, 300)
    ref = f["E"](aa ** 3 / 4)
    for (lo, hi), col, ls in ((wins[0], AQUA, "--"), (wins[-1], YELLOW, "-")):
        sel = window(a, lo, hi)
        c = np.polyfit(a[sel], E[sel], 2)
        ax.plot(aa, (np.polyval(c, aa) - ref) * RY_MEV, color=col, ls=ls,
                label=f"quadratic, {lo:.2f}–{hi:.2f} Å ({sel.sum()} points)")
    ax.scatter(a, (E - f["E"](V)) * RY_MEV, color=BLUE, s=18, zorder=3, label="SCF")
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_ylim(-3, 3)
    ax.set_xlabel("lattice constant a (Å)")
    ax.set_ylabel("E − (Birch–Murnaghan fit) (meV/atom)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=8)
    ax = axs[1]
    n, a0 = [], []
    for lo, hi in wins:
        sel = window(a, lo, hi)
        c = np.polyfit(a[sel], E[sel], 2)
        n.append(sel.sum())
        a0.append(-c[1] / (2 * c[0]))
    ax.plot(n, a0, "o-", color=YELLOW, ms=5, label="quadratic fit")
    ax.axhline(a_of(f["V0"]), color=GRAY, ls="--", lw=1.0, label="Birch–Murnaghan (13 points)")
    ax.set_xticks(n)
    ax.set_xlabel("number of points in the fit (window centred at 3.63 Å)")
    ax.set_ylabel("a0 (Å)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=8)
    fig.tight_layout()
    fig.savefig(figdir / "quadratic_fit.png", dpi=200)
    plt.close(fig)


def fig_cutoff_vcrelax(data, figdir):
    rows = cutoff_rows(data)
    vcs = {j["a"]: j for (c, e, _), j in data.items() if c == "vc-relax" and e == 60.0 and j["a"] in START_COL}
    if len(rows) < 2 or not vcs:
        return
    fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.3))
    ax = axs[0]
    ec = [r[0] for r in rows]
    ax.plot(ec, [r[2] for r in rows], "o-", color=BLUE, ms=5, label="energy curve (Birch–Murnaghan)")
    ax.plot(ec, [r[4] for r in rows], "s--", color=AQUA, ms=5, label="SCF pressure = 0")
    vc = [(r[0], r[6]) for r in rows if r[6] is not None]
    ax.plot(*zip(*vc), "D:", color=YELLOW, ms=5, label="vc-relax from 3.64 Å")
    ax.set_xticks(ec)
    ax.set_xlabel("plane-wave cutoff (Ry)")
    ax.set_ylabel("lattice constant (Å)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=8)
    ax = axs[1]
    e60 = [r for r in rows if r[0] == 60.0]
    for a_start, j in sorted(vcs.items()):
        steps = np.arange(len(j["traj_a"]))
        ax.plot(steps, j["traj_a"], "o-", color=START_COL.get(a_start, BLUE), ms=4,
                label=f"from {a_start:.2f} Å")
    if e60:
        ax.axhline(e60[0][2], color=GRAY, ls="--", lw=1.0, label="energy curve (60 Ry)")
    ax.set_ylim(3.62, 3.64)
    ax.set_xlabel("SCF cycle of vc-relax (60 Ry)")
    ax.set_ylabel("lattice constant (Å)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(figdir / "cutoff_vcrelax.png", dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="ZIP files or folders")
    ap.add_argument("--figures", default="figures", help="folder for the figures (default: figures)")
    args = ap.parse_args()
    data = load_jobs(args.paths)
    table_scan(data)
    table_eos(data)
    table_cutoff(data)
    table_vcrelax(data)
    figdir = Path(args.figures)
    figdir.mkdir(parents=True, exist_ok=True)
    fig_eos(data, figdir)
    fig_quadratic(data, figdir)
    fig_cutoff_vcrelax(data, figdir)
    print(f"Figures written to {figdir}/")


if __name__ == "__main__":
    main()
