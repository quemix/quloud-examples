#!/usr/bin/env python3
"""Compare restricted and spin-broken solutions for finite H chains with Psi4."""
import argparse
import csv
from pathlib import Path
import numpy as np
import psi4

EV = 27.211386245988

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ns', type=int, nargs='+', default=[16, 32])
    parser.add_argument('--a', type=float, default=1.8)
    parser.add_argument('--prefix', default='hydrogen_chain_spin')
    args = parser.parse_args()
    if args.a <= 0 or any(n < 10 or n % 2 for n in args.ns):
        parser.error('positive spacing and even N >= 10 required')
    psi4.set_num_threads(2)
    psi4.core.set_output_file(args.prefix + '_psi4.log', False)
    summary, sites, bonds, levels = [], [], [], []
    for n in sorted(set(args.ns)):
        seed_files = {}
        geometry = '0 1\n' + '\n'.join(f'H {i * args.a:.12f} 0 0' for i in range(n)) + '\nunits angstrom\nsymmetry c1\nno_reorient\nno_com\n'
        for label, method, ref, guess, mix in [('RHF','scf','rhf','core',False), ('RKS-PBE','pbe','rhf','sad',False), ('UHF','scf','uhf','read',False), ('UKS-PBE','pbe','uks','read',False)]:
            psi4.core.clean_options()
            psi4.set_options({'basis':'sto-3g', 'reference':ref, 'scf_type':'pk', 'maxiter':500, 'guess':guess, 'guess_mix':mix, 'e_convergence':1e-9, 'd_convergence':1e-9})
            try:
                kwargs = {'restart_file': seed_files[method]} if ref in ('uhf', 'uks') else {}
                energy, wfn = psi4.energy(method, molecule=psi4.geometry(geometry), return_wfn=True, **kwargs)
            except psi4.ConvergenceError:
                print(f'N={n} {label} FAILED TO CONVERGE', flush=True)
                psi4.core.clean()
                continue
            S = np.asarray(wfn.S())
            eig, vec = np.linalg.eigh(S)
            shalf = (vec * np.sqrt(eig)) @ vec.T
            da, db = np.asarray(wfn.Da()), np.asarray(wfn.Db())
            pa, pb = shalf @ da @ shalf, shalf @ db @ shalf
            total, spin = pa + pb, pa - pb
            bo = np.diag(total, 1)
            mid = bo[n//2-4:n//2+4]
            alt = abs(mid[::2].mean() - mid[1::2].mean()) / 2
            mag = np.diag(spin)
            na, nb = wfn.nalpha(), wfn.nbeta()
            ea, eb = np.asarray(wfn.epsilon_a())*EV, np.asarray(wfn.epsilon_b())*EV
            homo = max(ea[na-1], eb[nb-1]); lumo = min(ea[na], eb[nb])
            s2 = ((na-nb)/2)*((na-nb)/2+1) + nb - np.trace(da @ S @ db @ S)
            if ref == 'rhf':
                invhalf = (vec * (1 / np.sqrt(eig))) @ vec.T
                f_orth = invhalf @ np.asarray(wfn.Fa()) @ invhalf
                stagger = np.diag(np.where(np.arange(n) % 2 == 0, -0.5, 0.5))
                _, ua = np.linalg.eigh(f_orth + stagger)
                _, ub = np.linalg.eigh(f_orth - stagger)
                seed = wfn.to_file()
                seed['matrix']['Ca'], seed['matrix']['Cb'] = invhalf @ ua, invhalf @ ub
                seed['boolean']['same_a_b_orbs'] = False
                seed['boolean']['same_a_b_dens'] = False
                seed['string']['name'] = 'UHF'
                filename = f'{args.prefix}_seed_{n}_{method}.npy'
                np.save(filename, seed, allow_pickle=True)
                seed_files[method] = filename
                p0a = ua[:, :na] @ ua[:, :na].T
                p0b = ub[:, :nb] @ ub[:, :nb].T
                print(f'N={n} {label} seed spin range: {np.diag(p0a-p0b).min():.5f} to {np.diag(p0a-p0b).max():.5f}', flush=True)
            summary.append([n,label,energy,homo,lumo,lumo-homo,ea[na]-ea[na-1],eb[nb]-eb[nb-1],alt,np.mean(np.abs(mag)),mag.min(),mag.max(),s2])
            for i in range(n): sites.append([n,label,i+1,total[i,i],mag[i]])
            for i in range(n-1): bonds.append([n,label,i+1,i+2,bo[i]])
            for spin_label, es, num in [('alpha',ea,na),('beta',eb,nb)]:
                for i,e in enumerate(es): levels.append([n,label,spin_label,i+1,e,int(i<num)])
            print(f'N={n} {label} E={energy:.9f} gap={lumo-homo:.5f} alt={alt:.5f} mean|spin|={np.mean(np.abs(mag)):.5f} <S2>={s2:.5f}', flush=True)
            psi4.core.clean()
    for suffix, header, data in [('_summary.csv',['n','method','energy_Eh','homo_eV','lumo_eV','combined_gap_eV','alpha_gap_eV','beta_gap_eV','central_bond_alternation','mean_abs_lowdin_spin','min_lowdin_spin','max_lowdin_spin','s_squared'],summary),('_sites.csv',['n','method','atom','lowdin_population','lowdin_spin_alpha_minus_beta'],sites),('_bonds.csv',['n','method','atom_i','atom_j','lowdin_bond_order'],bonds),('_orbitals.csv',['n','method','spin','orbital','energy_eV','occupancy'],levels)]:
        with Path(args.prefix+suffix).open('w',newline='') as f:
            writer=csv.writer(f); writer.writerow(header); writer.writerows(data)

if __name__ == '__main__': main()
