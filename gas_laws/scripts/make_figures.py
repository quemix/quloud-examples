#!/usr/bin/env python3
"""Deterministic figures and summaries from analyzed CSV/JSON, no MD runs."""
import argparse, csv, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from analyze_gases import write_csv
from theory import R, TEMPERATURE, MASSES, argon_pressure_virial

ORDER=['H2','N2','O2','Ar','CO2']
LABELS={'H2':r'$\mathrm{H_2}$','N2':r'$\mathrm{N_2}$','O2':r'$\mathrm{O_2}$','Ar':'Ar','CO2':r'$\mathrm{CO_2}$'}
COLORS=dict(zip(ORDER,['#0072B2','#009E73','#D55E00','#8A5CA7','#333333']))

def combine(jobs,key):
    means=np.array([j['stats'][key]['mean'] for j in jobs])
    sems=np.array([j['stats'][key]['sem'] for j in jobs])
    if len(jobs)<2: raise ValueError('At least two seeds needed')
    between=means.std(ddof=1)/len(jobs)**.5
    within=np.sqrt(np.sum(sems**2))/len(jobs)
    return float(means.mean()),float(max(between,within))

def save(fig,path):
    fig.savefig(path,dpi=180,bbox_inches='tight',metadata={'Software':'Matplotlib'})
    plt.close(fig)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('analysis',type=Path); p.add_argument('--figures',type=Path,required=True)
    p.add_argument('--only-argon',action='store_true',help='Regenerate the first article without five-gas data')
    args=p.parse_args(); data=args.analysis; figs=args.figures; figs.mkdir(parents=True,exist_ok=True)
    all_jobs=json.loads((data/'jobs.json').read_text())
    jobs=[j for j in all_jobs if j.get('selected_for_article',True)]
    pv=[]
    for length in (27.,30.,33.,33.3879144,36.,40.):
        subset=[j for j in jobs if j['gas']=='Ar' and abs(j['length_nm']-length)<.0001 and j['n_molecules']==1000 and j['integrator'].lower()=='md']
        mean,sem=combine(subset,'Pressure'); vm=np.mean([j['molar_volume_L_mol'] for j in subset])
        pv.append((length,vm,mean,sem,len(subset)))
    write_csv(data/'pv_summary.csv',['length_nm','Vm_L_mol','P_bar','P_sem_bar','n_seeds'],pv)
    gases=[]
    for gas in ([] if args.only_argon else ORDER):
        subset=[j for j in jobs if j['gas']==gas and j.get('experiment_role')=='comparison']
        pressure,ps=combine(subset,'Pressure'); speed,vs=combine(subset,'vrms_m_s'); temperature,ts=combine(subset,'Temperature')
        gases.append((gas,MASSES[gas],pressure,ps,pressure/1.01325,ps/1.01325,speed,vs,
                      np.sqrt(3*R*TEMPERATURE/(MASSES[gas]/1000)),temperature,ts,len(subset)))
    if gases:
        double_reference=[]
        for gas in ORDER:
            dt=.0005 if gas=='H2' else .002
            group=[j for j in all_jobs if j['gas']==gas and j['trajectory_precision']=='double'
                   and j['integrator'].lower()=='sd' and j['n_molecules']==1000
                   and abs(j['time_end_ps']-440)<.001 and abs(j['length_nm']-33.3879144)<.0001
                   and abs(j['dt_ps']-dt)<1e-8
                   and j['lincs_order']==(8 if gas=='CO2' else 4)
                   and j['lincs_iter']==(2 if gas=='CO2' else 1)]
            if len(group)!=3:
                raise ValueError(f'{gas}: need three double precision reference runs for the pressure comparison figure; use the distributed analysis CSV/JSON or include their output ZIPs')
            mean,sem=combine(group,'Pressure')
            double_reference.append((gas,mean,sem,dt,len(group)))
        write_csv(data/'double_pressure_reference.csv',['gas','P_bar','P_sem_bar','dt_ps','n_seeds'],double_reference)
        write_csv(data/'gas_summary.csv',['gas','mass_g_mol','P_bar','P_sem_bar','Z','Z_sem','vrms_m_s','vrms_sem_m_s','ideal_vrms_m_s','T_K','T_sem_K','n_seeds'],gases)
        write_csv(data/'speed_table.csv',['気体','モル質量（g/mol）','理論値（m/s）','MD平均±標準誤差（m/s）'],
                  [(g[0],f'{g[1]:g}',f'{g[8]:.1f}',f'{g[6]:.1f} ± {g[7]:.1f}') for g in gases])
        write_csv(data/'pressure_table.csv',['気体','MD圧力±標準誤差（bar）','Z±標準誤差'],
                  [(g[0],f'{g[2]:.5f} ± {g[3]:.5f}',f'{g[4]:.5f} ± {g[5]:.5f}') for g in gases])
    # Free intercept and slope; 30,33,36 nm bracket 1 atm. No ideal volume used.
    near=np.array(pv)[1:5]; x=1/near[:,1]; y=near[:,2]; err=near[:,3]
    design=np.column_stack((x,np.ones_like(x))); weights=np.diag(err**-2)
    linear_map=np.linalg.inv(design.T@weights@design)@design.T@weights
    params=linear_map@y
    # Common random seeds across volumes correlate the pressures. Carry these
    # correlations through the fit instead of assuming independent points.
    near_jobs=[[j for j in jobs if j['gas']=='Ar' and abs(j['length_nm']-l)<.0001 and j['n_molecules']==1000 and j['integrator'].lower()=='md'] for l in (30.,33.,33.3879144,36.)]
    near_jobs=[sorted(group,key=lambda j:j['seed']) for group in near_jobs]
    seed_pressures=np.array([[j['stats']['Pressure']['mean'] for j in group] for group in near_jobs]).T
    between_cov=np.cov(seed_pressures,rowvar=False,ddof=1)/len(seed_pressures)
    within_candidates=[]
    for width in (5,10,20,40,80):
        within=np.zeros((4,4))
        for seed_index in range(3):
            arrays=[]
            for group in near_jobs:
                e=np.genfromtxt(data/group[seed_index]['job_id']/'energy_raw.csv',delimiter=',',names=True,deletechars='')
                v=e['Pressure'][e['time_ps']>40.00001]; size=width*10
                arrays.append(v[:len(v)//size*size].reshape(-1,size).mean(axis=1))
            block_matrix=np.array(arrays).T
            within+=np.cov(block_matrix,rowvar=False,ddof=1)/len(block_matrix)/9
        within_candidates.append(within)
    chi2=float(np.sum(((design@params-y)/err)**2))
    slope,intercept=params
    gradient=np.array([1/(1.01325-intercept),slope/(1.01325-intercept)**2])
    covariances=[linear_map@(between_cov+within)@linear_map.T for within in within_candidates]
    covariance=max(covariances,key=lambda c:gradient@c@gradient)
    covariance*=max(1.,chi2/(len(x)-2))
    slope,intercept=params; estimate=slope/(1.01325-intercept)
    gradient=np.array([1/(1.01325-intercept),slope/(1.01325-intercept)**2])
    fit_sem=float(np.sqrt(gradient@covariance@gradient))
    fit=dict(method='weighted P = a/Vm+b, free a and b; L=30,33,33.3879144,36 nm',slope_bar_L_mol=float(slope),
             intercept_bar=float(intercept),covariance=covariance.tolist(),chi_squared=chi2,
             molar_volume_at_1atm_L_mol=float(estimate),fit_sem_L_mol=fit_sem,
             ideal_molar_volume_L_mol=R*TEMPERATURE/101325*1000,
             error_method='Paired-seed covariance + synchronized block covariance (maximum over 5..80 ps); propagated through fit. Conservative addition.',
             caveat='Statistical fit SEM; finite-size, force-field, and numerical biases excluded.')
    (data/'pv_fit.json').write_text(json.dumps(fit,indent=2)+'\n')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white'})
    ar=sorted([j for j in jobs if j.get('experiment_role')=='pilot'],key=lambda j:j['seed'])[0]
    folder=data/ar['job_id']
    e=np.genfromtxt(folder/'energy_raw.csv',delimiter=',',names=True,deletechars='')
    fig,(ax,bt)=plt.subplots(2,1,figsize=(7.3,5.4),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    ax.plot(e['time_ps'],e['Pressure'],color='#9db4c4',lw=.35,label='MD samples (0.1 ps)')
    ma=np.convolve(e['Pressure'],np.ones(100)/100,mode='valid')
    ax.plot(e['time_ps'][49:-50],ma,color='#0072B2',lw=1.2,label='10 ps moving mean')
    for a in (ax,bt): a.axvspan(0,40,color='#ddcc77',alpha=.35)
    ax.axhline(ar['ideal_pressure_bar'],color='black',ls='--',lw=1,label='Ideal gas')
    ax.set_ylabel('Pressure (bar)'); ax.legend(loc='lower center',bbox_to_anchor=(.5,1.01),ncol=2,fontsize=8)
    bt.plot(e['time_ps'],e['Temperature'],lw=.4,color='#009E73'); bt.axhline(273.15,color='black',ls='--',lw=.8)
    bt.set(xlabel='Time (ps)',ylabel='Temperature (K)',xlim=(0,440))
    fig.tight_layout(); save(fig,figs/'fig02_argon_pressure_time.png')
    fig,(ax,bx)=plt.subplots(2,1,figsize=(7.3,8)); vm=np.linspace(10.5,41,300)
    ax.plot(vm,R*TEMPERATURE/100/vm,color='black',label='Ideal gas (273.15 K)')
    ax.errorbar([r[1] for r in pv],[r[2] for r in pv],yerr=[r[3] for r in pv],fmt='o',capsize=4,color=COLORS['Ar'],label='MD mean +/- SEM (3 seeds)')
    fitx=np.linspace(15,29,150); ax.plot(fitx,slope/fitx+intercept,color='#0072B2',ls=':',label='Local fit (4 nearby volumes)')
    ax.axhline(1.01325,color='gray',ls='--',label='1 atm = 1.01325 bar')
    ax.set(xlabel='Molar volume (L/mol)',ylabel='Pressure (bar)'); ax.legend(fontsize=8)
    bx.axhline(1,color='black',label='Ideal gas')
    bx.axhline(.999,color='gray',ls='--',label='COM removed (N=1000)')
    b2=argon_pressure_virial(); inv=np.linspace(0,.09,200)
    bx.plot(inv,.999*(1+b2*inv),color='#009E73',ls=':',label='COM + truncated LJ pair prediction')
    deviation_rows=[]
    for row in pv:
        length,volume,pressure,ps,_=row
        group=[j for j in jobs if j['gas']=='Ar' and j['integrator'].lower()=='md' and abs(j['length_nm']-length)<.0001]
        temperature=np.mean([j['stats']['Temperature']['mean'] for j in group])
        ideal=R*TEMPERATURE/100/volume; predicted=.999*(1+b2/volume)*temperature/TEMPERATURE
        bx.errorbar(1/volume,pressure/ideal,yerr=ps/ideal,fmt='o',capsize=4,color=COLORS['Ar'])
        bx.plot(1/volume,predicted,'x',color='#D55E00')
        deviation_rows.append((length,volume,pressure/ideal,ps/ideal,temperature,predicted,(pressure/ideal-predicted)/(ps/ideal)))
    bx.plot([],[],'x',color='#D55E00',label='Pair prediction at measured mean T')
    write_csv(data/'argon_deviations.csv',['length_nm','Vm_L_mol','Z','Z_sem','T_mean_K','predicted_Z_at_measured_T','residual_in_SEM'],deviation_rows)
    bx.set(xlabel='Inverse molar volume (mol/L)',ylabel=r'$Z=P V_m/(RT)$',xlim=(0,.09))
    bx.legend(fontsize=8,loc='lower left')
    ax.text(.98,.95,f'MD: {estimate:.3f} +/- {fit_sem:.3f} L/mol\nIdeal: {fit["ideal_molar_volume_L_mol"]:.3f} L/mol',ha='right',va='top',transform=ax.transAxes,fontsize=9)
    fig.tight_layout(); save(fig,figs/'fig03_argon_pv.png')
    # A 2 nm central slice shows the actual sparseness without depth overlap.
    snap=np.genfromtxt(data/'argon_snapshot.csv',delimiter=',',names=True)
    track=np.genfromtxt(data/'argon_tracks.csv',delimiter=',',names=True)
    fig,ax=plt.subplots(figsize=(6,6)); L=ar['length_nm']
    snap=snap[np.abs(snap['z_nm']-L/2)<=1.]
    for row in snap:
        ax.add_patch(Circle((row['x_nm'],row['y_nm']),.50,color=COLORS['Ar'],alpha=.35,lw=0))
    for atom in np.unique(track['atom_index']):
        t=track[track['atom_index']==atom]
        breaks=np.where(np.any(np.abs(np.diff(np.column_stack((t['x_nm'],t['y_nm'])),axis=0))>L/2,axis=1))[0]+1
        for segment in np.split(t,breaks): ax.plot(segment['x_nm'],segment['y_nm'],lw=1,color='#222222')
    ax.add_patch(Rectangle((0,0),L,L,fill=False,color='black'))
    ax.set(xlim=(0,L),ylim=(0,L),xlabel='x (nm)',ylabel='y (nm)',aspect='equal',title=f'Ar: 2 nm slice at 440 ps ({len(snap)} of 1000 atoms)')
    fig.tight_layout(); save(fig,figs/'fig01_argon_trajectory.png')
    if args.only_argon:
        print(json.dumps(fit,indent=2)); return
    fig,ax=plt.subplots(figsize=(6.7,4.3)); mass=np.linspace(1.8,48,400)
    ax.plot(mass,np.sqrt(3*R*TEMPERATURE/(mass/1000)),color='black',label=r'Ideal: $v_{rms}=\sqrt{3RT/M}$')
    for row in gases:
        gas,m,_,_,_,_,v,vs,*_=row
        ax.errorbar(m,v,yerr=vs,fmt='o',capsize=4,color=COLORS[gas]); ax.annotate(LABELS[gas],(m,v),xytext=(5,6),textcoords='offset points')
    ax.set(xlabel='Molar mass (g/mol)',ylabel='Molecular COM rms speed (m/s)'); ax.legend(fontsize=9)
    fig.tight_layout(); save(fig,figs/'fig02_speed_vs_mass.png')
    # Only show the resolved scale. Tiny species differences are not converged.
    fig,ax=plt.subplots(figsize=(6.7,4.6)); inds=np.arange(5)
    ax.errorbar(inds-.08,[g[2] for g in gases],yerr=[g[3] for g in gases],fmt='o',capsize=5,color='#0072B2',label='Mixed precision SD')
    ax.errorbar(inds+.08,[g[1] for g in double_reference],yerr=[g[2] for g in double_reference],fmt='s',mfc='none',capsize=5,color='#D55E00',label='Double precision SD (reference)')
    ax.axhline(1.01325,color='black',ls='--',label='Ideal gas: 1.01325 bar')
    ax.set(xticks=inds,xticklabels=[LABELS[g] for g in ORDER],ylabel='Pressure (bar)',ylim=(0,1.2))
    ax.legend(fontsize=9,loc='lower center',bbox_to_anchor=(.5,1.02))
    ax.text(.5,.10,'Pressure depends on timestep and constraint precision.\nSmall species differences are not numerically converged.',ha='center',transform=ax.transAxes,fontsize=8)
    fig.tight_layout(); save(fig,figs/'fig03_pressure_five_gases.png')
    # Model diagram uses saved actual atom positions (one molecule per gas).
    models=json.loads((data/'model_coordinates.json').read_text())
    fig,axes=plt.subplots(5,1,figsize=(7,6.1))
    atom_colors={'H':'#dddddd','N':'#4477aa','O':'#cc6677','Ar':'#aa77bb','C':'#444444'}
    for ax,gas in zip(axes,ORDER):
        xyz=np.array(models[gas]['coordinates_nm']); xyz-=xyz.mean(axis=0)
        # Show along bond to compare distance; coordinates themselves came from TRR.
        direction=(xyz[-1]-xyz[0]); norm=np.linalg.norm(direction)
        pos=np.zeros(len(xyz)) if not norm else xyz@(direction/norm)
        height=np.zeros(len(xyz))
        if len(xyz)==3:
            perpendicular=xyz[1]-np.dot(xyz[1],direction/norm)*direction/norm
            if np.linalg.norm(perpendicular)>1e-12:
                height=xyz@(perpendicular/np.linalg.norm(perpendicular))
        if len(xyz)>1: ax.plot(pos,height,color='#999999',lw=3,zorder=1)
        for x,y,symbol in zip(pos,height,models[gas]['elements']):
            ax.add_patch(Circle((x,y),.022,color=atom_colors[symbol],ec='#555555',zorder=2))
        ax.set(xlim=(-.26,.26),ylim=(-.045,.045),aspect='equal'); ax.axis('off')
        ax.text(-.245,0,LABELS[gas],ha='left',va='center',fontsize=13)
        ax.text(.245,0,f'{MASSES[gas]:g} g/mol',ha='right',va='center',fontsize=12)
    fig.tight_layout(); save(fig,figs/'fig01_five_gases_models.png')
    print(json.dumps(fit,indent=2))

if __name__=='__main__': main()
