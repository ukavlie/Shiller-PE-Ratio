"""Bygger docs/index.html og docs/fig_*.svg fra data/shiller_cape.csv og data/meta.json.

Figurene tegnes med matplotlib og Economist-stilen i economist_style.py.
SVG lagres med tekst som baner og uten tidsstempel, slik at filene bare endres
naar dataene endres.
Krever: pandas, numpy, matplotlib
"""
import json
from html import escape
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

import economist_style as es  # aktiverer rcParams ved import

matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "shiller-dashboard"

DATA = Path("data")
OUT = Path("docs")
FWD = "10 Year Annualized Stock Returns"
SOURCE = "Robert Shiller (shillerdata.com)"


def load() -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(DATA / "shiller_cape.csv", parse_dates=["Date"])
    meta = json.loads((DATA / "meta.json").read_text())
    return df, meta


def save(fig, name: str) -> None:
    fig.savefig(OUT / name, format="svg", metadata={"Date": None})
    plt.close(fig)


def fig_cape(cape: pd.DataFrame) -> None:
    last = cape.iloc[-1]
    mean = cape["CAPE"].mean()
    fig, ax = plt.subplots()
    ax.plot(cape["Date"], cape["CAPE"], color=es.ECONOMIST_BLUE, lw=1.6)
    ax.axhline(mean, color="#4D4D4D", ls="--", lw=1)
    ax.text(pd.Timestamp("1915-01-01"), mean + 0.6, f"Mean: {mean:.1f}", color="#4D4D4D", fontsize=9, va="bottom")
    ax.plot([last["Date"]], [last["CAPE"]], "o", ms=7, mew=2, mec=es.ECONOMIST_RED,
            mfc=es.ECONOMIST_BG if last["Provisional"] else es.ECONOMIST_RED, zorder=5)
    ax.annotate(f"{last['CAPE']:.1f}", xy=(last["Date"], last["CAPE"]), xytext=(9, 0),
                textcoords="offset points", color=es.ECONOMIST_RED, fontweight="bold", va="center")
    ax.set_xlim(cape["Date"].iloc[0], last["Date"] + pd.DateOffset(years=7))
    ax.set_ylim(0, None)
    ax.xaxis.set_major_locator(mdates.YearLocator(20))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    es.economist_title(ax, "Shiller CAPE ratio",
                       f"Cyclically adjusted price-to-earnings ratio, S&P Composite, {cape['Date'].iloc[0].year}-{last['Date'].year}",
                       SOURCE)
    fig.subplots_adjust(left=0.06, right=0.97, top=0.80, bottom=0.13)
    save(fig, "fig_cape.svg")


def fig_scatter(df: pd.DataFrame, now_cape: float) -> str:
    v = df.dropna(subset=["CAPE", FWD])
    x, y = v["CAPE"].to_numpy(), v[FWD].to_numpy() * 100
    slope, intercept = np.polyfit(np.log(x), y, 1)
    r2 = np.corrcoef(np.log(x), y)[0, 1] ** 2
    implied = slope * np.log(now_cape) + intercept
    grid = np.linspace(x.min(), max(x.max(), now_cape), 200)

    fig, ax = plt.subplots()
    ax.scatter(x, y, s=10, color=es.ECONOMIST_BLUE, alpha=0.30, linewidths=0)
    ax.plot(grid, slope * np.log(grid) + intercept, color=es.ECONOMIST_RED, lw=2)
    ax.axhline(0, color=es.ECONOMIST_DARK, lw=0.8)
    ax.axvline(now_cape, color="#4D4D4D", ls="--", lw=1)
    ax.plot([now_cape], [implied], "o", ms=7, color=es.ECONOMIST_RED, zorder=5)
    ax.annotate(f"CAPE now: {now_cape:.1f}", xy=(now_cape, ax.get_ylim()[1]), xytext=(-6, -4),
                textcoords="offset points", ha="right", va="top", color="#4D4D4D", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda t, _: f"{t:.0f}%"))
    ax.set_xlabel("CAPE at start of period")
    es.economist_title(ax, "CAPE and what followed",
                       f"Annualised real return on US equities over the next 10 years v CAPE at start, "
                       f"{v['Date'].iloc[0].year}-{v['Date'].iloc[-1].year}",
                       SOURCE, source_y=-0.20)
    fig.subplots_adjust(left=0.06, right=0.97, top=0.80, bottom=0.18)
    save(fig, "fig_scatter.svg")
    return (f"The fitted line (log CAPE, in-sample, n = {len(v):,}, R-squared = {r2:.2f}) implies {implied:.1f}% a year "
            "at today's CAPE. The observations use overlapping 10-year windows and are strongly autocorrelated, so the "
            "uncertainty is far larger than the line suggests. This is a descriptive relationship, not a forecast.")


def fig_excess(df: pd.DataFrame) -> None:
    v = df.dropna(subset=["Excess CAPE Yield"])
    fig, ax = plt.subplots()
    ax.plot(v["Date"], v["Excess CAPE Yield"] * 100, color=es.ECONOMIST_BLUE, lw=1.6)
    ax.axhline(0, color=es.ECONOMIST_DARK, lw=0.8)
    last = v.iloc[-1]
    ax.plot([last["Date"]], [last["Excess CAPE Yield"] * 100], "o", ms=7, mew=2, mec=es.ECONOMIST_RED,
            mfc=es.ECONOMIST_BG if last["Provisional"] else es.ECONOMIST_RED, zorder=5)
    ax.annotate(f"{last['Excess CAPE Yield'] * 100:.1f}", xy=(last["Date"], last["Excess CAPE Yield"] * 100),
                xytext=(9, 0), textcoords="offset points", color=es.ECONOMIST_RED, fontweight="bold", va="center")
    ax.set_xlim(v["Date"].iloc[0], last["Date"] + pd.DateOffset(years=7))
    ax.xaxis.set_major_locator(mdates.YearLocator(20))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    es.economist_title(ax, "Excess CAPE yield",
                       "Inverse of CAPE minus real 10-year bond yield, percentage points", SOURCE)
    fig.subplots_adjust(left=0.06, right=0.97, top=0.80, bottom=0.13)
    save(fig, "fig_excess.svg")


def kpi(label: str, value: str, sub: str = "") -> str:
    return (f'<div class="kpi"><div class="kl">{escape(label)}</div>'
            f'<div class="kv">{escape(value)}</div><div class="ks">{escape(sub)}</div></div>')


def main() -> None:
    df, meta = load()
    OUT.mkdir(exist_ok=True)
    cape = df.dropna(subset=["CAPE"]).reset_index(drop=True)
    last = cape.iloc[-1]
    now = float(last["CAPE"])
    pct_all = (cape["CAPE"] < now).mean() * 100
    pct_90 = (cape.loc[cape["Date"] >= "1990-01-01", "CAPE"] < now).mean() * 100
    month = last["Date"].strftime("%B %Y")
    prov = bool(last["Provisional"])

    fig_cape(cape)
    scatter_note = fig_scatter(df, now)
    fig_excess(df)

    warn = ""
    if prov:
        warn = (f'<p class="warn">The latest month is provisional. The source says: "{escape(meta.get("footnote", ""))}". '
                "The value will probably be revised in the next update.</p>")
    kpis = "".join([
        kpi("CAPE", f"{now:.1f}", month + (" (provisional)" if prov else "")),
        kpi("Percentile since 1881", f"{pct_all:.0f}", "share of months with a lower CAPE"),
        kpi("Percentile since 1990", f"{pct_90:.0f}", "share of months with a lower CAPE"),
        kpi("Mean / median", f"{cape['CAPE'].mean():.1f} / {cape['CAPE'].median():.1f}", "full sample"),
    ])
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shiller CAPE dashboard</title>
<style>
:root {{ --red:{es.ECONOMIST_RED}; --bg:{es.ECONOMIST_BG}; --fg:{es.ECONOMIST_DARK}; --muted:#4D4D4D; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font-family:Arial,"Helvetica Neue",Helvetica,"Liberation Sans",sans-serif; border-top:8px solid var(--red); }}
main {{ max-width:1000px; margin:0 auto; padding:24px 16px 48px; }}
h1 {{ font-size:1.6rem; margin:0 0 4px; }}
.sub {{ color:var(--muted); margin:0 0 20px; font-size:.95rem; }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-bottom:20px; }}
.kpi {{ border-top:3px solid var(--red); padding-top:6px; }}
.kl {{ font-size:.8rem; color:var(--muted); }} .kv {{ font-size:1.7rem; font-weight:700; }} .ks {{ font-size:.75rem; color:var(--muted); }}
.warn {{ border-left:4px solid var(--red); padding:6px 12px; font-size:.9rem; }}
img {{ width:100%; height:auto; display:block; margin:8px 0; }}
.note {{ font-size:.85rem; color:var(--muted); margin:0 0 24px; }}
footer {{ font-size:.8rem; color:var(--muted); margin-top:32px; border-top:1px solid #D4D4D4; padding-top:12px; }}
</style></head><body><main>
<h1>Shiller CAPE dashboard</h1>
<p class="sub">Data through {escape(month)}. Fetched {escape(meta["fetched_at"][:10])}. Updated automatically when Shiller publishes a new file.</p>
<div class="kpis">{kpis}</div>
{warn}
<img src="fig_cape.svg" alt="Line chart of the Shiller CAPE ratio since 1881 with the long-run mean and the latest value">
<img src="fig_scatter.svg" alt="Scatter plot of CAPE against the real return over the following ten years with a fitted line">
<p class="note">{escape(scatter_note)}</p>
<img src="fig_excess.svg" alt="Line chart of the excess CAPE yield since 1881">
<footer>Source: Robert J. Shiller, shillerdata.com. Prices are monthly averages of daily closes, except a provisional latest month.
No representation is made as to accuracy. Not investment advice.</footer>
</main></body></html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote docs/index.html and 3 SVGs. CAPE {now:.1f} ({month})")


if __name__ == "__main__":
    main()
