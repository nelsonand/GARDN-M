"""
Sensitivity of GARDN-M zones to the choice of sources and weights.

Two perturbations of the default model:
  1. Leave-one-source-out: re-score with each source removed in turn.
  2. Weight perturbation: re-score many times with every source's perceived hierarchy P shifted by a
     random -1, 0 or +1 (clipped to 1-5).

For each location the output reports the spread of the composite M, how often each zone occurs, the source
whose removal moves M the most, and a robust zone: the baseline zone if at least --agreement of the
weight draws and every leave-one-out run agree with it, otherwise 'Borderline (<zones>)'.

Usage: python3 scripts/analysis/sensitivity.py [--data-version 2026] [--extended] [--draws 1000]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import main  # noqa: E402  (main sets the working directory to the repo root)


def sensitivity(data_version='2026', extended=False, draws=1000, agreement=0.9, seed=0):
    inputs = main.load_inputs(*main.data_dirs(data_version), extended=extended, strict=(data_version != '2023'))
    sources = [s for st_list in inputs['source_types'].values() for s in st_list]

    def run(**kwargs):
        return main.score(inputs, **kwargs).set_index(['State', 'City'])['M']

    base = run()
    index = base.index

    # 1. leave one source out
    loo = pd.DataFrame({s: run(exclude=(s,)).reindex(index) for s in sources})

    # 2. random shifts of P
    rng = np.random.default_rng(seed)
    base_P = {s: inputs['source_ratings'][s][0] for s in sources}
    mc = pd.DataFrame({
        i: run(ratings={s: int(np.clip(p + rng.integers(-1, 2), 1, 5)) for s, p in base_P.items()}).reindex(index)
        for i in range(draws)
    })

    zones = ['Green', 'Amber', 'Red']
    mc_zones = mc.apply(main.gar_zone)
    loo_zones = loo.apply(main.gar_zone)
    out = pd.DataFrame({'M': base, 'GAR': main.gar_zone(base)}, index=index)
    out['M_p05'] = mc.quantile(0.05, axis=1)
    out['M_p95'] = mc.quantile(0.95, axis=1)
    for z in zones:
        out[f'pct_{z}'] = (mc_zones == z).mean(axis=1).round(3)
    out['M_loo_min'] = loo.min(axis=1)
    out['M_loo_max'] = loo.max(axis=1)
    out['loo_zones'] = [', '.join(z for z in zones if z in set(row)) for row in loo_zones.values]
    shift = loo.sub(base, axis=0)
    out['most_influential_source'] = shift.abs().idxmax(axis=1)
    out['most_influential_shift'] = [shift.loc[i, s] if isinstance(s, str) else np.nan
                                     for i, s in zip(index, out['most_influential_source'])]

    robust = []
    for (i, row), loo_row in zip(out.iterrows(), loo_zones.values):
        if row['GAR'] == '':
            robust.append('')
            continue
        stable = row[f'pct_{row["GAR"]}'] >= agreement and set(loo_row) <= {row['GAR'], ''}
        seen = [z for z in zones if row[f'pct_{z}'] > 0 or z in set(loo_row)]
        robust.append(row['GAR'] if stable else f'Borderline ({"/".join(seen)})')
    out['robust_zone'] = robust

    name = f'gardnm_{data_version}' + ('_extended' if extended else '') + '_sensitivity'
    out.to_csv(f'data/outputs/{name}.csv')
    return out, name


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data-version', default='2026')
    parser.add_argument('--extended', action='store_true')
    parser.add_argument('--draws', type=int, default=1000)
    parser.add_argument('--agreement', type=float, default=0.9)
    parser.add_argument('--seed', type=int, default=0)
    args = parser.parse_args()

    out, name = sensitivity(args.data_version, args.extended, args.draws, args.agreement, args.seed)
    states = out.xs('', level='City').sort_values('M', ascending=False)
    print(f'Saved data/outputs/{name}.csv\n')
    print('Robust zones (states, DC and territories):')
    print(states['robust_zone'].value_counts().to_string())
    cols = ['M', 'GAR', 'M_p05', 'M_p95', 'pct_Green', 'pct_Amber', 'pct_Red', 'robust_zone', 'most_influential_source']
    print('\nBorderline states:')
    print(states[states.robust_zone.str.startswith('Borderline')][cols].round(2).to_string())
