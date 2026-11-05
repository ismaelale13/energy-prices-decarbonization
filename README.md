# Energy Prices and Corporate Decarbonization

Code for the Master's thesis *Energy Prices and Corporate Decarbonization* (Chair for Data Science in Business and Economics, University of Würzburg).

**Research question:** Did the 2022 energy price shock, triggered by Russia's invasion of Ukraine, accelerate decarbonization among energy-intensive European firms?

## Structure
```
src/                 data download, panel construction, HonestDiD export (Python) and analysis (R)
notebooks/           data checks, EDA, main results, robustness
data/raw/eurostat    Eurostat PPI and gas imports (public)
data/raw/ons         ONS MM22 UK producer price indices (public)
data/raw/lseg        LSEG firm data (NOT included, licensed)
data/processed       generated panel (NOT included)
output/              tables and figures
run_all.py           runs the full pipeline
DECISIONS.md         log of data and design decisions
RESULTS.md           summary of all results
```

## Reproduce

### Requirements
- Python 3.14 and R 4.6 (tested with Python 3.14.0, R 4.6.2, HonestDiD 0.2.8; R only for the sensitivity analysis)
- LSEG Workspace (desktop app, logged in) with an App Key, for the firm data
- Eurostat and ONS data are public and already included in `data/raw/`

### Step by step
1. Clone the repository and open a terminal in its root folder.
2. Create a virtual environment and install the packages:
   ```
   python -m venv .venv
   .venv\Scripts\activate          # Windows   (macOS/Linux: source .venv/bin/activate)
   pip install -r requirements.txt
   ```
3. Create an LSEG App Key: in LSEG Workspace search "APPKEY", register a new key and copy it.
4. Keep LSEG Workspace open and run the whole pipeline:
   ```
   python run_all.py
   ```
   It asks for the App Key once, downloads the firm data (several minutes), builds the panel,
   runs the HonestDiD analysis in R and executes all notebooks.
   If `Rscript` is not found, set its path first, e.g. on Windows:
   `$env:RSCRIPT = "C:\Program Files\R\R-4.x.x\bin\Rscript.exe"`

### Individual steps (what `run_all.py` does)
| Step | Command | Output |
|---|---|---|
| Firm data (LSEG) | `python src/download_lseg.py` | `data/raw/lseg/` |
| Public data (optional re-download) | `python src/download_eurostat.py`; ONS MM22 from https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/producerpriceindex | `data/raw/eurostat/`, `data/raw/ons/` |
| Panel | `python src/build_panel.py`, `python src/add_ppi.py` | `data/processed/` |
| HonestDiD | `python src/export_event_study.py`, `Rscript src/honestdid.R` | `output/honestdid/`, `output/tables/` |
| Analysis | notebooks `02_data_checks` -> `07_honestdid` | `output/tables/`, `output/figures/` |

### Notes on replication
- The firm data were downloaded on 2 November 2026. LSEG occasionally revises historical ESG and
  financial values, so a new download can produce slightly different numbers.
- The notebooks are stored with their outputs, so all results can be read on GitHub without running anything.
- Constituents are fixed to the STOXX Europe 600 on 31 December 2021 (`0#.STOXX(2021-12-31)`).

All tables are written to `output/tables/`, all figures to `output/figures/`. Key results are summarised in `RESULTS.md`; data and design decisions in `DECISIONS.md`.

LSEG data cannot be redistributed under its licence and is therefore not part of this repository.
