#!/usr/bin/env python3
"""Independent ideal gas predictions. SI constants are exact since 2019."""
import argparse, csv, json, math
from pathlib import Path

KB=1.380649e-23
NA=6.02214076e23
R=KB*NA
TEMPERATURE=273.15
ATM_PA=101325.
MASSES={'H2':2.016,'N2':28.014,'O2':31.998,'Ar':39.948,'CO2':44.009}

def argon_pressure_virial(cutoff_nm=1.2, points=100000):
    """Pressure second virial for potential-shift LJ, no dispersion tail.

    Bp = -2*pi*NA/(3*RT) integral r^3 U'(r) exp[-(U(r)-U(rc))/RT] dr.
    U is in kJ/mol, r in nm; return L/mol. This is a dilute pair
    approximation for the simulated force law, not a fitted parameter.
    """
    import numpy as np
    sigma, epsilon = .33952, .97105
    r=np.linspace(sigma*.15,cutoff_nm,points)
    q=(sigma/r)**6; qc=(sigma/cutoff_nm)**6
    u=4*epsilon*(q*q-q); uc=4*epsilon*(qc*qc-qc)
    derivative=24*epsilon*(q-2*q*q)/r
    integral=np.trapezoid(r**3*derivative*np.exp(-(u-uc)/(R*TEMPERATURE/1000)),r)
    return float(-2*math.pi/3/(R*TEMPERATURE/1000)*integral*NA*1e-24)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('analysis'))
    args=parser.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    with (args.out/'ideal_pv.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['length_nm','box_volume_nm3','molar_volume_L_mol','ideal_pressure_bar'])
        for length in (27.,30.,33.,33.3879144,36.,40.):
            volume=length**3
            w.writerow([length,volume,NA/1000*volume*1e-24,1000*KB*TEMPERATURE/(volume*1e-27)/1e5])
    with (args.out/'ideal_speeds.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['gas','molar_mass_g_mol','ideal_vrms_m_s'])
        for gas,mass in MASSES.items(): w.writerow([gas,mass,math.sqrt(3*R*TEMPERATURE/(mass/1000))])
    constants=dict(k_B_J_K=KB,N_A_mol_inverse=NA,R_J_mol_K=R,temperature_K=TEMPERATURE,
                   atm_Pa=ATM_PA,ideal_molar_volume_L_mol=R*TEMPERATURE/ATM_PA*1000)
    (args.out/'constants.json').write_text(json.dumps(constants,indent=2)+'\n')
    virial=dict(model='argon_vrabec',sigma_nm=.33952,epsilon_kJ_mol=.97105,
                cutoff_nm=1.2,potential_modifier='Potential-shift',DispCorr='no',
                pressure_second_virial_L_mol=argon_pressure_virial(),
                quadrature_difference_L_mol=abs(argon_pressure_virial()-argon_pressure_virial(points=50000)),
                approximation='dilute pair distribution; omits third and higher virials')
    (args.out/'argon_virial.json').write_text(json.dumps(virial,indent=2)+'\n')
    print(json.dumps(constants,indent=2))

if __name__=='__main__': main()
