"""Analyze the CO2 IR example from RSDFT jobs downloaded from Quloud.

Pass the ZIP files downloaded from the job pages of Quloud ("一括ダウンロード"
of the output files), folders holding them, or their extracted contents. Each
job is recognized from its output files, so the file names do not matter:

* MD (CPMD or BOMD): TRAJECTORY.cif, info.dat and DIPOLE.dat. DIPOLE.dat is
  written only when "MDDIPOLE /" is added to rsdft.in before the job is run.
  CPMD and BOMD are told apart by the number of columns of info.dat, and the
  starting structure by the first frame of TRAJECTORY.cif.
* Static SCF: rsdft.json and rsdft.atom. The mode and the displacement are read
  from the structure, compared with the reference structure of
  make_static_structures.py.

The script prints the numbers quoted in the article and writes the figures for
the jobs it finds; parts that need missing jobs are skipped.

Usage: python analyze_co2_ir.py <zip or folder> [...] [--figures DIR]
"""
import argparse
import io
import json
import zipfile
from pathlib import Path, PurePosixPath

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = Path("figures")

HA2CM = 219474.63  # hartree -> cm^-1
FS2AU = 1.0 / 2.418884326505e-2  # fs -> atomic time unit
C_CM_PER_FS = 2.99792458e-5  # speed of light (cm/fs)
AU2DEBYE = 2.541746
BOHR = 0.529177210903  # angstrom
AMU = 1822.888486  # electron masses
M_C, M_O = 12.011, 15.999
MASS = np.array([M_C, M_O, M_O])
R_CO = 2 * M_O / M_C
KMMOL = 42.2561  # A (km/mol) per (D / (A amu^1/2))^2
Z_O = 0.609861  # fractional z of the upper O atom in the reference structure (C at the cell center)

COL = {"x": "#2a78d6", "y": "#eb6834", "z": "#1baf7a"}
MODE_COL = {"sym": "#6250d6", "asym": "#1baf7a", "bend_x": "#2a78d6", "bend_y": "#eb6834"}
INK, MUTED = "#0b0b0b", "#52514e"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "lines.linewidth": 1.4,
})


def find_jobs(paths):
    """Output folders of RSDFT jobs (those holding rsdft.json) in ZIP files and folders.

    Returns a list of (name, read), where read(filename) gives the text of that
    file in the job's folder, or None if it is not there.
    """
    jobs = []

    def add_zip(zpath):
        zf = zipfile.ZipFile(zpath)
        names = [n for n in zf.namelist() if not n.endswith("/")]
        for n in names:
            p = PurePosixPath(n)
            if p.name == "rsdft.json":
                members = {PurePosixPath(m).name: m for m in names if PurePosixPath(m).parent == p.parent}
                label = f"{zpath}" + ("" if str(p.parent) == "." else f":{p.parent}")
                jobs.append((label, lambda f, zf=zf, m=members: zf.read(m[f]).decode() if f in m else None))

    for p in map(Path, paths):
        if p.is_file() and p.suffix.lower() == ".zip":
            add_zip(p)
        elif p.is_dir():
            for z in sorted(p.rglob("*.zip")):
                add_zip(z)
            for j in sorted(p.rglob("rsdft.json")):
                d = j.parent
                jobs.append((str(d), lambda f, d=d: (d / f).read_text() if (d / f).exists() else None))
        else:
            raise SystemExit(f"Not a ZIP file or a folder: {p}")
    return jobs


def read_cif(text):
    """Element symbols, cell lengths (A) and fractional coordinates of every frame of a CIF.

    Works for rsdft.atom (one frame) and TRAJECTORY.cif (one frame per MD step).
    Returns (symbols, cell, frac) with frac of shape (frames, atoms, 3).
    """
    frames, cell, angles = [], {}, {}
    keys, atoms, symbols = [], [], None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#RS-CPMD_STEP") or s.startswith("data_"):
            if atoms:
                frames.append(atoms)
                atoms = []
            continue
        if not s or s.startswith("#"):
            continue
        if s == "loop_":
            keys = []
        elif s.startswith("_cell_length_"):
            cell[s.split()[0][-1]] = float(s.split()[1])
        elif s.startswith("_cell_angle_"):
            angles[s.split()[0]] = float(s.split()[1])
        elif s.startswith("_"):
            keys.append(s.split()[0])
        elif "_atom_site_fract_x" in keys:
            v = s.split()
            if len(v) == len(keys):
                atoms.append(v)
    if atoms:
        frames.append(atoms)
    if any(abs(a - 90) > 1e-6 for a in angles.values()):
        raise SystemExit("Only orthogonal cells are supported")
    i_sym = keys.index("_atom_site_type_symbol")
    i_x = keys.index("_atom_site_fract_x")
    symbols = [a[i_sym] for a in frames[0]]
    frac = np.array([[[float(v) for v in a[i_x:i_x + 3]] for a in f] for f in frames])
    return symbols, np.array([cell["a"], cell["b"], cell["c"]]), frac


def co2_positions(text):
    """Cartesian positions (A) of C, O1, O2 for every frame; O1 is the O atom with larger z at the start."""
    symbols, cell, frac = read_cif(text)
    if sorted(symbols) != ["C", "O", "O"]:
        raise ValueError(f"not a CO2 molecule: {symbols}")
    c = symbols.index("C")
    o = sorted((i for i, s in enumerate(symbols) if s == "O"), key=lambda i: -frac[0, i, 2])
    return frac[:, [c] + o] * cell, cell


def load_md(read):
    """MD time series from TRAJECTORY.cif, info.dat and DIPOLE.dat."""
    R, _ = co2_positions(read("TRAJECTORY.cif"))
    info = np.loadtxt(io.StringIO(read("info.dat")))
    dip = np.loadtxt(io.StringIO(read("DIPOLE.dat")))
    if not len(R) == len(info) == len(dip) or np.abs(info[:, 0] - dip[:, 0]).max() > 1e-6:
        raise ValueError("TRAJECTORY.cif, info.dat and DIPOLE.dat do not share the same time steps")
    # info.dat columns: time, conserved energy, its change, Etot, ion KE,
    # [fictitious KE (CPMD only)], bath energy, temperature, ...
    cp = info.shape[1] == 10
    return {"method": "CPMD" if cp else "BOMD", "t": dip[:, 0], "mu": dip[:, 1:4], "R": R,
            "dE": info[:, 2], "fke": info[:, 5] if cp else np.zeros(len(info)), "temp": info[:, 7 if cp else 6]}


def static_point(text):
    """(mode, u) of a static structure: u (bohr) is the displacement of the upper O atom.

    nu1: the O atoms move by +u and -u along z; nu2 (x) and nu3 (z): both O atoms
    move by +u and C by -2 m_O u / m_C; shift: all atoms move by u along x.
    The structures are made with u in steps of 0.0001 bohr, so u of the modes is
    rounded to that step (rsdft.atom in the output keeps only 6 decimals).
    Returns None for a structure that is none of these.
    """
    R, cell = co2_positions(text)
    a = cell[0]
    ref = np.array([[0.5, 0.5, 0.5], [0.5, 0.5, Z_O], [0.5, 0.5, 1 - Z_O]]) * a
    d = (R[0] - ref) / BOHR
    tol = 2e-4  # bohr; rsdft.atom in the output has 6 decimals in fractional coordinates
    dc, d1, d2 = d
    if np.abs(d).max() < tol:
        return "ref", 0.0
    if np.abs(d[:, 1:]).max() < tol and np.ptp(d[:, 0]) < tol:
        return "shift", d[:, 0].mean()
    if np.abs(d[:, :2]).max() < tol and abs(dc[2]) < tol and abs(d1[2] + d2[2]) < tol:
        return "nu1", round((d1[2] - d2[2]) / 2, 4)
    for mode, k in (("nu2", 0), ("nu3", 2)):
        other = [i for i in range(3) if i != k]
        if np.abs(d[:, other]).max() < tol and abs(d1[k] - d2[k]) < tol and abs(dc[k] + R_CO * d1[k]) < tol:
            return mode, round((d1[k] + d2[k]) / 2, 4)
    return None


def load_jobs(paths):
    """Sort the jobs into MD runs (keyed by method and start) and static points."""
    runs, static, seen = {}, [], set()
    print("Jobs found:")
    for name, read in find_jobs(paths):
        ident = (read("rsdft.json"), read("info.dat") is not None)
        if ident in seen:
            print(f"  {name}: same as a job above, skipped")
            continue
        seen.add(ident)
        if read("TRAJECTORY.cif") is not None and read("info.dat") is not None:
            if read("DIPOLE.dat") is None:
                print(f"  {name}: MD without DIPOLE.dat (add 'MDDIPOLE /' to rsdft.in), skipped")
                continue
            run = load_md(read)
            r0 = internal(run["R"][:1])["sym"][0]
            start = "opt" if abs(r0 - 1.1645) < 0.002 else "1150" if abs(r0 - 1.150) < 0.002 else f"{r0:.4f}"
            key = ("bo_" if run["method"] == "BOMD" else "") + start
            print(f"  {name}: {run['method']}, {len(run['t']) - 1} steps of {run['t'][1] - run['t'][0]:g} fs,"
                  f" start C-O {r0:.4f} A -> run '{key}'")
            if key in runs:
                print(f"    run '{key}' already found, skipped")
                continue
            runs[key] = run
        else:
            etot = json.loads(read("rsdft.json"))["etot"]["value"]
            atom = read("rsdft.atom") or read("rsdft.atom.out.cif")
            pt = static_point(atom) if atom else None
            if pt is None:
                print(f"  {name}: static job with an unknown structure, skipped")
                continue
            static.append((pt[0], pt[1], etot))
    if static:
        modes = [m for m, _, _ in static]
        print(f"  static: {modes.count('ref')} reference, " + ", ".join(
            f"{modes.count(m)} {m}" for m in ("nu1", "nu2", "nu3", "shift")) + " points")
    return runs, static


def power_spectrum(x, dt_fs, npad=16):
    """Classical power spectrum of the mean-subtracted signal.

    Cosine transform of the autocorrelation function (biased estimator)
    multiplied by the half of a Hann window. Returns (cm^-1, spectrum).
    """
    x = x - x.mean()
    n = len(x)
    f = np.fft.rfft(x, 2 * n)
    acf = np.fft.irfft(np.abs(f) ** 2)[:n] / n
    a = acf * np.hanning(2 * n)[n:]
    N = npad * 2 * n
    spec = (2 * np.fft.rfft(a, N).real - a[0]) * dt_fs
    return np.fft.rfftfreq(N, d=dt_fs) / C_CM_PER_FS, spec


def peak(nu, s, lo, hi):
    m = (nu > lo) & (nu < hi)
    i = np.argmax(s[m])
    return nu[m][i], s[m][i]


def rsdft_style(t, mu):
    """Im chi as written by RSDFT (ft_dipole_module.f90) after the MD run.

    mu(t) - mu(0) is Fourier transformed with exp(-gamma t), gamma = pi/T,
    each component normalized separately, and multiplied by omega/2.
    """
    tau = (t - t[0]) * FS2AU
    dmu = mu - mu[0]
    gamma = np.pi / tau[-1]
    c = 1.0 / np.sqrt((dmu[1:] ** 2).mean(0))
    e = np.linspace(0, 0.5 / 27.2116, 2000)  # 0-0.5 eV in hartree
    ft = np.exp(1j * (e[:, None] + 1j * gamma) * tau[None, 1:]) @ dmu[1:] * (tau[1] - tau[0])
    return e * HA2CM, 0.5 * e[:, None] * np.abs(ft * c) ** 2


def internal(R):
    """Stretch and bend coordinates (A) from positions of C, O1, O2."""
    r1 = np.linalg.norm(R[:, 1] - R[:, 0], axis=1)
    r2 = np.linalg.norm(R[:, 2] - R[:, 0], axis=1)
    bend = R[:, 0] - (R[:, 1] + R[:, 2]) / 2  # C displacement from the O-O midpoint
    axis = R[:, 1] - R[:, 2]
    axis /= np.linalg.norm(axis, axis=1)[:, None]
    tilt = np.degrees(np.arccos(np.abs(axis[:, 2])))
    return {"sym": (r1 + r2) / 2, "asym": (r1 - r2) / 2, "bend_x": bend[:, 0], "bend_y": bend[:, 1],
            "tilt": tilt, "r1": r1, "r2": r2}



MEFF = {"nu1": 2 * M_O, "nu2": 2 * M_O + M_C * R_CO ** 2, "nu3": 2 * M_O + M_C * R_CO ** 2}  # amu
# sum_i m_i |d_i|^2 for unit displacement u of the O atoms (see make_static_structures.py)


def static_sets(static):
    """Energies relative to the reference, split into the standard (|u| >= 0.015 bohr) and small sets."""
    e0 = [e for m, _, e in static if m == "ref"]
    if not e0:
        return None
    sets = {"standard": {}, "small": {}, "shift": {0.0: 0.0}}
    for m, u, e in static:
        if m == "shift":
            sets["shift"][u] = e - e0[0]
        elif m != "ref":
            sets["standard" if abs(u) >= 0.015 else "small"][(m, u)] = e - e0[0]
    return sets


def harmonic_frequencies(sets):
    """Harmonic wavenumbers from the standard set of static total energies along the symmetry modes."""
    res = {}
    for m in ("nu1", "nu2", "nu3"):
        pts = [(u, e) for (mm, u), e in sets["standard"].items() if mm == m]
        if len(pts) < 3:
            print(f"  {m}: not enough points")
            continue
        u, e = np.array(pts).T
        if m != "nu1":  # E(-u) = E(u) by symmetry
            u, e = np.r_[u, -u], np.r_[e, e]
        u, e = np.r_[0.0, u], np.r_[0.0, e]
        k = np.linalg.lstsq(np.vstack([u ** 2 / 2, u ** 3, u ** 4]).T, e, rcond=None)[0][0]
        small = np.abs(u) <= 0.021
        k2 = np.linalg.lstsq((u[small] ** 2 / 2)[:, None], e[small], rcond=None)[0][0]
        w = [np.sqrt(kk / (MEFF[m] * AMU)) * HA2CM for kk in (k, k2)]
        res[m] = w
        print(f"  {m}: {w[0]:.0f} cm^-1 (quartic fit, |u|<=0.06 bohr), {w[1]:.0f} cm^-1 (quadratic, |u|<=0.02 bohr)")
    return res


def static_checks(sets):
    """Effective harmonic wavenumbers from single points, and the grid-shift energy variation."""
    for name in ("standard", "small"):
        e = {(m, round(u, 4)): v for (m, u), v in sets[name].items()}
        rows = []
        for (m, u), de in sorted(e.items()):
            if m == "nu1" and u > 0 and ("nu1", -u) in e:
                de = (de + e[("nu1", -u)]) / 2  # remove the linear term
            elif m not in ("nu2", "nu3"):
                continue
            w = np.sqrt(2 * de / u ** 2 / (MEFF[m] * AMU)) * HA2CM
            rows.append(f"{m} u={u:.4f}: {w:.0f}")
        if rows:
            print(f"  {name} set: 2 dE / u^2 -> " + ", ".join(rows))
    if len(sets["shift"]) > 1:
        rng = np.ptp(list(sets["shift"].values()))
        print(f"  rigid shift along x by up to {max(sets['shift']) * BOHR:.3f} A ({len(sets['shift'])} points):"
              f" energy range {rng * 1e6:.0f} uHa = {rng * 315775.0:.0f} K (E/k_B)")


def normal_coords(R):
    """Mass-weighted normal coordinates (amu^1/2 A) of a CO2 molecule along z."""
    dR = (R - R.mean(0)) * np.sqrt(MASS)[None, :, None]

    def unit(v):
        v = np.array(v) * np.sqrt(MASS)
        return v / np.linalg.norm(v)

    q_odd, q1 = unit([-R_CO, 1, 1]), unit([0, 1, -1])
    return {"nu3": dR[:, :, 2] @ q_odd, "nu1": dR[:, :, 2] @ q1,
            "nu2x": dR[:, :, 0] @ q_odd, "nu2y": dR[:, :, 1] @ q_odd}


def intensities(run, tmax=400.0):
    """dmu/dQ from regressing dipole on mass-weighted normal coordinates (t <= tmax)."""
    t = run["t"]
    mu = run["mu"] * AU2DEBYE
    Q = normal_coords(run["R"])
    sel = t <= tmax
    dmu = mu - mu.mean(0)
    res = {}
    for name, comp, other in (("nu3", 2, "nu1"), ("nu1", 2, "nu3"), ("nu2x", 0, "nu1"), ("nu2y", 1, "nu1")):
        A = np.vstack([Q[name][sel], Q[other][sel], np.ones(sel.sum())]).T
        c = np.linalg.lstsq(A, dmu[sel, comp], rcond=None)[0][0]
        res[name] = (c, KMMOL * c * c, Q[name].std())
    return res


def sideband_origin(run):
    """Split the nu3 +/- nu1 sidebands of mu_z into mechanical and electrical parts.

    mu_z is fitted by a Q3 + b Q1 Q3 + c. The a Q3 term carries sidebands only
    if the motion Q3 itself is modulated by nu1 (mechanical anharmonicity);
    the b Q1 Q3 term is the bond-length dependence of dmu_z/dQ3 (electrical).
    """
    dt = run["t"][1] - run["t"][0]
    mu = run["mu"][:, 2] * AU2DEBYE
    Q = normal_coords(run["R"])
    X = np.vstack([Q["nu3"], Q["nu1"] * Q["nu3"], np.ones(len(mu))]).T
    (a, b, c), *_ = np.linalg.lstsq(X, mu, rcond=None)
    print(f"  fit mu_z = a Q3 + b Q1 Q3 + c: a={a:.3f} D/(A amu^1/2), b={b:.3f} D/(A^2 amu),"
          f" residual rms / std(mu_z) = {(mu - X @ [a, b, c]).std() / mu.std():.2f}")
    for name, x in (("Q3 (motion)", Q["nu3"]), ("mu_z", mu), ("a Q3", a * Q["nu3"]),
                    ("b Q1 Q3", b * Q["nu1"] * Q["nu3"]), ("a Q3 + b Q1 Q3", X[:, :2] @ [a, b])):
        nu, s = power_spectrum(x, dt)
        main = peak(nu, s, 2100, 2300)[1]
        lo, hi = peak(nu, s, 900, 1100), peak(nu, s, 3300, 3500)
        at = [s[np.argmin(np.abs(nu - w))] for w in (985, 3410)]
        print(f"  {name:15s} power at 985/3410: {at[0]:.2g}/{at[1]:.2g} D^2 fs;"
              f" side peaks {lo[0]:.0f}: 1/{main / lo[1]:.0f}, {hi[0]:.0f}: 1/{main / hi[1]:.0f} of its own main peak")


def main():
    global FIG
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="+", help="ZIP files downloaded from Quloud, or folders holding them")
    ap.add_argument("--figures", default="figures", help="folder to write the figures to (default: figures)")
    args = ap.parse_args()
    FIG = Path(args.figures)
    FIG.mkdir(parents=True, exist_ok=True)
    runs, static = load_jobs(args.paths)

    harm = None
    sets = static_sets(static)
    if sets:
        print("\nHarmonic wavenumbers from static PBE energies:")
        harm = harmonic_frequencies(sets)
        static_checks(sets)

    spec, mot = {}, {}
    for key, run in runs.items():
        t, mu = run["t"], run["mu"]
        dt, T = t[1] - t[0], t[-1] - t[0]
        ic = internal(run["R"])
        print(f"\n=== run {key} ({run['method']}): {len(t)} steps, dt={dt:g} fs, T={T:g} fs,"
              f" 1/(cT)={1 / (C_CM_PER_FS * T):.1f} cm^-1")
        print(f"  C-O at t=0: {ic['r1'][0]:.4f} A; mean over run {ic['sym'].mean():.4f} A")
        print(f"  max |dE_conserved| {np.abs(run['dE']).max():.1e} Ha, max fictitious KE {run['fke'].max():.1e} Ha,"
              f" temperature mean {run['temp'].mean():.1f} K")
        print(f"  axis tilt from z: max {ic['tilt'].max():.1f} deg")
        spec[key] = {}
        for i, lab in enumerate("xyz"):
            nu, s = power_spectrum(mu[:, i], dt)
            spec[key][lab] = s
            pk = [f"{peak(nu, s, lo, hi)[0]:.0f}({peak(nu, s, lo, hi)[1]:.2g})"
                  for lo, hi in ((400, 900), (900, 1100), (1100, 1500), (1900, 2500), (3200, 3800))]
            print(f"  C_{lab}{lab} max in 400-900/900-1100/1100-1500/1900-2500/3200-3800: {' '.join(pk)}")
        nu, s = power_spectrum(mu[:, 2], dt)
        main_z = peak(nu, s, 1900, 2500)[1]
        side = [peak(nu, s, lo, hi) for lo, hi in ((850, 1150), (3300, 3800))]
        print(f"  C_zz side peaks: " + ", ".join(f"{w:.0f} (1/{main_z / v:.0f} of main)" for w, v in side)
              + f"; 1100-1400 max / main = {peak(nu, s, 1100, 1400)[1] / main_z:.1e}")
        spec[key]["nu"] = nu
        mot[key] = {}
        for name in ("sym", "asym", "bend_x", "bend_y"):
            nu2, s2 = power_spectrum(ic[name], dt)
            mot[key][name] = s2
            print(f"  motion {name}: peak {peak(nu2, s2, 300, 4000)[0]:.0f} cm^-1")
        mot[key]["nu"] = nu2
        wr, chi = rsdft_style(t, mu)
        h = chi.max(0)
        pos = [wr[np.argmax(chi[:, i])] for i in range(3)]
        print(f"  RSDFT-style Im chi peaks x,y,z: {pos[0]:.0f} {pos[1]:.0f} {pos[2]:.0f} cm^-1,"
              f" heights {h[0]:.3g} {h[1]:.3g} {h[2]:.3g}; z/x={h[2] / h[0]:.2f}, z/y={h[2] / h[1]:.2f},"
              f" w_z/w_x={pos[2] / pos[0]:.2f}, w_z/w_y={pos[2] / pos[1]:.2f}")
        run["rsdft"] = (wr, chi)
        run["ic"] = ic
        for name, (c, A, q) in intensities(run).items():
            print(f"  {name}: dmu/dQ={c:+.3f} D/(A amu^1/2), A={A:.1f} km/mol, std(Q)={q:.4f} amu^1/2 A")
        print(f"  variance of mu (D^2) x,y,z: " + " ".join(f"{v:.3g}" for v in (mu * AU2DEBYE).var(0)))

    if "1150" in runs:
        print("\nOrigin of the nu3 -/+ nu1 sidebands (CPMD run started at 1.150 A):")
        sideband_origin(runs["1150"])

    if runs:
        print("\nSymmetric-stretch and bend amplitudes per 100 fs (10^-3 A):")
    for key, run in runs.items():
        ic, t = run["ic"], run["t"]
        bp = np.hypot(ic["bend_x"], ic["bend_y"])
        rows = []
        for w0 in range(0, int(t[-1]), 100):
            m = (t >= w0) & (t < w0 + 100)
            rows.append(f"{w0}-{w0 + 100}: {1e3 * np.ptp(ic['sym'][m]) / 2:.1f}/{1e3 * bp[m].max():.1f}")
        print(f"  {key}: " + "  ".join(rows))

    if runs:
        print("\nKinetic energy of each normal coordinate as a temperature, <dQ/dt^2>/k_B (K):")
    amu_a2_fs2_to_k = 1.66053907e-27 * 1e10 / 1.380649e-23  # amu A^2/fs^2 -> K
    for key, run in runs.items():
        nc = normal_coords(run["R"])
        dt = run["t"][1] - run["t"][0]
        print(f"  {key}: " + "  ".join(f"{k} {np.mean(np.gradient(q, dt) ** 2) * amu_a2_fs2_to_k:.2f}"
                                       for k, q in nc.items()))

    plot_modes()
    if "opt" in runs or "bo_opt" in runs:
        plot_dipole(runs.get("opt"), runs.get("bo_opt"))
    for key, method, fname in (("opt", "CPMD", "spectra.png"), ("bo_opt", "BOMD", "spectra_bomd.png")):
        if key in runs:
            plot_spectra(spec[key], mot[key], harm, method, fname)
    if "opt" in runs:
        plot_rsdft(runs["opt"])
    if any(p + "opt" in spec and p + "1150" in spec for p in ("", "bo_")):
        plot_sidebands(spec)
    if any(k in runs for k in ("opt", "1150", "bo_1150")):
        plot_energy_flow(runs)
    print(f"\nFigures written to {FIG}/")


def plot_modes():
    """Schematic of the three normal modes of CO2 (not to scale)."""
    fig, axes = plt.subplots(1, 3, figsize=(7.5, 1.9))
    titles = [r"$\nu_1$  symmetric stretch", r"$\nu_2$  bend ($\times 2$)", r"$\nu_3$  antisymmetric stretch"]
    # arrows (dx, dy) for O1, C, O2
    arrows = [[(-0.35, 0), (0, 0), (0.35, 0)], [(0, 0.3), (0, -0.4), (0, 0.3)], [(0.3, 0), (-0.4, 0), (0.3, 0)]]
    sub = ["IR inactive", "IR active", "IR active"]
    for ax, title, arr, s in zip(axes, titles, arrows, sub):
        xs = [-1.0, 0.0, 1.0]
        ax.plot(xs, [0, 0, 0], color=MUTED, lw=1.2, zorder=1)
        for x, el, (dx, dy) in zip(xs, ("O", "C", "O"), arr):
            ax.scatter([x], [0], s=420 if el == "O" else 330, color="#e34948" if el == "O" else "#52514e",
                       zorder=2, edgecolors="white", linewidths=1.5)
            ax.text(x, 0, el, ha="center", va="center", color="white", fontsize=8, fontweight="bold", zorder=3)
            if dy:  # bend: arrows start at the atom and point along y
                ax.annotate("", xy=(x, dy * 1.4 + np.sign(dy) * 0.2), xytext=(x, np.sign(dy) * 0.2),
                            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3), zorder=4)
            elif dx:  # stretch: arrows above the atom, centered on it
                ax.annotate("", xy=(x + dx * 0.9, 0.4), xytext=(x - dx * 0.4, 0.4),
                            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3), zorder=4)
        ax.set_title(title, fontsize=9, color=INK)
        ax.text(0, -0.85, s, ha="center", color=MUTED, fontsize=8.5)
        ax.set_xlim(-1.9, 1.9)
        ax.set_ylim(-1.0, 0.9)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(FIG / "co2_modes.png", dpi=200)
    plt.close(fig)


def plot_dipole(cp, bo):
    """Dipole time series of the CPMD and BOMD runs started from the same structure and velocities."""
    fig, ax = plt.subplots(3, 2, figsize=(7.5, 4.9), sharex="col", gridspec_kw={"width_ratios": [2.2, 1]})
    pairs = [(r, c, l) for r, c, l in ((cp, "#2a78d6", "CPMD"), (bo, "#eb6834", "BOMD")) if r is not None]
    for run, col, label in pairs:
        t, mu = run["t"], run["mu"]
        dmu = mu - mu.mean(0)
        for i, lab in enumerate("xyz"):
            for j, (lo, hi) in enumerate(((0, 800), (0, 100))):
                m = (t >= lo) & (t <= hi)
                ax[i, j].plot(t[m], dmu[m, i] * 1e3, color=col, lw=0.7 if j == 0 else 1.2, label=label)
                ax[i, j].set_xlim(lo, hi)
    for i, lab in enumerate("xyz"):
        ax[i, 0].set_ylabel(rf"$\delta\mu_{lab}$ ($10^{{-3}}$ a.u.)")
        lim = 1.15 * max(np.abs(r["mu"][:, i] - r["mu"][:, i].mean()).max() for r, _, _ in pairs) * 1e3
        for j in range(2):
            ax[i, j].set_ylim(-lim, lim)
    ax[0, 0].set_title("0-800 fs", fontsize=9)
    ax[0, 1].set_title("0-100 fs (zoom)", fontsize=9)
    fig.legend(*ax[0, 0].get_legend_handles_labels(), loc="upper left", ncol=2, fontsize=8,
               bbox_to_anchor=(0.08, 1.0))
    ax[2, 0].set_xlabel("Time (fs)")
    ax[2, 1].set_xlabel("Time (fs)")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(FIG / "dipole_time.png", dpi=200)
    plt.close(fig)


def plot_spectra(spec, mot, harm, method, fname):
    # two panels side by side; legends sit above each panel so that they never cover the curves
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.9))
    for a in ax:
        for m in (harm or {}):
            a.axvline(harm[m][0], color=MUTED, ls=":", lw=0.8)
    nu = spec["nu"]
    for lab in "xyz":
        ax[0].semilogy(nu, spec[lab], color=COL[lab], label=rf"$\mu_{lab}$")
    if harm:
        ax[0].plot([], [], color=MUTED, ls=":", lw=0.8, label="static harmonic")
    ax[0].set_ylim(1e-8, 1)
    ax[0].set_ylabel(f"Dipole power spectrum, {method} (a.u.)")
    nu2 = mot["nu"]
    names = {"sym": "sym. stretch", "asym": "antisym. stretch", "bend_x": "bend (x)", "bend_y": "bend (y)"}
    for k, label in names.items():
        s = mot[k] / mot[k][(nu2 > 300) & (nu2 < 4000)].max()
        ax[1].semilogy(nu2, s, color=MODE_COL[k], label=label)
    ax[1].set_ylim(1e-7, 2)
    ax[1].set_ylabel(f"Atomic-motion spectrum, {method}\n(each normalized)")
    for a in ax:
        a.legend(loc="lower left", bbox_to_anchor=(0, 1.01), ncol=4, fontsize=8,
                 handlelength=1.6, columnspacing=1.0, borderaxespad=0)
        a.set_xlim(0, 4000)
        a.set_xlabel(r"Wavenumber (cm$^{-1}$)")
    fig.tight_layout()
    fig.savefig(FIG / fname, dpi=200)
    plt.close(fig)


def plot_rsdft(run):
    wr, chi = run["rsdft"]
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    for i, lab in enumerate("xyz"):
        ax.plot(wr, chi[:, i], color=COL[lab], label=lab)
        k = np.argmax(chi[:, i])
        ax.annotate(f"{wr[k]:.0f}", (wr[k], chi[k, i]), textcoords="offset points",
                    xytext=(8 if lab != "y" else -8, -2), ha="left" if lab != "y" else "right",
                    fontsize=8, color=MUTED)
    ax.set_xlim(0, 4000)
    ax.set_xlabel(r"Wavenumber (cm$^{-1}$)")
    ax.set_ylabel(r"Im $\chi$ as output by RSDFT")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "rsdft_output.png", dpi=200)
    plt.close(fig)


def plot_sidebands(spec):
    methods = [(m, p) for m, p in (("CPMD", ""), ("BOMD", "bo_")) if p + "opt" in spec and p + "1150" in spec]
    fig, ax = plt.subplots(len(methods), 1, figsize=(7.5, 2.5 * len(methods)), sharex=True, squeeze=False)
    ax = ax[:, 0]
    for a, (method, pre) in zip(ax, methods):
        a.semilogy(spec[pre + "opt"]["nu"], spec[pre + "opt"]["z"], color="#2a78d6",
                   label="start at 1.1645 Å (optimized)")
        a.semilogy(spec[pre + "1150"]["nu"], spec[pre + "1150"]["z"], color="#eb6834", label="start at 1.150 Å")
        a.set_ylim(1e-8, 1)
        a.set_ylabel(r"Power spectrum of $\mu_z$ (a.u.)")
        a.set_title(method, fontsize=9, loc="right")
        a.legend(loc="upper left")
    ax[-1].set_xlim(0, 4000)
    ax[-1].set_xlabel(r"Wavenumber (cm$^{-1}$)")
    fig.tight_layout()
    fig.savefig(FIG / "sidebands.png", dpi=200)
    plt.close(fig)


def plot_energy_flow(runs):
    fig, ax = plt.subplots(2, 1, figsize=(7.5, 4.4), sharex=True)
    for key, col, label in (("opt", "#2a78d6", "CPMD, start at 1.1645 Å"), ("1150", "#eb6834", "CPMD, start at 1.150 Å"),
                            ("bo_1150", "#1baf7a", "BOMD, start at 1.150 Å")):
        if key not in runs:
            continue
        ic, t = runs[key]["ic"], runs[key]["t"]
        ax[0].plot(t, ic["sym"], color=col, lw=0.6, label=label)
        ax[1].plot(t, np.hypot(ic["bend_x"], ic["bend_y"]) * 1e3, color=col, lw=0.6, label=label)
    ax[0].set_ylabel("Mean C–O length (Å)")
    ax[1].set_ylabel("C off the O–O line\n($10^{-3}$ Å)")
    ax[1].set_xlabel("Time (fs)")
    ax[1].set_xlim(0, 800)
    ax[0].legend(loc="lower left", bbox_to_anchor=(0, 1.01), ncol=3, fontsize=8, borderaxespad=0)
    fig.tight_layout()
    fig.savefig(FIG / "energy_flow.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
