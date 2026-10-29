# sexual_orientation category: 2026 refresh (retrieved 2026-10-29)

All CSVs are in `data/processed_data_2026/`, and raw snapshots or URL notes are in `data/raw_data_2026/<key>/`. Every value was parsed from a page or PDF that was actually retrieved. No value was estimated.

## Datasets produced

| key | publisher / URL | edition | level | rows | scoring column | proposed P | status |
|---|---|---|---|---|---|---|---|
| `map_equaliltyMaps_2026` | Movement Advancement Project, https://www.lgbtmap.org/equality-maps | live tally retrieved 2026-10-29 | state | 51 (50 + DC; 5 territories dropped) | `Score` = min-max of the Overall Policy Tally (out of 47; observed range -16.5 to 44.5) scaled to 0-100. The SO (/22) and GI (/25) sub-tallies are kept as extra columns. | 5 | REPLACES `map_equaliltyMaps` (old typo stem kept on purpose) |
| `hrc_stateEquityIndex_2024` | HRC Foundation & Equality Federation, https://www.hrc.org/resources/state-equality-index and https://reports.hrc.org/2024-state-equality-index | 2024 SEI, published January 2025. This is the latest edition: the 2025 and 2026 report URLs return 404. | state | 51 | `Processed`, based on the 4 HRC categories: High Priority = 0 (24 states), Building = 3.33 (UT), Solidifying = 6.67 (AK, IA, PA, WI), Working Toward Innovative = 10 (21 + DC). | 5 | REPLACES `hrc_stateEquityIndex` |
| `hrc_municipalEqualityIndex_2025` | HRC Foundation MEI, https://reports.hrc.org/municipal-equality-index-2025. City scorecard PDFs are listed at https://www.hrc.org/resources/mei-state/<state>/ | MEI 2025 (14th edition, November 2025). The 2026 edition is not out yet. | city (S=2) | 509 cities in 50 states (no DC) | `Score` = the "Final Score" (0-100) printed on each city scorecard PDF. All 509 PDFs were downloaded and parsed. | 5 | NEW |
| `move_lgbtqFamily_2025` | Move.org (with SafeWise), https://www.move.org/best-worst-states-start-lgbtq-family/ | "Best States to Start an LGBTQ+ Family in 2025", updated 2026-01-26 | state | 50 (no DC) | `Rank`, 1-50 as published. | 3 | REPLACES `move_lgbtqFamily` |
| `outLeadership_lgbtqBusinessClimate_2026` | Out Leadership, https://outleadership.com/wp-content/uploads/2026/08/2026-Index-1.pdf (landing page https://outleadership.com/driving-equality/2026-state-business-climate-index/) | 2026 index (8th edition, June 2026) | state | 50 | `Score` = 2026 expanded score (32 indicators, normalized to 100). The legacy 2025 and 2026 scores and the 5 category scores are extra columns. | 4 | Effectively REPLACES `axios_lgbtq_equality` (see note below) |
| `safehome_lgbtqStateSafety_2026` | SafeHome.org, https://www.safehome.org/data-lgbtq-state-safety-rankings/ | 2026 report, 2026-05-22 | state | 51 | `Score` = published composite "Total score" (44.7-95.8). | 3 | NEW |
| `erinInTheMorning_transAdultRiskMap_2026` | Erin Reed / Erin in the Morning, https://www.erininthemorning.com/p/anti-trans-national-legal-risk-assessment-bb2 | July 2026 adult map (2026-07-13). This is the latest one found. | state | 51 | `Processed` from the 6 tiers: Do Not Travel = 0 (FL, ID, KS, TX), Worst = 2 (15 states), High = 4 (5), Moderate = 6 (3), Low = 8 (8 + DC), Most Protective = 10 (15). I chose the equal spacing. | 3 | NEW |
| `equaldex_equalityIndex_2026` | Equaldex, https://www.equaldex.com/equality-index/united-states | live, retrieved 2026-10-29 | state | 51 (Puerto Rico dropped) | `Score` = Equality Index (0-100), which is the mean of the Legal Index and the Public Opinion Index (both kept as extra columns). | 2 | NEW (optional) |

### Notes on the datasets
- **Axios is the same data as Out Leadership.** The old `axios_lgbtq_equality` values match Out Leadership's 2022 State LGBTQ+ Business Climate Index exactly (CO 86.33, NY 93.67). Axios was only reporting it, so `outLeadership_lgbtqBusinessClimate_2026` is its successor. Do not keep both.
- **Overlaps between sources.** MAP tallies feed into SafeHome (its law score), Move.org (its legislation input) and SafeWise. Counting all of them at once would over-weight MAP's view.
- **Why the P values:**
  - MAP, HRC SEI and HRC MEI (P=5): advocacy research organizations with transparent policy rubrics.
  - Out Leadership (P=4): 32 published indicators and 7 years of continuity, but run by a business network.
  - SafeHome (P=3): media/commercial, but discloses its methodology (survey-weighted MAP laws plus FBI hate-crime data).
  - Move.org (P=3): moving-company content that mixes in cost of living.
  - Erin in the Morning (P=3): mostly the qualitative judgment of one expert, but it is the only source that is explicitly trans-risk focused and updated during 2026.
  - Equaldex (P=2): crowd-edited and based partly on user surveys.
- **HRC SEI is coarse.** The 2024 SEI only gives 4 categories, with no numeric score. The old `hrc_stateEquityIndex` file had finer hand-assigned values whose rule I could not reproduce, so I used the 4 categories directly.
- **MEI counts.** HRC's press release says 506 cities and 132 perfect scores. The scorecard PDFs give 509 cities, 133 at 100, and a mean of 70.2. The PDFs were used as-is. City names come from the scorecard headers (e.g. "Port Saint Lucie", "Winston-Salem"), so they may need harmonizing with the city names in other datasets before merging on State+City.

## Existing sources: refresh status
- `hrc_stateEquityIndex`: refreshed to the 2024 SEI (published January 2025). HRC has not released a 2025 or 2026 SEI as of 2026-10-29: its pages still say "2024", and reports.hrc.org/2025-state-equality-index returns 404.
- `move_lgbtqFamily`: refreshed to the 2025 edition.
- `map_equaliltyMaps`: refreshed to the live data as of 2026-10-29.
- `axios_lgbtq_equality`: no newer Axios piece found. It was a one-time article about Out Leadership's 2022 index, which is now superseded by the Out Leadership 2026 dataset above.

## Candidates found but not extracted
- **Erin in the Morning youth trans risk map (July 2026)**, same URL as the adult map. I skipped it because a conference audience is adults.
- **SafeWise LGBTQ+ safety ranking.** Only a rank column, republished in the Move.org table (kept there as `Rank_SafeWise_LGBTQ_Safety`). I did not find a standalone 2026 SafeWise page.
- **Trans Legislation Tracker**, https://translegislation.com. Counts of anti-trans bills by state; it is a count, not an index.
- **MAP Gender Identity sub-tally**, already included as a column in `map_equaliltyMaps_2026` if a trans-only score is wanted.
- **24/7 Wall St "Best and Worst States for LGBTQ People"** (2023), https://247wallst.com/special-report/2023/07/06/the-best-and-worst-states-for-lgbtq-people-3/. Too old and a weak source.

## Summary reports
- **"Uneven Ground: Six Years of Diverging LGBTQ Policy and What's at Stake in 2026"**, MAP, September 2026, https://mapresearch.org/report/uneven-ground-six-years-of-diverging-lgbtq-policy/. Covers January 2020 to July 2026. 16 states + DC rank High on gender identity policy and 26 rank Negative; protections increasingly depend on where people live.
- **"The Revival of Anti-LGBTQ Ballot Measures"**, MAP, 2026, https://mapresearch.org/brief/the-revival-of-anti-lgbtq-ballot-measures/. November 2026 brings the first-ever anti-transgender ballot measures, in five states.
- **2024 State Equality Index report**, HRC/EFI, January 2025, https://reports.hrc.org/2024-state-equality-index. Reviews 2024 state legislation and the outlook for 2025; 24 states are in the lowest tier.
- **2026 State LGBTQ+ Business Climate Index**, Out Leadership, June 2026 (PDF above). The national average has fallen for 4 straight years, to 60.87 on the expanded scale; MA and NY are top and AR is last.
- **2026 LGBTQ+ State Safety Report Cards**, SafeHome.org, May 2026 (URL above). 13 states get an A and 6 get an F. It includes a survey of 1,004 LGBTQ+ adults: 28% have considered moving states and 61% have avoided public spaces.
- **"The Impact of 2025 Anti-Transgender Legislation on Youth"**, Williams Institute, UCLA, January 2026, https://williamsinstitute.law.ucla.edu/publications/ (not opened directly; reported via search and news coverage). More than half of trans youth live in states with restrictive laws.
- **MEI 2025 report**, HRC, November 2025, https://reports.hrc.org/municipal-equality-index-2025. A record number of cities score 100 even as state preemption overrides local protections.
