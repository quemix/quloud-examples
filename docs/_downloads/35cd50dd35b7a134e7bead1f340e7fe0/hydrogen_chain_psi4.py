#!/usr/bin/env python3
"""Finite neutral H chains: RHF/RKS MO energies versus standing-wave pseudo-k.

Requires Psi4, numpy and matplotlib.
Run:     python hydrogen_chain_psi4.py --method rhf --a 1.8

This is a pedagogical, spin-restricted, fixed-geometry calculation. The pseudo-k
assignment and cosine fit are approximate and are NOT a real periodic band plot.
"""
import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import psi4

EV_PER_HARTREE = 27.211386245988


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--method', choices=['rhf', 'rks'], default='rhf')
    p.add_argument('--xc', default='pbe', help='DFT XC functional (RKS only)')
    p.add_argument('--a', type=float, default=1.8, help='H-H spacing in angstrom')
    p.add_argument('--basis', default='sto-3g')
    p.add_argument('--ns', type=int, nargs='+', default=[2, 4, 8, 16, 24])
    p.add_argument('--prefix', default='hydrogen_chain')
    args = p.parse_args()

    if args.a <= 0:
        p.error('--a must be positive')
    if any(n < 2 or n % 2 for n in args.ns):
        p.error('This spin-restricted demo accepts even atom counts >= 2 only')

    psi4.set_num_threads(2)
    psi4.core.set_output_file(f'{args.prefix}_psi4.log', False)
    fig, ax = plt.subplots(figsize=(8, 5.5))
    records = []
    last = None

    for n in sorted(set(args.ns)):
        geometry = "0 1\n" + "\n".join(
            f"H {i * args.a:.12f} 0.0 0.0" for i in range(n)
        ) + "\nunits angstrom\nsymmetry c1\nno_reorient\nno_com\n"
        mol = psi4.geometry(geometry)
        psi4.set_options({'basis': args.basis, 'reference': 'rhf',
                          'maxiter': 500, 'guess': 'core', 'e_convergence': 1e-9,
                          'd_convergence': 1e-9})
        method = 'scf' if args.method == 'rhf' else args.xc
        try:
            _, wfn = psi4.energy(method, molecule=mol, return_wfn=True)
        except psi4.ConvergenceError:
            print(f'WARNING: N={n} SCF did not converge; omitted')
            psi4.core.clean()
            continue
        e_ev = np.asarray(wfn.epsilon_a()) * EV_PER_HARTREE
        if len(e_ev) != n:
            raise ValueError('This pseudo-k demonstration requires one basis function per atom; use STO-3G')
        occ = np.zeros(len(e_ev))
        occ[:wfn.nalpha()] = 2
        e_rel = e_ev - np.mean(e_ev)
        # Standing-wave pseudo-k: exact only in the nearest-neighbor TB model.
        ka = np.arange(1, len(e_ev) + 1) * np.pi / (len(e_ev) + 1)
        ax.scatter(ka, e_rel, s=28, alpha=0.85, label=f'N={n}')

        homo = np.max(e_ev[occ > 0])
        lumo = np.min(e_ev[occ == 0])
        print(f'N={n:2d}: N(MO)={len(e_ev):2d}, '
              f'HOMO-LUMO orbital gap={lumo-homo:9.5f} eV')
        for j, (x, e, er, o) in enumerate(zip(ka, e_ev, e_rel, occ), start=1):
            records.append([n, j, x, e, er, o])
        last = n, ka, e_rel
        psi4.core.clean()

    if last is None:
        raise RuntimeError('No converged SCF results. Try smaller Ns or another spacing.')

    # A cosine least-squares fit to the largest converged chain (not TB input).
    n, ka, e_rel = last
    fit = np.polyfit(np.cos(ka), e_rel, 1)
    xgrid = np.linspace(0, np.pi, 500)
    ax.plot(xgrid, np.polyval(fit, np.cos(xgrid)), 'k--', lw=1.7,
            label=f'cosine fit to N={n}')
    ax.axvline(np.pi / 2, color='gray', linestyle=':', linewidth=1)
    ax.set(xlim=(0, np.pi), xlabel=r'Pseudo wave number $ka$',
           ylabel='MO energy minus chain mean (eV)',
           title=f'Finite hydrogen chains: {args.method.upper()}, '
                 f'{args.basis}, a={args.a:g} angstrom')
    ax.legend(fontsize=9, ncol=2)
    fig.tight_layout()
    path = Path(f'{args.prefix}_bands.png')
    fig.savefig(path, dpi=170)
    plt.close(fig)

    csvpath = Path(f'{args.prefix}_orbitals.csv')
    with csvpath.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['n_atoms', 'orbital_index', 'pseudo_ka',
                         'energy_eV', 'energy_relative_to_mean_eV', 'occupancy'])
        writer.writerows(records)
    print(f'Saved: {path}, {csvpath}')


if __name__ == '__main__':
    main()
