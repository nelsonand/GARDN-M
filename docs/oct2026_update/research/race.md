# Race category: 2026 refresh report (as of 2026-10-29)

All CSVs are in data/processed_data_2026/. Raw files are in data/raw_data_2026/<key>/. Every value comes from a retrieved source. Nothing was estimated.

## Datasets produced

| key | publisher / URL | edition / data year | level | rows | scoring column | P | status |
|---|---|---|---|---|---|---|---|
| usNews_stateRankingsEquality_2026 | U.S. News Best States, https://www.usnews.com/news/best-states/rankings/opportunity/equality (from the Wayback snapshot 20260914185739; the embedded `rankings` JSON lists all 50 states) | 2026 edition (released 2026-07-28) | state | 50 | `Rank` = Equality subcategory rank (1 = best), not inverted. Extra columns hold the 6 component ranks (3 race gaps, 2 gender gaps, 1 disability gap). | 4 | REPLACES usNews_stateRankingsEquality |
| usNews_raceEqualityGaps_2026 (optional alternative) | same source | 2026 | state | 50 | `Rank` = rank (method=min, so ties share a rank) of the mean of the 3 race-gap ranks: education, income and unemployment gaps between non-Hispanic whites and other groups | 4 | Alternative to the row above. It keeps only the race metrics so gender and disability are not double counted. Use one of the two, not both. |
| wallethub_statesRacialEquality_2024 | WalletHub, https://wallethub.com/edu/state-economies-with-most-racial-equality/75810 | Published 2024-06-11, data as of 2024-05-15. The page title says "(2026)", but that label is auto-updated and there is no newer edition. | state (+DC) | 51 | `Score` = WalletHub Total Score (0-100, higher = more equal) | 4 | REPLACES wallethub_statesRacialEquality |
| wallethub_racialIntegration_2026 | WalletHub, https://wallethub.com/edu/states-with-the-most-and-least-racial-progress/18428 ("States with the Most Racial Integration" table) | Published 2026-01-13, data as of 2025-12-16 | state (+DC) | 51 | `Score` = Total Score (0-100); 4 sub-ranks kept | 4 | REPLACES wallethub_racialIntegration |
| wallethub_racialEqualityEducation_2026 | WalletHub, https://wallethub.com/edu/states-education-with-the-most-racial-equality/75962 | Published 2026-06-02, data as of 2026-05-05 | state | 50 | `Score` = Total Score (0-100) | 4 | NEW |
| census_diversityIndex_2025 | U.S. Census Bureau ACS 2025 1-year, table B03002, https://www2.census.gov/programs-surveys/acs/summary_file/2025/table-based-SF/data/1YRData/acsdt1y2025-b03002.dat | ACS 2025 1-year | state (+DC) | 51 | `Score` = Census Diversity Index × 100. DI = 1 − Σp², computed over 8 groups: Hispanic, and non-Hispanic White, Black, AIAN, Asian, NHPI, Other, and Two or more races. Group shares are kept as columns. Hawaii scores 76.55, which matches the 2020 Census DI of 76.0. | 4 | REPLACES wisevoter_mostDiverseStates. WiseVoter has dropped its rankings, and its source was the 2020 Census DI. Diversity measures demographics, not equity. |
| sentencingProject_blackWhiteImprisonmentDisparity_2021 | The Sentencing Project, Detailed State Data Tool, https://www.sentencingproject.org/research/detailed-state-data-tool/ (xlsx: https://www.sentencingproject.org/app/uploads/2026/10/SP-TSP-State-Data-2026-7-14.xlsx) | Workbook is dated 2026-07-14, but the workbook itself says "State rates are from 2021" (Color of Justice report) | state | 50 (no DC) | `Rank` by Black:white imprisonment ratio, ascending (1 = smallest disparity, which is inverted from the ratio; ties use method=min). The Black:white and Latino:white ratios are kept. | 5 | NEW. Data is older than ideal, but it is the current official series. |
| berkeleyOBI_citySegregation_2023 | UC Berkeley Othering & Belonging Institute, https://belonging.berkeley.edu/most-segregated-cities-us-2020-2023 (2023 ACS tab, div#table2023) | 2025 update, 2023 ACS data | city (all cities ≥200k) | 121 | `Processed` = 10·(Dmax−D)/(Dmax−Dmin), where D is the Divergence Index (inverted: less segregated is higher). Dissimilarity, Theil H and entropy columns are kept. | 5 | City-level replacement for bloomberg_blackWomenMetros (or add as NEW) |

Caveats:
- The U.S. News race-gap ranks and the WalletHub education ranking favor very white states such as VT, ME, WV and WY, where the gaps are small but the minority populations are tiny.
- The OBI Divergence Index rates homogeneous cities as integrated (Laredo, ~95% Hispanic, ranks #1).
- OBI city names follow Census place names (e.g. "Boise City"). Check them before merging on City.
- The disabilities agent's usNews_equalityRankings_2026 comes from the same U.S. News JSON (different Rank column).

## Existing sources not refreshed
- bloomberg_blackWomenMetros: the 2020 Bloomberg CityLab / Junia Howell analysis has never been updated. Proposed replacement: berkeleyOBI_citySegregation_2023, or MoneyGeek (below).
- wisevoter_mostDiverseStates: discontinued. wisevoter.com is now a community-polling site and the URL no longer serves rankings. Replaced by census_diversityIndex_2025, computed directly from Census data.

## Candidates found but not extracted
- MoneyGeek, "Best Cities for Black Women to Flourish Financially" (Dec 2024; 164 cities): https://www.moneygeek.com/living/best-cities-black-women/. The URL now serves a generic resources page and the table was not retrieved.
- diversitydatakids.org Child Opportunity Index 3.0, "Racial/ethnic inequity in the 100 largest metro areas": https://www.diversitydatakids.org/research-library/data-visualization/racialethnic-inequity-100-largest-metro-areas. Cloudflare returned 403. A strong P=5 metro-level candidate if downloaded by hand.
- OBI metro segregation table, 2020 and 2023 (225 CBSAs): https://belonging.berkeley.edu/most-segregated-metro-areas-us-2020-2023. Easy to extract, but the CBSA names span several states.
- Commonwealth Fund 2024 State Health Disparities Report: https://www.commonwealthfund.org/publications/fund-reports/2024/apr/advancing-racial-equity-us-health-care. It scores each racial group within each state, with no single state equity score.
- Annie E. Casey Race for Results 2024 (KIDS COUNT): https://www.aecf.org/race4results. It also scores each racial group within each state.
- WalletHub "Racial Progress" table, 2026, on the same page as integration. It measures change over time, not current equity, so it was left out on purpose.
- Sentencing Project felony disenfranchisement rate (2024) is in the same xlsx. It fits better under social/civic.

## Summary reports
- OBI, Roots of Structural Racism Project, 2025 update (2025): https://belonging.berkeley.edu/roots-structural-racism-project-2025-update. Most US metros are more segregated than in 1990, and no metro area qualifies as "integrated" in 2023.
- The Sentencing Project, The Color of Justice (2021): https://www.sentencingproject.org/reports/the-color-of-justice-racial-and-ethnic-disparity-in-state-prisons/. Black Americans are imprisoned at about 4.8× the white rate (2023 U.S. rate), and in 7 states the ratio is above 9:1.
- Commonwealth Fund, Advancing Racial Equity in U.S. Health Care (Apr 2024): link above. Large racial and ethnic health-care disparities exist in every state, even top performers.
- AECF, 2024 Race for Results: link above. No state equips all children for success. Gaps are smallest in VT, NJ, MA, NH and ME.
