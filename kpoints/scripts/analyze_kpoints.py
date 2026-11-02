"""Analyze the k-point convergence example from Quantum ESPRESSO jobs downloaded from Quloud.

Pass the ZIP files downloaded from the job pages of Quloud ("一括ダウンロード" of
the output files), folders holding them, or their extracted contents. A job is
an output of pw.x (a file holding "Program PWSCF") with the copy of its input
in the same folder (a file holding "K_POINTS"). The file names do not matter;
each job is recognized from its contents:

* element and number of atoms, lattice constant (the cubic lattice constant
  "lattice parameter (alat)" of an fcc cell written with ibrav = 2),
* k-point mesh n (K_POINTS automatic n n n 0 0 0 in the input),
* occupations: smearing width, tetrahedron method (Bloechl, optimized or
  linear), or fixed occupations.

The script prints the numbers quoted in the article and writes the figures for
the jobs it finds; parts that need missing jobs are skipped.

Usage: python analyze_kpoints.py <zip or folder> [...] [--figures DIR]
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

CU, SI = "#2a78d6", "#eb6834"
TETRA_COL = {"tetra": "#1baf7a", "tetra_opt": "#eda100"}
OCC_LABEL = {"tetra": "tetrahedra (Bloechl)", "tetra_opt": "tetrahedra_opt", "tetra_lin": "tetrahedra_lin"}
WIDTH_COL = {0.005: "#86b6ef", 0.01: "#3987e5", 0.02: "#1c5cab", 0.04: "#0d366b"}
A_COL = {3.60: "#86b6ef", 3.64: "#2a78d6", 3.68: "#0d366b"}
INK, MUTED = "#0b0b0b", "#52514e"

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


def parse_job(inp, out):
    """The quantities of one SCF job, or None if it is not a finished SCF of a cubic cell."""
    if "JOB DONE." not in out or "convergence has been achieved" not in out:
        return None
    if last(r"bravais-lattice index\s*=\s*(-?\d+)", out, int) != 2:
        return None
    m = re.search(r"K_POINTS\s*\{?\s*automatic\s*\}?\s*\n\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d)\s+(\d)\s+(\d)",
                  inp or "", re.I)
    if not m or len(set(m.groups()[:3])) != 1 or any(int(x) for x in m.groups()[3:]):
        return None
    species = re.search(r"atomic species\s+valence\s+mass\s+pseudopotential\s*\n\s*(\w+)", out)
    width = last(r"smearing, width \(Ry\)=\s*([\d.]+)", out)
    if "(tetrahedron method)" in out:
        occ = ("tetra_opt" if "Optimized tetrahedron method" in out
               else "tetra_lin" if "Linear tetrahedron method" in out else "tetra")
    else:
        occ = width or 0.0  # smearing width in Ry, or 0.0 for fixed occupations
    kpts = re.search(r"number of k points=\s*(\d+).*?\n\s*cart\. coord\. in units 2pi/alat\n(.*?)\n\s*\n", out, re.S)
    klist = [tuple(map(float, re.findall(r"[-\d.]+", line)[1:])) for line in kpts.group(2).splitlines()]
    wall = re.search(r"PWSCF\s+:.*?CPU\s+(?:(\d+)h\s*)?(?:(\d+)m\s*)?([\d.]+)s WALL", out)
    e = last(r"^!\s+total energy\s+=\s+([-\d.]+)\s+Ry", out)
    return {
        "element": species.group(1),
        "nat": last(r"number of atoms/cell\s*=\s*(\d+)", out, int),
        "a": round(last(r"lattice parameter \(alat\)\s*=\s*([\d.]+)", out) * BOHR, 3),
        "n": int(m.group(1)),
        "width": width or 0.0,
        "occ": occ,
        "E": e,  # free energy F with smearing
        "U": last(r"internal energy E=F\+TS\s+=\s+([-\d.]+)\s+Ry", out) if width else e,
        "P": last(r"P=\s*([-\d.]+)", out),
        "EF": last(r"the Fermi energy is\s+([-\d.]+)\s+ev", out),
        "nk": int(kpts.group(1)),
        "klist": klist,  # (kx, ky, kz, weight); kx..kz in 2pi/alat, weights sum to 2
        "nsym": last(r"(\d+) Sym\. Ops\.", out, int),
        "wall": int(wall.group(1) or 0) * 3600 + int(wall.group(2) or 0) * 60 + float(wall.group(3)),
    }


def load_jobs(paths):
    data, seen = {}, set()
    print("Jobs found:")
    for label, inp, out in find_jobs(paths):
        j = parse_job(inp, out)
        if j is None:
            print(f"  {label}: not a finished SCF of an fcc cell (ibrav = 2) with an unshifted mesh, skipped")
            continue
        key = (j["element"], j["a"], j["occ"], j["n"])
        if key in seen:
            print(f"  {label}: same conditions as a job above, skipped")
            continue
        seen.add(key)
        occ = occ_label(j["occ"])
        print(f"  {label}: {j['element']}{j['nat']} a = {j['a']:.2f} A, {j['n']}^3 mesh, {occ},"
              f" {j['nk']} k-points, {j['nsym']} sym. ops.")
        data[key] = j
    print(f"{len(data)} jobs\n")
    return data


def occ_label(occ):
    if isinstance(occ, str):
        return OCC_LABEL[occ]
    return f"MV {occ:g} Ry" if occ else "fixed"


def series(data, el, a, occ):
    """{n: job} for one element, lattice constant and occupations (smearing width,
    0.0 for fixed occupations, or "tetra", "tetra_opt", "tetra_lin")."""
    return dict(sorted((k[3], j) for k, j in data.items() if k[:3] == (el, a, occ)))


def emev(j):
    """Energy per atom in meV."""
    return j["E"] * RY_MEV / j["nat"]


# --- tables ------------------------------------------------------------------------

def table_kpoints(data):
    cu, si = series(data, "Cu", 3.64, 0.02), series(data, "Si", 5.47, 0.0)
    ns = sorted(set(cu) | set(si))
    if not ns:
        return
    print("Table: k-points of the n x n x n mesh (Cu 3.64 A MV 0.02 Ry, Si 5.47 A fixed)")
    print("   n    n^3  irreducible   wall time (s): Cu     Si")
    for n in ns:
        nk = (cu.get(n) or si.get(n))["nk"]
        w = [f"{s[n]['wall']:6.1f}" if n in s else "     -" for s in (cu, si)]
        print(f"  {n:2d} {n**3:6d} {nk:8d}       {w[0]:>16s} {w[1]}")
    if 4 in cu:
        print("\nTable: irreducible k-points of the 4 x 4 x 4 mesh of Cu (cart. coord. in 2pi/a)")
        print("        kx      ky      kz    weight  points of the mesh")
        for kx, ky, kz, wk in cu[4]["klist"]:
            print(f"   {kx:7.3f} {ky:7.3f} {kz:7.3f}   {wk / 2:7.5f}  {wk / 2 * 64:4.0f}")
    print()


def converged_from(ns, err, tol):
    """Smallest n such that |err| <= tol for this n and every larger n in the list."""
    ok = None
    for n, e in sorted(zip(ns, err), reverse=True):
        if abs(e) > tol:
            break
        ok = n
    return ok


def table_energy(data):
    for el, a, w, nat_label in (("Cu", 3.64, 0.02, "MV 0.02 Ry"), ("Si", 5.47, 0.0, "fixed")):
        s = series(data, el, a, w)
        if len(s) < 2:
            continue
        nref = max(s)
        print(f"{el} {a:.2f} A ({nat_label}): E(n) - E({nref}^3) (meV/atom), P (kbar)")
        for n, j in s.items():
            ef = j["EF"] if j["EF"] is not None else float("nan")
            print(f"  {n:2d}  {emev(j) - emev(s[nref]):10.3f}   P = {j['P']:8.2f}   EF = {ef:7.3f} eV")
        ns = [n for n in s if n != nref]
        for tol in (1.0, 0.1):
            print(f"  |E(n) - E(ref)| <= {tol} meV/atom from n = "
                  f"{converged_from(ns, [emev(s[n]) - emev(s[nref]) for n in ns], tol)}")
        print()


def table_smearing(data):
    widths = sorted(w for w in WIDTH_COL if series(data, "Cu", 3.64, w))
    if not widths:
        return
    s0 = series(data, "Cu", 3.64, widths[0])
    ref = emev(s0[max(s0)])
    print(f"Cu 3.64 A, MV smearing: F(n) - F(width {widths[0]} Ry, {max(s0)}^3) (meV/atom)")
    ns = sorted({n for w in widths for n in series(data, "Cu", 3.64, w) if n >= 8})
    print("   n " + "".join(f"{w:>10g}" for w in widths))
    for n in ns:
        row = []
        for w in widths:
            s = series(data, "Cu", 3.64, w)
            row.append(f"{emev(s[n]) - ref:10.3f}" if n in s else "         -")
        print(f"  {n:2d} " + "".join(row))
    print("\nAt the densest mesh of each width:  F, U = F + TS, -TS (meV/atom, from F of the first row), P (kbar)")
    for w in widths:
        s = series(data, "Cu", 3.64, w)
        j = s[max(s)]
        u = j["U"] * RY_MEV / j["nat"]
        print(f"  {w:5g} Ry ({max(s)}^3):  F {emev(j) - ref:7.3f}   U {u - ref:7.3f}"
              f"   -TS {emev(j) - u:7.3f}   P {j['P']:7.2f}")
    print()


def table_differences(data):
    cu, si = (3.60, 3.64, 3.68), (5.42, 5.47, 5.52)
    for el, (a_lo, a0, a_hi), w in (("Cu", cu, 0.02), ("Cu", cu, "tetra"), ("Cu", cu, "tetra_opt"),
                                    ("Si", si, 0.0)):
        lo, mid, hi = (series(data, el, a, w) for a in (a_lo, a0, a_hi))
        ns = [n for n in mid if n in lo and n in hi]
        if not ns:
            continue
        print(f"{el} ({occ_label(w)}): energy differences (meV/atom) and pressure (kbar)")
        print(f"   n   E({a_lo})-E({a0})  E({a_hi})-E({a0})    P({a_lo})  P({a0})  P({a_hi})")
        for n in ns:
            print(f"  {n:2d}  {emev(lo[n]) - emev(mid[n]):14.3f} {emev(hi[n]) - emev(mid[n]):14.3f}"
                  f"   {lo[n]['P']:8.2f} {mid[n]['P']:8.2f} {hi[n]['P']:8.2f}")
        nref = max(ns)
        dpda = (hi[nref]["P"] - lo[nref]["P"]) / (a_hi - a_lo)
        print(f"  dP/da at {nref}^3: {dpda:.0f} kbar/A, i.e. {abs(dpda) * 1e-3:.2f} kbar per 0.001 A")
        rest = [n for n in ns if n != nref]
        for name, f, tol in (
                (f"E({a_lo})-E({a0})", lambda n: emev(lo[n]) - emev(mid[n]), 0.1),
                (f"E({a_hi})-E({a0})", lambda n: emev(hi[n]) - emev(mid[n]), 0.1),
                (f"P({a0})", lambda n: mid[n]["P"], 0.5),
                (f"P({a0})", lambda n: mid[n]["P"], 0.2)):
            print(f"  |{name}(n) - same at {nref}^3| <= {tol} from n = "
                  f"{converged_from(rest, [f(n) - f(nref) for n in rest], tol)}")
        print()


def table_tetra(data):
    occs = [o for o in (0.02, "tetra", "tetra_opt") if len(series(data, "Cu", 3.64, o)) > 1]
    if not any(isinstance(o, str) for o in occs):
        return
    opt = series(data, "Cu", 3.64, "tetra_opt")
    ref = emev(opt[max(opt)]) if opt else None
    print("Cu 3.64 A, smearing and tetrahedron methods:")
    print("  E(n) - E(ref of the same method), P (kbar), wall time (s)")
    print("   n " + "".join(f"{occ_label(o):>30s}" for o in occs))
    ss = [series(data, "Cu", 3.64, o) for o in occs]
    for n in sorted({n for s in ss for n in s if n >= 8}):
        print(f"  {n:2d} " + "".join(
            f"{emev(s[n]) - emev(s[max(s)]):12.3f} {s[n]['P']:8.2f} {s[n]['wall']:7.1f} " if n in s
            else " " * 30 for s in ss))
    for o, s in zip(occs, ss):
        ns = [n for n in s if n != max(s)]
        err = [emev(s[n]) - emev(s[max(s)]) for n in ns]
        line = f"  {occ_label(o)}: |E(n) - E({max(s)}^3)| <= 1 meV/atom from n = {converged_from(ns, err, 1.0)}," \
               f" <= 0.1 from n = {converged_from(ns, err, 0.1)}"
        if ref is not None:
            line += f"; E({max(s)}^3) - E(tetrahedra_opt {max(opt)}^3) = {emev(s[max(s)]) - ref:.3f} meV/atom"
        print(line)
    print()


# --- figures -----------------------------------------------------------------------

def fig_energy(data, figdir):
    cu, si = series(data, "Cu", 3.64, 0.02), series(data, "Si", 5.47, 0.0)
    if len(cu) < 2 or len(si) < 2:
        return
    fig, ax = plt.subplots(figsize=(5.4, 3.5))
    for s, col, lab in ((cu, CU, "Cu (metal, MV 0.02 Ry)"), (si, SI, "Si (semiconductor, fixed occ.)")):
        nref = max(s)
        ns = np.array([n for n in s if n != nref])
        d = np.array([emev(s[n]) - emev(s[nref]) for n in ns])
        ax.semilogy(ns, np.abs(d), color=col, lw=1.2, label=lab)
        ax.scatter(ns[d > 0], np.abs(d[d > 0]), color=col, s=24, zorder=3)
        ax.scatter(ns[d <= 0], np.abs(d[d <= 0]), facecolor="white", edgecolor=col, s=24, lw=1.2, zorder=3)
    ax.axhline(1.0, color=MUTED, ls=":", lw=0.8)
    ax.set_xlabel("k-point mesh n (n × n × n)")
    ax.set_ylabel("|E(n) − E(ref)| (meV/atom)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(figdir / "energy_convergence.png", dpi=200)
    plt.close(fig)


def fig_smearing(data, figdir):
    widths = [w for w in WIDTH_COL if series(data, "Cu", 3.64, w)]
    if len(widths) < 2:
        return
    s0 = series(data, "Cu", 3.64, widths[0])
    ref = emev(s0[max(s0)])
    fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.3))
    for w in widths:
        s = series(data, "Cu", 3.64, w)
        ns = [n for n in s if n >= 8]
        axs[0].plot(ns, [emev(s[n]) - ref for n in ns], "o-", color=WIDTH_COL[w], ms=4, label=f"{w:g} Ry")
        axs[1].plot(ns, [s[n]["P"] for n in ns], "o-", color=WIDTH_COL[w], ms=4)
    axs[0].axhline(0, color=MUTED, lw=0.8)
    axs[0].set_ylim(-2, 6)
    axs[0].set_ylabel(f"F(n) − F({widths[0]:g} Ry, {max(s0)}³) (meV/atom)")
    axs[1].set_ylim(-13, -10)
    axs[1].set_ylabel("pressure (kbar)")
    for ax in axs:
        ax.set_xlabel("k-point mesh n")
        ax.set_xlim(6, 50)
    fig.legend(*axs[0].get_legend_handles_labels(), loc="upper center", ncol=4, fontsize=8,
               title="MV smearing width", title_fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.85))
    fig.savefig(figdir / "smearing.png", dpi=200)
    plt.close(fig)


def fig_quantities(data, figdir):
    lo, mid, hi = (series(data, "Cu", a, 0.02) for a in (3.60, 3.64, 3.68))
    ns = [n for n in mid if n in lo and n in hi and n >= 8]
    if not ns:
        return
    nref = max(ns)
    fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.3))
    ax = axs[0]
    ax.plot(ns, [emev(mid[n]) - emev(mid[nref]) for n in ns], "o-", color="#898781", ms=4,
            label="total energy E(3.64 Å)")
    for s, a in ((lo, 3.60), (hi, 3.68)):
        d = [emev(s[n]) - emev(mid[n]) for n in ns]
        ax.plot(ns, [x - d[-1] for x in d], "s-", color=A_COL[a], ms=4, label=f"E({a:.2f} Å) − E(3.64 Å)")
    ax.set_ylim(-3, 6)
    ax.set_ylabel(f"deviation from the {nref}³ value (meV/atom)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=1, fontsize=8)
    ax = axs[1]
    for s, a in ((lo, 3.60), (mid, 3.64), (hi, 3.68)):
        ax.plot(ns, [s[n]["P"] - s[nref]["P"] for n in ns], "o-", color=A_COL[a], ms=4, label=f"P({a:.2f} Å)")
    ax.set_ylim(-3, 3)
    ax.set_ylabel(f"deviation from the {nref}³ value (kbar)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, fontsize=8)
    for ax in axs:
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_xlabel("k-point mesh n")
    fig.tight_layout()
    fig.savefig(figdir / "energy_difference_pressure.png", dpi=200)
    plt.close(fig)


def fig_tetra(data, figdir):
    opt = series(data, "Cu", 3.64, "tetra_opt")
    occs = [o for o in (0.02, "tetra", "tetra_opt") if len(series(data, "Cu", 3.64, o)) > 1]
    if not opt or len(occs) < 2:
        return
    ref = emev(opt[max(opt)])
    style = {0.02: (CU, "o", "MV smearing 0.02 Ry"), "tetra": (TETRA_COL["tetra"], "s", "tetrahedra (Blöchl)"),
             "tetra_opt": (TETRA_COL["tetra_opt"], "D", "tetrahedra_opt")}
    fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.3))
    for o in occs:
        col, mk, lab = style[o]
        s = series(data, "Cu", 3.64, o)
        ns = [n for n in s if n >= 8]
        axs[0].plot(ns, [emev(s[n]) - ref for n in ns], "-", marker=mk, color=col, ms=4, label=lab)
        axs[1].plot(ns, [s[n]["P"] for n in ns], "-", marker=mk, color=col, ms=4)
    axs[0].axhline(0, color=MUTED, lw=0.8)
    axs[0].set_ylim(-4, 6)
    axs[0].set_ylabel(f"E(n) − E(tetrahedra_opt, {max(opt)}³) (meV/atom)")
    axs[1].set_ylim(-12.8, -10.8)
    axs[1].set_ylabel("pressure (kbar)")
    for ax in axs:
        ax.set_xlabel("k-point mesh n")
        ax.set_xlim(6, 50)
    fig.legend(*axs[0].get_legend_handles_labels(), loc="upper center", ncol=3, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(figdir / "tetrahedra.png", dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="ZIP files or folders")
    ap.add_argument("--figures", default="figures", help="folder for the figures (default: figures)")
    args = ap.parse_args()
    data = load_jobs(args.paths)
    table_kpoints(data)
    table_energy(data)
    table_smearing(data)
    table_differences(data)
    table_tetra(data)
    figdir = Path(args.figures)
    figdir.mkdir(parents=True, exist_ok=True)
    fig_energy(data, figdir)
    fig_smearing(data, figdir)
    fig_quantities(data, figdir)
    fig_tetra(data, figdir)
    print(f"Figures written to {figdir}/")


if __name__ == "__main__":
    main()
