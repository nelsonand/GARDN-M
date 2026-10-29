# GARDN-M October 2026 data update

This update refreshes the GARDN-M input data, which dated from about 2020–2023. It adds newer editions of existing sources, new sources with similar data, and recent summary reports for the write-up. The original data and outputs are unchanged, so the two versions can be compared directly.

## How to run

```bash
pip install -r requirements.txt
python3 scripts/analysis/main.py                  # 2026 data -> data/outputs/gardnm_2026_normalized.csv
python3 -c "import sys; sys.path.insert(0,'scripts/analysis'); import main; \
  main.gardnm(extended=True); main.gardnm(data_version='2023')"
python3 scripts/analysis/compare_2023_2026.py     # comparison tables + cross-check
python3 scripts/analysis/sensitivity.py           # robustness of zones (add --extended for the extended run)
python3 -m pytest tests                           # 17 tests, including a regression check against the 2023 output
```

Optional methodology settings, all off by default (see "Methodology changes" below):

```python
main.gardnm(absolute_scales=True)      # keep absolute-scale sources on their native scale
main.gardnm(recency_half_life=5)       # age-based discount of P instead of the manual staleness adjustment
main.gardnm(min_categories=4)          # no composite score for places with data in fewer categories
```

| Run | Inputs | Output |
|---|---|---|
| 2026 core (default) | `data/sources_2026/source_types.json`, `data/processed_data_2026/` | `data/outputs/gardnm_2026_normalized.csv` |
| 2026 extended | adds the `immigration`, `safety` and `health_access` categories (`source_types_extended.json`) | `data/outputs/gardnm_2026_extended_normalized.csv` |
| 2023 data, current code | `data/sources/`, `data/processed_data/` | `data/outputs/gardnm_2023_normalized.csv` |
| Sensitivity analysis | 2026 core or extended | `data/outputs/gardnm_2026[_extended]_sensitivity.csv` |

`data/sources_2026/notes.csv` lists every 2026 source with its category, base perceived-hierarchy weight P, staleness adjustment, data year, scale type, overlap group, edition, status (new, replaced, carried over or excluded), URL and processing notes. The machine-readable versions are `source_ratings.json` (P), `source_subtypes.json` (overlap groups) and `source_metadata.json` (data year, scale, staleness adjustment).

## Code changes

1. **Ported to numpy 2 and pandas 3.** `np.NaN`, `fillna(method=...)` and chained in-place `where` no longer work. The GitPython dependency was dropped. With 2023 data, the port reproduces the old output exactly.
2. **Added the `data_version` and `extended` options** to `gardnm()`.
3. **Fixed how city-level and state-level data are combined.** This bug predates the update. The old code filled gaps by copying values down the table (forward-fill) after sorting by state and city, which caused two problems:
   - A city's score in a category used only that category's city-level sources and ignored its state-level sources. With HRC's Municipal Equality Index added, Atlanta's sexual-orientation score was just HRC's city score (10/10) and ignored Georgia's laws. The S (scope sensitivity) weight also had no effect.
   - Values leaked between cities. A city missing from a source inherited the value of the city listed just before it. For example, Avondale Estates, GA was given Augusta's disability score.

   City rows now take state-level values only from their own state's row (`fill_from_state`). State-level results are unchanged; the 2023 data gives identical state rows before and after the fix. City scores do change: for example, Memphis on 2023 data goes from 2.62 (old code) to 3.50.

   The historical output `gardnm_algorithm_rework_normalized.csv` is left untouched. Use `gardnm_2023_normalized.csv` for comparisons with 2026.

## Methodology changes

These put into code what the GARDN-M write-up already describes, or make its assumptions explicit. Items 1–4 are on by default. Items 5–7 change what the scores mean, so they are options, off by default, for the authors to decide on.

1. **Repetition weight W is now applied.** The write-up says measures of the same thing should not be double-counted, but the code always set W = 1 (the alternative was an unfinished `# TODO`).
   - Sources in the same overlap group within a category now split one weight, W = 1/k.
   - The 2026 overlap groups (in `source_subtypes.json`) are:
     - the two WalletHub women's rankings
     - the two reproductive-policy scores (CRR and the Population Institute)
     - MAP and the two rankings built on MAP's data (SafeHome, Move.org)
     - the two disability employment-gap measures (Census and US News)
   - SafeHome's P went back from 2 to 3, because its overlap with MAP is now handled by W.
   - The 2023 subtypes are all distinct, so the 2023 results are unaffected.
   - Effect on 2026: state scores change by 0.14 on average (at most 0.38; rank correlation 0.995). Three states change zone (Nevada down to Amber; South Dakota and Texas down to Red), which shows how close many states sit to the cutoffs.
2. **Sensitivity analysis.** `scripts/analysis/sensitivity.py` re-scores the model with each source left out in turn, and 1,000 times with every source's P shifted randomly by −1, 0 or +1.
   - For each place it reports the range of scores, how often each zone occurs, and the source with the most influence.
   - A place gets a "robust" zone if at least 90% of runs and every leave-one-out run agree with its baseline zone; otherwise it is "Borderline". See Results.
3. **Input validation.** Every processed file is checked on load: exactly one scoring column, known state names, no duplicate locations, numeric scores in range (`Score` 0–100, `Processed` 0–10, `Rank` ≥ 1, with a warning if ranks run beyond the number of rows). Problems stop the run. For the 2023 data, several scoring columns only produce a warning, so the original files still run.
   - **A source only counts towards the weights where it has a value.** Previously a row with no score still added its source's weight to the denominator of the weighted average. This affected Baton Rouge (social) and Washington DC (disability) in the 2023 data; their city scores changed by about 0.8 in that category. Rows without a score are now dropped with a warning, and a source with the same value everywhere (which has no information after normalization) is skipped.
   - The carried-over infogram file had both `Score` and `Rank` columns. Its `Rank` column was renamed `Source rank`.
4. **Tests** (`tests/test_gardnm.py`, 17 tests):
   - hand-checkable small examples of normalization, P×S×W weighting, how city and state data combine, W, partial rank lists, and each option
   - tests that fail under the old city-leak code and without the empty-weight fix
   - validation checks
   - a regression test that the 2023 state results still match the original committed output
5. **Absolute scales (option `absolute_scales`).** By default every source is stretched so its worst place scores 0 and its best 10. So the zones are relative: Green means "better than most US places", not "meets a standard", and they would not change if every state got worse.
   - With this option, the 12 sources whose scores have a fixed meaning keep their native scale. These are marked `scale: absolute` in `source_metadata.json`: policy rubrics and tiers (HRC, CRR, Erin Reed, ILRC, Population Institute, Oxfam, New America, Out Leadership, NCAJ) and the ADA-station and disability-parity percentages.
   - Rankings and relative indices are still stretched.
   - Effect: small (rank correlation 0.998). South Dakota and Texas move from Red to Amber. Relative sources still dominate the spread of scores, so this only partly answers the concern; the write-up should state that the zones are relative.
6. **Age-based discount (option `recency_half_life`).** By default, stale sources carry a manual `stale_adjustment` to P: −2 for the infogram cities ranking (2020 data) and −1 for NCAJ (2021).
   - With this option, P is instead multiplied by 0.5^((age − grace)/half-life), with a 2-year grace period.
   - Age is measured from each source's `data_year`: the year of the underlying data where the source states it (for example the National Equity Atlas 2024 release uses 2022 data), and otherwise the edition year.
   - Effect with a 5-year half-life: rank correlation 0.999. Nevada moves up to Green and South Dakota up to Amber.
7. **Missing categories are flagged (option `min_categories`).** The output now has `n_categories` and `missing_categories` columns. All 50 states and DC have data in all five categories.
   - Puerto Rico has data in three (social, race and disability; no gender or sexual-orientation source covers it). With `min_categories=4` or 5 it would get no composite score; `min_categories=3` changes nothing.

The output also now includes a `GAR` zone column. The cutoffs (Green at 6.0 and above, Amber from 3.6, otherwise Red) are defined once in `main.py` and shared by all scripts.

## Source changes by category

P is the base perceived-hierarchy weight (1–5, 5 = most trusted). Sources carried over unchanged also get a staleness adjustment (see Methodology changes item 6). Full detail and URLs are in `data/sources_2026/notes.csv`. The research reports in `research/` explain how each value was obtained.

### Social
| Source | Edition | P | Status |
|---|---|---|---|
| Oxfam, Best States to Work Index | 2025 | 4 | new |
| Census ACS income inequality (1 − Gini) | 2025 | 4 | new |
| Motley Fool social equity cities (infogram) | 2019–20 data | 5 (−2 stale) | carried over: no new edition; the page shows a 2024 date but the data is unchanged |
| National Equity Atlas, Racial Equity Index | Dec 2024 download (2022 data) | 4 | refreshed from a manual download; now covers states and the 100 largest cities (the old file used metro areas) |

### Race
| Source | Edition | P | Status |
|---|---|---|---|
| US News, race gaps only (education, income, unemployment) | 2026 | 4 | replaces the US News overall equality rank, which also included gender and disability measures |
| WalletHub, racial economic equality | 2024 (latest) | 4 | refreshed |
| WalletHub, racial integration | 2026 | 4 | refreshed |
| WalletHub, racial equality in education | 2026 | 4 | new |
| Census diversity index (ACS B03002) | 2025 | 4 | replaces WiseVoter, whose rankings no longer exist |
| Sentencing Project, Black:white imprisonment ratio | 2021 data | 5 | new |
| Berkeley OBI city segregation (divergence index) | 2023 ACS | 4 | replaces Bloomberg/CityLab "metros for Black women" (2020, never updated); city-level |

### Gender (including reproductive rights)
| Source | Edition | P | Status |
|---|---|---|---|
| WalletHub, women's equality | 2026 | 4 | refreshed |
| WalletHub, best states for women | 2026 | 4 | new |
| Commonwealth Fund, women's health and reproductive care scorecard | 2024 | 5 | new |
| Population Institute, reproductive health and rights report card | 2026 | 4 | replaces IWPR reproductive rights index (2022, before Dobbs) |
| Center for Reproductive Rights, abortion laws by state | Sep 2026 | 5 | new |

Dropped: the Georgetown US WPS Index (2020; no new state-level edition), the US News gender equality ranking (a one-off 2022 analysis) and IWPR Status of Women (2015; discontinued).

### Sexual orientation and gender identity
| Source | Edition | P | Status |
|---|---|---|---|
| Movement Advancement Project policy tally | Oct 2026 | 5 | refreshed |
| HRC State Equality Index | 2024 (published Jan 2025, latest) | 5 | refreshed (4 published tiers mapped to 0/3.33/6.67/10) |
| HRC Municipal Equality Index | 2025 | 5 | new; city-level, 509 cities |
| Out Leadership LGBTQ+ business climate index | 2026 | 4 | replaces Axios 2022, which was reporting this index |
| Move.org, LGBTQ family | 2025 | 3 | refreshed; commercial, and shares one weight with MAP and SafeHome (overlap group) |
| Erin in the Morning, adult anti-trans legal risk map | Jul 2026 | 3 | new; the only source specific to trans risk that is updated regularly |
| SafeHome.org, LGBTQ+ state safety | 2026 | 3 | new; commercial, and largely built on MAP's data, so it shares one weight with MAP and Move.org |

### Disabilities
| Source | Edition | P | Status |
|---|---|---|---|
| WalletHub, best cities for people with disabilities | 2026 | 4 | refreshed; city-level |
| US News, disability unemployment gap | 2026 | 4 | refreshed (older editions measured the employment gap) |
| Census ACS disability employment parity | 2025 | 5 | new |
| New America, competitive integrated employment | 2026 | 4 | new |
| FTA National Transit Database, % ADA-accessible stations | 2025 | 3 | new; city-level; little spread (42 of 53 areas at 100%) |
| NCAJ Justice Index, disability access | 2021 | 4 (−1 stale) | carried over: no new edition |
| AARP long-term services and supports scorecard | 2023 (latest) | 4 | new, from a manual download; covers older adults and people with physical disabilities |

Dropped: BenefitsPro (a one-off 2022 article; its report link is dead) and the Disability:IN DEI report (company-level only).

### New optional categories (extended run only)
| Category | Source | Edition | P |
|---|---|---|---|
| `immigration` | ILRC state immigration-enforcement map (20 policy types) | Sep 2026 | 3 |
| `safety` | Giffords gun-law strength rank | Dec 2025 | 3 |
| `health_access` | Commonwealth Fund state health system performance (from manually downloaded state profiles) | Jun 2025 | 3 |

These are not in the core run because adding categories changes what the composite score means. The project team should decide whether to adopt them. Several reviewed candidates were rejected: FBI hate-crime counts (reporting is voluntary, so the data would reward states that under-report), ADL religious-incident counts, and ICE 287(g) agreement counts. The research reports give the reasons.

### Collected but not used as inputs
- **Berkeley OBI Inclusiveness Index 2025.** A composite covering race, gender, LGBTQ, disability and religion. It is kept as an independent cross-check rather than an input; using it as both would double-count those dimensions and make the check circular.
- **Archbridge social mobility.** It measures mobility, not equity, and rewards low taxes and light regulation.
- **US News overall equality rank, 2026.** Superseded by the race-gaps-only version above.
- **CAWP women in state legislatures.** Its values were read through a summarizing fetch tool because the site blocks downloads. **They need checking against the site before use.**
- **Equaldex.** Crowd-edited.

## Results

The full tables are in `data/outputs/comparison_states_2023_vs_2026.csv` and `comparison_cities_2023_vs_2026.csv`. The Green/Amber/Red cutoffs are unchanged: 6.0 and above is Green, 3.6–6.0 Amber, below 3.6 Red.

- **Overall agreement.** State rankings stay broadly consistent (Spearman 0.89 between 2023 and 2026). By category, gender (0.94) and sexual orientation (0.93) agree closely; race (0.69), social (0.54) and disability (0.23) changed substantially because most of their sources were replaced.
- **Zone counts.** 2023 had 19 Green, 31 Amber and 6 Red; 2026 has 21 Green, 23 Amber and 8 Red, plus 4 territories with no 2026 data.
  - The 2023 Red count includes American Samoa, Guam and the Northern Mariana Islands, which have no 2026 data. Among states, DC and Puerto Rico, Red grows from 3 (Louisiana, Mississippi, South Dakota) to 8.
  - 2026 Red: Alabama, Arkansas, Louisiana, Mississippi, South Carolina, South Dakota, Texas and Puerto Rico.
  - Moved from Amber to Red: Alabama, Arkansas, South Carolina, Texas and Puerto Rico. South Dakota was Red in both years.
  - Moved from Amber to Green: Michigan, Minnesota and New Hampshire. Nevada moved from Green to Amber.
- **Largest drops:**

  | Place | Change | Main drivers (category change) |
  |---|---|---|
  | Puerto Rico | −2.6 | mostly a change in coverage: 2023 data covered sexual orientation and disability; 2026 data covers social, race and disability (disability −0.7) |
  | Florida | −1.7 | sexual orientation −2.9, disability −2.7, gender −1.8 |
  | Texas | −1.4 | gender −2.9, social −2.3, disability −1.7 |
  | Georgia | −1.4 | social −3.3, disability −2.2, gender −1.7 |
  | North Carolina | −1.3 | social −3.3, gender −1.5 |

- **Largest gains:** Minnesota (+1.0), South Dakota (+0.9), Delaware (+0.9) and New Hampshire (+0.8).
  - South Dakota's, Delaware's and New Hampshire's gains come mostly from disability (+3.3, +3.9 and +3.7), driven by disability-employment measures.
  - Gap-based race measures and disability-employment parity favor states with small minority populations and tight labor markets. The team should review these sources' weights.
- **Robustness (core run).** Of the 52 places with data:
  - 43 keep the same zone under all perturbations: 19 Green, 18 Amber and 6 Red.
  - 9 are borderline:
    - Green/Amber: Alaska, DC, New Mexico and Nevada.
    - Amber/Red: Oklahoma, South Dakota, Tennessee, Texas and West Virginia.
  - Their zones depend on modelling choices, so they need individual review rather than a mechanical label.
  - The robust Red group is Alabama, Arkansas, Louisiana, Mississippi, South Carolina and Puerto Rico.
- **Cross-check.** Agreement with the independent OBI Inclusiveness Index improved from 0.40 (2023) to 0.50 (2026). The agreement is moderate, partly because OBI's own ranking contains surprises such as Massachusetts at 48th.
- **Example cities from the DPP list.**
  - Memphis moves from Red to Amber.
  - Boston, Washington DC and Chicago fall slightly but remain Green. Arlington, VA (Green, 6.8) is now matched; it had no city-level data in 2023.
  - Las Vegas drops from Green to Amber.
  - Atlanta, Houston and Orlando fall within Amber.
- **The extended run** (adding immigration, safety and health access) is much harsher on the South.
  - Red grows to 15: the core-run Red states, plus Florida, Georgia, Missouri, Oklahoma, Tennessee, West Virginia and Wyoming.
  - Houston and Memphis become Red, and Pittsburgh rises to Green.
  - Its robustness analysis gives 8 robust Red places (Alabama, Arkansas, Louisiana, Mississippi, Oklahoma, South Carolina, Texas, Puerto Rico) and 9 borderline Amber/Red: Florida, Georgia, Idaho, Kentucky, Missouri, South Dakota, Tennessee, West Virginia and Wyoming.

## Review fixes (Oct 29, 2026)

A code review and an independent audit of the data and this document found the following, now fixed.

- **Puerto Rico had been dropped** from five sources whose raw files include it: Census Gini, Census diversity, Census disability parity, Oxfam, and FTA (San Juan). `scripts/gather/oct2026/add_puerto_rico.py` restores these rows from the raw files, checking the method against an existing row each time. Puerto Rico now has data in three categories instead of one; its score fell from 3.48 to 2.03 and it stays Red. Adding it also slightly widens the ranges of those sources, so other states' scores shift a little.
- **City names.** Three fixes in `harmonize_city_names.py`:
  - The carried-over infogram file misspelled San Bernardino as "San Benandino", so it never merged with the other sources.
  - Arlington, VA appears in HRC's data as "Arlington County"; it is now matched as Arlington.
  - OBI lists Louisville, KY twice. The consolidated city–county government row is now used as Louisville, and the other row (population 246,161, apparently the pre-merger city limits) is labelled separately. This choice could not be confirmed against OBI's documentation.
- **Data years.** Four sources now use the year of their underlying data rather than the edition year: National Equity Atlas (2022), Commonwealth women's health (2022), Population Institute (2025) and New America (2025). This affects only the optional age-based discount.
- **Abortion-law categories.** The CRR raw page is a JavaScript shell with no per-state data. The screenshot used for verification and a per-state category table are now committed in `data/raw_data_2026/crr_abortionLawsByState_2026/`.
- **Code.** The following were fixed in the scoring code:
  - a constant source or an empty value could distort the weighted average
  - truncated rank lists were scaled without warning; the special case for one partial ranking is now a per-source `n_ranked` setting
  - sources outside the selected categories were loaded
  - the sensitivity script crashed on places without a score
  - asking for a city by name could print the wrong state's city; `'Portland, OR'` style is now accepted
  - `main.py` no longer changes the working directory when imported
- **Corrected figures in this document:** the effect of W, the number of FTA areas at 100% (42 of 53), the correlations, and the list of states that changed zone.

## Manual downloads (Oct 29, 2026)

Files downloaded by hand are kept in `manual_downloads/`, which is not committed because the files are large. They are processed by `scripts/gather/oct2026/manual/process_manual_downloads.py`, and small extracts of the values used go to `data/raw_data_2026/<key>/`.

| Download | Used for |
|---|---|
| National Equity Atlas `REI_DATA_DOWNLOAD_20241126.xlsx` | `nationalEquityAtlas_2024` (replaces the stale 2020 file) |
| AARP LTSS Scorecard 2023 report PDF | `aarp_ltssScorecard_2023` (Exhibit 3 overall ranks) |
| Commonwealth Fund 2025 state profiles (zip) | `commonwealthFund_healthSystemPerformance_2025` (extended run only) |
| Commonwealth Fund 2024 women's health profiles (zip) | Verification: all 51 overall ranks match `commonwealthFund_womensHealthReproCare_2024` |
| Screenshot of the CRR abortion-laws map | Verification: all 51 categories match `crr_abortionLawsByState_2026` |
| Child Opportunity Index files and April 2024 report | Not used. The tract, county and ZIP files have no child population by race, and the report lists only the top, middle and bottom 10 metros, so the metro racial-inequity measure could not be reproduced. `diversitydatakids.csv` is a child-care cost table, not the metro data. |

## Summary material for the write-up

The research reports in `research/` have the full citations.

- **The landscape has diverged sharply by state.**
  - MAP's "Uneven Ground" (Sep 2026) finds 16 states plus DC rated High on gender-identity policy and 26 rated Negative.
  - Five states vote on anti-transgender ballot measures in November 2026.
  - Out Leadership's national average has fallen four years running.
- **Reproductive rights after Dobbs.**
  - As of end-2025, 13 states have total abortion bans and 6 have 6- or 12-week bans (Guttmacher).
  - The Population Institute gives the US an F for the seventh straight year.
  - The Commonwealth Fund (2024) finds that states which restricted abortion before Dobbs rank lower on women's health.
- **Visa and immigration-enforcement risk is now the main new driver of meeting relocations.**
  - Physics Today (Aug 2025) reports US physics-meeting attendance down about 20–30% because of visa and border concerns.
  - The Academy of Management (May 2026) is moving its 2027–2030 meetings out of the US.
  - Several societies moved their 2025 meetings to Canada.
  - This risk is largely federal, so a state-level score such as ILRC's should be paired with hybrid or non-US satellite options. APS already offers these.
- **Peer-society site-selection policies.**
  - AAS (2017) and the American Philosophical Association, which requires specific HRC MEI criteria.
  - AHA (cancellation without penalty), ACNP (no new contracts in states with discriminatory laws "at the time of contracting") and SPSP (2026; force-majeure clause covering "the passing of laws").
  - SOBP (2025) and ACHA (2026; laws "may inform, but shall not solely govern" site choice).
  - AGU monitors reproductive rights, LGBTQ+ rights and gun safety.
  - **No current public APS site-selection policy text was found**; it is worth asking APS Meetings staff directly.
- **Travel advisories and bans.**
  - California's AB 1887 state travel-ban list was **repealed in Sep 2023 (SB 447)**, and no official multi-state list has replaced it.
  - The NAACP, LULAC and Equality Florida issued Florida advisories in May 2023. The Canadian Association of University Teachers (2025) advises against non-essential US travel.

### Suggested edits to "Considering Laws or Recent Developments"
- Note the AB 1887 repeal, and that committees now need to do their own legal review.
- Recommend force-majeure or change-in-law contract clauses, citing the AHA, SPSP, ACNP and ACHA examples.
- Add international-attendee visa and enforcement risk as a new primary concern, and recommend hybrid or satellite options.
- Note that physical safety is now an explicit criterion in several policies. Caution against ranking by hate-crime statistics.
- Recommend checking GARDN-M output against an independent composite such as OBI.
- List fast-moving signals to recheck before each event: advisories, ballot measures, and the CRR and MAP trackers.

## Known limitations and follow-ups
- **Still not obtained.**
  - Social Progress Imperative state and city data (interactive tool only).
  - Child Opportunity Index metro racial-inequity table (see Manual downloads).
  - MoneyGeek's best cities for Black women.
- **Values read through a summarizing fetch tool** (because the sites block downloads):
  - CRR tiers: now verified against a screenshot.
  - CAWP women in state legislatures: still excluded until checked against https://cawp.rutgers.edu/data/levels-office/state-legislature.
- **Gap-based measures favor homogeneous states.** The race-gap and disability-parity measures reward states with small minority populations or tight labor markets, and the OBI segregation index ranks homogeneous cities as integrated (Laredo, TX is #1).
- **City names were harmonized** across all city-level sources, including the carried-over infogram file, by `scripts/gather/oct2026/harmonize_city_names.py`. The original spellings are kept in a `City_source` column.
- **Coverage gaps.** Coverage of DC and Puerto Rico varies by source; Puerto Rico has no gender or sexual-orientation data. The 2026 data has no rows for the other territories.
- **Parsing scripts.** The scripts the research agents used are in `scripts/gather/oct2026/<category>/` for reference. They were one-off scripts and may need path changes before they can be re-run.
