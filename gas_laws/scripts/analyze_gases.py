#!/usr/bin/env python3
"""Analyze GROMACS output folders or Quloud download ZIPs (not ZIP names).

Requires Python 3, NumPy and GROMACS 2026.2. Never runs MD. TRR layout:
https://github.com/gromacs/gromacs/blob/v2026.2/src/gromacs/fileio/trrio.cpp
"""
import argparse
import csv
import hashlib
import json
import re
import shlex
import struct
import subprocess
import tempfile
import zipfile
from pathlib import Path

import numpy as np

KB = 1.380649e-23
NA = 6.02214076e23
R = KB * NA
T0 = 273.15
P0 = 1.01325


def write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)


def trr_frames(path):
    """Stream single/double precision TRR; reject obsolete embedded blocks."""
    with Path(path).open('rb') as f:
        def read(n):
            b = f.read(n)
            if len(b) != n:
                raise ValueError(f'Truncated TRR: {path}')
            return b
        def integer():
            return struct.unpack('>i', read(4))[0]
        while True:
            magic = f.read(4)
            if not magic:
                return
            if len(magic) != 4 or struct.unpack('>i', magic)[0] != 1993:
                raise ValueError(f'Invalid TRR magic: {path}')
            string_size = integer()
            n = integer()
            if n != 12 or string_size != 13 or read((n+3)//4*4) != b'GMX_trn_file':
                raise ValueError('Unsupported TRR version')
            sizes = [integer() for _ in range(10)]
            natoms, step, _ = integer(), integer(), integer()
            if any(sizes[i] for i in (0, 1, 5, 6)) or natoms <= 0 or min(sizes) < 0:
                raise ValueError('Unsupported TRR embedded block or atom count')
            precision = next((sizes[i]//n for i,n in ((2,9),(7,natoms*3),(8,natoms*3),(9,natoms*3)) if sizes[i]),0)
            if precision not in (4,8):
                raise ValueError('Invalid TRR precision')
            dtype = '>f4' if precision == 4 else '>f8'
            time, _ = np.frombuffer(read(2*precision),dtype=dtype)
            arrays = []
            for size in sizes[2:5] + sizes[7:10]:
                arrays.append(np.frombuffer(read(size),dtype=dtype).astype(float) if size else None)
            box, _, _, x, v, force = arrays
            yield dict(time=float(time), step=step, natoms=natoms, precision_bytes=precision,
                       box=None if box is None else box.reshape(3,3),
                       x=None if x is None else x.reshape(natoms,3),
                       v=None if v is None else v.reshape(natoms,3),
                       force=None if force is None else force.reshape(natoms,3))


def topology_from_dump(text):
    """Use TPR's molecule blocks and masses, never element-name mass guesses."""
    header, body = text.split('   ffparams:',1)
    blocks = re.findall(r'moltype\s*=\s*(\d+)\s+"([^"]+)"\s+#molecules\s*=\s*(\d+)',header)
    templates = {}
    sections = re.split(r'\n   moltype \((\d+)\):\n',body)
    for i in range(1,len(sections),2):
        masses = re.findall(r'atom\[\s*\d+\]=\{type=.*?\bm=\s*([\deE+.\-]+), q=\s*([\deE+.\-]+)',sections[i+1])
        templates[int(sections[i])] = np.array(masses,dtype=float)
    molecules, names, charges = [], [], []
    for typ,name,count in blocks:
        sites = templates[int(typ)]
        for _ in range(int(count)):
            molecules.append(sites[:,0]); charges.extend(sites[:,1]); names.append(name)
    if not molecules:
        raise ValueError('No molecule blocks in GROMACS TPR dump')
    masses = np.concatenate(molecules)
    if len(masses) != int(re.search(r'#atoms\s*=\s*(\d+)',header)[1]):
        raise ValueError('TPR molecule/atom count mismatch')
    return molecules, names, masses, np.asarray(charges)


def xvg(path):
    legends = []
    for line in path.read_text().splitlines():
        if match := re.match(r'@ s\d+ legend "([^"]+)"',line):
            legends.append(match[1])
    return np.loadtxt(path,comments=['#','@'],ndmin=2), legends


def block_stats(time,values):
    """Maximum block SEM over 5,10,20,40,80 ps; save all for inspection."""
    mean = float(np.mean(values))
    result=[]
    origin=time[0]
    for width in (5.,10.,20.,40.,80.):
        nblocks=int(round((time[-1]-time[0]+np.median(np.diff(time)))/width))
        if nblocks<4: continue
        blocks=[np.mean(values[(time>=origin+i*width-1e-5)&(time<origin+(i+1)*width-1e-5)]) for i in range(nblocks)]
        if not np.all(np.isfinite(blocks)): continue
        sem=float(np.std(blocks,ddof=1)/np.sqrt(nblocks))
        result.append((width,nblocks,sem))
    return mean, max((a[2] for a in result),default=float('nan')), result

def autocorrelation_time(time, values):
    """Integrated correlation time: initial positive pairs, regular samples.

    Convention: independent samples have tau_int = sample_interval/2.
    A finite record gives an estimate, not a guarantee of equilibration.
    """
    x=np.asarray(values)-np.mean(values); n=len(x)
    spectrum=np.fft.rfft(x,n=2*n)
    acf=np.fft.irfft(spectrum*spectrum.conjugate(),n=2*n)[:n]
    if acf[0]<=0: return 0.
    acf/=acf[0]; total=0.
    for i in range(1,n-1,2):
        pair=acf[i]+acf[i+1]
        if pair<=0: break
        total+=pair
    return float(np.median(np.diff(time))*(.5+total))


def analyze_job(output,dest,gmx,equil=40.):
    required=['nvt.edr','nvt.tpr','nvt.trr','nvt.log']
    if not all((output/p).exists() for p in required):
        raise ValueError(f'Missing required output: {output}')
    if 'Finished mdrun' not in (output/'nvt.log').read_text():
        raise ValueError(f'Incomplete MD: {output}')
    dest.mkdir(parents=True,exist_ok=True)
    dump_path=dest/'tpr_dump.txt'
    if not dump_path.exists():
        result=subprocess.run(gmx+['dump','-s',str(output/'nvt.tpr')],capture_output=True,text=True,check=True)
        dump_path.write_text(result.stdout)
    dump=dump_path.read_text()
    molecules,names,masses,charges=topology_from_dump(dump)
    if len(set(names))!=1: raise ValueError('This comparison expects a pure gas')
    known_names={'AR':'Ar','H2':'H2','N2':'N2','O2':'O2','CO2':'CO2'}
    if names[0] not in known_names: raise ValueError('Unsupported gas molecule type')
    gas=known_names[names[0]]
    reference_temperature=float(re.search(r'ref-t:\s*(\S+)',dump)[1])
    if abs(reference_temperature-T0)>.001:
        raise ValueError('This example expects a target temperature of 273.15 K')
    energy_path=dest/'energy.xvg'
    if not energy_path.exists():
        result=subprocess.run(gmx+['energy','-f',str(output/'nvt.edr'),'-o',str(energy_path)],
                              input='Pressure\nTemperature\nPotential\nKinetic-En.\nTotal-Energy\nConserved-En.\n0\n',
                              capture_output=True,text=True,check=True)
        (dest/'energy_extraction.log').write_text(result.stdout+'\n'+result.stderr)
    energy,legends=xvg(energy_path)
    if not set(['Pressure','Temperature','Potential','Kinetic En.','Total Energy']).issubset(legends):
        raise ValueError(f'Energy selection failed: {legends}')
    write_csv(dest/'energy_raw.csv',['time_ps']+legends,energy)
    data={name:energy[:,i+1] for i,name in enumerate(legends)}
    selected=energy[:,0]>equil+1e-5
    if np.count_nonzero(selected)<2:
        raise ValueError('No measurement interval after equilibration')
    requested_dt=float(re.search(r'\n\s+dt\s*=\s*(\S+)',dump)[1])
    requested_steps=int(re.search(r'\n\s+nsteps\s*=\s*(\S+)',dump)[1])
    if requested_steps>0 and energy[-1,0]<requested_dt*requested_steps-2*requested_dt:
        raise ValueError('Run ended before the requested simulation length')
    times=energy[selected,0]
    stats={}; blocks=[]
    for key in ('Pressure','Temperature','Potential','Kinetic En.','Total Energy','Conserved En.'):
        if key not in data: continue
        mean,sem,scan=block_stats(times,data[key][selected])
        stats[key]=dict(mean=mean,sem=sem,tau_int_ps=autocorrelation_time(times,data[key][selected]))
        blocks.extend((key,*row) for row in scan)
    starts=np.cumsum([0]+[len(m) for m in molecules[:-1]])
    mol_mass=np.array([sum(m) for m in molecules])
    rows=[]; com_rows=[]; lengths=[]; angles=[]
    first_box=None
    for frame in trr_frames(output/'nvt.trr'):
        if frame['natoms']!=len(masses): raise ValueError('TRR/TPR mismatch')
        if frame['box'] is not None:
            if first_box is None: first_box=frame['box']
            if not np.allclose(frame['box'],first_box,rtol=0,atol=1e-6):
                raise ValueError('Volume changed in an NVT comparison')
        if frame['v'] is None: continue
        v=frame['v']; com=np.add.reduceat(v*masses[:,None],starts,axis=0)/mol_mass[:,None]
        speed2=np.sum(com**2,axis=1)*1e6
        system_com=np.sum(v*masses[:,None],axis=0)/sum(masses)*1000
        rows.append((frame['time'],float(np.mean(speed2)),float(np.sqrt(np.mean(speed2))),
                     float(.5*np.sum(masses[:,None]*v**2)),float(np.linalg.norm(system_com))))
        com_rows.append((frame['time'],*com[0]))
        if frame['x'] is not None and gas!='Ar' and frame['time']>equil:
            x=frame['x']; vectors=[]
            for i,j in ([(0,1),(2,1)] if gas=='CO2' else [(1,0)]):
                d=x[starts+i]-x[starts+j]
                fractional=d@np.linalg.inv(frame['box'])
                d-=np.rint(fractional)@frame['box']
                vectors.append(d)
                lengths.extend(np.linalg.norm(d,axis=1))
            if gas=='CO2':
                cos=np.sum(vectors[0]*vectors[1],axis=1)/(np.linalg.norm(vectors[0],axis=1)*np.linalg.norm(vectors[1],axis=1))
                angles.extend(np.degrees(np.arccos(np.clip(cos,-1,1))))
    velocity=np.array(rows)
    if not len(velocity): raise ValueError('TRR contains no velocities')
    tpr_box_rows=re.findall(r'\bbox\[\s*\d+\]\s*=\{([^}]+)\}',dump)
    if len(tpr_box_rows)!=3:
        raise ValueError('Cannot identify the TPR box matrix')
    tpr_box=np.array([[float(v) for v in row.split(',')] for row in tpr_box_rows])
    if not np.allclose(first_box,tpr_box,rtol=2e-6,atol=2e-5):
        raise ValueError('TRR/TPR box mismatch')
    gro_box_checked=False
    if (output/'box.gro').exists():
        gro_lines=(output/'box.gro').read_text().splitlines()
        if int(gro_lines[1])!=len(masses): raise ValueError('GRO/TPR atom count mismatch')
        gro_box=np.array([float(v) for v in gro_lines[-1].split()])
        if len(gro_box)==3:
            if not np.allclose(first_box,np.diag(gro_box),rtol=2e-6,atol=2e-5):
                raise ValueError('GRO/TRR box mismatch')
            gro_box_checked=True
    mask=velocity[:,0]>equil+1e-5
    v2,v2sem,scan=block_stats(velocity[mask,0],velocity[mask,1])
    vrms=np.sqrt(v2); vsem=v2sem/(2*vrms)
    stats['vrms_m_s']=dict(mean=vrms,sem=vsem)
    blocks.extend(('speed_squared',*row) for row in scan)
    write_csv(dest/'velocity_raw.csv',['time_ps','mean_com_speed_squared_m2_s2','vrms_m_s','atomic_kinetic_kJ_mol','system_com_m_s'],velocity)
    write_csv(dest/'first_molecule_com.csv',['time_ps','vx_nm_ps','vy_nm_ps','vz_nm_ps'],com_rows)
    write_csv(dest/'block_scan.csv',['quantity','block_ps','n_blocks','sem'],blocks)
    n=len(molecules); volume=float(np.linalg.det(first_box)); vm=NA/n*volume*1e-24
    vrms_theory=float(np.sqrt(3*R*T0/(mol_mass[0]/1000)))
    half=(times[0]+times[-1])/2
    summary=dict(gas=gas,n_molecules=n,n_atoms=len(masses),volume_nm3=volume,length_nm=volume**(1/3),
                 molar_volume_L_mol=vm,molecular_mass_g_mol=float(mol_mass[0]),
                 net_charge_e=float(sum(charges)),ideal_pressure_bar=n*KB*T0/(volume*1e-27)/1e5,
                 ideal_vrms_m_s=vrms_theory,equilibration_ps=equil,
                 time_end_ps=float(energy[-1,0]),n_energy_samples=int(sum(selected)),n_velocity_samples=int(sum(mask)),
                 dt_ps=float(re.search(r'\n\s+dt\s*=\s*(\S+)',dump)[1]),
                 integrator=re.search(r'integrator\s*=\s*(\S+)',dump)[1],
                 lincs_order=int(re.search(r'lincs-order\s*=\s*(\S+)',dump)[1]),
                 lincs_iter=int(re.search(r'lincs-iter\s*=\s*(\S+)',dump)[1]),
                 verlet_buffer_tolerance=float(re.search(r'verlet-buffer-tolerance\s*=\s*(\S+)',dump)[1]),
                 trajectory_precision='double' if frame['precision_bytes']==8 else 'single',
                 nstcomm=int(re.search(r'nstcomm\s*=\s*(\S+)',dump)[1]),
                 thermostat_degrees_of_freedom=float(re.search(r'nrdf:\s*(\S+)',dump)[1]),
                 target_temperature_K=reference_temperature,
                 volume_source='TRR box determinant; constant across all stored frames',
                 tpr_box_checked=True,gro_atom_count_checked=(output/'box.gro').exists(),gro_box_checked=gro_box_checked,
                 thermostat_seed=int(re.search(r'\n\s+ld-seed\s*=\s*(\S+)',dump)[1]),
                 coulombtype=re.search(r'coulombtype\s*=\s*(\S+)',dump)[1],
                 rcoulomb_nm=float(re.search(r'rcoulomb\s*=\s*(\S+)',dump)[1]),
                 pressure_first_half_bar=float(data['Pressure'][selected][times<half].mean()),
                 pressure_second_half_bar=float(data['Pressure'][selected][times>=half].mean()),
                 max_system_com_m_s=float(np.max(velocity[mask,4])),
                 bond_min_nm=float(min(lengths)) if lengths else None,
                 bond_max_nm=float(max(lengths)) if lengths else None,
                 angle_mean_deg=float(np.mean(angles)) if angles else None,
                 angle_min_deg=float(min(angles)) if angles else None,
                 angle_max_deg=float(max(angles)) if angles else None,stats=stats,
                 source_sha256={p:hashlib.sha256((output/p).read_bytes()).hexdigest() for p in required})
    (dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def extract_zip(archive,dest):
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            target=(dest/member.filename).resolve()
            if not target.is_relative_to(dest.resolve()): raise ValueError('Unsafe ZIP path')
        z.extractall(dest)


def assign_roles(results):
    """Select this experiment's conditions from content, independent of ZIP names."""
    for j in results:
        full=abs(j['time_end_ps']-440)<.001 and j['n_molecules']==1000
        fixed=abs(j['length_nm']-33.3879144)<.0001
        role='control'
        if full and j['gas']=='Ar' and j['integrator'].lower()=='md' and j.get('verlet_buffer_tolerance',.005)>=0:
            if fixed: role='pilot'
            elif any(abs(j['length_nm']-l)<.0001 for l in (27,30,33,36,40)): role='pv'
        dt=.0005 if j['gas']=='H2' else .002
        if full and fixed and j['integrator'].lower()=='sd' and abs(j['dt_ps']-dt)<1e-8:
            role='comparison'
        j['experiment_role']=role
        j['selected_for_article']=role!='control'
    for gas in ('Ar','H2','N2','O2','CO2'):
        candidates=[j for j in results if j['experiment_role']=='comparison' and j['gas']==gas]
        if any(j['trajectory_precision']=='single' for j in candidates):
            for j in candidates:
                if j['trajectory_precision']!='single':
                    j['experiment_role']='control';j['selected_for_article']=False


def export_geometry(results,sources,dest):
    pilots=sorted([j for j in results if j.get('experiment_role')=='pilot' and j.get('selected_for_article',True)],key=lambda j:j['seed'])
    if pilots:
        pilot=pilots[0];path=sources[pilot['job_id']]/'nvt.trr'
        for last in trr_frames(path): pass
        wrapped=np.mod(last['x'],last['box'].diagonal()); L=last['box'][2,2]
        selected=np.where(np.abs(wrapped[:,2]-L/2)<=1.)[0]; chosen=selected[:5]
        write_csv(dest/'argon_snapshot.csv',['atom_index','x_nm','y_nm','z_nm'],[(i,*x) for i,x in enumerate(wrapped)])
        tracks=[]
        for frame in trr_frames(path):
            if last['time']-10<=frame['time']<=last['time']:
                for i in chosen:tracks.append((frame['time'],i,*np.mod(frame['x'][i],frame['box'].diagonal())))
        write_csv(dest/'argon_tracks.csv',['time_ps','atom_index','x_nm','y_nm','z_nm'],tracks)
        (dest/'argon_snapshot_meta.json').write_text(json.dumps(dict(slice_center_z_nm=float(L/2),slice_thickness_nm=2.,n_atoms_in_slice=len(selected),tracked_atom_indices=chosen.tolist()),indent=2)+'\n')
    elements={'Ar':['Ar'],'H2':['H','H'],'N2':['N','N'],'O2':['O','O'],'CO2':['O','C','O']};models={}
    for gas,symbols in elements.items():
        candidates=sorted([j for j in results if j.get('experiment_role')=='comparison' and j['gas']==gas and j.get('selected_for_article',True)],key=lambda j:j['seed'])
        if not candidates:continue
        j=candidates[0]
        for frame in trr_frames(sources[j['job_id']]/'nvt.trr'):last=frame
        x=last['x'][:len(symbols)].copy();dr=x-x[0]
        x-=np.rint(dr@np.linalg.inv(last['box']))@last['box']
        models[gas]=dict(coordinates_nm=x.tolist(),elements=symbols,time_ps=last['time'],job_id=j['job_id'])
    (dest/'model_coordinates.json').write_text(json.dumps(models,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path); p.add_argument('--out',type=Path,required=True)
    p.add_argument('--gmx',default='gmx'); p.add_argument('--equilibration-ps',type=float,default=40.)
    args=p.parse_args(); args.out=args.out.resolve(); args.out.mkdir(parents=True,exist_ok=True)
    gmx=shlex.split(args.gmx)
    with tempfile.TemporaryDirectory() as temporary:
        temp=Path(temporary)
        if args.source.is_file():
            extract_zip(args.source,temp/'input'); search=temp/'input'
        else:
            search=args.source.resolve()
        roots=sorted({path.parent for path in search.rglob('nvt.edr') if (path.parent/'nvt.tpr').exists()})
        for i,archive in enumerate(sorted(search.glob('*.zip'))):
            unpack=temp/str(i); extract_zip(archive,unpack)
            roots.extend(sorted({path.parent for path in unpack.rglob('nvt.edr') if (path.parent/'nvt.tpr').exists()}))
        results=[]; seen=set(); sources={}
        for root in roots:
            # Identity comes from file content, not an arbitrary downloaded ZIP name.
            identity=hashlib.sha256((root/'nvt.tpr').read_bytes()).hexdigest()[:12]
            if identity in seen: continue
            try:
                result=analyze_job(root,args.out/identity,gmx,args.equilibration_ps)
            except (ValueError,subprocess.CalledProcessError) as e:
                print(f'SKIPPED {root}: {e}'); continue
            result['analysis_id']=identity;result['job_id']=identity
            mdp=root/'nvt.mdp'
            seed=re.search(r'^\s*gen[-_]seed\s*=\s*(-?\d+)',mdp.read_text(),re.M) if mdp.exists() else None
            result['seed']=int(seed[1]) if seed else result['thermostat_seed']
            sources[identity]=root;results.append(result)
            seen.add(identity)
            print(identity,result['gas'],result['stats']['Pressure'],result['stats']['vrms_m_s'])
        if not results: raise SystemExit('No complete supported MD outputs found')
        assign_roles(results)
        export_geometry(results,sources,args.out)
        (args.out/'jobs.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__': main()
