"""Recalculate paper claims from unchanged archived raw records, not new simulations."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ARCHIVES={
 'quantum_noise_historical.zip':'b76f05afca3d872ce3bc7b4ea043ec7e10ef3d555e042cdadc0eda8e5f0b0d95',
 'qsv2g_stage05_final_20261113T092554Z.zip':'87418c800c96537b143b7df594eaa79ee4015a05c867303f6239b40097316ee6'}
EXPECTED={'QSS':[62.76,65.67,74.83,88.41],
 'CLASSICAL_SHARING':[61.27,61.62,62.87,64.81],'QUORUM':[60.96,60.79,60.83,60.89]}

def checked_counts(values,expected):
 counts=values.value_counts().to_dict()
 if counts!=expected:raise ValueError(f'Outcome counts mismatch: {counts} != {expected}')
 return counts

def checked_medians(df):
 if len(df)!=18000 or not (df.status=='TERMINATED').all():
  raise ValueError('Timing campaign must contain 18000 completed transactions')
 counts=df.groupby(['L','variant']).size()
 if len(counts)!=12 or not (counts==1500).all():raise ValueError('Missing or unequal timing conditions')
 if df.duplicated(['L','variant','pair','block','trial']).any():raise ValueError('Duplicate timing trial identifiers')
 if not np.isfinite(df.inclusive_software_ms).all() or (df.inclusive_software_ms<0).any():raise ValueError('Invalid timings')
 table=df.groupby(['L','variant']).inclusive_software_ms.median().unstack()
 for variant,expected in EXPECTED.items():
  if not np.allclose(table.loc[[9,27,81,162],variant].round(2),expected,rtol=0,atol=1e-8):
   raise ValueError(f'Manuscript median mismatch: {variant}')
 return table

def read_member(archive,suffix):
 names=[n for n in archive.namelist() if n.endswith(suffix)]
 if len(names)!=1:raise ValueError(f'Ambiguous or absent archive member {suffix}')
 return archive.read(names[0])

def audit(repo,out):
 repo=Path(repo);out=Path(out)
 if out.exists() and any(out.iterdir()):raise FileExistsError('Choose an empty output directory')
 out.mkdir(parents=True,exist_ok=True)
 paths=[repo/'results/archives'/n for n in ARCHIVES]
 hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
 if hashes!=ARCHIVES:raise ValueError('Historical archive SHA-256 mismatch')
 with zipfile.ZipFile(paths[0]) as z:
  noise=pd.read_csv(io.BytesIO(read_member(z,'noise_trial_events.csv.gz')),compression='gzip')
 with zipfile.ZipFile(paths[1]) as z:
  times=pd.read_csv(io.BytesIO(read_member(z,'e1/e1_trials.csv')))
  vectors=pd.read_csv(io.BytesIO(read_member(z,'e3/e3_vector_trials.csv')))
  tokens=pd.read_csv(io.BytesIO(read_member(z,'e3/e3_token_trials.csv')))
  manifest=json.loads(read_member(z,'e1/manifest.json'))
  original_revision=read_member(z,'git_revision.txt').decode().strip()
 if len(noise)!=315000 or noise.duplicated(['config_id','trial']).any():raise ValueError('Single-trit trial identity/count mismatch')
 if not (noise.groupby('config_id').size()==1000).all() or noise.config_id.nunique()!=315:raise ValueError('Noise configuration counts mismatch')
 if not (noise[['correct','wrong','aborted']].sum(axis=1)==1).all():raise ValueError('Invalid noise outcomes')
 ng=noise.groupby(['model','p']).agg(trials=('correct','size'),correct=('correct','sum'),wrong=('wrong','sum'),aborted=('aborted','sum')).reset_index()
 ng['correct_probability']=ng.correct/ng.trials
 if len(ng)!=35 or not (ng.trials==9000).all():raise ValueError('Noise grid incomplete')
 endpoints={'x':.7007,'dephasing':1.,'depolarizing':.8028,'erasure':.7038,'combined':.5901}
 for model,value in endpoints.items():
  obs=float(ng.loc[(ng.model==model)&(ng.p==.3),'correct_probability'].iloc[0])
  if round(obs,4)!=value:raise ValueError(f'Noise endpoint mismatch: {model}')
 medians=checked_medians(times)
 vc=checked_counts(vectors.outcome,{'COMMITMENT_GATE_ELIGIBLE':191736,'COMMITMENT_REJECT':81400,'ERASURE_ABORT':26864})
 tc=checked_counts(tokens.outcome,{'ACCEPTED_AT_EV':3854,'COMMITMENT_REJECT':1606,'ERASURE_ABORT':540})
 ng.to_csv(out/'single_trit_from_raw.csv',index=False);medians.to_csv(out/'inclusive_medians_from_raw.csv')
 report={'status':'PASS','scope':'Reaggregation of preserved historical observations, not independent rerun or authenticated cloud provenance',
  'archive_sha256':hashes,'historical_stage05_revision':original_revision,'historical_e1_manifest':manifest,
  'single_trit_rows':len(noise),'timing_rows':len(times),'vector_outcomes':vc,'endpoint_outcomes':tc,
  'medians_ms':medians.to_dict(),'QSS_excess_percent':(100*(medians.QSS/medians.CLASSICAL_SHARING-1)).to_dict(),
  'limitations':['Historical source versions differ from current modular code','Timing is environment-dependent','No quantum deployment or full security proof','No confidence intervals invented']}
 (out/'claim_verification.json').write_text(json.dumps(report,indent=2))
 # Draw directly from the checked records; no copied manuscript values feed the plots.
 import matplotlib
 matplotlib.use('Agg')
 from matplotlib import pyplot as plt
 plt.rcParams.update({'font.size':8,'pdf.fonttype':42,'svg.fonttype':'none'})
 fig,ax=plt.subplots(figsize=(3.5,2.5))
 for name,label,style in [('dephasing','Dephasing','s-'),('depolarizing','Depolarization','^--'),('x','X shift','o-.'),('erasure','Flagged erasure','x:'),('combined','Combined','D-')]:
  g=ng[ng.model==name];ax.plot(g.p,g.correct_probability,style,label=label,ms=3,lw=1)
 ax.set(xlabel='Noise probability p',ylabel='Correct-trit probability',ylim=(.56,1.02));ax.legend(fontsize=6.5);ax.grid(alpha=.2);fig.tight_layout()
 for ext in ['pdf','svg']:fig.savefig(out/f'noise_from_raw.{ext}')
 plt.close(fig)
 fig,ax=plt.subplots(figsize=(3.5,2.5))
 for name,label,style in [('QSS','QSS','o-'),('CLASSICAL_SHARING','Classical 2-of-3','s--'),('QUORUM','Signature quorum*','^:')]:ax.plot(medians.index,medians[name],style,label=label,ms=3,lw=1)
 ax.set(xlabel='Dealer vector length L',ylabel='Median inclusive software time (ms)',xticks=[9,27,81,162]);ax.legend(fontsize=7);ax.grid(alpha=.2);fig.tight_layout()
 for ext in ['pdf','svg']:fig.savefig(out/f'latency_from_raw.{ext}')
 plt.close(fig)
 (out/'README.md').write_text('Figures are regenerated from verified historical raw records. Noise is single-trit recovery with erasures counted as failures; no interval is inferred. Latency includes preparation. *Signature quorum omits reconstruction and is weaker-function. These are reaggregations, not new experiment measurements. See claim_verification.json for archive hashes and historical revision.\n')
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 report=audit(a.repo,a.out);print(json.dumps({k:report[k] for k in ['status','single_trit_rows','timing_rows','vector_outcomes','endpoint_outcomes']},indent=2))
if __name__=='__main__':main()
