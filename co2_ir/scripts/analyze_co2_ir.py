"""Analyze the CO2 CPMD runs and make the article figures.

Reads the CSV files in ../data (made by collect_rsdft_outputs.py), prints the
numbers quoted in the article, and writes the figures to ../figures.

Usage: python analyze_co2_ir.py
"""
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
FIG = HERE.parent / "figures"

HA2CM = 219474.63  # hartree -> cm^-1
FS2AU = 1.0 / 2.418884326505e-2  # fs -> atomic time unit
C_CM_PER_FS = 2.99792458e-5  # speed of light (cm/fs)
AU2DEBYE = 2.541746
AMU = 1822.888486  # electron masses
M_C, M_O = 12.011, 15.999
MASS = np.array([M_C, M_O, M_O])
R_CO = 2 * M_O / M_C
KMMOL = 42.2561  # A (km/mol) per (D / (A amu^1/2))^2

COL = {"x": "#2a78d6", "y": "#eb6834", "z": "#1baf7a"}
MODE_COL = {"sym": "#6250d6", "asym": "#1baf7a", "bend_x": "#2a78d6", "bend_y": "#eb6834"}
INK, MUTED = "#0b0b0b", "#52514e"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "lines.linewidth": 1.4,
})


def load(name):
    d = np.loadtxt(DATA / name, delimiter=",", skiprows=1)
    return {"t": d[:, 0], "mu": d[:, 1:4], "R": d[:, 4:13].reshape(-1, 3, 3),
            "dE": d[:, 13], "fke": d[:, 14], "temp": d[:, 15]}


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


def harmonic_frequencies():
    """Harmonic wavenumbers from static total energies along the symmetry modes."""
    d = np.genfromtxt(DATA / "harmonic_energies.csv", delimiter=",", names=True, dtype=None, encoding=None)
    e0 = d["etot_Ha"][d["mode"] == "ref"][0]
    # sum_i m_i |d_i|^2 for unit displacement u of the O atoms (see make_harmonic_inputs.py)
    meff = {"nu1": 2 * M_O, "nu2": 2 * M_O + M_C * R_CO ** 2, "nu3": 2 * M_O + M_C * R_CO ** 2}
    res = {}
    for m in ("nu1", "nu2", "nu3"):
        u = d["u_bohr"][d["mode"] == m]
        e = d["etot_Ha"][d["mode"] == m] - e0
        if m != "nu1":  # E(-u) = E(u) by symmetry
            u, e = np.r_[u, -u], np.r_[e, e]
        u, e = np.r_[0.0, u], np.r_[0.0, e]
        k = np.linalg.lstsq(np.vstack([u ** 2 / 2, u ** 3, u ** 4]).T, e, rcond=None)[0][0]
        small = np.abs(u) <= 0.021
        k2 = np.linalg.lstsq((u[small] ** 2 / 2)[:, None], e[small], rcond=None)[0][0]
        w = [np.sqrt(kk / (meff[m] * AMU)) * HA2CM for kk in (k, k2)]
        res[m] = w
        print(f"  {m}: {w[0]:.0f} cm^-1 (quartic fit, |u|<=0.06 bohr), {w[1]:.0f} cm^-1 (quadratic, |u|<=0.02 bohr)")
    return res


def static_checks():
    """Effective harmonic wavenumbers from single points, and the grid-shift energy variation."""
    meff = {"nu1": 2 * M_O, "nu2": 2 * M_O + M_C * R_CO ** 2, "nu3": 2 * M_O + M_C * R_CO ** 2}
    for name in ("harmonic_energies.csv", "harmonic_small_energies.csv"):
        d = np.genfromtxt(DATA / name, delimiter=",", names=True, dtype=None, encoding=None)
        e0 = d["etot_Ha"][d["mode"] == "ref"][0]
        e = {(m, round(u, 4)): v - e0 for m, u, v in zip(d["mode"], d["u_bohr"], d["etot_Ha"])}
        rows = []
        for (m, u), de in sorted(e.items()):
            if m == "nu1" and u > 0 and ("nu1", -u) in e:
                de = (de + e[("nu1", -u)]) / 2  # remove the linear term
            elif m not in ("nu2", "nu3"):
                continue
            w = np.sqrt(2 * de / u ** 2 / (meff[m] * AMU)) * HA2CM
            rows.append(f"{m} u={u:.4f}: {w:.0f}")
        print(f"  {name}: 2 dE / u^2 -> " + ", ".join(rows))
    d = np.genfromtxt(DATA / "grid_shift_energies.csv", delimiter=",", names=True, dtype=None, encoding=None)
    rng = np.ptp(d["etot_Ha"])
    print(f"  rigid shift along x over one grid spacing: energy range {rng * 1e6:.0f} uHa"
          f" = {rng * 315775.0:.0f} K (E/k_B)")


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
    FIG.mkdir(exist_ok=True)
    runs = {"opt": load("md_start_optimized.csv.gz"), "1150": load("md_start_1150.csv.gz"),
            "bo_opt": load("md_bomd_start_optimized.csv.gz"), "bo_1150": load("md_bomd_start_1150.csv.gz")}
    print("Harmonic wavenumbers from static PBE energies:")
    harm = harmonic_frequencies()
    static_checks()

    spec, mot = {}, {}
    for key, run in runs.items():
        t, mu = run["t"], run["mu"]
        dt, T = t[1] - t[0], t[-1] - t[0]
        ic = internal(run["R"])
        print(f"\n=== run {key}: {len(t)} steps, dt={dt} fs, T={T} fs, 1/(cT)={1 / (C_CM_PER_FS * T):.1f} cm^-1")
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

    print("\nOrigin of the nu3 -/+ nu1 sidebands (run started at 1.150 A):")
    sideband_origin(runs["1150"])

    print("\nSymmetric-stretch and bend amplitudes per 100 fs (10^-3 A):")
    for key, run in runs.items():
        ic, t = run["ic"], run["t"]
        bp = np.hypot(ic["bend_x"], ic["bend_y"])
        rows = []
        for w0 in range(0, 800, 100):
            m = (t >= w0) & (t < w0 + 100)
            rows.append(f"{w0}-{w0 + 100}: {1e3 * np.ptp(ic['sym'][m]) / 2:.1f}/{1e3 * bp[m].max():.1f}")
        print(f"  {key}: " + "  ".join(rows))

    print("\nKinetic energy of each normal coordinate as a temperature, <dQ/dt^2>/k_B (K):")
    amu_a2_fs2_to_k = 1.66053907e-27 * 1e10 / 1.380649e-23  # amu A^2/fs^2 -> K
    for key, run in runs.items():
        nc = normal_coords(run["R"])
        dt = run["t"][1] - run["t"][0]
        print(f"  {key}: " + "  ".join(f"{k} {np.mean(np.gradient(q, dt) ** 2) * amu_a2_fs2_to_k:.2f}"
                                       for k, q in nc.items()))

    plot_modes()
    plot_dipole(runs["opt"], runs["bo_opt"])
    plot_spectra(spec["opt"], mot["opt"], harm, "CPMD", "spectra.png")
    plot_spectra(spec["bo_opt"], mot["bo_opt"], harm, "BOMD", "spectra_bomd.png")
    plot_rsdft(runs["opt"])
    plot_sidebands(spec)
    plot_energy_flow(runs)


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
    for run, col, label in ((cp, "#2a78d6", "CPMD"), (bo, "#eb6834", "BOMD")):
        t, mu = run["t"], run["mu"]
        dmu = mu - mu.mean(0)
        for i, lab in enumerate("xyz"):
            for j, (lo, hi) in enumerate(((0, 800), (0, 100))):
                m = (t >= lo) & (t <= hi)
                ax[i, j].plot(t[m], dmu[m, i] * 1e3, color=col, lw=0.7 if j == 0 else 1.2, label=label)
                ax[i, j].set_xlim(lo, hi)
    for i, lab in enumerate("xyz"):
        ax[i, 0].set_ylabel(rf"$\delta\mu_{lab}$ ($10^{{-3}}$ a.u.)")
        lim = 1.15 * max(np.abs(r["mu"][:, i] - r["mu"][:, i].mean()).max() for r in (cp, bo)) * 1e3
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
        for m in ("nu1", "nu2", "nu3"):
            a.axvline(harm[m][0], color=MUTED, ls=":", lw=0.8)
    nu = spec["nu"]
    for lab in "xyz":
        ax[0].semilogy(nu, spec[lab], color=COL[lab], label=rf"$\mu_{lab}$")
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
    fig, ax = plt.subplots(2, 1, figsize=(7.5, 5.0), sharex=True)
    for a, (method, pre) in zip(ax, (("CPMD", ""), ("BOMD", "bo_"))):
        a.semilogy(spec[pre + "opt"]["nu"], spec[pre + "opt"]["z"], color="#2a78d6",
                   label="start at 1.1645 Å (optimized)")
        a.semilogy(spec[pre + "1150"]["nu"], spec[pre + "1150"]["z"], color="#eb6834", label="start at 1.150 Å")
        a.set_ylim(1e-8, 1)
        a.set_ylabel(r"Power spectrum of $\mu_z$ (a.u.)")
        a.set_title(method, fontsize=9, loc="right")
        a.legend(loc="upper left")
    ax[1].set_xlim(0, 4000)
    ax[1].set_xlabel(r"Wavenumber (cm$^{-1}$)")
    fig.tight_layout()
    fig.savefig(FIG / "sidebands.png", dpi=200)
    plt.close(fig)


def plot_energy_flow(runs):
    fig, ax = plt.subplots(2, 1, figsize=(7.5, 4.4), sharex=True)
    for key, col, label in (("opt", "#2a78d6", "CPMD, start at 1.1645 Å"), ("1150", "#eb6834", "CPMD, start at 1.150 Å"),
                            ("bo_1150", "#1baf7a", "BOMD, start at 1.150 Å")):
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
