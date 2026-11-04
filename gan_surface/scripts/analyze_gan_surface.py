"""Surface phase diagram of GaN(0001) under MOVPE conditions from Quantum ESPRESSO and Psi4 jobs.

Pass the ZIP files downloaded from the job pages of Quloud ("一括ダウンロード" of the
output files), folders holding them, or their extracted contents. The file names do
not matter; each job is recognized from its contents:

* Quantum ESPRESSO (an output of pw.x holding "Program PWSCF", with the copy of its
  input holding "K_POINTS" in the same folder):
  - the Ga atom: one Ga atom and nothing else. The spin-polarized one (nspin = 2)
    is the reference; a non-spin-polarized one, if any, is only compared with it,
  - the H2 molecule: two H atoms and nothing else,
  - surface slabs: structures holding N. The slab without adsorbed H and with the
    fewest Ga atoms is the ideal surface; the others are classified by the excess
    Ga and H atoms. Species other than Ga, N and H (here "Hn", the pseudo-hydrogen
    passivating the bottom) are counted as part of the slab.
* Psi4 (an output holding "Freq [cm^-1]"): the harmonic frequency and the rotational
  constant of the H2 molecule.

The script prints the numbers quoted in the article and writes the figures.

Usage: python analyze_gan_surface.py <zip or folder> [...] [--figures DIR]
"""
import argparse
import math
import re
import zipfile
from pathlib import Path, PurePosixPath

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle, Patch, Polygon

RY_EV = 13.605693122994
KB = 1.380649e-23  # J/K
H_PLANCK = 6.62607015e-34  # J s
C_LIGHT = 2.99792458e10  # cm/s
AMU = 1.66053906660e-27  # kg
EV = 1.602176634e-19  # J
ATM = 101325.0  # Pa

MASS = {"Ga": 69.723, "H": 1.00794}  # standard atomic weights

# Growth conditions of Kusaba et al., JJAP 56, 070304 (2017), Fig. 2
P_TOT, P_NH3, ALPHA = 1.0, 0.5, 0.25  # atm, atm, NH3 decomposition ratio
T_C = np.arange(900.0, 1300.0 + 1e-9, 2.0)  # growth temperature (deg C)
V_III = np.arange(500.0, 5000.0 + 1e-9, 25.0)  # p0_NH3 / p0_TMG

INK, MUTED = "#0b0b0b", "#52514e"
PHASE_COL = {"Ideal": "#2a5bd7", "Ga adatom": "#e0412f", "3Ga-H": "#1baf5a"}
ATOM_COL = {"Ga": "#c49a8c", "N": "#2a4fd6", "H": "#ffffff", "Hn": "#b9b9b9"}
ATOM_R = {"Ga": 0.62, "N": 0.45, "H": 0.30, "Hn": 0.25}

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "legend.frameon": False, "lines.linewidth": 1.4,
})


# --- finding and reading jobs ------------------------------------------------------

def find_groups(paths):
    """(label, {file name: text}) for every folder in the ZIP files and folders."""
    groups = []
    skip = (".upf", ".dat", ".xml", ".zip")

    def add_zip(zpath):
        zf = zipfile.ZipFile(zpath)
        folders = {}
        for n in zf.namelist():
            if n.endswith("/") or n.lower().endswith(skip):
                continue
            folders.setdefault(PurePosixPath(n).parent, []).append(n)
        for parent, members in sorted(folders.items()):
            texts = {PurePosixPath(m).name: zf.read(m).decode(errors="replace") for m in members}
            groups.append((f"{zpath}" + ("" if str(parent) == "." else f":{parent}"), texts))

    for p in map(Path, paths):
        if p.is_file() and p.suffix.lower() == ".zip":
            add_zip(p)
        elif p.is_dir():
            for z in sorted(p.rglob("*.zip")):
                add_zip(z)
            for d in sorted({f.parent for f in p.rglob("*") if f.is_file() and f.suffix.lower() != ".zip"}):
                texts = {f.name: f.read_text(errors="replace") for f in d.iterdir()
                         if f.is_file() and f.stat().st_size < 50_000_000 and f.suffix.lower() not in skip}
                groups.append((str(d), texts))
        else:
            raise SystemExit(f"Not a ZIP file or a folder: {p}")
    return groups


def parse_qe(label, inp, out):
    """Composition, energy and final structure of a pw.x job."""
    nat = int(re.search(r"\bnat\s*=\s*(\d+)", inp).group(1))
    block = inp.split("ATOMIC_POSITIONS")[1].splitlines()[1:nat + 1]
    species = [line.split()[0] for line in block]

    energies = re.findall(r"^!\s+total energy\s+=\s+(-?\d+\.\d+) Ry", out, re.M)
    if not energies:
        raise SystemExit(f"{label}: no final total energy ('!' line)")
    free = float(energies[-1])  # Ry; with smearing this is F = E - TS
    smear = re.findall(r"smearing contrib\. \(-TS\)\s+=\s+(-?\d+\.\d+) Ry", out)
    # Gaussian smearing: (F + E)/2 approximates the energy at zero smearing width.
    e0 = free - 0.5 * float(smear[-1]) if smear else free

    relax = re.search(r"calculation\s*=\s*'relax'", inp) is not None
    if relax:
        ok = "End of BFGS Geometry Optimization" in out and "bfgs converged" in out
    else:
        ok = "convergence has been achieved" in out
    ok = ok and "convergence NOT achieved" not in out

    cell = None
    m = re.search(r"CELL_PARAMETERS\s*\(?angstrom\)?\s*\n(.*\n.*\n.*\n)", inp)
    if m:
        cell = np.array([[float(v) for v in row.split()] for row in m.group(1).strip().splitlines()])
    pos = None
    if relax and "Begin final coordinates" in out:
        fin = out.split("Begin final coordinates")[1].split("End final coordinates")[0]
        rows = [r.split() for r in fin.split("ATOMIC_POSITIONS")[1].splitlines()[1:nat + 1]]
        pos = np.array([[float(v) for v in r[1:4]] for r in rows])
    elif "angstrom" in inp.split("ATOMIC_POSITIONS")[1].splitlines()[0]:
        pos = np.array([[float(v) for v in line.split()[1:4]] for line in block])
    m = re.search(r"\bnspin\s*=\s*(\d)", inp)
    nspin = int(m.group(1)) if m else 1
    return dict(label=label, species=species, energy_ry=e0, free_ry=free, nspin=nspin,
                smear_ry=float(smear[-1]) if smear else 0.0, ok=ok, relax=relax, cell=cell, pos=pos)


def parse_psi4(label, out):
    """Harmonic frequencies and the rotational constant B of a linear molecule."""
    freqs = [float(v) for line in re.findall(r"Freq \[cm\^-1\]\s+(.*)", out) for v in line.split()]
    rot = re.search(r"Rotational constants:.*?B =\s+([\d.]+)\s+C =\s+([\d.]+) \[cm\^-1\]", out)
    geom = out.split("==> Harmonic Vibrational Analysis <==")[0]
    return dict(label=label, freqs=freqs, B=float(rot.group(1)),
                ok="Psi4 exiting successfully" in out or "FINAL ENERGY" in out,
                geometry=geom)


def collect(paths):
    qe, psi4 = [], []
    for label, texts in find_groups(paths):
        outs = [t for t in texts.values() if "Program PWSCF" in t]
        ins = [t for t in texts.values() if "K_POINTS" in t and "Program PWSCF" not in t]
        for out in outs:
            if len(ins) != 1:
                raise SystemExit(f"{label}: expected one QE input next to the output, found {len(ins)}")
            qe.append(parse_qe(label, ins[0], out))
        for name, t in texts.items():
            if "Freq [cm^-1]" in t:
                psi4.append(parse_psi4(f"{label}:{name}", t))
    return qe, psi4


# --- surface models ----------------------------------------------------------------

def count(species):
    c = {}
    for s in species:
        c[s] = c.get(s, 0) + 1
    return c


def adatom_site(job):
    """'T4', 'H3' or 'top' from the in-plane position of the highest Ga atom."""
    sp, pos, cell = job["species"], job["pos"], job["cell"]
    ga = [i for i, s in enumerate(sp) if s == "Ga"]
    ad = max(ga, key=lambda i: pos[i, 2])
    inv = np.linalg.inv(cell[:2, :2])
    below = []
    for i, s in enumerate(sp):
        if i == ad or pos[i, 2] >= pos[ad, 2]:
            continue
        frac = (pos[i, :2] - pos[ad, :2]) @ inv
        frac -= np.round(frac)
        d = np.linalg.norm(frac @ cell[:2, :2])
        if d < 0.6:
            below.append((pos[i, 2], s))
    if not below:
        return "H3"
    return "T4" if max(below)[1] == "N" else "top"


def classify(qe):
    gas = {}
    slabs = []
    ga_atoms = []
    for j in qe:
        c = count(j["species"])
        if c == {"Ga": 1}:
            ga_atoms.append(j)
        elif c == {"H": 2}:
            gas["H2"] = j
        elif "N" in c:
            slabs.append((c, j))
    if ga_atoms:
        gas["Ga"] = max(ga_atoms, key=lambda j: j["nspin"])
        others = [j for j in ga_atoms if j is not gas["Ga"]]
        if others:
            gas["Ga (nspin=1)"] = others[0]
    plain = [(c, j) for c, j in slabs if c.get("H", 0) == 0]
    if not plain:
        raise SystemExit("No ideal slab (a slab without adsorbed H) was found")
    c_ideal, ideal = min(plain, key=lambda cj: cj[0]["Ga"])
    models = {"Ideal": dict(job=ideal, dGa=0, dH=0)}
    extra = []
    for c, j in slabs:
        if j is ideal:
            continue
        rest = {k: v for k, v in c.items() if k not in ("Ga", "H")}
        if rest != {k: v for k, v in c_ideal.items() if k not in ("Ga", "H")}:
            raise SystemExit(f"{j['label']}: the slab below the surface differs from the ideal slab")
        dGa, dH = c["Ga"] - c_ideal["Ga"], c.get("H", 0)
        if (dGa, dH) == (1, 0):
            name = f"Ga adatom ({adatom_site(j)})"
        elif (dGa, dH) == (0, 3):
            name = "3Ga-H"
        else:
            name = f"Ga{dGa:+d} H{dH}"
        if name in models:
            raise SystemExit(f"Two slabs are classified as {name}: {models[name]['job']['label']}, {j['label']}")
        models[name] = dict(job=j, dGa=dGa, dH=dH)
    return gas, models


# --- ideal-gas chemical potentials (Kusaba et al. Eqs. 11-14) ------------------------

def mu_tilde(T, p_atm, mass_amu, g=1, sigma=None, B_cm=None, freqs_cm=()):
    """Finite-temperature part of the chemical potential (eV): mu = E(0 K) + mu_tilde."""
    T = np.asarray(T, dtype=float)
    kT = KB * T
    lnq = np.log(kT / (p_atm * ATM)) + 1.5 * np.log(2 * math.pi * mass_amu * AMU * kT / H_PLANCK ** 2)
    lnq = lnq + math.log(g)
    if B_cm is not None:  # linear rotor
        lnq = lnq + np.log(kT / (sigma * H_PLANCK * C_LIGHT * B_cm))
    for nu in freqs_cm:  # without the zero-point factor, as in Eq. (14)
        lnq = lnq - np.log1p(-np.exp(-H_PLANCK * C_LIGHT * nu / kT))
    return -kT * lnq / EV


def decomposed_pressures(v_iii, F):
    """Partial pressures at the growth section (atm), Eqs. (4)-(8). F: H2 fraction of the carrier."""
    p_tmg = P_NH3 / v_iii
    carrier = P_TOT - P_NH3 - p_tmg
    raw = dict(Ga=p_tmg, CH4=3 * p_tmg, NH3=(1 - ALPHA) * P_NH3,
               N2=(1 - F) * carrier + 0.5 * ALPHA * P_NH3, H2=F * carrier + 1.5 * ALPHA * P_NH3)
    c = P_TOT / sum(raw.values())
    return {k: v * c for k, v in raw.items()}


class Thermo:
    def __init__(self, h2_freq, h2_B):
        self.h2 = dict(mass_amu=2 * MASS["H"], sigma=2, B_cm=h2_B, freqs_cm=(h2_freq,))
        self.ga = dict(mass_amu=MASS["Ga"], g=2)  # 2P1/2 ground state

    def mu_ga(self, T, p):
        return mu_tilde(T, p, **self.ga)

    def mu_h2(self, T, p):
        return mu_tilde(T, p, **self.h2)


def delta_g(models, eads, thermo, T_K, p):
    """Gibbs energy of each model relative to the ideal surface (eV per 2x2 cell), Eq. (10)."""
    return {name: eads[name] - m["dGa"] * thermo.mu_ga(T_K, p["Ga"]) - 0.5 * m["dH"] * thermo.mu_h2(T_K, p["H2"])
            for name, m in models.items()}


def phase_map(names, models, eads, thermo, F):
    idx = np.zeros((len(V_III), len(T_C)), dtype=int)
    T_K = T_C + 273.15
    for i, v in enumerate(V_III):
        g = delta_g({n: models[n] for n in names}, eads, thermo, T_K, decomposed_pressures(v, F))
        idx[i] = np.argmin(np.vstack([g[n] for n in names]), axis=0)
    return idx


def transitions(names, models, eads, thermo, F, v):
    T_fine = np.arange(900.0, 1300.0 + 1e-9, 0.5)
    g = delta_g({n: models[n] for n in names}, eads, thermo, T_fine + 273.15, decomposed_pressures(v, F))
    k = np.argmin(np.vstack([g[n] for n in names]), axis=0)
    out = [f"{names[k[0]]}"]
    for i in range(1, len(k)):
        if k[i] != k[i - 1]:
            out.append(f"-> {names[k[i]]} at {T_fine[i]:.0f} C")
    return " ".join(out)


# --- figures -----------------------------------------------------------------------

def draw_top(ax, job):
    """Top view of the topmost Ga-N bilayer and the adsorbates in one 2x2 cell.

    Atoms above the topmost N layer are drawn; the N atoms of that layer are drawn
    smaller and lighter, and adsorbates (atoms more than 1 angstrom above the top
    Ga layer, and H) with a thick outline.
    """
    sp, pos, cell = job["species"], job["pos"], job["cell"]
    a1, a2 = cell[0, :2], cell[1, :2]
    z_n = max(r[2] for s, r in zip(sp, pos) if s == "N")
    z_ga = np.median([r[2] for s, r in zip(sp, pos) if s == "Ga" and r[2] > z_n])
    inv = np.linalg.inv(cell[:2, :2])
    items = []
    for s, r in zip(sp, pos):
        if r[2] < z_n - 0.3:
            continue
        f = r[:2] @ inv
        f -= np.floor(f)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                g = f + (di, dj)
                if -0.08 <= g[0] <= 1.08 and -0.08 <= g[1] <= 1.08:
                    items.append((r[2], s, g @ cell[:2, :2]))
    for z, s, xy in sorted(items, key=lambda t: t[0]):
        ads = s == "H" or z > z_ga + 1.0
        low = s == "N"
        ax.add_patch(Circle(xy, ATOM_R[s] * (0.8 if low else 1.0), facecolor=ATOM_COL[s],
                            edgecolor=INK if ads else "#333333", linewidth=1.6 if ads else 0.5,
                            alpha=0.75 if low else 1.0))
    ax.add_patch(Polygon([(0, 0), a1, a1 + a2, a2], closed=True, fill=False, edgecolor=MUTED, linewidth=0.8))
    ax.set_aspect("equal")
    ax.set_xlim(a2[0] - 0.9, a1[0] + 0.9)
    ax.set_ylim(-0.9, a2[1] + 0.9)
    ax.axis("off")


def draw_side(ax, job, height=None):
    """Side view projected along a2 (horizontal: fractional coordinate along a1).

    `height` (angstrom) fixes the vertical range so that several panels share a scale.
    """
    sp, pos, cell = job["species"], job["pos"], job["cell"]
    inv = np.linalg.inv(cell[:2, :2])
    L = np.linalg.norm(cell[0])
    items = []
    for s, r in zip(sp, pos):
        f = (r[:2] @ inv)[0] % 1.0
        for g in (f - 1, f, f + 1):
            if -0.06 <= g <= 1.06:
                items.append((r[1], s, g * L, r[2]))
    for _, s, x, z in sorted(items, key=lambda t: -t[0]):
        ax.add_patch(Circle((x, z), ATOM_R[s], facecolor=ATOM_COL[s], edgecolor="#333333", linewidth=0.5))
    zmin, zmax = pos[:, 2].min(), pos[:, 2].max()
    ax.set_aspect("equal")
    ax.set_xlim(-0.8, L + 0.8)
    ax.set_ylim(zmin - 0.8, zmin - 0.8 + (height or zmax - zmin + 1.7))
    ax.axis("off")


def fig_models(models, names, figdir):
    fig, axes = plt.subplots(2, len(names), figsize=(2.2 * len(names), 5.6),
                             gridspec_kw=dict(height_ratios=[1, 1.5]))
    height = max(np.ptp(models[n]["job"]["pos"][:, 2]) for n in names) + 1.7
    for k, name in enumerate(names):
        draw_top(axes[0, k], models[name]["job"])
        draw_side(axes[1, k], models[name]["job"], height)
        axes[0, k].set_title(name, fontsize=10)
    handles = [Patch(facecolor=ATOM_COL[s], edgecolor="#333333", label=lab) for s, lab in
               (("Ga", "Ga"), ("N", "N"), ("H", "H"), ("Hn", "pseudo-H (Z = 0.75)"))]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(figdir / "models.png", dpi=200)
    plt.close(fig)


def plot_phase(ax, idx, names):
    cmap = ListedColormap([PHASE_COL[n.split(" (")[0]] for n in names])
    ax.pcolormesh(T_C, V_III, idx, cmap=cmap, vmin=-0.5, vmax=len(names) - 0.5, shading="auto")
    ax.set_xlim(900, 1300)
    ax.set_ylim(500, 5000)
    ax.set_xticks([900, 1000, 1100, 1200, 1300])


def legend_phases(fig, names, y=1.0):
    handles = [Patch(facecolor=PHASE_COL[n.split(" (")[0]], label=n) for n in names]
    fig.legend(handles=handles, loc="upper center", ncol=len(names), bbox_to_anchor=(0.5, y), fontsize=8.5)


def fig_phase(models, eads, thermo, names, figdir):
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.4), sharey=True)
    for ax, (F, title) in zip(axes, ((0, "N$_2$ carrier (F = 0)"), (1, "H$_2$ carrier (F = 1)"))):
        plot_phase(ax, phase_map(names, models, eads, thermo, F), names)
        ax.set_title(title, fontsize=9.5)
        ax.set_xlabel("Temperature (°C)")
    axes[0].set_ylabel("V/III ratio  ($p^0_{\\mathrm{NH_3}} / p^0_{\\mathrm{TMG}}$)")
    legend_phases(fig, names)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(figdir / "phase_diagram.png", dpi=200)
    plt.close(fig)


def fig_delta_g(models, eads, thermo, names, v, figdir):
    T_K = T_C + 273.15
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.3), sharey=True)
    for ax, (F, title) in zip(axes, ((0, "N$_2$ carrier"), (1, "H$_2$ carrier"))):
        g = delta_g({n: models[n] for n in names}, eads, thermo, T_K, decomposed_pressures(v, F))
        for n in names:
            ax.plot(T_C, g[n], color=PHASE_COL[n.split(" (")[0]], label=n)
        ax.axhline(0, color=MUTED, linewidth=0.6)
        ax.set_title(f"{title}, V/III = {v:.0f}", fontsize=9.5)
        ax.set_xlabel("Temperature (°C)")
        ax.set_xlim(900, 1300)
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("$\\Delta G$ relative to Ideal (eV / 2×2 cell)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(names), fontsize=8.5)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(figdir / "delta_g.png", dpi=200)
    plt.close(fig)


def fig_sites(models, eads, thermo, figdir):
    rows = [n for n in ("Ga adatom (H3)", "Ga adatom (T4)") if n in models]
    fig, axes = plt.subplots(len(rows), 3, figsize=(8.6, 2.9 * len(rows)),
                             gridspec_kw=dict(width_ratios=[0.62, 1, 1]), squeeze=False)
    for r, ad in enumerate(rows):
        names = ["Ideal", ad, "3Ga-H"]
        draw_top(axes[r, 0], models[ad]["job"])
        axes[r, 0].set_title(f"{ad}\n$E_\\mathrm{{ads}}$ = {eads[ad]:.2f} eV", fontsize=9)
        for c, (F, title) in enumerate(((0, "N$_2$ carrier"), (1, "H$_2$ carrier")), start=1):
            ax = axes[r, c]
            plot_phase(ax, phase_map(names, models, eads, thermo, F), names)
            ax.set_title(title, fontsize=9.5)
            if r == len(rows) - 1:
                ax.set_xlabel("Temperature (°C)")
            else:
                ax.set_xticklabels([])
            if c == 1:
                ax.set_ylabel("V/III ratio")
            else:
                ax.set_yticklabels([])
    legend_phases(fig, ["Ideal", "Ga adatom", "3Ga-H"])
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(figdir / "adatom_site.png", dpi=200)
    plt.close(fig)


# --- main --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="ZIP files or folders downloaded from Quloud")
    ap.add_argument("--figures", default="figures", help="folder for the figures (default: figures)")
    args = ap.parse_args()
    figdir = Path(args.figures)
    figdir.mkdir(parents=True, exist_ok=True)

    qe, psi4 = collect(args.paths)
    gas, models = classify(qe)
    for need in ("Ga", "H2"):
        if need not in gas:
            raise SystemExit(f"The QE job of the {need} reference was not found")
    h2 = [p for p in psi4 if len(p["freqs"]) == 1]
    if not h2:
        raise SystemExit("The Psi4 frequency job of H2 was not found")
    h2 = h2[0]

    print("== Quantum ESPRESSO jobs")
    for name, j in list(gas.items()) + [(n, m["job"]) for n, m in models.items()]:
        if name == "Ga":
            name = f"Ga (nspin={j['nspin']})"
        note = "" if j["ok"] else "  ** not converged **"
        sm = f"  (smearing -TS = {j['smear_ry'] * RY_EV:+.4f} eV, (F+E)/2 used)" if j["smear_ry"] else ""
        print(f"  {name:16s} E = {j['energy_ry']:.8f} Ry = {j['energy_ry'] * RY_EV:.4f} eV{sm}{note}  [{j['label']}]")

    print("== Psi4 (H2)")
    print(f"  harmonic frequency = {h2['freqs'][0]:.2f} cm-1, rotational constant B = {h2['B']:.4f} cm-1"
          + ("" if h2["ok"] else "  ** not finished **") + f"  [{h2['label']}]")

    e_ga, e_h2 = gas["Ga"]["energy_ry"] * RY_EV, gas["H2"]["energy_ry"] * RY_EV
    if "Ga (nspin=1)" in gas:
        print(f"  Ga atom without spin polarization is {gas['Ga (nspin=1)']['energy_ry'] * RY_EV - e_ga:.3f} eV"
              f" higher; the reference is the spin-polarized one (nspin={gas['Ga']['nspin']})")
    e_ideal = models["Ideal"]["job"]["energy_ry"] * RY_EV
    eads = {n: m["job"]["energy_ry"] * RY_EV - e_ideal - m["dGa"] * e_ga - 0.5 * m["dH"] * e_h2
            for n, m in models.items()}
    print("== Adsorption energies E_ads = E(slab) - E(ideal) - dGa E(Ga) - dH/2 E(H2)  (eV per 2x2 cell)")
    for n, m in models.items():
        if n != "Ideal":
            per = f"  ({eads[n] / m['dH']:.3f} eV per H)" if m["dH"] else ""
            print(f"  {n:16s} {eads[n]:8.3f}{per}")
    if "Ga adatom (T4)" in eads and "Ga adatom (H3)" in eads:
        print(f"  T4 is {eads['Ga adatom (H3)'] - eads['Ga adatom (T4)']:.3f} eV more stable than H3")

    thermo = Thermo(h2["freqs"][0], h2["B"])
    print("== Decomposed partial pressures (atm)")
    for F in (0, 1):
        for v in (500, 5000):
            p = decomposed_pressures(v, F)
            print(f"  F = {F}, V/III = {v:4d}: " + ", ".join(f"{k} {p[k]:.3g}" for k in ("Ga", "H2", "N2", "NH3")))
    print("== Chemical potentials mu_tilde (eV) at 1100 C, V/III = 3000")
    for F in (0, 1):
        p = decomposed_pressures(3000, F)
        print(f"  F = {F}: Ga {thermo.mu_ga(1373.15, p['Ga']):.3f}, 3/2 H2 {1.5 * thermo.mu_h2(1373.15, p['H2']):.3f}")

    main_ad = "Ga adatom (T4)" if "Ga adatom (T4)" in models else next(n for n in models if n.startswith("Ga adatom"))
    names = ["Ideal", main_ad] + (["3Ga-H"] if "3Ga-H" in models else [])
    print(f"== Phase transitions with increasing temperature ({', '.join(names)})")
    for F, carrier in ((0, "N2"), (1, "H2")):
        for v in (500, 1000, 2000, 3000, 5000):
            print(f"  {carrier} carrier, V/III = {v:4d}: {transitions(names, models, eads, thermo, F, v)}")
    if "3Ga-H" in models:
        T_K = T_C + 273.15
        bound = []
        for i, v in enumerate(V_III):
            g = delta_g({n: models[n] for n in names}, eads, thermo, T_K, decomposed_pressures(v, 1))
            ok = (g["3Ga-H"] < g[main_ad]) & (g["3Ga-H"] < g["Ideal"])
            if ok.any():
                bound.append((v, T_C[ok].min()))
        if bound:
            v0 = min(b[0] for b in bound)
            print(f"  H2 carrier: 3Ga-H appears at V/III >= {v0:.0f} (grid step {V_III[1] - V_III[0]:.0f})")

    fig_models(models, [n for n in ("Ideal", main_ad, "3Ga-H") if n in models], figdir)
    fig_delta_g(models, eads, thermo, names, 5000, figdir)
    fig_phase(models, eads, thermo, names, figdir)
    if "Ga adatom (H3)" in models and "3Ga-H" in models:
        fig_sites(models, eads, thermo, figdir)
    print(f"== Figures written to {figdir}/")


if __name__ == "__main__":
    main()
