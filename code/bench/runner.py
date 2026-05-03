"""
runner.py — experiment driver. Dispatch via:
    python -m bench.runner --experiment 3.1
    python -m bench.runner --experiment 3.6
    python -m bench.runner --experiment all

Each experiment writes a single CSV to results/. Plot generation lives in
plots/figures.py and reads those CSVs.
"""

from __future__ import annotations

import argparse
import csv
import gc
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from algorithms.layered_simple_wedge import LayeredSimpleWedgeCounter
from algorithms.naive_recompute import NaiveRecomputeCounter
from algorithms.simple_wedge import SimpleWedgeCounter
from algorithms.sparse_wedge import SparseWedgeCounter
from algorithms.warmup_v3 import WarmupV3Counter
from bench.memory import current_rss_mb, measure_build_memory
from graphs.adversarial import layered_hub
from graphs.generators import (
    barabasi_albert,
    erdos_renyi,
    erdos_renyi_density,
)
from graphs.streams import ClassChecker, hub_biased, insert_only

RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Hard ceiling per cell from EXPERIMENTS_PLAN.md §6.2.
CELL_TIMEOUT_S = 600.0


def _apply(counter, op, u, v, *, warmup_v3: bool) -> None:
    if warmup_v3:
        lp, a, b = counter._classify_edge(u, v)
        getattr(counter, op)(lp, a, b)
    else:
        getattr(counter, op)(u, v)


def _bulk_load(counter, edges, *, warmup_v3: bool) -> None:
    for u, v in edges:
        _apply(counter, "insert", u, v, warmup_v3=warmup_v3)


def time_stream(counter, ops, *, warmup_v3: bool = False, call_count: bool = True) -> float:
    """Time a sequence of updates. By default `count()` is called after every
    update — required for Naive (work is in count()) and harmless overhead
    for the maintained counters (a single attribute read).
    """
    start = time.perf_counter()
    if call_count:
        for op, u, v in ops:
            _apply(counter, op, u, v, warmup_v3=warmup_v3)
            counter.count()
    else:
        for op, u, v in ops:
            _apply(counter, op, u, v, warmup_v3=warmup_v3)
    return time.perf_counter() - start


def median_iqr(values: list[float]) -> tuple[float, float]:
    if not values:
        return float("nan"), float("nan")
    s = sorted(values)
    med = statistics.median(s)
    q1 = s[max(0, len(s) // 4)]
    q3 = s[min(len(s) - 1, (3 * len(s)) // 4)]
    return med, q3 - q1


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path} ({len(rows)} rows)")


# ---------------------------------------------------------------------------
# Experiment 3.1 — asymptotic curves on Erdős–Rényi
# ---------------------------------------------------------------------------

def experiment_3_1(n_seeds: int = 5, n_ops: int = 200) -> None:
    print("[3.1] asymptotic curves on ER")
    sizes = [200, 500, 1000, 2000, 5000]
    gammas = [1.3, 1.5, 1.7]
    rows = []
    for gamma in gammas:
        for n in sizes:
            for algo in ("naive", "simple"):
                if algo == "naive" and n >= 5000:
                    print(f"  skip naive at n={n} (out-of-budget; will TIMEOUT)")
                    rows.append(["3.1", algo, n, gamma, "", "", "", "", "TIMEOUT"])
                    continue
                per_op_us = []
                m_count = 0
                for seed in range(n_seeds):
                    n_g, edges = erdos_renyi_density(n, gamma, c=1.0, seed=seed)
                    half = len(edges) // 2
                    pre = edges[:half]
                    rest = edges[half:]
                    rng = np.random.default_rng(seed * 7 + 1)
                    rng.shuffle(rest)  # in-place, deterministic
                    stream_pairs = rest[:n_ops]
                    if len(stream_pairs) < n_ops:
                        # Top up with new random non-edges.
                        present = set((min(u, v), max(u, v)) for u, v in pre + list(stream_pairs))
                        extras = []
                        rng2 = np.random.default_rng(seed * 7 + 2)
                        attempts = 0
                        while len(extras) + len(stream_pairs) < n_ops and attempts < 10 * n_ops:
                            u, v = int(rng2.integers(0, n)), int(rng2.integers(0, n))
                            if u == v:
                                attempts += 1
                                continue
                            e = (min(u, v), max(u, v))
                            if e in present:
                                attempts += 1
                                continue
                            present.add(e)
                            extras.append(e)
                        stream_pairs = list(stream_pairs) + extras
                    if len(stream_pairs) < n_ops:
                        continue
                    ops = [("insert", u, v) for (u, v) in stream_pairs[:n_ops]]
                    m_count = len(pre) + n_ops

                    if algo == "naive":
                        c = NaiveRecomputeCounter(n)
                    else:
                        c = SimpleWedgeCounter(n)
                    _bulk_load(c, pre, warmup_v3=False)
                    t0 = time.perf_counter()
                    elapsed = time_stream(c, ops, warmup_v3=False)
                    if elapsed > CELL_TIMEOUT_S:
                        rows.append(["3.1", algo, n, gamma, m_count, seed, "", "", "TIMEOUT"])
                        per_op_us = []
                        break
                    per_op_us.append(elapsed * 1e6 / n_ops)
                    del c
                    gc.collect()

                if per_op_us:
                    med, iqr = median_iqr(per_op_us)
                    rows.append(
                        ["3.1", algo, n, gamma, m_count, n_seeds, f"{med:.3f}", f"{iqr:.3f}", "ok"]
                    )
                    print(f"  {algo:>6s} n={n:>5d} γ={gamma} m≈{m_count:>7d} {med:>9.2f} µs/op ± {iqr:.2f}")

    write_csv(
        RESULTS_DIR / "exp_3_1.csv",
        ["experiment", "algorithm", "n", "gamma", "m", "n_seeds", "median_us_per_op", "iqr_us", "status"],
        rows,
    )


# ---------------------------------------------------------------------------
# Experiment 3.2 — crossover: naive vs simple over stream lengths
# ---------------------------------------------------------------------------

def experiment_3_2(n_seeds: int = 3) -> None:
    print("[3.2] crossover naive vs simple")
    n = 1000
    gamma = 1.5
    Ks = [1, 10, 100, 1000, 10000, 100000]
    rows = []
    # Predicted timeouts based on naive ~9 ms/op at n=1000 γ=1.5; K=100000
    # would take ~15 min, over the 10-min cell ceiling.
    for K in Ks:
        for algo in ("naive", "simple"):
            if algo == "naive" and K >= 100000:
                rows.append(["3.2", algo, n, gamma, "", K, n_seeds, "", "", "", "TIMEOUT_PREDICTED"])
                continue
            totals = []
            m_count = 0
            for seed in range(n_seeds):
                _, edges = erdos_renyi_density(n, gamma, c=1.0, seed=seed)
                half = len(edges) // 2
                pre = edges[:half]
                rest = edges[half:]
                rng = np.random.default_rng(seed)
                rng.shuffle(rest)
                stream = rest[:K]
                if len(stream) < K:
                    present = set(pre) | set(stream)
                    extra_seed = seed * 31
                    rng2 = np.random.default_rng(extra_seed)
                    while len(stream) < K:
                        u, v = int(rng2.integers(0, n)), int(rng2.integers(0, n))
                        if u == v:
                            continue
                        e = (min(u, v), max(u, v))
                        if e in present:
                            continue
                        present.add(e)
                        stream.append(e)
                ops = [("insert", u, v) for (u, v) in stream]
                m_count = len(pre) + K

                if algo == "naive":
                    c = NaiveRecomputeCounter(n)
                else:
                    c = SimpleWedgeCounter(n)
                t0 = time.perf_counter()
                _bulk_load(c, pre, warmup_v3=False)
                t_build = time.perf_counter() - t0
                if t_build > CELL_TIMEOUT_S:
                    totals = []
                    break
                t1 = time.perf_counter()
                t_stream = time_stream(c, ops, warmup_v3=False)
                if t_stream > CELL_TIMEOUT_S:
                    totals = []
                    break
                totals.append((t_build, t_stream, t_build + t_stream))
                del c
                gc.collect()
            if totals:
                meds = [
                    statistics.median(t[i] for t in totals) for i in range(3)
                ]
                rows.append(
                    [
                        "3.2", algo, n, gamma, m_count, K, n_seeds,
                        f"{meds[0]:.4f}", f"{meds[1]:.4f}", f"{meds[2]:.4f}", "ok",
                    ]
                )
                print(f"  {algo:>6s} K={K:>6d} build={meds[0]:.3f}s stream={meds[1]:.3f}s")
            else:
                rows.append(["3.2", algo, n, gamma, m_count, K, n_seeds, "", "", "", "TIMEOUT"])
    write_csv(
        RESULTS_DIR / "exp_3_2.csv",
        [
            "experiment", "algorithm", "n", "gamma", "m", "K", "n_seeds",
            "build_s", "stream_s", "total_s", "status",
        ],
        rows,
    )


# ---------------------------------------------------------------------------
# Experiment 3.3 — memory cliff: dense vs sparse W
# ---------------------------------------------------------------------------

def experiment_3_3() -> None:
    print("[3.3] memory cliff dense vs sparse")
    sizes = [1000, 2000, 5000, 10000, 20000, 50000]
    rows = []
    for n in sizes:
        p = 5.0 / n
        _, edges = erdos_renyi(n, p, seed=0)
        m = len(edges)
        for algo in ("simple", "sparse"):
            print(f"  {algo:>6s} n={n:>5d} m={m}", flush=True)
            try:
                if algo == "simple":
                    # Refuse predictively when dense W would not fit.
                    bytes_needed = n * n * 4
                    if bytes_needed > 8 * 1024**3:  # > 8 GB
                        print(f"    skip (dense W = {bytes_needed/1024**3:.1f} GB)")
                        rows.append(["3.3", algo, n, m, "", "", "OOM_PREDICTED"])
                        continue

                    def build():
                        c = SimpleWedgeCounter(n)
                        _bulk_load(c, edges, warmup_v3=False)
                        return c
                else:
                    def build():
                        c = SparseWedgeCounter(n)
                        _bulk_load(c, edges, warmup_v3=False)
                        return c

                t0 = time.perf_counter()
                before, peak, c = measure_build_memory(build)
                t_build = time.perf_counter() - t0
                if t_build > CELL_TIMEOUT_S:
                    rows.append(["3.3", algo, n, m, f"{before:.1f}", f"{peak:.1f}", "TIMEOUT"])
                    del c
                    gc.collect()
                    continue
                rows.append(
                    ["3.3", algo, n, m, f"{before:.1f}", f"{peak:.1f}", "ok"]
                )
                print(f"    rss {before:.0f} → {peak:.0f} MB, build {t_build:.1f}s")
                del c
                gc.collect()
            except MemoryError:
                rows.append(["3.3", algo, n, m, "", "", "OOM"])
                print(f"    MemoryError")
    write_csv(
        RESULTS_DIR / "exp_3_3.csv",
        ["experiment", "algorithm", "n", "m", "rss_before_mb", "rss_peak_mb", "status"],
        rows,
    )


# ---------------------------------------------------------------------------
# Experiment 3.4 — real-world graphs (sparse wedge only)
# ---------------------------------------------------------------------------

def experiment_3_4() -> None:
    print("[3.4] real-world graphs")
    from graphs.snap_loader import load_snap_graph

    datasets = [
        ("ca-GrQc", "ca-GrQc.txt.gz"),
        ("ca-HepTh", "ca-HepTh.txt.gz"),
        ("email-Enron", "email-Enron.txt.gz"),
    ]
    rows = []
    for name, fname in datasets:
        print(f"  {name}", flush=True)
        try:
            n, edges = load_snap_graph(fname)
        except FileNotFoundError as e:
            print(f"    not downloaded yet: {e}")
            rows.append(["3.4", name, "", "", "", "", "", "", "MISSING"])
            continue
        m = len(edges)
        # Hold out 10% for stream.
        rng = np.random.default_rng(0)
        idx = np.arange(m)
        rng.shuffle(idx)
        cut = int(0.9 * m)
        pre = [edges[i] for i in idx[:cut]]
        held = [edges[i] for i in idx[cut:]]
        try:
            t0 = time.perf_counter()
            c = SparseWedgeCounter(n)
            _bulk_load(c, pre, warmup_v3=False)
            t_build = time.perf_counter() - t0
            before = current_rss_mb()
            t1 = time.perf_counter()
            for u, v in held:
                c.insert(u, v)
            t_stream = time.perf_counter() - t1
            peak = current_rss_mb()
            count = c.count()
            ops_per_s = len(held) / t_stream if t_stream > 0 else float("nan")
            rows.append(
                ["3.4", name, n, m, len(held), f"{t_build:.2f}", f"{t_stream:.3f}",
                 f"{ops_per_s:.0f}", f"{peak:.1f}", count, "ok"]
            )
            print(f"    n={n}, m={m}, throughput={ops_per_s:.0f} op/s, peak={peak:.1f} MB, count={count}")
            del c
            gc.collect()
        except MemoryError:
            rows.append(["3.4", name, n, m, "", "", "", "", "", "", "OOM"])
            print(f"    OOM")
    write_csv(
        RESULTS_DIR / "exp_3_4.csv",
        [
            "experiment", "graph", "n", "m", "stream_len",
            "build_s", "stream_s", "throughput_ops_per_s", "rss_peak_mb",
            "final_count", "status",
        ],
        rows,
    )


# ---------------------------------------------------------------------------
# Experiment 3.5 — swapped-order divergence
# ---------------------------------------------------------------------------

def experiment_3_5() -> None:
    print("[3.5] swapped-order divergence")
    from algorithms.brute_force import BruteForceCounter

    n = 30
    p = 0.3
    rows = []
    for seed in range(20):
        _, edges = erdos_renyi(n, p, seed=seed)
        bf = BruteForceCounter(n)
        sw = SimpleWedgeCounter(n, ordering="swapped")
        for u, v in edges:
            bf.insert(u, v)
            sw.insert(u, v)
        diverge_step = -1
        rng = np.random.default_rng(seed)
        present = set(edges)
        for step in range(50):
            if present and rng.random() < 0.4:
                e = list(present)[int(rng.integers(0, len(present)))]
                bf.delete(*e)
                sw.delete(*e)
                present.discard(e)
            else:
                while True:
                    u, v = int(rng.integers(0, n)), int(rng.integers(0, n))
                    if u == v:
                        continue
                    e = (min(u, v), max(u, v))
                    if e in present:
                        continue
                    bf.insert(*e)
                    sw.insert(*e)
                    present.add(e)
                    break
            if sw.count() != bf.count() and diverge_step < 0:
                diverge_step = step
        rows.append(["3.5", seed, diverge_step, sw.count(), bf.count()])
    diverge_indices = [r[2] for r in rows if r[2] >= 0]
    print(
        f"  swapped diverged in {len(diverge_indices)}/20 seeds; "
        f"median first-divergence step = {statistics.median(diverge_indices) if diverge_indices else 'n/a'}"
    )
    write_csv(
        RESULTS_DIR / "exp_3_5.csv",
        ["experiment", "seed", "first_divergence_step", "swapped_count", "true_count"],
        rows,
    )


# ---------------------------------------------------------------------------
# Experiment 3.6 — Warmup_v3 vs Simple Wedge on planted-hub graphs
# ---------------------------------------------------------------------------

def _build_simple(g):
    c = SimpleWedgeCounter(g.n)
    _bulk_load(c, g.edges, warmup_v3=False)
    return c, False, False


def _build_layered_simple(g):
    return LayeredSimpleWedgeCounter.from_layered_graph(g), False, False


def _build_warmup_v3(g):
    return WarmupV3Counter.from_layered_graph(g), True, False


_THREE_BUILDERS: dict[str, callable] = {
    "simple": _build_simple,
    "layered_simple": _build_layered_simple,
    "warmup_v3": _build_warmup_v3,
}


def experiment_3_6(n_seeds: int = 3, n_ops: int = 200) -> None:
    print("[3.6] HEADLINE — Simple / LayeredSimple / Warmup_v3 on planted-hub layered graphs")
    sizes = [200, 500, 1000, 2000]
    k_hubs = 5
    hub_bias = 0.75
    rows = []
    for n_per in sizes:
        for algo, builder in _THREE_BUILDERS.items():
            per_op_us = []
            build_s = []
            ms = []
            for seed in range(n_seeds):
                g = layered_hub(
                    n_per_layer=n_per, k_hubs=k_hubs, low_deg=5,
                    hub_density=0.5, seed=seed,
                )
                checker = ClassChecker(
                    g.classes, g.class_bounds, g.initial_degrees()
                )
                D_pool = [
                    (u, v) for u, v in g.edge_pool
                    if {g.layer_of(u), g.layer_of(v)} == {0, 3}
                ]
                ops = hub_biased(
                    g.n, g.edges, g.hubs, n_ops=n_ops,
                    hub_bias=hub_bias, seed=seed * 17 + 1,
                    pool=D_pool, class_check=checker,
                )

                t_build_0 = time.perf_counter()
                c, is_warmup, _ = builder(g)
                t_build = time.perf_counter() - t_build_0
                if t_build > CELL_TIMEOUT_S:
                    print(f"    {algo} build TIMEOUT at n_per={n_per}")
                    per_op_us = []
                    break

                elapsed = time_stream(c, ops, warmup_v3=is_warmup)
                if elapsed > CELL_TIMEOUT_S:
                    print(f"    {algo} stream TIMEOUT at n_per={n_per}")
                    per_op_us = []
                    break
                per_op_us.append(elapsed * 1e6 / n_ops)
                build_s.append(t_build)
                ms.append(len(g.edges) + n_ops)
                del c
                gc.collect()

            if per_op_us:
                med, iqr = median_iqr(per_op_us)
                med_build = statistics.median(build_s)
                rows.append(
                    ["3.6", algo, n_per, k_hubs, hub_bias, n_ops,
                     int(np.median(ms)), n_seeds, f"{med:.3f}", f"{iqr:.3f}",
                     f"{med_build:.3f}", "ok"]
                )
                print(f"  {algo:>15s} n_per={n_per:>5d} {med:>9.2f} µs/op ± {iqr:>5.2f} | build {med_build:>6.2f}s")
            else:
                rows.append(["3.6", algo, n_per, k_hubs, hub_bias, n_ops,
                             "", "", "", "", "", "TIMEOUT"])
    write_csv(
        RESULTS_DIR / "exp_3_6.csv",
        [
            "experiment", "algorithm", "n_per_layer", "k_hubs", "hub_bias",
            "n_ops", "m", "n_seeds", "median_us_per_op", "iqr_us",
            "build_s", "status",
        ],
        rows,
    )


# ---------------------------------------------------------------------------
# Experiment 3.6.1 — Robustness on ER (no hubs)
# ---------------------------------------------------------------------------

def experiment_3_6_1(n_seeds: int = 3, n_ops: int = 200) -> None:
    """Robustness check on no-hub layered graphs.

    All three counters run on the SAME graphs and SAME stream. Stream is
    uniformly random (no hub bias). The plan predicted Simple Wedge would
    win here because Warmup_v3's machinery has overhead with no hubs to
    exploit. With the FAIR baseline (LayeredSimpleWedge), this prediction
    holds.
    """
    print("[3.6.1] robustness on no-hub layered graphs — Simple / LayeredSimple / Warmup_v3")
    n_per = 250
    densities = [3, 7, 15]
    rows = []
    for low_deg in densities:
        per_algo: dict[str, list[float]] = {k: [] for k in _THREE_BUILDERS}
        build_per_algo: dict[str, list[float]] = {k: [] for k in _THREE_BUILDERS}
        m_avg = 0
        for seed in range(n_seeds):
            g = layered_hub(
                n_per_layer=n_per, k_hubs=0, low_deg=low_deg,
                hub_density=0.0, seed=seed,
            )
            checker = ClassChecker(g.classes, g.class_bounds, g.initial_degrees())
            D_pool = [
                (u, v) for u, v in g.edge_pool
                if {g.layer_of(u), g.layer_of(v)} == {0, 3}
            ]
            ops = hub_biased(
                g.n, g.edges, g.hubs, n_ops=n_ops, hub_bias=0.0,
                seed=seed * 17 + 5, pool=D_pool, class_check=checker,
            )
            m_avg = len(g.edges)

            for algo, builder in _THREE_BUILDERS.items():
                t_build_0 = time.perf_counter()
                c, is_warmup, _ = builder(g)
                t_build = time.perf_counter() - t_build_0

                t = time_stream(c, ops, warmup_v3=is_warmup)
                per_algo[algo].append(t * 1e6 / n_ops)
                build_per_algo[algo].append(t_build)
                del c
                gc.collect()

        for algo in _THREE_BUILDERS:
            med, iqr = median_iqr(per_algo[algo])
            med_build = statistics.median(build_per_algo[algo])
            rows.append([
                "3.6.1", algo, n_per, low_deg, m_avg, n_seeds,
                f"{med:.3f}", f"{iqr:.3f}", f"{med_build:.3f}", "ok",
            ])
            print(f"  {algo:>15s} low_deg={low_deg:>2d} m≈{m_avg:>5d} {med:>8.2f} µs/op ± {iqr:>5.2f} | build {med_build:>6.3f}s")
    write_csv(
        RESULTS_DIR / "exp_3_6_1.csv",
        ["experiment", "algorithm", "n_per_layer", "low_deg", "m", "n_seeds",
         "median_us_per_op", "iqr_us", "build_s", "status"],
        rows,
    )


# ---------------------------------------------------------------------------
# Experiment 3.6.2 — bilateral-hub graphs (HH-query regime)
# ---------------------------------------------------------------------------

def experiment_3_6_2(n_seeds: int = 3, n_ops: int = 200) -> None:
    """Bilateral-hub graphs: hubs in L1 AND L4. Stream is hub-biased D-only,
    so a large fraction of D-edge updates touch hubs on both sides — the HH
    query regime where Warmup_v3 has an O(1) lookup via precomputed ABC^HH
    while LayeredSimple still pays O(deg_C(L4 hub)) ≈ O(n).
    """
    print("[3.6.2] BILATERAL hubs — HH-query regime")
    sizes = [200, 500, 1000, 2000]
    k_hubs = 5
    hub_bias = 0.85
    rows = []
    for n_per in sizes:
        for algo, builder in _THREE_BUILDERS.items():
            per_op_us = []
            build_s = []
            ms = []
            for seed in range(n_seeds):
                g = layered_hub(
                    n_per_layer=n_per, k_hubs=k_hubs, k_hubs_l4=k_hubs,
                    low_deg=5, hub_density=0.5, seed=seed,
                )
                checker = ClassChecker(
                    g.classes, g.class_bounds, g.initial_degrees()
                )
                D_pool = [
                    (u, v) for u, v in g.edge_pool
                    if {g.layer_of(u), g.layer_of(v)} == {0, 3}
                ]
                ops = hub_biased(
                    g.n, g.edges, g.hubs, n_ops=n_ops,
                    hub_bias=hub_bias, seed=seed * 17 + 11,
                    pool=D_pool, class_check=checker,
                )

                t_build_0 = time.perf_counter()
                c, is_warmup, _ = builder(g)
                t_build = time.perf_counter() - t_build_0
                if t_build > CELL_TIMEOUT_S:
                    print(f"    {algo} build TIMEOUT at n_per={n_per}")
                    per_op_us = []
                    break

                elapsed = time_stream(c, ops, warmup_v3=is_warmup)
                if elapsed > CELL_TIMEOUT_S:
                    per_op_us = []
                    break
                per_op_us.append(elapsed * 1e6 / n_ops)
                build_s.append(t_build)
                ms.append(len(g.edges) + n_ops)
                del c
                gc.collect()

            if per_op_us:
                med, iqr = median_iqr(per_op_us)
                med_build = statistics.median(build_s)
                rows.append([
                    "3.6.2", algo, n_per, k_hubs, hub_bias, n_ops,
                    int(np.median(ms)), n_seeds, f"{med:.3f}",
                    f"{iqr:.3f}", f"{med_build:.3f}", "ok",
                ])
                print(f"  {algo:>15s} n_per={n_per:>5d} {med:>9.2f} µs/op ± {iqr:>5.2f} | build {med_build:>6.2f}s")
            else:
                rows.append(["3.6.2", algo, n_per, k_hubs, hub_bias, n_ops,
                             "", "", "", "", "", "TIMEOUT"])
    write_csv(
        RESULTS_DIR / "exp_3_6_2.csv",
        [
            "experiment", "algorithm", "n_per_layer", "k_hubs", "hub_bias",
            "n_ops", "m", "n_seeds", "median_us_per_op", "iqr_us",
            "build_s", "status",
        ],
        rows,
    )


# ---------------------------------------------------------------------------
# Experiment 3.7 — k_hubs sweep (stretch)
# ---------------------------------------------------------------------------

def experiment_3_7(n_seeds: int = 2, n_ops: int = 200) -> None:
    print("[3.7] k_hubs sweep at fixed n_per_layer")
    n_per = 500
    k_hubs_values = [0, 1, 2, 5, 10, 20]
    hub_bias = 0.75
    rows = []
    for k in k_hubs_values:
        for algo in ("simple", "warmup_v3"):
            per_op_us = []
            for seed in range(n_seeds):
                g = layered_hub(
                    n_per_layer=n_per, k_hubs=max(1, k) if k > 0 else 0,
                    low_deg=5, hub_density=0.5 if k > 0 else 0.0,
                    seed=seed,
                )
                if k == 0:
                    g.hubs = set()
                checker = ClassChecker(g.classes, g.class_bounds, g.initial_degrees())
                D_pool = [
                    (u, v) for u, v in g.edge_pool
                    if {g.layer_of(u), g.layer_of(v)} == {0, 3}
                ]
                hubs_for_stream = g.hubs if k > 0 else set()
                ops = hub_biased(
                    g.n, g.edges, hubs_for_stream, n_ops=n_ops,
                    hub_bias=hub_bias if k > 0 else 0.0,
                    seed=seed * 17, pool=D_pool, class_check=checker,
                )
                if algo == "simple":
                    c = SimpleWedgeCounter(g.n)
                    _bulk_load(c, g.edges, warmup_v3=False)
                    is_w = False
                else:
                    c = WarmupV3Counter.from_layered_graph(g)
                    is_w = True
                t = time_stream(c, ops, warmup_v3=is_w)
                per_op_us.append(t * 1e6 / n_ops)
                del c
                gc.collect()
            if per_op_us:
                med, iqr = median_iqr(per_op_us)
                rows.append(["3.7", algo, n_per, k, hub_bias, n_seeds, f"{med:.3f}", f"{iqr:.3f}", "ok"])
                print(f"  {algo:>10s} k_hubs={k:>3d} {med:.2f} µs/op")
    write_csv(
        RESULTS_DIR / "exp_3_7.csv",
        ["experiment", "algorithm", "n_per_layer", "k_hubs", "hub_bias", "n_seeds",
         "median_us_per_op", "iqr_us", "status"],
        rows,
    )


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

EXPERIMENTS: dict[str, Callable[[], None]] = {
    "3.1": experiment_3_1,
    "3.2": experiment_3_2,
    "3.3": experiment_3_3,
    "3.4": experiment_3_4,
    "3.5": experiment_3_5,
    "3.6": experiment_3_6,
    "3.6.1": experiment_3_6_1,
    "3.6.2": experiment_3_6_2,
    "3.7": experiment_3_7,
}


def main() -> None:
    p = argparse.ArgumentParser(description="run a single experiment cell")
    p.add_argument(
        "--experiment", required=True,
        choices=list(EXPERIMENTS.keys()) + ["all"],
        help="experiment id, e.g. 3.1; 'all' runs every experiment in sequence",
    )
    args = p.parse_args()
    if args.experiment == "all":
        for k in EXPERIMENTS:
            EXPERIMENTS[k]()
    else:
        EXPERIMENTS[args.experiment]()


if __name__ == "__main__":
    main()
