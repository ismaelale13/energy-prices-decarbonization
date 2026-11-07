# Results log

Single place for all key findings. Numbers come from the notebooks; tables in `output/tables/`.
Updated: 2026-11-02.

## Samples
| Sample | Firms | Firm-years | Definition |
|---|---|---|---|
| Universe | 601 | | STOXX Europe 600 constituents on 31 Dec 2021 |
| H1 | 387 | 3,214 | non-financial, carbon intensity before and after 2022, energy intensity 2016-2019 |
| H2 | 230 | 1,936 | industrial firms (NACE 05-39) of H1 with sector PPI |

Treatment: above-median mean energy use / revenue 2016-2019 (within sample). Outcome H1: ln((Scope 1+2) / revenue).

## H1 (`04_h1`) — supported
| Model | beta | SE | p | Effect |
|---|---|---|---|---|
| Main (Post x High) | -0.209 | 0.069 | 0.003 | -19% |
| Continuous exposure (std.) | -0.161 | 0.052 | 0.002 | -15% per SD |
| With ln(assets) | -0.211 | 0.070 | 0.003 | -19% |
| Industry only | -0.265 | 0.078 | <0.001 | -23% |

Event study (ref. 2019): pre-period coefficients 2016-2021 between -0.08 and +0.04, joint test p = 0.74;
post 2022 / 2023 / 2024: -0.21 / -0.25 / -0.23 (all p < 0.05).

## H2 (`05_h2`) — consistent with real decarbonization, imprecise
Baseline DiD, industry sample:
| Outcome | beta | p |
|---|---|---|
| ln(CO2e / nominal revenue) | -0.277 | 0.001 |
| ln(emissions) | -0.255 | 0.002 |
| ln(nominal revenue) | +0.022 | 0.53 |
| ln(sector price index) | +0.188 | <0.001 |
| ln(real revenue) | -0.166 | <0.001 |
| ln(CO2e / real revenue) | -0.089 | 0.28 |
| ln(Scope 1) | -0.278 | 0.004 |
| ln(Scope 2) | -0.238 | 0.002 |

Pre-trends: real revenue violates parallel trends (joint p < 0.001; continuous decline since 2016);
emissions (p = 0.73) and real intensity (p = 0.64) do not.

Detrended (firm-specific linear trends 2016-2019, 198 firms): real revenue +0.005 (p = 0.94),
real intensity -0.241 (p = 0.07), emissions -0.236 (p = 0.09).

Interpretation: emissions fell, output did not deviate from its pre-existing trend -> evidence consistent with
real decarbonization rather than output contraction; imprecise (10% level).

## Sensitivity: HonestDiD (Rambachan & Roth 2023, R package 0.2.8; `07_honestdid`)
Reference 2019, pre = 2016-2018, target = average of 2022-2024 (2020-21 = anticipation). 95% CIs.

Relative magnitudes (breakdown Mbar):
- H1 ln_ci: original [-0.407, -0.053]; Mbar 0.25 [-0.480, -0.020]; fails at 0.5 -> breakdown 0.25-0.5.
- H2 emissions: original [-0.492, -0.110]; Mbar 0.25 [-0.603, -0.025]; fails at 0.5 -> breakdown 0.25-0.5.
- H2 real intensity: not significant even in original [-0.361, 0.028].
- H2 real revenue: original [-0.227, -0.042]; fails at 0.25.

Smoothness (M = deviation from linear pre-trend):
- H1 ln_ci: M = 0 (linear trend extrapolated) [-0.630, -0.045] significant; fails at M = 0.01.
- H2 emissions: M = 0 [-0.568, 0.070] not significant.
- H2 real intensity: M = 0 [-0.576, 0.026] not significant.
- H2 real revenue: M = 0 [-0.077, 0.223] -> decline disappears once its pre-trend is extrapolated.

Interpretation: H1 robust to moderate violations of parallel trends (up to 1/4 of max pre-period deviation)
and to linear extrapolation of pre-trends, not beyond. Real-revenue decline reflects its pre-existing trend.
Only 3 pre periods -> smoothness bounds widen fast; report honestly in Limitations.

## Robustness (`06_robustness`)
- H1 robust (-0.16 to -0.29, all p < 0.05): reported only, winsorized, drop jumps, balanced (234 firms),
  without 2020, shock 2021, top vs bottom tercile (-0.29), country x year FE, sector x year FE (-0.27).
- Emissions (H2) robust in the same checks.
- Sector x year FE: real revenue +0.02 (p = 0.65), real intensity -0.264 (p = 0.03) -> supports real decarbonization.
- Treatment = energy-intensive sector (NACE 17/19/20/23/24): H1 -0.01 (n.s.) -> firm-level energy intensity, not sector membership, drives the effect.
- Market-based Scope 2 (2020-2024, only 2 pre years): +0.10 (n.s.) -> weak test, discuss in Limitations.

## Added checks (7 Nov 2026, `06_robustness`)
- Without NACE 35 and 19 (360 firms): H1 ln_ci -0.178 (SE 0.073, p = 0.015); H2 emissions -0.259 (p = 0.005), real revenue -0.162, real CI -0.097 (n.s.). Effect slightly smaller, still significant.
- H2 with continuous exposure (per 1 SD of ln pre-crisis energy intensity):
  - emissions: baseline -0.188 (p = 0.011), firm trends -0.185 (p = 0.042), sector x year FE -0.238 (p = 0.043)
  - real revenue: baseline -0.081 (p = 0.022), firm trends 0.009 (p = 0.69), sector x year FE 0.053 (p = 0.32)
  - real CI: baseline -0.108 (p = 0.13), firm trends -0.194 (p = 0.041), sector x year FE -0.291 (p = 0.003)
  - Supports H2 once pre-trends are accounted for; supplementary evidence only.

## Answer to the RQ (current draft)
Yes: after the 2022 shock, firms with high pre-crisis energy intensity reduced carbon intensity by about 19%
more than other firms. The decline reflects lower emissions; output did not fall beyond pre-existing trends,
so the evidence is consistent with real decarbonization, though the mechanism estimates are imprecise.
