"""Download firm data from LSEG Workspace (requires LSEG access and an App Key).

Universe: STOXX Europe 600 constituents on 31 Dec 2021 (0#.STOXX(2021-12-31)).
Period: fiscal years 2015-2025, values in EUR.
Run from the repository root with LSEG Workspace open:
    python src/download_lseg.py
Output: data/raw/lseg/raw_*.csv  (NOT committed: LSEG licence forbids redistribution)
"""
import time, warnings
import getpass
from pathlib import Path
import pandas as pd
import lseg.data as ld
warnings.filterwarnings("ignore")

OUT = Path("data/raw/lseg"); OUT.mkdir(parents=True, exist_ok=True)
TS_FIELDS = {
    "scope1": "TR.CO2DirectScope1",
    "scope2": "TR.CO2IndirectScope2",
    "scope12_total": "TR.CO2EmissionTotal",
    "scope12_marketbased": "TR.CO2EquivalentEmissionsTotalMarketbased",
    "co2_estimation_method": "TR.CO2EstimationMethod",
    "energy_use_total": "TR.EnergyUseTotal",
    "energy_purchased": "TR.EnergyPurchasedDirect",
    "revenue": "TR.TotalRevenue",
    "total_assets": "TR.TotalAssetsReported",
}
STATIC = ["TR.CommonName", "TR.ISIN", "TR.HeadquartersCountry", "TR.TRBCIndustry", "TR.NACEClassification"]
# Wide window: LSEG filters financial data by filing date, so EDate must cover the year after the last FY.
PARAMS = {"SDate": "2015-01-01", "EDate": "2025-12-31", "Frq": "FY", "Curn": "EUR"}
CHUNK = 100


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def main():
    ld.open_session(app_key=getpass.getpass("LSEG App Key (hidden): ").strip())
    cons = ld.get_data(universe="0#.STOXX(2021-12-31)", fields=["TR.RIC"])
    rics = cons.iloc[:, 0].dropna().astype(str).unique().tolist()
    print(f"Firms: {len(rics)}")
    pd.concat([ld.get_data(universe=c, fields=STATIC) for c in chunks(rics, CHUNK)]).to_csv(OUT / "raw_static.csv", index=False)
    for name, code in TS_FIELDS.items():
        parts = []
        for c in chunks(rics, CHUNK):
            for _ in range(3):
                try:
                    parts.append(ld.get_data(universe=c, fields=[code, code + ".date"], parameters=PARAMS)); break
                except Exception as e:
                    print(f"  retry {name}: {str(e)[:80]}"); time.sleep(5)
        df = pd.concat(parts); df.columns = ["ric", "value", "date"]
        df["year"] = pd.to_datetime(df["date"], errors="coerce").dt.year
        df.to_csv(OUT / f"raw_{name}.csv", index=False)
        print(f"  {name}: {df.dropna(subset=['value']).ric.nunique()} firms")
    ld.close_session()


if __name__ == "__main__":
    main()
