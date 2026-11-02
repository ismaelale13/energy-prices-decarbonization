"""Shared sample definitions used by all notebooks (single source of truth)."""
from pathlib import Path
import numpy as np
import pandas as pd

PANEL = Path("data/processed/panel_2016_2024.csv")
PRE, POST = range(2016, 2022), range(2022, 2025)
SHOCK_YEAR, REF_YEAR = 2022, 2019


def load_panel(path=PANEL):
    return pd.read_csv(path, dtype={"nace2": str, "nace4": str})


def _pre_post(df, var):
    ok = df.dropna(subset=[var])
    pre = set(ok[ok.fyear.isin(PRE)].ric)
    post = set(ok[ok.fyear.isin(POST)].ric)
    return df[df.ric.isin(pre & post)]


def _add_groups(df):
    """Median split and terciles of pre-crisis energy intensity, computed WITHIN the sample."""
    firms = df.drop_duplicates("ric")[["ric", "exposure"]]
    med = firms.exposure.median()
    firms = firms.assign(
        high_exposure=(firms.exposure > med).astype(int),
        exposure_tercile=pd.qcut(firms.exposure, 3, labels=["low", "mid", "high"]),
        ln_exposure=np.log(firms.exposure),
    )
    firms["exposure_std"] = (firms.ln_exposure - firms.ln_exposure.mean()) / firms.ln_exposure.std()
    df = df.drop(columns=[c for c in ["high_exposure"] if c in df]).merge(firms.drop(columns="exposure"), on="ric")
    df["post"] = (df.fyear >= SHOCK_YEAR).astype(int)
    return df


def main_sample(p):
    """H1 sample: non-financial firms with carbon intensity before and after 2022 and pre-crisis exposure."""
    df = p[(~p.financial) & p.exposure.notna() & (p.exposure > 0)]
    df = _pre_post(df.dropna(subset=["ln_ci"]), "ln_ci")
    return _add_groups(df)


def industry_sample(p):
    """H2 sample: industrial firms (NACE 05-39) with real carbon intensity before and after 2022."""
    df = p[(~p.financial) & p.industry & p.exposure.notna() & (p.exposure > 0)]
    df = _pre_post(df.dropna(subset=["ln_real_ci"]), "ln_real_ci")
    return _add_groups(df)
