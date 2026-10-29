"""
Tests for the GARDN-M scoring code. Run with `python3 -m pytest tests` (or `python3 -m unittest discover tests`).
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts' / 'analysis'))
import main  # noqa: E402  (main sets the working directory to the repo root)


def write_inputs(tmp, sources, categories, ratings, subtypes=None, metadata=None):
    """Write a small synthetic set of source metadata and processed data to a temporary directory"""
    tmp = Path(tmp)
    for name, df in sources.items():
        df.to_csv(tmp / f'{name}.csv', index=False)
    files = {
        'source_ratings.json': {s: [p, 1, 2] for s, p in ratings.items()},
        'source_types.json': categories,
        'source_subtypes.json': subtypes or {s: s for s in sources},
        'source_metadata.json': metadata or {},
    }
    for fname, content in files.items():
        (tmp / fname).write_text(json.dumps(content))
    return str(tmp) + '/', str(tmp) + '/'


def row(rankings, state, city=''):
    return rankings[(rankings.State == state) & (rankings.City == city)].iloc[0]


class TestToyModel(unittest.TestCase):
    """Hand-checkable examples of normalization, weighting and the city/state combination"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.sources = {
            # state-level: after normalization MA = 10, TX = 0
            'stateA': pd.DataFrame({'State': ['Massachusetts', 'Texas'], 'Score': [80, 20]}),
            # city-level: after normalization Boston = 10, Cambridge = 0, Houston = 5
            'cityB': pd.DataFrame({'State': ['MA', 'MA', 'TX'], 'City': ['Boston', 'Cambridge', 'Houston'],
                                   'Score': [60, 40, 50]}),
            # state-level, in a second category: MA = 10, TX = 0
            'stateC': pd.DataFrame({'State': ['MA', 'TX'], 'Rank': [1, 2]}),
        }
        self.categories = {'one': ['stateA', 'cityB'], 'two': ['stateC']}
        self.ratings = {'stateA': 4, 'cityB': 4, 'stateC': 4}

    def tearDown(self):
        self.tmp.cleanup()

    def scored(self, **kwargs):
        dirs = write_inputs(self.tmp.name, self.sources, self.categories, self.ratings,
                            kwargs.pop('subtypes', None), kwargs.pop('metadata', None))
        return main.score(main.load_inputs(*dirs), **kwargs)

    def test_city_rows_combine_city_and_state_sources(self):
        r = self.scored()
        # weights: state source P*S = 4*1, city source 4*2
        self.assertAlmostEqual(row(r, 'MA', 'Boston')['M_one'], (10 * 4 + 10 * 8) / 12)
        self.assertAlmostEqual(row(r, 'MA', 'Cambridge')['M_one'], (10 * 4 + 0 * 8) / 12)
        self.assertAlmostEqual(row(r, 'TX', 'Houston')['M_one'], (0 * 4 + 5 * 8) / 12)
        self.assertEqual(row(r, 'MA', 'Cambridge')['n_one'], 2)

    def test_state_rows_use_state_sources_only(self):
        r = self.scored()
        self.assertAlmostEqual(row(r, 'MA')['M_one'], 10)
        self.assertAlmostEqual(row(r, 'TX')['M_one'], 0)

    def test_categories_without_city_data_use_the_cities_own_state(self):
        r = self.scored()
        self.assertAlmostEqual(row(r, 'MA', 'Cambridge')['M_two'], 10)
        self.assertAlmostEqual(row(r, 'TX', 'Houston')['M_two'], 0)
        self.assertAlmostEqual(row(r, 'TX', 'Houston')['M'], np.mean([(0 * 4 + 5 * 8) / 12, 0]))

    def test_no_values_leak_between_cities(self):
        # Cambridge sorts right after Boston and is missing from cityB; the old forward-fill gave it Boston's value
        self.sources['cityB'] = pd.DataFrame({'State': ['MA', 'TX'], 'City': ['Boston', 'Houston'], 'Score': [40, 60]})
        self.sources['cityE'] = pd.DataFrame({'State': ['MA', 'TX'], 'City': ['Cambridge', 'Dallas'], 'Score': [100, 0]})
        self.categories['one'].append('cityE')
        self.ratings['cityE'] = 4
        r = self.scored()
        cambridge = row(r, 'MA', 'Cambridge')
        self.assertEqual(cambridge['n_one'], 2) # stateA and cityE, not Boston's cityB value
        self.assertAlmostEqual(cambridge['M_one'], (10 * 4 + 10 * 8) / 12)

    def test_repetition_weight_splits_a_shared_weight(self):
        self.sources['stateD'] = pd.DataFrame({'State': ['MA', 'TX'], 'Score': [30, 70]}) # MA = 0, TX = 10
        self.categories['one'].append('stateD')
        self.ratings['stateD'] = 4
        subtypes = {'stateA': 'shared', 'stateD': 'shared', 'cityB': 'cityB', 'stateC': 'stateC'}
        # stateA and stateD each get W = 1/2, so together they weigh as much as one state source
        r = self.scored(subtypes=subtypes)
        self.assertAlmostEqual(row(r, 'MA', 'Boston')['M_one'], (10 * 2 + 0 * 2 + 10 * 8) / 12)
        r = self.scored(subtypes=subtypes, ignore_subtypes=True)
        self.assertAlmostEqual(row(r, 'MA', 'Boston')['M_one'], (10 * 4 + 0 * 4 + 10 * 8) / 16)

    def test_absolute_scales_keep_native_values(self):
        metadata = {'stateA': {'scale': 'absolute'}}
        r = self.scored(metadata=metadata, absolute_scales=True)
        self.assertAlmostEqual(row(r, 'MA')['M_one'], 8)
        self.assertAlmostEqual(row(r, 'TX')['M_one'], 2)

    def test_recency_discount_and_stale_adjustment(self):
        metadata = {'stateA': {'data_year': main.REFERENCE_YEAR - 7, 'stale_adjustment': -2},
                    'cityB': {'data_year': main.REFERENCE_YEAR}, 'stateC': {'data_year': main.REFERENCE_YEAR}}
        # default: manual adjustment, P = 4 - 2
        r = self.scored(metadata=metadata)
        self.assertAlmostEqual(row(r, 'MA', 'Cambridge')['M_one'], (10 * 2 + 0 * 8) / 10)
        # recency: P = 4 * 0.5 ** ((7 - 2) / 5) = 2 as well, ignoring the manual adjustment
        r = self.scored(metadata=metadata, recency_half_life=5, recency_grace=2)
        self.assertAlmostEqual(row(r, 'MA', 'Cambridge')['M_one'], (10 * 2 + 0 * 8) / 10)

    def test_missing_categories_are_flagged_and_can_be_required(self):
        self.sources['stateA'] = pd.DataFrame({'State': ['MA', 'TX', 'VT'], 'Score': [80, 20, 50]})
        r = self.scored()
        self.assertEqual(row(r, 'VT')['n_categories'], 1)
        self.assertEqual(row(r, 'VT')['missing_categories'], 'two')
        r = self.scored(min_categories=2)
        self.assertTrue(np.isnan(row(r, 'VT')['M']))
        self.assertEqual(row(r, 'VT')['GAR'], '')
        self.assertFalse(np.isnan(row(r, 'MA')['M']))

    def test_gar_zones(self):
        self.assertEqual(list(main.gar_zone([6.0, 5.99, 3.6, 3.59, np.nan])), ['Green', 'Amber', 'Amber', 'Red', ''])


class TestValidation(unittest.TestCase):

    valid = {'MA', 'TX'}

    def check(self, df, strict=True):
        df = df.copy()
        if 'City' not in df:
            df['City'] = ''
        return main.validate_source(df, 'test', self.valid, strict)

    def test_accepts_clean_data(self):
        self.check(pd.DataFrame({'State': ['MA', 'TX'], 'Score': [10, 90]}))

    def test_rejects_problems(self):
        bad = [
            pd.DataFrame({'State': ['MA', 'TX'], 'Value': [1, 2]}),                     # no scoring column
            pd.DataFrame({'State': ['MA', 'XX'], 'Score': [10, 90]}),                   # unknown state
            pd.DataFrame({'State': ['MA', 'MA'], 'Score': [10, 90]}),                   # duplicate
            pd.DataFrame({'State': ['MA', 'TX'], 'Score': [10, 190]}),                  # out of range
            pd.DataFrame({'State': ['MA', 'TX'], 'Processed': [10, 11]}),               # out of range
            pd.DataFrame({'State': ['MA', 'TX'], 'Rank': [0, 1]}),                      # rank below 1
            pd.DataFrame({'State': ['MA', 'TX'], 'Score': ['10', 'n/a']}),              # non-numeric
            pd.DataFrame({'State': ['MA', 'TX'], 'Score': [10, 90], 'Rank': [2, 1]}),   # ambiguous
        ]
        for df in bad:
            with self.assertRaises(ValueError, msg=str(df)):
                self.check(df)

    def test_ambiguous_columns_only_warn_when_not_strict(self):
        out = self.check(pd.DataFrame({'State': ['MA', 'TX'], 'Score': [10, 90], 'Rank': [2, 1]}), strict=False)
        self.assertEqual(len(out), 2)

    def test_rows_without_scores_are_dropped(self):
        out = self.check(pd.DataFrame({'State': ['MA', 'TX'], 'Score': [10, np.nan]}))
        self.assertEqual(out.State.tolist(), ['MA'])


class TestRegression(unittest.TestCase):
    """The real data still produce the committed results"""

    def test_2023_state_results_match_original_output(self):
        inputs = main.load_inputs(*main.data_dirs('2023'), strict=False)
        new = main.score(inputs).set_index(['State', 'City'])
        old = pd.read_csv('data/outputs/gardnm_algorithm_rework_normalized.csv', index_col=0)
        old = old[old.City.isna()].assign(City='').set_index(['State', 'City'])
        cols = [c for c in old.columns if c.startswith(('M', 'n'))]
        np.testing.assert_allclose(new.loc[old.index, cols].astype(float).values, old[cols].values, atol=1e-9)

    def test_2026_data_validate_and_score(self):
        for extended in (False, True):
            inputs = main.load_inputs(*main.data_dirs('2026'), extended=extended)
            r = main.score(inputs)
            states = r[r.City == '']
            self.assertGreaterEqual(len(states), 51)
            self.assertTrue(states.M.between(0, 10).all())
            self.assertFalse(r.duplicated(['State', 'City']).any())


if __name__ == '__main__':
    unittest.main()
