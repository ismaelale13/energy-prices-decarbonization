"""Export event-study coefficients and covariance matrices for the official R HonestDiD package.

Reference year 2019. Following Rambachan and Roth (2023), anticipation in 2020-2021 is allowed by
treating 2020 onwards as "post" periods; the pre-periods used to bound violations are 2016-2018.
The target parameter is the average effect over 2022-2024.

Run from the repository root:  python src/export_event_study.py
Output: output/honestdid/<name>_beta.csv, <name>_sigma.csv, <name>_meta.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyfixest as pf
sys.path.insert(0, "src")
import sample as S

OUT = Path("output/honestdid"); OUT.mkdir(parents=True, exist_ok=True)
YEARS = [2016, 2017, 2018, 2020, 2021, 2022, 2023, 2024]  # 2019 = reference
PRE = [2016, 2017, 2018]


def export(df, y, name):
    m = pf.feols(f"{y} ~ i(fyear, high_exposure, ref=2019) | ric + fyear", data=df.dropna(subset=[y]),
                 vcov={"CRV1": "ric"})
    names = list(m.coef().index)
    order = [next(i for i, n in enumerate(names) if str(yr) in n) for yr in YEARS]
    beta = m.coef().values[order]
    sigma = m._vcov[np.ix_(order, order)]
    pd.DataFrame({"year": YEARS, "beta": beta}).to_csv(OUT / f"{name}_beta.csv", index=False)
    pd.DataFrame(sigma, columns=YEARS).to_csv(OUT / f"{name}_sigma.csv", index=False)
    post = [yr for yr in YEARS if yr not in PRE]
    l_vec = [1 / 3 if yr >= 2022 else 0 for yr in post]
    pd.DataFrame({"numPrePeriods": [len(PRE)], "numPostPeriods": [len(post)],
                  "l_vec": [";".join(f"{v:.10f}" for v in l_vec)], "outcome": [y]}).to_csv(OUT / f"{name}_meta.csv", index=False)
    print(f"{name}: exported {len(beta)} coefficients")


p = S.load_panel()
export(S.main_sample(p), "ln_ci", "h1_ln_ci")
h2 = S.industry_sample(p)
export(h2, "ln_emissions", "h2_ln_emissions")
export(h2, "ln_real_ci", "h2_ln_real_ci")
export(h2, "ln_real_revenue", "h2_ln_real_revenue")
