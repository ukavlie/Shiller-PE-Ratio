"""Henter siste ie_data.xls fra shillerdata.com og skriver en ren CSV.

Nedlastingslenken har en ny filsti og en ny ver-parameter hver gang Shiller
oppdaterer filen, og gamle lenker returnerer gamle data uten feilmelding.
Skriptet finner derfor lenken på siden hver gang, og hopper over resten hvis
ver-verdien er uendret siden forrige kjoering.

Bruk:  python update_shiller.py [--force] [--out data]
Krever: pandas, requests, xlrd
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import requests

PAGE_URL = "https://shillerdata.com/"
HEADERS = {"User-Agent": "Mozilla/5.0 (shiller-updater)"}

# Kilden har flerlinjede overskrifter, så navnene settes manuelt etter posisjon.
COLUMNS = [
    "DROP", "SP", "Dividends", "Earnings", "CPI", "Date", "GS10",
    "Real Price", "Real Dividends", "Real Total Return", "Real Earnings",
    "Real TR Scaled Earnings", "CAPE", "DROP", "TR CAPE", "DROP",
    "Excess CAPE Yield", "Monthly Total Bond Returns", "Real Total Bond Returns",
    "10 Year Annualized Stock Returns", "10 Year Annualized Bond Returns",
    "Real 10 Year Excess Annualized Returns",
]


def find_download_url() -> tuple[str, str]:
    """Returnerer (url, ver) for ie_data.xls slik den star paa siden naa."""
    html = requests.get(PAGE_URL, headers=HEADERS, timeout=60).text
    m = re.search(r'href="((?:https:)?//[^"]*?/ie_data\.xls\?ver=(\d+))"', html)
    if not m:
        raise RuntimeError("Fant ikke lenken til ie_data.xls paa siden. Sjekk sideoppsettet.")
    url = m.group(1)
    if url.startswith("//"):
        url = "https:" + url
    return url, m.group(2)


def frac_to_date(x: float) -> pd.Timestamp:
    """Kolonnen 'Date' er brokaar (1871.0417 = januar 1871)."""
    year = int(np.floor(x))
    month = min(int(np.floor((x - year) * 12)) + 1, 12)
    return pd.Timestamp(year=year, month=month, day=1)


def parse(content: bytes) -> tuple[pd.DataFrame, str]:
    # Unike navn paa plassholderne, ellers gir pandas dem navn som DROP.1 og beholder dem.
    names = [f"DROP{i}" if c == "DROP" else c for i, c in enumerate(COLUMNS)]
    df = pd.read_excel(BytesIO(content), sheet_name="Data", skiprows=8,
                       header=None, names=names)
    df = df.drop(columns=[c for c in df.columns if c.startswith("DROP")])
    df["Date"] = pd.to_numeric(df["Date"], errors="coerce")

    # Raden nederst inneholder en fotnote (f.eks. at siste maaned bare er en dagskurs).
    texts = df.loc[df["Date"].isna(), "SP"].dropna().astype(str)
    footnote = "; ".join(t for t in texts if not re.fullmatch(r"[\d.\s-]+", t))

    df = df.dropna(subset=["Date"]).copy()
    df["Date"] = df["Date"].apply(frac_to_date)
    for col in df.columns.drop("Date"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Provisional"] = False
    if footnote:
        df.loc[df.index[-1], "Provisional"] = True  # siste maaned er foreloepig
    return df.reset_index(drop=True), footnote


def validate(df: pd.DataFrame, previous_rows: int) -> None:
    """Stopper heller enn å publisere feil hvis kilden endrer layout."""
    assert df["Date"].is_unique, "Duplikate datoer"
    assert df["Date"].is_monotonic_increasing, "Datoer er ikke sortert"
    assert len(df) >= 1800, f"For faa rader ({len(df)})"
    assert len(df) >= previous_rows, "Faerre rader enn forrige versjon"
    assert df["CAPE"].notna().sum() > 1500, "CAPE ser ut til aa vaere feilplassert"
    assert df["SP"].dropna().iloc[-1] > 100, "SP ser ut til aa vaere feilplassert"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}

    url, ver = find_download_url()
    if meta.get("ver") == ver and not args.force:
        print(f"Ingen ny versjon (ver={ver}).")
        return 0

    resp = requests.get(url, headers=HEADERS, timeout=180)
    resp.raise_for_status()
    df, footnote = parse(resp.content)
    validate(df, previous_rows=meta.get("rows", 0))

    df.to_csv(out / "shiller_cape.csv", index=False, date_format="%Y-%m-%d")
    meta = {
        "ver": ver,
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rows": int(len(df)),
        "first_date": df["Date"].min().strftime("%Y-%m-%d"),
        "last_date": df["Date"].max().strftime("%Y-%m-%d"),
        "footnote": footnote,
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"Oppdatert: {meta['rows']} rader, siste maaned {meta['last_date']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
