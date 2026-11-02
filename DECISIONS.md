# Decision log

| # | Date | Check | Finding | Decision |
|---|------|-------|---------|----------|
| 1 | 2026-11-02 | Sample universe | Current index composition causes survivorship bias | STOXX Europe 600 composition on 31 Dec 2021 (601 firms) |
| 2 | 2026-11-02 | LSEG date window | Financial data filtered by filing date; FY2024 missing with EDate 2024-12-31 | Download window 2015-01-01 to 2025-12-31; analysis FY2016-2024 |
| 3 | 2026-11-02 | Fiscal year | Some firms end FY in Jan-May | FY ending Jan-May assigned to previous calendar year |
| 4 | 2026-11-02 | Market-based Scope 2 coverage | 0 firms 2016-2017, 27 in 2018, 77 in 2019 | Main outcome: Scope 1+2 total; market-based only robustness 2020-2024 |
| 5 | 2026-11-02 | Total vs. Scope 1 + Scope 2 | Equal in 99.5% of firm-years | Use TR.CO2EmissionTotal as Scope 1+2 |
| 6 | 2026-11-02 | Financial firms | Banks/insurers lack revenue, not energy-intensive | Exclude NACE 64-66 |
| 7 | 2026-11-02 | Reported vs. estimated | Excluding estimates removes almost no firms | Main sample keeps reported values; estimates excluded in robustness |
| 8 | 2026-11-02 | PPI coverage | PPI only for industry (NACE 05-39); UK missing in Eurostat | UK PPI from ONS MM22; H2 on industrial firms (251), H1 on all (~425) plus industry-only comparison |
| 9 | 2026-11-02 | Missing country-sector PPI | 24 industrial firms lack country PPI | EU27 PPI as fallback |
| 10 | 2026-10-31 | Russian gas dependence (Eurostat imports) | Transit/unspecified partners distort shares (AT, DK, HR, NO) | Postponed; if needed use Zhou et al. (2023) |
| 11 | 2026-11-02 | Duplicate firm-years | LSEG static file lists some RICs twice (one empty row) -> 81 duplicate firm-years | Keep most complete static row per firm (H1: 3,425 firm-years) |
| 12 | 2026-11-02 | Treatment groups | Median was computed on all firms incl. financials | Median split and terciles computed within each estimation sample (`src/sample.py`) |
| 13 | 2026-11-02 | Treatment and COVID | Exposure averaged over 2016-2021 inflated by collapsed 2020-21 revenue (airlines, hotels, tour operators) | Exposure = mean energy intensity 2016-2019 |
| 14 | 2026-11-02 | H2 pre-trends (EDA) | Pre-crisis slopes of real carbon intensity differ by exposure (p = 0.04) | H2 models add firm-specific linear trends and Rambachan-Roth sensitivity; discussed in Limitations |
