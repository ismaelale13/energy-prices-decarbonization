# Energy Prices and Corporate Decarbonization

Code for the Master's thesis *Energy Prices and Corporate Decarbonization* (Chair for Data Science in Business and Economics, University of Würzburg).

**Research question:** Did the 2022 energy price shock, triggered by Russia's invasion of Ukraine, accelerate decarbonization among energy-intensive European firms?

## Structure
```
src/                 data download and panel construction
notebooks/           data checks, EDA, main results, robustness
data/raw/eurostat    Eurostat PPI and gas imports (public)
data/raw/ons         ONS MM22 UK producer price indices (public)
data/raw/lseg        LSEG firm data (NOT included, licensed)
data/processed       generated panel (NOT included)
output/              tables and figures
DECISIONS.md         log of data and design decisions
```

## Reproduce
1. `pip install -r requirements.txt`
2. Firm data: requires LSEG Workspace access. Run `python src/download_lseg.py` (asks for an App Key).
3. Public data: `python src/download_eurostat.py`; download ONS MM22 (`mm22.csv`) into `data/raw/ons/`.
4. Build panel: `python src/build_panel.py` then `python src/add_ppi.py`.
5. Run the notebooks in order.

LSEG data cannot be redistributed under its licence and is therefore not part of this repository.
