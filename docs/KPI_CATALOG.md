# KPI Catalog - Indian Voter Turnout

## A. Computed in this project (data available)
| # | KPI | Formula | Output |
|---|-----|---------|--------|
| 1 | Overall Voter Turnout Ratio (VTR) | Total votes / Total electors x 100 | scorecard, state, PC |
| 2 | Male / Female VTR | Gender votes / gender electors x 100 | state, PC, region |
| 3 | Gender Turnout Gap (pp) | Male VTR - Female VTR (negative = women out-vote men) | state, PC, region |
| 4 | Elector Gender Ratio | Female electors / Male electors x 1000 | state, region |
| 5 | Female Share of Votes | Female votes / Total votes x 100 | state |
| 6 | Non-voters | Electors - Votes | state, PC |
| 7 | Gap vs National (pp) | State VTR - National VTR | state |
| 8 | Mobilisation Potential | Extra votes if a below-average state reached the national VTR | state |
| 9 | Turnout Dispersion | Std dev, range, coefficient of variation of PC-level VTR | national, state |
| 10 | Low-Turnout Constituency Share | % of PCs below 60% (and below 50%) | scorecard, list |
| 11 | High-Turnout Constituency Share | % of PCs at or above 75% | scorecard |
| 12 | Outlier PCs | VTR outside Q1-1.5xIQR / Q3+1.5xIQR | table 10 |
| 13 | Regional VTR & gap | Six-region grouping | region table |
| 14 | Size-Turnout Correlation | Pearson r(electors, VTR) | scorecard |
| 15 | Gender Gap-Turnout Correlation | Pearson r(gap, VTR) | scorecard |

## B. Listed in the brief but NOT computable from these two files
| KPI | Extra data needed |
|-----|-------------------|
| Net Turnout Swing | Previous-election VTR (add another year's CSV, then join on PC/state) |
| Elector-to-Population Ratio | Projected 18+ population (Census / RGI projections) |
| Non-Voter-to-Margin Ratio | Winning margin per PC (ECI Statistical Report) |
| EVM vs Postal turnout, Postal participation, Rejected postal rate | EVM / postal split (ECI Form 20 or report) |
| First-time voter, PwD, Third-gender, NRI turnout | Age/category-wise electors and votes |
| Urban-Rural differential | PC urban/rural classification (Census / Delimitation Commission) |
| Booth-level variance, low-turnout booth share | Form 20 booth-level data |
| Time-slot turnout velocity | ECI ENCORE / Voter Turnout app hourly data |
| Turnout-to-Swing elasticity | Vote-share by party for two elections |
| Phase-wise drift | Phase of each PC |

## C. Data-quality notes
- Numbers use Indian digit grouping ("1,42,782") - parsed in `src/clean.py`.
- State names standardised: Chattisgarh -> Chhattisgarh, Orissa -> Odisha, NCT OF Delhi -> Delhi.
- Andhra Pradesh has 42 PCs (includes today's Telangana), and electors total 83.4 crore at 66.40% VTR - this matches the **2014** Lok Sabha election, not 2024. Do not compare it with the 2024 figures (66.10%, 946 F per 1000 M) quoted in the brief.
- PC names are not unique (Aurangabad, Hamirpur, Maharajganj) - always key on State + PC Code.
