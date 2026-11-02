"""Add sector PPI (Eurostat; ONS for UK) and real-revenue variables for H2."""
import sys, numpy as np, pandas as pd
CLEAN, RAW = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("data/processed", "data/raw")
p = pd.read_csv(f"{CLEAN}/panel_2016_2024.csv", dtype={"nace2": str, "nace4": str})

# Eurostat PPI (2021=100), NACE 2-digit codes like C20, B08, D35
eu = pd.read_csv(f"{RAW}/eurostat/ppi_nace_country_2016_2024.csv")
eu = eu[eu.nace_r2.str.fullmatch(r"[B-E]\d{2}")].copy()
eu["nace2"] = eu.nace_r2.str[1:]
eu = eu.rename(columns={"year": "fyear", "value": "ppi"})[["geo", "nace2", "fyear", "ppi"]]

# ONS MM22: domestic output PPI by SIC07 2-digit (2015=100) -> rebase 2021=100
t = pd.read_csv(f"{RAW}/ons/mm22.csv", header=None, low_memory=False)
titles = t.iloc[0].astype(str)
ann = t[t[0].astype(str).str.fullmatch(r"\d{4}")].set_index(0)
rows = []
for i, x in titles.items():
    m = pd.Series([x]).str.extract(r"PPI INDEX OUTPUT DOMESTIC - ([BC])(\d{2}) ")
    if m.notna().all(axis=None) and "including" not in x:
        s = pd.to_numeric(ann[i], errors="coerce")
        s = s / s.loc["2021"] * 100
        for y in range(2016, 2025):
            rows.append({"geo": "UK", "nace2": m.iloc[0, 1], "fyear": y, "ppi": s.loc[str(y)]})
uk = pd.DataFrame(rows).drop_duplicates(["nace2", "fyear"])
ppi = pd.concat([eu, uk])

cmap = {"Austria":"AT","Belgium":"BE","Cyprus":"CY","Czech Republic":"CZ","Denmark":"DK","Finland":"FI","France":"FR",
        "Germany":"DE","Greece":"EL","Hungary":"HU","Ireland":"IE","Italy":"IT","Luxembourg":"LU","Netherlands":"NL",
        "Norway":"NO","Poland":"PL","Portugal":"PT","Spain":"ES","Sweden":"SE","Switzerland":"CH","United Kingdom":"UK",
        "Jersey":"UK"}
p["geo"] = p.country.map(cmap)
p["industry"] = pd.to_numeric(p.nace2, errors="coerce").between(5, 39)

own = p.merge(ppi, on=["geo", "nace2", "fyear"], how="left")
eu27 = ppi[ppi.geo == "EU27_2020"].rename(columns={"ppi": "ppi_eu27"}).drop(columns="geo")
own = own.merge(eu27, on=["nace2", "fyear"], how="left")
own["ppi_source"] = np.where(own.ppi.notna(), "country", np.where(own.ppi_eu27.notna(), "EU27 fallback", "none"))
own["ppi"] = own.ppi.fillna(own.ppi_eu27)
own.loc[~own.industry, ["ppi", "ppi_source"]] = [np.nan, "service (no PPI)"]

own["real_revenue"] = own.revenue / (own.ppi / 100)
pos = (own.scope12_total > 0) & (own.real_revenue > 0)
own["ln_emissions"] = np.log(own.scope12_total.where(own.scope12_total > 0))
own["ln_real_revenue"] = np.log(own.real_revenue.where(own.real_revenue > 0))
own["ln_real_ci"] = np.where(pos, own.ln_emissions - own.ln_real_revenue, np.nan)
own = own.drop(columns="ppi_eu27")
own.to_csv(f"{CLEAN}/panel_2016_2024.csv", index=False)

h2 = own[own.industry & ~own.financial & own.exposure.notna() & own.ln_real_ci.notna()]
print("H2 sample firms:", h2.ric.nunique(), "obs:", len(h2))
print(h2.drop_duplicates("ric").ppi_source.value_counts().to_string())
print("UK firms in H2:", h2[h2.geo == "UK"].ric.nunique())
miss = own[own.industry & ~own.financial & own.exposure.notna() & own.ppi.isna() & own.revenue.notna()]
print("industrial firm-years without PPI:", len(miss), miss[["country", "nace2"]].drop_duplicates().head(10).to_string())
