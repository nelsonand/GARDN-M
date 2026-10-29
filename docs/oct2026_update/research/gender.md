# GARDN-M 2026 update: gender category (agent report, 2026-10-29)

All CSVs are in `data/processed_data_2026/`. Raw files, where kept, are in `data/raw_data_2026/<key>/`.

## Datasets produced

| Key | Publisher / URL | Edition / data | Level, rows | Scoring column | Proposed P | Replaces / New |
|---|---|---|---|---|---|---|
| wallethub_womenEquity_2026 | WalletHub, https://wallethub.com/edu/best-and-worst-states-for-women-equality/5835 | Published Aug 17 2026 (data as of Jul 20 2026), 17 metrics | State, 50 | `Score` = WalletHub "Total Score" (0-100, higher is better), no transformation. Sub-ranks kept as extra columns. | 4 (media/aggregator ranking with published methodology) | REPLACES wallethub_womenEquity |
| wallethub_bestStatesWomen_2026 | WalletHub, https://wallethub.com/edu/best-and-worst-states-for-women/10728 | Published Mar 2 2026, 25 metrics (economic/social well-being; health care and safety) | State, 51 (includes DC) | `Score` = Total Score (0-100), no transformation | 4 (same reason as above) | NEW. It overlaps conceptually with the equity ranking above, so consider using one or down-weighting. |
| commonwealthFund_womensHealthReproCare_2024 | Commonwealth Fund, *2024 State Scorecard on Women's Health and Reproductive Care*, https://www.commonwealthfund.org/publications/scorecard/2024/jul/2024-state-scorecard-womens-health-and-reproductive-care ; data from Appendix B2 PDF https://www.commonwealthfund.org/sites/default/files/2024-07/Collins_2024_state_scorecard_womens_health_APPENDICES.pdf | July 2024, mostly 2021-22 data, 32 measures; explicitly post-Dobbs. No newer edition found. | State, 51 (includes DC) | `Rank` = overall rank (1 is best; ties exist, e.g. 29 and 48). Dimension ranks kept as extra columns. | 5 (research foundation, transparent indicator-level methodology) | NEW |
| populationInstitute_reproFreedomReportCard_2026 | rePROs Fight Back (Population Institute), 14th annual 50-State Report Card, https://reportcard.reprosfightback.com/ ; PDF https://reportcard.reprosfightback.com/wp-content/uploads/2026/03/50-State-Report-Card.pdf (48 MB, not kept) | March 2026, policies as of 2025 | State, 51 (includes DC) | `Score` = the state's composite "NN / 100" from its report-card page (0-100). 11 policy criteria: sex ed, emergency contraception, minors' contraception, Medicaid expansion, family-planning waiver, postpartum coverage, abortion insurance coverage, abortion restrictions, TRAP laws, medication abortion, gender-affirming care (10 pts). Letter grade kept. | 4 (advocacy organization with transparent points rubric, but it is policy-only and openly advocacy) | Effective REPLACEMENT for iwpr_reproductiveRights, which was never updated after 2022. Note that the gender-affirming-care criterion overlaps with the sexual_orientation category. |
| crr_abortionLawsByState_2026 | Center for Reproductive Rights, "Abortion Laws by State", https://reproductiverights.org/maps/abortion-laws-by-state/ (data endpoint `/wp-json/crr-maps/v1/map-data?type=us-arf`) | Page says "updated September 2026" | State, 51 (includes DC) | `Processed` (0-10), mapped from CRR's 5-tier ordinal category: Expanded Access = 10, Protected = 7.5, Not Protected = 5, Hostile = 2.5, Illegal = 0. The mapping is our own linear choice. The category is kept in `crr_category`. | 5 (leading legal advocacy/research org with a legal-analysis methodology), or 4 because it is coarse | NEW |
| cawp_womenStateLegislators_2026 | Rutgers CAWP, https://cawp.rutgers.edu/data/levels-office/state-legislature | Page states data as of October 2026 | State (2-letter abbreviation), 50 | `Rank` computed by us from "% Women Overall" (descending; ties share the minimum rank). Percentages and seat counts kept. | 5 (academic center, authoritative counts) | NEW |

Extraction notes:

- **CRR and CAWP values are not from the raw JSON.** curl was blocked (Cloudflare/403), so values were retrieved via WebFetch.
  - CRR: the counts match CRR's own page text, which says abortion is protected in 25 states plus DC (11 Expanded Access + 14 Protected + DC). Seven rows were re-checked against quoted raw JSON (`status_label`).
  - CAWP: every row is internally consistent (women/seats matches %). Seven rows were re-quoted verbatim.
  - CAWP's own "State Rank" column was internally inconsistent (VT 10 and AK 13 both at 43.3%; FL 10 at 42.5%), so it was dropped and the rank recomputed.
  - On the CAWP page, Alaska's senate plus house women (5+20) does not equal its total (26). The 26/60 = 43.3% figure was used.
- **Main.py rank normalization (nNorm):** commonwealthFund has 51 rows, so main.py will print the nNorm != 50 warning and normalize by 51. CAWP has 50 rows.
- **DC rows:** these 4 CSVs include DC: wallethub_bestStatesWomen, commonwealthFund, populationInstitute, crr.
- **Population Institute, earlier edition:** the March 2025 (13th) edition was also read (https://www.populationinstitute.org/wp-content/uploads/2026/07/PI-2025-50-State-Report-Card.pdf) but not kept, because the 2026 edition supersedes it.

## Existing sources not refreshed

- **georgetown_usaIndex:** there is no newer US-state edition. The GIWPS site re-uploaded the same "US WPS Index 2020" data in Sep 2025 (https://giwps.georgetown.edu/wp-content/uploads/2025/09/US-Index-Data.xlsx). The 2025/26 WPS Index is countries only. Keep the old file.
- **usaNews_statesGenderEquality:** this was a one-off 2022 U.S. News analysis, and no later edition was found. usnews.com still blocks scripted access.
- **statusWomen_bestWorstStates (IWPR):** the page is still the 2015 edition, and there have been no composite updates since then. IWPR's Status of Women series is effectively discontinued for composite rankings. Treat it as stale and consider dropping it.
- **iwpr_reproductiveRights:** the July 2022 edition is still the latest (https://iwpr.org/articles/iwpr-reproductive-rights-index-a-state-by-state-analysis-and-ranking/). The old URL now returns 404. It predates or straddles Dobbs, so it is stale; the replacements are the Population Institute and CRR datasets.

## Candidates found but not extracted

- **Guttmacher Institute abortion policy map** (https://www.guttmacher.org/state-policy). This is a 7-category policy classification, and CRR was used instead.
- **KFF Women's Health Policy state indicators** (https://www.kff.org/statedata/). These are individual indicators, not a composite.
- **March of Dimes Report Card / Maternity Care Deserts** (https://www.marchofdimes.org/report-card). This is more of a maternal-health outcome than an equity measure, and it was not pursued.
- **NCSL Women in State Legislatures 2025** (https://www.ncsl.org/womens-legislative-network/women-in-state-legislatures-for-2025). This is a duplicate of CAWP.

## Summary reports (for the write-up)

- **Commonwealth Fund, 2024 State Scorecard on Women's Health and Reproductive Care (Jul 2024).** States with pre-Dobbs abortion restrictions rank lower on maternal provider supply and outcomes. The maternal mortality rate nearly doubled from 2018 to 2022, and the Southeast performs worst.
- **rePROs Fight Back (Population Institute), 50-State Report Card (Mar 2026), https://reportcard.reprosfightback.com/.** The US received an "F" for the 7th year running: 25 states fail, and 16 earn A or B. It frames access as a patchwork that depends on state of residence after Dobbs.
- **Guttmacher Institute, full-year 2025 abortion estimates (Mar 2026), https://www.guttmacher.org/2025/09/states-without-total-abortion-bans-see-declines-clinician-provided-abortions-and-out-state (plus related 2026 releases).** As of end-2025 there were 13 states with total bans and 6 with 6- or 12-week bans. Interstate travel fell from about 154k to 142k, while telehealth to ban states rose to about 91k.
- **CAWP, "Virginia gains, New Jersey drops" 2026 rankings press release (Jan 27 2026), https://cawp.rutgers.edu/news-media/press-releases/virginia-gains-new-jersey-drops-cawp-state-rankings.** Women hold a record ~33% of state legislative seats. Nevada (61.9%) leads and West Virginia is last.
