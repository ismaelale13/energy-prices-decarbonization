"""
Run the full pipeline from the repository root:  python run_all.py

Steps
    1. LSEG download        (skipped if data/raw/lseg/ already holds the raw files)
    2. Eurostat download    (skipped: raw files are part of the repository)
    3. Build panel + PPI
    4. Export event studies + HonestDiD (R)
    5. Execute all notebooks (tables -> output/tables, figures -> output/figures)

R is located via the RSCRIPT environment variable, the PATH, or the default
Windows install folders.
"""

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

PY = sys.executable
NOTEBOOKS = ["02_data_checks", "03_eda", "04_h1", "05_h2", "06_robustness", "07_honestdid"]


def run(cmd):
    print("\n>>", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def find_rscript():
    if os.environ.get("RSCRIPT"):
        return os.environ["RSCRIPT"]
    if shutil.which("Rscript"):
        return shutil.which("Rscript")
    patterns = [
        r"C:\Program Files\R\R-*\bin\Rscript.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\R\R-*\bin\Rscript.exe"),
    ]
    hits = sorted(h for p in patterns for h in glob.glob(p))
    if hits:
        return hits[-1]
    sys.exit("Rscript not found. Install R 4.2+ or set the RSCRIPT environment variable to Rscript's full path.")


def main():
    if not list(Path("data/raw/lseg").glob("raw_*.csv")):
        run([PY, "src/download_lseg.py"])
    else:
        print("LSEG raw files found -> download skipped")

    run([PY, "src/build_panel.py"])
    run([PY, "src/add_ppi.py"])

    run([PY, "src/export_event_study.py"])
    run([find_rscript(), "src/honestdid.R"])

    for nb in NOTEBOOKS:
        run([PY, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", f"notebooks/{nb}.ipynb"])

    print("\nDone. Tables: output/tables/  Figures: output/figures/  Summary: RESULTS.md")


if __name__ == "__main__":
    main()
