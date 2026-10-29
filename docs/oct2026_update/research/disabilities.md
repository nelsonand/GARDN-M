# Disabilities category: 2026 refresh report (2026-10-29)

All outputs are in `data/processed_data_2026/`. Raw files are in `data/raw_data_2026/<key>/`. Every value comes from a retrieved file. Nothing was estimated.

## Datasets produced

| Key | Level | Rows | Scoring column | Proposed P | Status |
|---|---|---|---|---|---|
| wallethub_citiesDisabilities_2026 | city | 182 | Score (WalletHub total score, 0-100) | 4 | REPLACES wallethub_citiesDisabilities |
| usNews_equalityRankings_2026 | state | 50 | Rank (unemployment gap by disability status rank) | 4 | REPLACES usNews_equalityRankings |
| census_acsDisabilityEmploymentParity_2025 | state (+DC) | 51 | Score (derived parity ratio) | 5 | NEW |
| newAmerica_competitiveIntegratedEmployment_2026 | state (+DC) | 51 | Score (New America total score, 0-100) | 4 | NEW |
| fta_ntdAdaAccessibleStations_2025 | city (urbanized area) | 52 | Score (% of transit stations that are ADA accessible) | 3 | NEW |

### 1. wallethub_citiesDisabilities_2026 (REPLACES wallethub_citiesDisabilities)
- URL: https://wallethub.com/edu/best-worst-cities-for-people-with-disabilities/7164
- Edition: 2026, published 2026-09-23. Covers 182 cities on 33 indicators in three groups: Economy, Quality of Life and Health Care.
- Scoring: `Score` is WalletHub's Total Score as published (higher is better). Overall Rank and the three category ranks are kept as extra columns.
- Top: St. Louis (61.17), Minneapolis, Columbus. Bottom: Juneau (37.94).
- Raw: the page HTML is saved in `data/raw_data_2026/wallethub_citiesDisabilities_2026/`.
- P = 4: a reputable aggregator with a published methodology. It matches the existing rating.

### 2. usNews_equalityRankings_2026 (REPLACES usNews_equalityRankings)
- URL: https://www.usnews.com/news/best-states/rankings/opportunity/equality
- Edition: Best States 2026 (`release: "2026"` in the page JSON).
- How it was retrieved: usnews.com blocks bots, so the page came from the Wayback snapshot of 2026-09-14 (`web.archive.org/web/20260914185739id_/...`). The full 50-state `rankings` JSON was extracted and saved to `data/raw_data_2026/usNews_equalityRankings_2026/rankings_json_from_wayback_20260914.json`.
- Scoring: `Rank` is the "Unemployment Gap by Disability Status" rank (`opp_eq_emdi`, where 1 = smallest gap). This mirrors the old file, which used the disability employment-gap rank. The other equality sub-ranks, the overall equality rank and the overall Best States rank are kept as extra columns.
  - Note: the metric is now the *unemployment* gap. Earlier editions used the *employment* gap.
  - Check: Vermont's card on the page shows #17, which matches the JSON.
- Coverage: 50 states, no DC.
- P = 4: a reputable media ranking. It matches the existing rating.

### 3. census_acsDisabilityEmploymentParity_2025 (NEW)
- Source: U.S. Census Bureau, ACS 2025 1-year estimates, table C18120 (Employment Status by Disability Status, civilian noninstitutionalized population aged 18-64).
- URL: https://data.census.gov/api/access/data/table?id=ACSDT1Y2025.C18120&g=010XX00US$0400000
  - api.census.gov now requires a key, so the data.census.gov table API was used instead.
- Raw: `acs1_2025_C18120_state.json`.
- Scoring: `Score` = 100 × (employment-to-population rate for people with a disability) ÷ (the same rate for people without a disability).
  - Each rate is employed ÷ (employed + unemployed + not in labor force) for that group.
  - Higher means more parity, which is better. The values fit a 0-100 scale naturally.
  - Extra columns: both employment rates, the gap in percentage points, and the number of people aged 18-64 with a disability.
- Range: North Dakota 68.7 (top) to West Virginia 43.9 (bottom). Puerto Rico was dropped. DC is included.
- P = 5: official federal survey data with a fully transparent derivation. The caveat is that it measures a single outcome (employment).

### 4. newAmerica_competitiveIntegratedEmployment_2026 (NEW)
- URL: https://www.newamerica.org/insights/the-road-to-competitive-integrated-employment/updated-state-policy-data-and-rankings/
  - Published 2026-01-25 and based on 2025 data.
- How it was retrieved: the score table came from the page's Datawrapper chart (`https://datawrapper.dwcdn.net/5lATQ/10/dataset.csv`). The underlying Google data sheet was also saved. Both are in `data/raw_data_2026/newAmerica_competitiveIntegratedEmployment_2026/`.
- Scoring: `Score` is New America's Total Score (0-100, the mean of four category scores, higher is better). The four categories are:
  1. Policy engagement with subminimum wage
  2. Use of subminimum wage 2018-2023
  3. Employment policy and funding initiatives
  4. Support of financial security (ABLE accounts and related policy)
  - New America's own rank is kept as an extra column. The "*" was removed from "West Virginia*" (New America's footnote on that state's Category 2 data).
- Range: Colorado 97.2 (top) to Wisconsin 31.8 (bottom).
- P = 4: a think-tank policy index with a published methodology appendix. It is narrow in scope (disability employment policy and subminimum wage).

### 5. fta_ntdAdaAccessibleStations_2025 (NEW, city-level)
- Sources: FTA National Transit Database, 2025 Annual Data.
  - "Transit Stations": https://data.transportation.gov/d/k9se-yvyg
  - "Reporter Agency Information", used to map agencies to urbanized areas: https://data.transportation.gov/d/jm7a-9hsy
  - Raw CSVs (1.2 MB) are saved.
- Method:
  - Summed the Primary Mode ADA-accessible stations and Primary Mode total stations for every reporting agency in each urbanized area (UZA). Secondary-mode counts were excluded to avoid double counting.
  - Kept UZAs with at least 10 stations. Non-UZA rural areas and Puerto Rico were excluded.
  - City and State are the first-listed principal city and state of the UZA name (e.g. "Philadelphia, PA--NJ--DE--MD" becomes Philadelphia, PA). The full UZA name is kept as a column.
- Scoring: `Score` = % of stations that are ADA accessible.
- Caveats:
  - The values are saturated: 43 of 52 areas are at 100%.
  - The only ones below 100% are legacy rail systems: Philadelphia 48%, Hartford 52%, New York 59%, Pittsburgh 63%, Baltimore 78%, Chicago 81%, Boston 82%, Cleveland 83%, San Francisco 98% and Washington 99%.
  - Cities without fixed-guideway or station-based transit are absent.
- P = 3: authoritative federal data that is directly relevant to attendee mobility. It is a single narrow indicator with little spread, so it is probably most useful as a penalty for legacy rail systems.

## Existing sources not refreshed
- **ncaj_disabilityAccess**: no new edition exists.
  - NCAJ's current download (`https://ncaj.org/sites/default/files/2024-10/Justice%20Index%20Dataset%202024-09-25.xlsx`, sheet "6) Disability Access Index") holds the same 2021 Disability Access Index.
  - Its scaled scores match the existing CSV for every state, apart from floating-point rounding. DC (32.5) is the only addition.
  - Keep the existing file. No 2026 file was written.
- **benefitspro_citiesDisabilities**: a one-off October 2022 BenefitsPro article on a Better Benefits study, which mainly covered disabled-parking placard rules and fees. It has no newer edition and the full report link is dead. Treat it as discontinued. Its P=5 rating also looks too high for this kind of source.
- **disabilityin_deiReport**: the Disability:IN Disability Equality Index is company-level only and has no state or city breakdown. It cannot be used for state or city scoring.

## Candidate sources found but not extracted
- **AARP/Commonwealth/SCAN LTSS State Scorecard 2023** (older adults and people with physical disabilities; 51-state overall rank in five tiers). P would be 5.
  - longtermscorecard.org and ltsschoices.aarp.org now redirect to a 404. The full ranking was only found in graphics and per-state pages.
  - Index page: https://www.aarp.org/pri/topics/ltss/ltss-scorecard-2023-state-fact-sheets/
  - No 2026 edition was found, although the three-year cycle would put one around now. Worth re-checking.
- **ANCOR/UCP Case for Inclusion** (https://caseforinclusion.org/data): the composite state ranking stopped after about 2019-2020. The site now publishes about 80 unaltered indicators and data snapshots, with no composite score.
- **BTS "ADA-Accessible Rail Transit Stations by Agency"** (https://www.bts.gov/content/ada-accessible-rail-transit-stations-agency): returned 403. The NTD table above covers the same data.
- **Everway "Untapped talent"** (https://www.everway.com/research-insights/workplace-disability-inclusion-united-states/): a state ranking of disability employment rates built from Cornell's analysis of ACS 2023. It is redundant with the ACS 2025 dataset above.
- **Cornell Yang-Tan disabilitystatistics.org** and the **UNH Annual Disability Statistics Compendium** (https://disabilitycompendium.org): authoritative, but both are ACS-derived and redundant with dataset 3.
- **Low-quality sources, not recommended**:
  - AAA State of Play "best and worst US states for people with disabilities" (https://www.aaastateofplay.com/the-best-and-worst-us-states-for-people-with-disabilities/), a gambling-affiliate site.
  - Policygenius best states for living with a disability (https://www.policygenius.com/disability-insurance/the-best-states-for-living-with-a-disability/), an older insurance-marketing piece.

## Summary reports (landscape)
- **BLS, "Persons with a Disability: Labor Force Characteristics — 2025"** (released March 2026; https://www.bls.gov/news.release/archives/disabl_03032026.pdf, and the TED note https://www.bls.gov/opub/ted/2026/unemployment-rate-for-people-with-a-disability-rose-to-8-3-percent-in-2025.htm).
  - Unemployment for people with a disability rose to 8.3% in 2025, about double the rate for people without one (around 4.1%).
- **New America, "The Road to Competitive Integrated Employment"** (January 2026; URL above).
  - States keep phasing out subminimum wage. Colorado, Maryland and Maine lead; Wisconsin, Idaho and Missouri trail.
- **ANCOR, "The State of America's Direct Support Workforce Crisis 2026"** (https://www.ancor.org/) and **Case for Inclusion data snapshot "Progress in Peril?"** (https://caseforinclusion.org/).
  - Community-based intellectual and developmental disability (IDD) services face workforce shortages and pending Medicaid funding cuts that threaten recent gains.
- **Federal Evidence Agenda on Disability** (January 2025; https://www.ancor.org/wp-content/uploads/2025/01/Federal-Evidence-Agenda-on-Disability.pdf).
  - A federal framework for building disability data and evidence across agencies. Useful context for gaps in the data.
- **FTA/BTS ADA station trend** (from search snippets, not independently verified).
  - The share of ADA-compliant rail stations rose from about 68.5% (2014) to about 77% (2024).
  - In our 2025 NTD extraction the shortfall is concentrated in a few legacy systems: NYC, Philadelphia, Boston, Chicago, Pittsburgh, Baltimore and Hartford.
