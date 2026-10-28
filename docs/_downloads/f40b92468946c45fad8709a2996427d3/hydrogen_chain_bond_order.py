#!/usr/bin/env python3
"""Finite neutral H chains: bond-order alternation, RHF versus RKS.

Requires Psi4 and numpy.
Run:     python hydrogen_chain_bond_order.py --a 1.8 --ns 16 32 64

Nearest-neighbor bond orders are the off-diagonal elements P(i,i+1) of the total
density matrix in the Lowdin-orthogonalized AO basis. The RHF run also performs
Psi4's stability analysis (eigenvalues are written to the Psi4 log). PK integrals
are used because Psi4 1.10 has no stability analysis for density-fitted SCF.
"""
import argparse
import csv
from pathlib import Path

import numpy as np
import psi4

EV_PER_HARTREE = 27.211386245988


def lowdin_bond_orders(wfn):
    """Return P(i,i+1) and the atomic populations in the Lowdin basis."""
    w, u = np.linalg.eigh(np.asarray(wfn.S()))
    s_half = u @ np.diag(np.sqrt(w)) @ u.T
    p = 2 * s_half @ np.asarray(wfn.Da()) @ s_half
    return np.diag(p, k=1), np.diag(p)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--xc', default='pbe', help='DFT XC functional for the RKS run')
    p.add_argument('--a', type=float, default=1.8, help='H-H spacing in angstrom')
    p.add_argument('--basis', default='sto-3g')
    p.add_argument('--ns', type=int, nargs='+', default=[16, 32])
    p.add_argument('--prefix', default='hydrogen_chain_bond_order')
    args = p.parse_args()

    if args.a <= 0:
        p.error('--a must be positive')
    if any(n < 10 or n % 2 for n in args.ns):
        p.error('Even atom counts >= 10 only (eight central bonds are averaged)')

    psi4.set_num_threads(2)
    psi4.core.set_output_file(f'{args.prefix}_psi4.log', False)
    runs = [('RHF', 'scf', 'core'), (f'RKS-{args.xc.upper()}', args.xc, 'sad')]
    records = []

    for n in sorted(set(args.ns)):
        geometry = "0 1\n" + "\n".join(
            f"H {i * args.a:.12f} 0.0 0.0" for i in range(n)
        ) + "\nunits angstrom\nsymmetry c1\nno_reorient\nno_com\n"
        for label, method, guess in runs:
            mol = psi4.geometry(geometry)
            psi4.core.clean_options()
            options = {'basis': args.basis, 'reference': 'rhf', 'scf_type': 'pk',
                       'maxiter': 500, 'guess': guess, 'e_convergence': 1e-9,
                       'd_convergence': 1e-9}
            if method == 'scf':
                options['stability_analysis'] = 'check'
            psi4.set_options(options)
            energy, wfn = psi4.energy(method, molecule=mol, return_wfn=True)

            bond_orders, populations = lowdin_bond_orders(wfn)
            e_ev = np.asarray(wfn.epsilon_a()) * EV_PER_HARTREE
            nocc = wfn.nalpha()
            middle = bond_orders[n // 2 - 4:n // 2 + 4]
            alternation = abs(middle[0::2].mean() - middle[1::2].mean()) / 2
            print(f'N={n:3d} {label:8s} E={energy:.8f} Eh  '
                  f'gap={e_ev[nocc] - e_ev[nocc - 1]:.4f} eV  '
                  f'central bonds={middle[3]:.4f}/{middle[4]:.4f}  '
                  f'alternation={alternation:.4f}  '
                  f'populations={populations.min():.4f}..{populations.max():.4f}')
            for i, bo in enumerate(bond_orders):
                records.append([n, label, i, i + 1, bo])
            psi4.core.clean()

    csvpath = Path(f'{args.prefix}.csv')
    with csvpath.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['n_atoms', 'method', 'atom_i', 'atom_j', 'lowdin_bond_order'])
        writer.writerows(records)
    print(f'Saved: {csvpath}; RHF stability eigenvalues are in {args.prefix}_psi4.log')


if __name__ == '__main__':
    main()
