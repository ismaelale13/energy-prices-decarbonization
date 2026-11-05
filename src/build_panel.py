"""Build firm-year panel from LSEG raw files and report sample sizes."""
import os, sys, re
import numpy as np, pandas as pd
RAW, OUT = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("data/raw/lseg", "data/processed")
os.makedirs(OUT, exist_ok=True)
VARS = ["scope1","scope2","scope12_total","scope12_marketbased","co2_estimation_method",
        "energy_use_total","energy_purchased","revenue","total_assets"]

def load(v):
    d = pd.read_csv(f"{RAW}/raw_{v}.csv")
    d["date"] = pd.to_datetime(d["date"], errors="coerce")
    d = d.dropna(subset=["date"])
    # fiscal year convention: FY ending Jan-May belongs to previous calendar year
    d["fyear"] = d["date"].dt.year - (d["date"].dt.month <= 5).astype(int)
    if v != "co2_estimation_method":
        d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"]).sort_values("date").drop_duplicates(["ric","fyear"], keep="last")
    return d[["ric","fyear","value"]].rename(columns={"value": v})

panel = None
for v in VARS:
    d = load(v)
    panel = d if panel is None else panel.merge(d, on=["ric","fyear"], how="outer")

st = pd.read_csv(f"{RAW}/raw_static.csv").rename(columns={
    "Instrument":"ric","Company Common Name":"name","Country of Headquarters":"country",
    "TRBC Industry Name":"trbc_industry","NACE Classification":"nace_label"})
# static file can list a RIC twice (one row empty): keep the most complete row per firm
st = st.assign(_n=st.notna().sum(axis=1)).sort_values("_n", ascending=False).drop_duplicates("ric").drop(columns="_n")
st["nace4"] = st["nace_label"].astype(str).str.extract(r"\((\d{2}\.\d{1,2})\)\s*$")[0]
st["nace2"] = st["nace4"].str[:2]
panel = panel.merge(st[["ric","name","ISIN","country","trbc_industry","nace_label","nace4","nace2"]], on="ric", how="left")
panel = panel[(panel.fyear >= 2016) & (panel.fyear <= 2024)].copy()

panel["reported"] = panel["co2_estimation_method"].eq("Reported")
panel["financial"] = panel["nace2"].isin(["64","65","66"])
panel["post"] = (panel.fyear >= 2022).astype(int)
ok = (panel.scope12_total > 0) & (panel.revenue > 0)
panel["carbon_intensity"] = np.where(ok, panel.scope12_total / panel.revenue * 1e6, np.nan)  # t CO2e per EUR m
panel["ln_ci"] = np.log(panel["carbon_intensity"])
panel["energy_intensity"] = np.where((panel.energy_use_total > 0) & (panel.revenue > 0),
                                     panel.energy_use_total / panel.revenue * 1e6, np.nan)

# exposure = mean energy intensity 2016-2019 (excludes COVID years 2020-21, when collapsed revenue inflated energy intensity)
pre = panel[panel.fyear.between(2016, 2019)]
exposure = pre.groupby("ric")["energy_intensity"].mean().rename("exposure")
panel = panel.merge(exposure, on="ric", how="left")
med = panel.drop_duplicates("ric")["exposure"].median()
panel["high_exposure"] = (panel["exposure"] > med).astype(float).where(panel["exposure"].notna())
panel.to_csv(f"{OUT}/panel_2016_2024.csv", index=False)

def n_firms(df): return df["ric"].nunique()
has_ci = panel.dropna(subset=["ln_ci"])
pre_ok = set(has_ci[has_ci.fyear <= 2021].ric); post_ok = set(has_ci[has_ci.fyear >= 2022].ric)
s_a = has_ci[has_ci.ric.isin(pre_ok & post_ok)]
s_b = s_a[s_a.exposure.notna()]
s_b_nf = s_b[~s_b.financial]
s_c = s_b_nf[s_b_nf.reported]
pre_c = set(s_c[s_c.fyear <= 2021].ric); post_c = set(s_c[s_c.fyear >= 2022].ric)
s_c = s_c[s_c.ric.isin(pre_c & post_c)]
yrs = s_b_nf.groupby("ric").fyear.nunique(); s_d = s_b_nf[s_b_nf.ric.isin(yrs[yrs == 9].index)]
yrs_c = s_c.groupby("ric").fyear.nunique(); s_e = s_c[s_c.ric.isin(yrs_c[yrs_c == 9].index)]

lines = [
 f"Constituents (31.12.2021): {panel.ric.nunique()}",
 f"A  carbon intensity in >=1 pre and >=1 post year: {n_firms(s_a)} firms, {len(s_a)} obs",
 f"B  A + energy exposure (2016-2019): {n_firms(s_b)} firms",
 f"B' B without banks/insurers (NACE 64-66): {n_firms(s_b_nf)} firms, {len(s_b_nf)} obs  <- MAIN SAMPLE",
 f"C  B' with reported emissions only: {n_firms(s_c)} firms, {len(s_c)} obs",
 f"D  B' balanced 2016-2024: {n_firms(s_d)} firms",
 f"E  C balanced 2016-2024: {n_firms(s_e)} firms",
 f"Exposure median: {med:.1f} (energy use per EUR m revenue, LSEG units)",
 f"High-exposure firms in B': {int(s_b_nf.drop_duplicates('ric').high_exposure.sum())}",
 "", "Obs per year in main sample B':", s_b_nf.groupby('fyear').ric.nunique().to_string(),
 "", "Top NACE 2-digit in B' (firms):", s_b_nf.drop_duplicates('ric').nace2.value_counts().head(12).to_string(),
 "", "Countries in B' (firms):", s_b_nf.drop_duplicates('ric').country.value_counts().to_string(),
]
open(f"{OUT}/sample_report.txt","w").write("\n".join(lines)); print("\n".join(lines))
