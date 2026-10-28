"""Generate the figures of the hydrogen-chain example from the CSV files in ../data.

Run:     python plot_article_figures.py

No Psi4 calculation is performed. The PNG files are written to ../figures.
"""
from pathlib import Path
import csv

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)


def records(filename):
    with (DATA / filename).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def central_alternation(bond_orders):
    """Half of the difference between the means of the two alternating groups
    of the eight central bonds (same definition as the Psi4 analysis scripts)."""
    n_bonds = len(bond_orders)
    mid = (n_bonds + 1) // 2
    center = np.asarray(bond_orders[mid - 4:mid + 4])
    assert len(center) == 8
    return abs(center[::2].mean() - center[1::2].mean()) / 2


plt.rcParams.update({'font.size': 11, 'axes.spines.top': False,
                     'axes.spines.right': False, 'savefig.dpi': 180})

# Figure: schematic of the model geometry
fig, axes = plt.subplots(4, 1, figsize=(9, 4.8), sharex=True)
for ax, n in zip(axes, [2, 4, 8, 16]):
    x = np.arange(n, dtype=float)
    x *= min(0.65, 11.0 / (n - 1))
    x -= x.mean()
    ax.plot(x, np.zeros_like(x), lw=2.5, c='#5a97c7', zorder=1)
    ax.scatter(x, np.zeros_like(x), s=135, edgecolors='#356b95', linewidths=1.2,
               c='#b7d6ed', zorder=2)
    ax.text(0.015, .67, f'$N={n}$', transform=ax.transAxes, fontsize=13, va='center')
    ax.set_ylim(-.36, .36)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines[['bottom', 'left']].set_visible(False)
fig.text(.5, .02, 'Schematic: equally spaced H atoms with fixed nuclei, open ends',
         ha='center', fontsize=10)
fig.tight_layout(rect=(0, .045, 1, 1))
fig.savefig(FIG / 'model_chains.png', bbox_inches='tight')
plt.close(fig)

# Figure: converged restricted PBE orbital energies versus pseudo wave number.
# N=32 exists in both the core-guess and SAD-guess files; the core result is used
# (the two agree to the printed precision).
pbe = {}
for r in records('pbe_core_orbitals.csv') + records('pbe_sad_orbitals.csv'):
    pbe.setdefault((int(r['n_atoms']), int(r['orbital_index'])), r)
fig, ax = plt.subplots(figsize=(9.0, 5.6))
for n in (2, 4, 8, 16, 32, 64):
    rr = [pbe[(n, j)] for j in range(1, n + 1)]
    ax.scatter([float(r['pseudo_ka']) for r in rr],
               [float(r['energy_relative_to_mean_eV']) for r in rr],
               label=f'N={n}', s=48 if n < 16 else 22 if n < 64 else 15, alpha=.9)
ax.axvline(np.pi / 2, c='0.65', ls=':', lw=1)
ax.set_xlabel('Assigned pseudo wave number  ka')
ax.set_ylabel('MO energy relative to chain mean (eV)')
ax.set_title('Restricted PBE: more atoms, denser orbital levels')
ax.set_xlim(0, np.pi)
ax.legend(ncol=3, loc='upper left', fontsize=10)
fig.tight_layout()
fig.savefig(FIG / 'pbe_levels.png', bbox_inches='tight')
plt.close(fig)

# Figure: HOMO-LUMO orbital gap versus N with the finite-size reference.
rows = records('rhf_pbe_comparison.csv')
N = np.array([int(r['n_atoms']) for r in rows])
HF = np.array([float(r['rhf_gap_eV']) for r in rows])
PBE = np.array([float(r['pbe_gap_eV']) for r in rows])
fig, ax = plt.subplots(figsize=(8.8, 5.3))
ax.plot(N, HF, 'o-', label='RHF', lw=2.1, ms=5.5)
ax.plot(N, PBE, 'o-', label='RKS-PBE', lw=2.1, ms=5.5)
x = np.linspace(2, 64, 300)
ax.plot(x, 11.75 / (x + 1), '--', color='0.4', label='11.75 / (N + 1)  eV')
ax.set_yscale('log')
ax.set_xlim(0, 68)
ax.set_xlabel('Number of H atoms, N')
ax.set_ylabel('HOMO-LUMO orbital gap (eV, log scale)')
ax.set_title('Different size dependence of RHF and restricted PBE gaps')
ax.legend(loc='upper right')
ax.grid(axis='y', which='both', alpha=.18)
fig.tight_layout()
fig.savefig(FIG / 'orbital_gaps.png', bbox_inches='tight')
plt.close(fig)

# Figure: RHF and restricted PBE orbital energies of the N=64 chain.
rhf = [r for r in records('rhf_orbitals.csv') if int(r['n_atoms']) == 64]
fig, ax = plt.subplots(figsize=(8.8, 5.4))
for label, rr, marker in [('RHF', rhf, 'o'),
                          ('RKS-PBE', [pbe[(64, j)] for j in range(1, 65)], 's')]:
    ka = np.array([float(r['pseudo_ka']) for r in rr])
    e = np.array([float(r['energy_relative_to_mean_eV']) for r in rr])
    occ = np.array([float(r['occupancy']) for r in rr]) > 0
    line, = ax.plot(ka[occ], e[occ], marker, ms=4.5, label=f'{label} (occupied)')
    ax.plot(ka[~occ], e[~occ], marker, ms=4.5, mfc='none', c=line.get_color(),
            label=f'{label} (unoccupied)')
ax.axvline(np.pi / 2, c='0.65', ls=':', lw=1)
ax.set_xlim(0, np.pi)
ax.set_xlabel('Assigned pseudo wave number  ka')
ax.set_ylabel('MO energy relative to chain mean (eV)')
ax.set_title('N = 64: RHF has a step at ka = pi/2, restricted PBE does not')
ax.legend(loc='upper left', fontsize=10)
fig.tight_layout()
fig.savefig(FIG / 'rhf_pbe_levels_n64.png', bbox_inches='tight')
plt.close(fig)

# Figure: central Lowdin bond-order alternation versus N.
groups = {}
for r in records('hydrogen_chain_bond_order.csv'):
    groups.setdefault((int(r['n_atoms']), r['method']), []).append(
        (int(r['atom_i']), float(r['lowdin_bond_order'])))
nums = [16, 32, 64]
series = {m: [central_alternation([v for _, v in sorted(groups[(n, m)])]) for n in nums]
          for m in ('RHF', 'RKS-PBE')}
fig, ax = plt.subplots(figsize=(8.5, 5.0))
for meth, vals in series.items():
    ax.plot(nums, vals, 'o-', label=meth, ms=7, lw=2.2)
ax.set_xlabel('Number of H atoms, N')
ax.set_ylabel('Central bond-order alternation amplitude')
ax.set_title('RHF bond alternation persists, while PBE boundary oscillation shrinks')
ax.set_ylim(0, .28)
ax.set_xticks(nums)
ax.grid(axis='y', alpha=.2)
ax.legend()
fig.tight_layout()
fig.savefig(FIG / 'bond_alternation.png', bbox_inches='tight')
plt.close(fig)

# Figure: bond orders and spin populations of the N=32 chain,
# restricted and unrestricted solutions.
methods = ('RHF', 'RKS-PBE', 'UHF', 'UKS-PBE')
bonds = {m: [] for m in methods}
for r in records('hydrogen_chain_spin_bonds.csv'):
    if int(r['n']) == 32:
        bonds[r['method']].append((int(r['atom_i']), float(r['lowdin_bond_order'])))
spins = {m: [] for m in methods}
for r in records('hydrogen_chain_spin_sites.csv'):
    if int(r['n']) == 32:
        spins[r['method']].append((int(r['atom']), float(r['lowdin_spin_alpha_minus_beta'])))
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.0, 8.0))
for m in methods:
    i, v = zip(*sorted(bonds[m]))
    ax1.plot(i, v, 'o-', ms=3.5, lw=1.6, label=m)
ax1.set_xlabel('Bond: atom i to i+1')
ax1.set_ylabel('Lowdin bond order')
ax1.set_title('N = 32, spacing 1.8 angstrom, STO-3G')
ax1.legend(ncol=4, loc='upper center', fontsize=10, bbox_to_anchor=(.5, -.18))
for m in ('UHF', 'UKS-PBE'):
    i, v = zip(*sorted(spins[m]))
    ax2.plot(i, v, 'o-', ms=3.5, lw=1.6, label=m, c='C2' if m == 'UHF' else 'C3')
ax2.axhline(0, c='0.6', lw=.8)
ax2.set_xlabel('Atom index')
ax2.set_ylabel('Lowdin spin population (alpha - beta)')
ax2.legend(loc='upper right', fontsize=10)
fig.tight_layout()
fig.savefig(FIG / 'spin_and_bonds_n32.png', bbox_inches='tight')
plt.close(fig)

print('Generated:', *sorted(p.name for p in FIG.glob('*.png')), sep='\n  ')
print('Central bond alternation:')
for meth, vals in series.items():
    print(' ', meth, dict(zip(nums, [round(float(v), 5) for v in vals])))
