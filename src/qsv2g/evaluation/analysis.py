"""Stage 05 manuscript-ready descriptive summaries from NEW raw trial files only.

Usage: python experiments/stage05/analyze.py results/stage05/<run_id>
Does not merge, overwrite or reinterpret historical Stage 01--04 results.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


def wilson(success,n,z=1.959963984540054):
    if n<=0:return float('nan'),float('nan')
    p=success/n;den=1+z*z/n
    mid=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0,mid-half),min(1,mid+half)


def analyze(root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    summary={}
    e1=root/'e1/e1_trials.csv'
    if e1.exists():
        df=pd.read_csv(e1)
        observed=len(df)
        failures=df[df.status!='TERMINATED']
        summary['e1_total_observations']=observed
        summary['e1_rejected_or_incomplete']=len(failures)
        if len(failures):
            failures.to_csv(root/'e1/e1_incomplete.csv',index=False)
            raise RuntimeError(f'E1 cannot be summarized as successful: {len(failures)} incomplete transactions')
        result=df.groupby(['L','variant']).agg(n=('full_software_ms','size'),
            full_median_ms=('full_software_ms','median'),
            full_p95_ms=('full_software_ms',lambda x:float(np.percentile(x,95))),
            online_median_ms=('authorization_ms','median'),
            prep_median_ms=('preparation_ms','median'),
            inclusive_median_ms=('inclusive_software_ms','median'),
            selected_bytes_median=('selected_packet_bytes','median'),
            blocks=('block','nunique')).reset_index()
        result.to_csv(root/'e1/e1_summary.csv',index=False)
        summary['e1_successful_observations']=len(df)
        # Five process blocks enable cluster-aware resampling; no per-transaction
        # independence is asserted. Uncertainty on p95 with 5 blocks remains limited.
        if 'block' in df and df.block.nunique()>=3:
            rng=np.random.default_rng(3031);rows=[]
            for (L,variant),group in df.groupby(['L','variant']):
                block_ids=group.block.unique();samples=[]
                for _ in range(1500):
                    draw=rng.choice(block_ids,size=len(block_ids),replace=True)
                    values=np.concatenate([group.loc[group.block==b,'full_software_ms'].to_numpy() for b in draw])
                    samples.append(np.median(values))
                low,high=np.quantile(samples,[.025,.975]);rows.append(dict(
                    L=L,variant=variant,bootstrap_median_low_ms=low,
                    bootstrap_median_high_ms=high,process_blocks=len(block_ids)))
            pd.DataFrame(rows).to_csv(root/'e1/e1_block_bootstrap.csv',index=False)
    e3=root/'e3/e3_summary.csv'
    if e3.exists():
        df=pd.read_csv(e3)
        lows,highs=zip(*(wilson(int(s),int(n)) for s,n in zip(df.eligible,df.trials)))
        df['wilson_low']=lows;df['wilson_high']=highs
        df['empirical_acceptance']=df.eligible/df.trials
        df.to_csv(root/'e3/e3_summary_with_ci.csv',index=False)
        summary['e3_total_vector_attempts']=int(df.trials.sum())
        from matplotlib import pyplot as plt
        selected=df[(df.L==max(df.L)) & (df.pair=='AB')]
        fig,ax=plt.subplots(figsize=(7,4))
        styles=['o-','s--','^-.','x:', 'd-']
        for (i,channel) in enumerate(sorted(selected.channel.unique())):
            g=selected[selected.channel==channel].sort_values('p')
            ax.errorbar(g.p,g.empirical_acceptance,
                yerr=[np.maximum(0,g.empirical_acceptance-g.wilson_low),
                      np.maximum(0,g.wilson_high-g.empirical_acceptance)],
                fmt=styles[i],color=str(.12+.15*i),label=channel,capsize=2)
        ax.set(xlabel='Noise parameter p',ylabel='All-vector commitment-gate acceptance',
               ylim=(-.02,1.03),title=f'Modeled full-vector acceptance (L={max(df.L)}, AB)')
        ax.legend(fontsize=8);ax.grid(alpha=.2)
        fig.tight_layout();fig.savefig(root/'e3/e3_gate_plot.pdf');plt.close(fig)
    # Tier B: genuine ML-KEM/ML-DSA token-acceptance path, disaggregated by L.
    # Do not mislabel Tier A commitment-gate outcomes as endpoint acceptance.
    e3_tokens=root/'e3/e3_token_trials.csv'
    if e3_tokens.exists():
        tokens=pd.read_csv(e3_tokens)
        allowed={'ACCEPTED_AT_EV','COMMITMENT_REJECT','ERASURE_ABORT',
                 'TOKEN_VERIFY_REJECT','OTHER_ABORT'}
        if not set(tokens.outcome).issubset(allowed):
            raise RuntimeError('Unexpected E3 genuine-token terminal outcome labels')
        metrics=[]
        for (L,pair,channel,p),group in tokens.groupby(['L','pair','channel','p']):
            n=len(group);ok=int((group.outcome=='ACCEPTED_AT_EV').sum())
            lo,hi=wilson(ok,n)
            metrics.append(dict(L=L,pair=pair,channel=channel,p=p,trials=n,
                endpoint_accepted=ok,commitment_rejected=int((group.outcome=='COMMITMENT_REJECT').sum()),
                erasure_abort=int((group.outcome=='ERASURE_ABORT').sum()),
                token_verify_reject=int((group.outcome=='TOKEN_VERIFY_REJECT').sum()),
                other_abort=int((group.outcome=='OTHER_ABORT').sum()),
                endpoint_acceptance=ok/n,wilson_low=lo,wilson_high=hi))
        pd.DataFrame(metrics).to_csv(root/'e3/e3_token_summary_with_ci.csv',index=False)
        summary['e3_real_pqc_token_attempts']=len(tokens)
        summary['e3_token_lengths']=sorted(int(x) for x in tokens.L.unique())
        summary['e3_tokens_accepted_at_ev']=int((tokens.outcome=='ACCEPTED_AT_EV').sum())
        if (tokens.p==0).any() and (tokens.loc[tokens.p==0,'outcome']!='ACCEPTED_AT_EV').any():
            raise RuntimeError('E3 p=0 real-PQC token validation failed; inspect token CSV')
        if (tokens.outcome=='OTHER_ABORT').any() or (tokens.outcome=='TOKEN_VERIFY_REJECT').any():
            raise RuntimeError('E3 unexpected endpoint/token failure; inspect token CSV')
        config=root/'e3/manifest.json'
        if config.exists():
            param=json.loads(config.read_text()).get('params',{})
            expected=param.get('token_lengths',[])
            if expected and sorted(map(int,expected))!=summary['e3_token_lengths']:
                raise RuntimeError('E3 genuine-token L coverage incomplete')
    for experiment,filename in [('e2','e2_cases.csv'),('e4','e4_failure_matrix.csv')]:
        target=root/experiment/filename
        if target.exists():
            table=pd.read_csv(target)
            summary[experiment+'_rows']=len(table)
            if experiment=='e2':
                mismatches=(table['match'].astype(str).str.lower()!='true').sum()
                summary['e2_mismatches']=int(mismatches)
                if mismatches:raise RuntimeError(f'E2 has {mismatches} mismatched outcomes')
    (root/'analysis_summary.json').write_text(json.dumps(summary,indent=2))
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root',type=Path)
    args=parser.parse_args()
    print(json.dumps(analyze(args.root),indent=2))
