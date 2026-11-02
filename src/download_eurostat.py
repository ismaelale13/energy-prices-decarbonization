"""
Download the Eurostat data needed for the thesis.

    1. sts_inpp_a  - Producer prices in industry (PPI), annual, by NACE sector and country
                     -> used to deflate firm revenue (H2: real revenue, real carbon intensity)
    2. nrg_ti_gas  - Imports of natural gas by partner country, annual
                     -> share of Russian gas in each country's imports in 2021 (robustness)

Usage (on your own computer):
    pip install eurostat pandas
    python get_eurostat.py

Output (in the same folder):
    raw_sts_inpp_a.csv, raw_nrg_ti_gas.csv      untouched raw downloads
    ppi_nace_country_2016_2024.csv              filtered PPI panel
    russian_gas_share_2021.csv                  Russian share of gas imports by country
    codes_overview.txt                          dimension codes found (send this to Claude)
"""

import os
import eurostat
import pandas as pd

YEARS = [str(y) for y in range(2016, 2026)]  # 2016-2025 (2025 kept if available)


def year_cols(df):
    return [c for c in df.columns if str(c)[:4].isdigit()]


def describe(df, name, f):
    f.write(f"=== {name} ===\n")
    for col in df.columns:
        if col in year_cols(df):
            continue
        vals = sorted(df[col].dropna().astype(str).unique())
        f.write(f"{col} ({len(vals)}): {vals[:60]}{' ...' if len(vals) > 60 else ''}\n")
    f.write(f"years: {year_cols(df)}\n\n")


def tidy(df, id_cols):
    ycols = [c for c in year_cols(df) if str(c)[:4] in YEARS]
    long = df.melt(id_vars=id_cols, value_vars=ycols, var_name="year", value_name="value")
    long["year"] = long["year"].astype(str).str[:4].astype(int)
    return long.dropna(subset=["value"])


def main():
    os.makedirs("data/raw/eurostat", exist_ok=True); os.chdir("data/raw/eurostat")
    # ---------- 1. PPI ----------
    print("Downloading sts_inpp_a ...")
    ppi = eurostat.get_data_df("sts_inpp_a")
    ppi.columns = [str(c).replace("\\TIME_PERIOD", "") for c in ppi.columns]
    ppi.to_csv("raw_sts_inpp_a.csv", index=False)

    id_cols = [c for c in ppi.columns if c not in year_cols(ppi)]
    p = ppi.copy()
    # keep producer price index (not growth rates); keep a single index base if several exist
    if "indic_bt" in p.columns:
        p = p[p["indic_bt"].astype(str).str.upper().str.contains("PRC_PRR|PRC_PRR_DOM|PRIX|PRC", regex=True)]
    if "unit" in p.columns:
        idx_units = [u for u in p["unit"].unique() if str(u).startswith("I")]  # e.g. I15, I21
        if idx_units:
            p = p[p["unit"] == sorted(idx_units)[-1]]  # most recent base year
    ppi_long = tidy(p, id_cols)
    ppi_long.to_csv("ppi_nace_country_2016_2024.csv", index=False)
    print(f"  PPI rows: {len(ppi_long)}")

    # ---------- 2. Gas imports ----------
    print("Downloading nrg_ti_gas ...")
    gas = eurostat.get_data_df("nrg_ti_gas")
    gas.columns = [str(c).replace("\\TIME_PERIOD", "") for c in gas.columns]
    gas.to_csv("raw_nrg_ti_gas.csv", index=False)

    g_id = [c for c in gas.columns if c not in year_cols(gas)]
    g = tidy(gas, g_id)
    g = g[g["year"] == 2021]
    if "siec" in g.columns:
        g = g[g["siec"] == "G3000"]  # natural gas
    if "unit" in g.columns and g["unit"].nunique() > 1:
        g = g[g["unit"] == sorted(g["unit"].unique())[0]]
    geo = "geo" if "geo" in g.columns else [c for c in g_id if "geo" in c.lower()][0]
    total = g[g["partner"] == "TOTAL"].set_index(geo)["value"]
    russia = g[g["partner"] == "RU"].set_index(geo)["value"]
    share = (russia / total).rename("russian_gas_share_2021").reset_index()
    share.to_csv("russian_gas_share_2021.csv", index=False)
    print(f"  Countries with Russian gas share: {share['russian_gas_share_2021'].notna().sum()}")

    # ---------- overview ----------
    with open("codes_overview.txt", "w", encoding="utf-8") as f:
        describe(ppi, "sts_inpp_a", f)
        describe(gas, "nrg_ti_gas", f)
    print("Done. Please send codes_overview.txt (and the CSVs) back to Claude.")


if __name__ == "__main__":
    main()
