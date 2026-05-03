"""
figures.py — read results/*.csv, write figures/*.pdf.

Each figure corresponds to one row of the deliverables table in
EXPERIMENTS_PLAN.md §5:
    Fig 5 ← exp_3_1.csv  (asymptotic curves)
    Fig 6 ← exp_3_2.csv  (crossover)
    Fig 7 ← exp_3_3.csv  (memory cliff)
    Fig 8 ← exp_3_6.csv  (Warmup_v3 vs Simple — headline)
Plus a Table 3 LaTeX snippet from exp_3_4.csv (real-world graphs).
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # noqa: E402
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def _fit_loglog_slope(xs: list[float], ys: list[float]) -> tuple[float, float]:
    if len(xs) < 2:
        return float("nan"), float("nan")
    lx = np.log(xs)
    ly = np.log(ys)
    slope, intercept = np.polyfit(lx, ly, 1)
    return float(slope), float(intercept)


# ---------------------------------------------------------------------------
# Figure 5 — asymptotic curves on ER (§3.1)
# ---------------------------------------------------------------------------

def figure_5() -> None:
    rows = _read_csv(RESULTS / "exp_3_1.csv")
    if not rows:
        print("[fig5] no exp_3_1.csv yet, skipping")
        return
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    by_key: dict[tuple[str, str], list[tuple[float, float]]] = {}
    for r in rows:
        if r["status"] != "ok":
            continue
        key = (r["algorithm"], r["gamma"])
        by_key.setdefault(key, []).append((float(r["n"]), float(r["median_us_per_op"])))
    legend_lines = []
    for (algo, gamma), pts in sorted(by_key.items()):
        pts.sort()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        slope, _ = _fit_loglog_slope(xs, ys)
        label = f"{algo} γ={gamma}  slope={slope:.2f}"
        ax.loglog(xs, ys, marker="o", label=label)
        legend_lines.append(label)
    ax.set_xlabel("n (number of vertices)")
    ax.set_ylabel("median µs / update")
    ax.set_title("Fig 5: per-update time vs n on Erdős–Rényi (m ≈ n^γ)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    out = FIGURES / "fig5_asymptotic_er.pdf"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    print(f"[fig5] wrote {out}")


# ---------------------------------------------------------------------------
# Figure 6 — crossover (§3.2)
# ---------------------------------------------------------------------------

def figure_6() -> None:
    rows = _read_csv(RESULTS / "exp_3_2.csv")
    if not rows:
        print("[fig6] no exp_3_2.csv yet, skipping")
        return
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    by_algo: dict[str, list[tuple[int, float]]] = {}
    for r in rows:
        if r["status"] != "ok":
            continue
        by_algo.setdefault(r["algorithm"], []).append(
            (int(r["K"]), float(r["total_s"]))
        )
    for algo, pts in sorted(by_algo.items()):
        pts.sort()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.loglog(xs, ys, marker="o", label=algo)
    # Crossover: smallest K where simple total < naive total.
    if "naive" in by_algo and "simple" in by_algo:
        n_dict = dict(by_algo["naive"])
        s_dict = dict(by_algo["simple"])
        common_K = sorted(set(n_dict) & set(s_dict))
        crossover_K = None
        for K in common_K:
            if s_dict[K] < n_dict[K]:
                crossover_K = K
                break
        if crossover_K is not None:
            ax.axvline(crossover_K, color="grey", linestyle="--", alpha=0.6,
                       label=f"crossover K* ≈ {crossover_K}")
    ax.set_xlabel("stream length K")
    ax.set_ylabel("total wall-clock seconds")
    ax.set_title("Fig 6: total time vs stream length, n=1000, γ=1.5")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    out = FIGURES / "fig6_crossover.pdf"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    print(f"[fig6] wrote {out}")


# ---------------------------------------------------------------------------
# Figure 7 — memory cliff (§3.3)
# ---------------------------------------------------------------------------

def figure_7() -> None:
    rows = _read_csv(RESULTS / "exp_3_3.csv")
    if not rows:
        print("[fig7] no exp_3_3.csv yet, skipping")
        return
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    by_algo: dict[str, list[tuple[int, float]]] = {}
    for r in rows:
        if r["status"] != "ok":
            continue
        peak = float(r["rss_peak_mb"])
        before = float(r["rss_before_mb"])
        delta = peak - before
        by_algo.setdefault(r["algorithm"], []).append(
            (int(r["n"]), max(delta, 0.1))
        )
    for algo, pts in sorted(by_algo.items()):
        pts.sort()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.loglog(xs, ys, marker="o", label=algo)
    ax.axhline(4096, color="red", linestyle="--", alpha=0.5, label="4 GB")
    ax.set_xlabel("n (number of vertices)")
    ax.set_ylabel("Δ peak RSS (MB)")
    ax.set_title("Fig 7: memory cost of W on ER (p=5/n)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    out = FIGURES / "fig7_memory.pdf"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    print(f"[fig7] wrote {out}")


# ---------------------------------------------------------------------------
# Figure 8 — Warmup_v3 vs Simple Wedge on planted-hub layered graphs (§3.6)
# ---------------------------------------------------------------------------

_ALGO_ORDER = ["simple", "layered_simple", "warmup_v3"]
_ALGO_LABEL = {
    "simple": "Simple Wedge (general 4-cycles)",
    "layered_simple": "Layered Simple Wedge (fair baseline)",
    "warmup_v3": "Warmup_v3 (paper §3)",
}
_ALGO_COLOR = {
    "simple": "#1f77b4",
    "layered_simple": "#2ca02c",
    "warmup_v3": "#d62728",
}


def figure_8() -> None:
    rows = _read_csv(RESULTS / "exp_3_6.csv")
    if not rows:
        print("[fig8] no exp_3_6.csv yet, skipping")
        return
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    by_algo: dict[str, list[tuple[int, float, float, float]]] = {}
    for r in rows:
        if r["status"] != "ok":
            continue
        by_algo.setdefault(r["algorithm"], []).append((
            int(r["n_per_layer"]),
            float(r["median_us_per_op"]),
            float(r["iqr_us"]),
            float(r.get("build_s") or 0.0),
        ))
    for algo in _ALGO_ORDER:
        if algo not in by_algo:
            continue
        pts = sorted(by_algo[algo])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        errs = [p[2] for p in pts]
        slope, _ = _fit_loglog_slope(xs, ys)
        label = f"{_ALGO_LABEL[algo]}  slope={slope:.2f}"
        ax.errorbar(
            xs, ys, yerr=errs, marker="o", capsize=3,
            color=_ALGO_COLOR[algo], label=label,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n_per_layer")
    ax.set_ylabel("median µs / update")
    ax.set_title(
        "Fig 8: per-update time on planted-hub layered graphs\n"
        "(k_hubs=5, hub_bias=0.75 D-only stream)",
        fontsize=10,
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="best")

    # Build cost annotation: warmup_v3's GEMM precompute is a hidden cost.
    if "warmup_v3" in by_algo and "simple" in by_algo:
        wv = sorted(by_algo["warmup_v3"])
        sw = sorted(by_algo["simple"])
        if wv and sw:
            n_max = wv[-1][0]
            wv_build = wv[-1][3]
            sw_build = sw[-1][3]
            ax.text(
                0.02, 0.02,
                f"Build cost at n_per={n_max}:  Simple {sw_build:.2f}s   "
                f"Warmup_v3 {wv_build:.2f}s   "
                f"(excluded from per-op timing)",
                transform=ax.transAxes, fontsize=7, alpha=0.7,
            )

    out = FIGURES / "fig8_warmup_vs_simple.pdf"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    print(f"[fig8] wrote {out}")


# ---------------------------------------------------------------------------
# Table 3 — real-world graphs (§3.4) as a LaTeX tabular
# ---------------------------------------------------------------------------

def _format_count(s: str) -> str:
    """Short scientific form for a big integer count (e.g. 36262229 -> 3.63e7)."""
    try:
        n = int(s)
    except (ValueError, TypeError):
        return s
    if n < 1000:
        return str(n)
    exp = int(math.log10(n))
    mantissa = n / (10 ** exp)
    return f"$\\sci{{{mantissa:.2f}}}{{{exp}}}$"


def table_3() -> None:
    rows = _read_csv(RESULTS / "exp_3_4.csv")
    if not rows:
        print("[tab3] no exp_3_4.csv yet, skipping")
        return
    out = FIGURES / "tab3_realworld.tex"
    with out.open("w") as f:
        f.write("% Auto-generated by plots/figures.py — do not edit by hand.\n")
        # \sci macro is defined inline in the paper preamble.
        f.write("\\providecommand{\\sci}[2]{#1\\!\\cdot\\!10^{#2}}\n")
        f.write("\\begin{tabular}{lrrrrr}\n")
        f.write("\\toprule\n")
        f.write("graph & $n$ & $m$ & ops/s & RSS\\,MB & $\\#C_4$ \\\\\n")
        f.write("\\midrule\n")
        for r in rows:
            if r["status"] != "ok":
                f.write(
                    f"\\texttt{{{r['graph']}}} & -- & -- & -- & -- & {r['status']} \\\\\n"
                )
                continue
            count_str = _format_count(r["final_count"])
            try:
                tput = f"{int(float(r['throughput_ops_per_s'])):,}"
            except (ValueError, TypeError):
                tput = r["throughput_ops_per_s"]
            try:
                rss = f"{float(r['rss_peak_mb']):.0f}"
            except (ValueError, TypeError):
                rss = r["rss_peak_mb"]
            try:
                n_str = f"{int(r['n']):,}"
                m_str = f"{int(r['m']):,}"
            except (ValueError, TypeError):
                n_str, m_str = r["n"], r["m"]
            f.write(
                f"\\texttt{{{r['graph']}}} & {n_str} & {m_str} & "
                f"{tput} & {rss} & {count_str} \\\\\n"
            )
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
    print(f"[tab3] wrote {out}")


# ---------------------------------------------------------------------------
# Bonus: §3.6.1 robustness side-by-side
# ---------------------------------------------------------------------------

def figure_3_6_1() -> None:
    rows = _read_csv(RESULTS / "exp_3_6_1.csv")
    if not rows:
        print("[fig3.6.1] no exp_3_6_1.csv, skipping")
        return
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    by_algo: dict[str, list[tuple[float, float, float]]] = {}
    for r in rows:
        if r["status"] != "ok":
            continue
        x = float(r.get("m") or r.get("low_deg") or 0)
        by_algo.setdefault(r["algorithm"], []).append(
            (x, float(r["median_us_per_op"]), float(r.get("iqr_us") or 0))
        )
    for algo in _ALGO_ORDER:
        if algo not in by_algo:
            continue
        pts = sorted(by_algo[algo])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        errs = [p[2] for p in pts]
        ax.errorbar(xs, ys, yerr=errs, marker="o", capsize=3,
                    color=_ALGO_COLOR[algo], label=_ALGO_LABEL[algo])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("m (edges in initial graph)")
    ax.set_ylabel("median µs / update")
    ax.set_title(
        "Fig 8b: robustness on no-hub layered graphs\n"
        "(k_hubs=0, uniform-random D-stream — no class structure to exploit)",
        fontsize=10,
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="best")
    out = FIGURES / "fig8b_robustness_nohub.pdf"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    print(f"[fig3.6.1] wrote {out}")


def figure_3_6_2() -> None:
    """Bilateral hubs: where Warmup_v3 actually wins via HH lookup."""
    rows = _read_csv(RESULTS / "exp_3_6_2.csv")
    if not rows:
        print("[fig3.6.2] no exp_3_6_2.csv, skipping")
        return
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    by_algo: dict[str, list[tuple[int, float, float]]] = {}
    for r in rows:
        if r["status"] != "ok":
            continue
        by_algo.setdefault(r["algorithm"], []).append((
            int(r["n_per_layer"]),
            float(r["median_us_per_op"]),
            float(r.get("iqr_us") or 0),
        ))
    for algo in _ALGO_ORDER:
        if algo not in by_algo:
            continue
        pts = sorted(by_algo[algo])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        errs = [p[2] for p in pts]
        slope, _ = _fit_loglog_slope(xs, ys)
        label = f"{_ALGO_LABEL[algo]}  slope={slope:.2f}"
        ax.errorbar(xs, ys, yerr=errs, marker="o", capsize=3,
                    color=_ALGO_COLOR[algo], label=label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n_per_layer")
    ax.set_ylabel("median µs / update")
    ax.set_title(
        "Fig 8c: bilateral-hub graphs — HH-query regime\n"
        "(k_hubs=5 in BOTH L1 and L4, hub_bias=0.85)",
        fontsize=10,
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="best")
    out = FIGURES / "fig8c_bilateral.pdf"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    print(f"[fig3.6.2] wrote {out}")


def figure_3_7() -> None:
    rows = _read_csv(RESULTS / "exp_3_7.csv")
    if not rows:
        print("[fig3.7] no exp_3_7.csv, skipping")
        return
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    by_algo: dict[str, list[tuple[int, float]]] = {}
    for r in rows:
        if r["status"] != "ok":
            continue
        by_algo.setdefault(r["algorithm"], []).append(
            (int(r["k_hubs"]), float(r["median_us_per_op"]))
        )
    for algo, pts in sorted(by_algo.items()):
        pts.sort()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.plot(xs, ys, marker="o", label=algo)
    ax.set_yscale("log")
    ax.set_xlabel("k_hubs")
    ax.set_ylabel("median µs / update")
    ax.set_title("§3.7: per-update time vs k_hubs (n_per_layer=500)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    out = FIGURES / "fig9_khubs_sweep.pdf"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    print(f"[fig3.7] wrote {out}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true")
    args = p.parse_args()
    figure_5()
    figure_6()
    figure_7()
    figure_8()
    table_3()
    figure_3_6_1()
    figure_3_6_2()
    figure_3_7()


if __name__ == "__main__":
    main()
