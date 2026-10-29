# GARDN-M October 2026 data update

This update refreshes the GARDN-M input data, which dated from about 2020–2023. It adds newer editions of existing sources, new sources with similar data, and recent summary reports for the write-up. The original data and outputs are unchanged, so the two versions can be compared directly.

## How to run

```bash
pip install -r requirements.txt
python3 scripts/analysis/main.py                  # 2026 data -> data/outputs/gardnm_2026_normalized.csv
python3 -c "import sys; sys.path.insert(0,'scripts/analysis'); import main; \
  main.gardnm(extended=True); main.gardnm(data_version='2023')"
python3 scripts/analysis/compare_2023_2026.py     # comparison tables + cross-check
```

| Run | Inputs | Output |
|---|---|---|
| 2026 core (default) | `data/sources_2026/source_types.json`, `data/processed_data_2026/` | `data/outputs/gardnm_2026_normalized.csv` |
| 2026 extended | adds the `immigration` and `safety` categories (`source_types_extended.json`) | `data/outputs/gardnm_2026_extended_normalized.csv` |
| 2023 data, current code | `data/sources/`, `data/processed_data/` | `data/outputs/gardnm_2023_normalized.csv` |

`data/sources_2026/notes.csv` lists every 2026 source with its category, perceived-hierarchy weight P, edition, status (new, replaced, carried over or excluded), URL and processing notes.

## Code changes

1. **Ported to numpy 2 and pandas 3.** `np.NaN`, `fillna(method=...)` and chained in-place `where` no longer work. The GitPython dependency was dropped. With 2023 data, the port reproduces the old output exactly.
2. **Added the `data_version` and `extended` options** to `gardnm()`.
3. **Fixed how city-level and state-level data are combined.** This bug predates the update. The old code filled gaps by copying values down the table (forward-fill) after sorting by state and city, which caused two problems:
   - A city's score in a category used only that category's city-level sources and ignored its state-level sources. With HRC's Municipal Equality Index added, Atlanta's sexual-orientation score was just HRC's city score (10/10) and ignored Georgia's laws. The S (scope sensitivity) weight also had no effect.
   - Values leaked between cities. A city missing from a source inherited the value of the city listed just before it. For example, Avondale Estates, GA was given Augusta's disability score.

   City rows now take state-level values only from their own state's row (`fill_from_state`). State-level results are unchanged; the 2023 data gives identical state rows before and after the fix. City scores do change: for example, Memphis on 2023 data goes from 2.62 (old code) to 3.50.

   The historical output `gardnm_algorithm_rework_normalized.csv` is left untouched. Use `gardnm_2023_normalized.csv` for comparisons with 2026.

## Source changes by category

P is the perceived-hierarchy weight (1–5, 5 = most trusted). For sources carried over unchanged, P was lowered by one level because their data is old. Full detail and URLs are in `data/sources_2026/notes.csv`. The research reports in `research/` explain how each value was obtained.

### Social
| Source | Edition | P | Status |
|---|---|---|---|
| Oxfam, Best States to Work Index | 2025 | 4 | new |
| Census ACS income inequality (1 − Gini) | 2025 | 4 | new |
| Motley Fool social equity cities (infogram) | 2019–20 data | 3 | carried over: no new edition; the page shows a 2024 date but the data is unchanged |
| National Equity Atlas | 2020 | 3 | carried over: site blocked automated access, so a newer edition could not be checked |

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
| Move.org, LGBTQ family | 2025 | 3 | refreshed; P lowered because it is partly built on MAP's data |
| Erin in the Morning, adult anti-trans legal risk map | Jul 2026 | 3 | new; the only source specific to trans risk that is updated regularly |
| SafeHome.org, LGBTQ+ state safety | 2026 | 2 | new; low P because it is largely built on MAP's data |

### Disabilities
| Source | Edition | P | Status |
|---|---|---|---|
| WalletHub, best cities for people with disabilities | 2026 | 4 | refreshed; city-level |
| US News, disability unemployment gap | 2026 | 4 | refreshed (older editions measured the employment gap) |
| Census ACS disability employment parity | 2025 | 5 | new |
| New America, competitive integrated employment | 2026 | 4 | new |
| FTA National Transit Database, % ADA-accessible stations | 2025 | 3 | new; city-level; little spread (43 of 52 areas at 100%) |
| NCAJ Justice Index, disability access | 2021 | 3 | carried over: no new edition |

Dropped: BenefitsPro (a one-off 2022 article; its report link is dead) and the Disability:IN DEI report (company-level only).

### New optional categories (extended run only)
| Category | Source | Edition | P |
|---|---|---|---|
| `immigration` | ILRC state immigration-enforcement map (20 policy types) | Sep 2026 | 3 |
| `safety` | Giffords gun-law strength rank | Dec 2025 | 3 |

These are not in the core run because adding categories changes what the composite score means. The project team should decide whether to adopt them. Several reviewed candidates were rejected: FBI hate-crime counts (reporting is voluntary, so the data would reward states that under-report), ADL religious-incident counts, and ICE 287(g) agreement counts. The research reports give the reasons.

### Collected but not used as inputs
- **Berkeley OBI Inclusiveness Index 2025.** A composite covering race, gender, LGBTQ, disability and religion. It is kept as an independent cross-check rather than an input; using it as both would double-count those dimensions and make the check circular.
- **Archbridge social mobility.** It measures mobility, not equity, and rewards low taxes and light regulation.
- **US News overall equality rank, 2026.** Superseded by the race-gaps-only version above.
- **CAWP women in state legislatures.** Its values were read through a summarizing fetch tool because the site blocks downloads. **They need checking against the site before use.**
- **Equaldex.** Crowd-edited.

## Results

The full tables are in `data/outputs/comparison_states_2023_vs_2026.csv` and `comparison_cities_2023_vs_2026.csv`. The Green/Amber/Red cutoffs are unchanged: 6.0 and above is Green, 3.6–6.0 Amber, below 3.6 Red.

- **Overall agreement.** State rankings stay broadly consistent (Spearman 0.89 between 2023 and 2026). By category, gender and sexual orientation agree closely (0.94); race (0.74), social (0.55) and disability (0.27) changed substantially because most of their sources were replaced.
- **Zone counts.** 2023 had 19 Green, 31 Amber and 6 Red; 2026 has 23 Green, 23 Amber and 6 Red, plus 4 territories with no 2026 data. The red group shifted: South Carolina, Alabama, Arkansas and Puerto Rico are now Red, while South Dakota moves up to Amber.
- **Largest drops:**

  | State | Change | Main drivers (category change) |
  |---|---|---|
  | Florida | −1.5 | sexual orientation −2.6, disability −2.0, gender −1.7 |
  | Texas | −1.2 | gender −2.8, social −2.4 |
  | Connecticut | −1.2 | race −2.0, social −1.6, disability −1.1 |
  | Georgia | −1.0 | social −2.8, gender −1.5 |

- **Largest gains:** South Dakota (+1.2), Delaware (+0.9) and Wyoming (+0.8).
  - South Dakota's gain comes almost entirely from disability (+4.7, driven by its high disability employment parity) and social (+2.3).
  - Gap-based race measures and disability-employment parity favor states with small minority populations and tight labor markets. The team should review these sources' weights.
- **Cross-check.** Agreement with the independent OBI Inclusiveness Index improved from 0.40 (2023) to 0.51 (2026). The agreement is moderate, partly because OBI's own ranking contains surprises such as Massachusetts at 48th.
- **Example cities from the DPP list.**
  - Memphis moves from Red to Amber.
  - Boston, Washington DC and Chicago fall slightly but remain Green.
  - Atlanta, Houston and Orlando fall within Amber.
  - In the extended run, adding immigration and safety pushes Texas and Idaho into Red.

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
- **Sources the agents could not access.**
  - National Equity Atlas, the AARP long-term services and supports scorecard, the Child Opportunity Index metro data, and the Social Progress Imperative state and city data were blocked or behind interactive tools.
  - All of them would be worth downloading by hand.
- **Values read through a summarizing fetch tool** (because the sites block downloads):
  - CRR tiers: cross-checked against CRR's published totals.
  - CAWP: excluded until verified.
- **Gap-based measures favor homogeneous states.** The race-gap and disability-parity measures reward states with small minority populations or tight labor markets, and the OBI segregation index ranks homogeneous cities as integrated (Laredo, TX is #1).
- **City names were harmonized** across city-level sources by `scripts/gather/oct2026/harmonize_city_names.py`. The original spellings are kept in a `City_source` column.
- **Coverage gaps.** Coverage of DC and Puerto Rico varies by source. The 2026 data has no rows for the other territories.
- **Parsing scripts.** The scripts the research agents used are in `scripts/gather/oct2026/<category>/` for reference. They were one-off scripts and may need path changes before they can be re-run.
