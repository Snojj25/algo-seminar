"""
test_correctness.py — §3.0 correctness gate.

Lockstep agreement of all counters on small random graphs and update streams.
Must pass before any timing experiment runs.

Default: 20 seeds × 50 updates at n=20. Set RUN_FULL_GATE=1 to expand to the
plan's 100 × 100. Warmup_v3 lockstep runs once that algorithm is in place.
"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

import pytest

# Allow running pytest from either repo root or code/ directory.
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from algorithms.brute_force import BruteForceCounter
from algorithms.layered_simple_wedge import LayeredSimpleWedgeCounter
from algorithms.naive_recompute import NaiveRecomputeCounter
from algorithms.simple_wedge import SimpleWedgeCounter
from algorithms.sparse_wedge import SparseWedgeCounter
from algorithms.warmup_v3 import WarmupV3Counter
from graphs.adversarial import layered_hub
from graphs.generators import erdos_renyi
from graphs.streams import ClassChecker, hub_biased


FULL = os.environ.get("RUN_FULL_GATE") == "1"
N_SEEDS = 100 if FULL else 20
STREAM_LEN = 100 if FULL else 50
N = 20
P = 0.2


def _make_initial(n: int, p: float, seed: int) -> list[tuple[int, int]]:
    _, edges = erdos_renyi(n, p, seed)
    return edges


def _make_stream(
    n: int, edges: list[tuple[int, int]], length: int, seed: int
) -> list[tuple[str, int, int]]:
    rng = random.Random(seed * 7919 + 1)
    present = {(min(u, v), max(u, v)) for u, v in edges}
    ops: list[tuple[str, int, int]] = []
    for _ in range(length):
        if present and rng.random() < 0.4:
            e = rng.choice(list(present))
            ops.append(("delete", e[0], e[1]))
            present.discard(e)
        else:
            tries = 0
            while True:
                u, v = rng.randrange(n), rng.randrange(n)
                if u == v:
                    tries += 1
                    if tries > 1000:
                        raise RuntimeError("near-complete graph")
                    continue
                e = (min(u, v), max(u, v))
                if e in present:
                    tries += 1
                    if tries > 1000:
                        raise RuntimeError("near-complete graph")
                    continue
                ops.append(("insert", e[0], e[1]))
                present.add(e)
                break
    return ops


@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_lockstep_baselines(seed: int) -> None:
    """Naive, Simple, Sparse must all agree with BruteForce after every op."""
    edges = _make_initial(N, P, seed)

    bf = BruteForceCounter(N)
    naive = NaiveRecomputeCounter(N)
    simple = SimpleWedgeCounter(N)
    sparse = SparseWedgeCounter(N)

    for u, v in edges:
        bf.insert(u, v)
        naive.insert(u, v)
        simple.insert(u, v)
        sparse.insert(u, v)

    truth = bf.count()
    assert naive.count() == truth, f"seed={seed} initial Naive disagrees"
    assert simple.count() == truth, f"seed={seed} initial Simple disagrees"
    assert sparse.count() == truth, f"seed={seed} initial Sparse disagrees"

    ops = _make_stream(N, edges, STREAM_LEN, seed)
    for i, (op, u, v) in enumerate(ops):
        for c in (bf, naive, simple, sparse):
            getattr(c, op)(u, v)
        truth = bf.count()
        nv = naive.count()
        sv = simple.count()
        spv = sparse.count()
        assert nv == truth, f"seed={seed} step {i} ({op} {u},{v}): Naive={nv} truth={truth}"
        assert sv == truth, f"seed={seed} step {i} ({op} {u},{v}): Simple={sv} truth={truth}"
        assert spv == truth, f"seed={seed} step {i} ({op} {u},{v}): Sparse={spv} truth={truth}"


@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_warmup_v3_lockstep_with_trace(seed: int) -> None:
    """Warmup_v3 must match trace(A·B·C·D) after every step on a small
    layered graph, on a class-stable hub-biased stream of B and D updates.
    """
    g = layered_hub(n_per_layer=15, k_hubs=2, low_deg=2, hub_density=0.4, seed=seed)
    counter = WarmupV3Counter.from_layered_graph(g)
    assert counter.total == int(
        np.trace(counter.A @ counter.B @ counter.C @ counter.D)
    ), f"seed={seed}: initial total disagrees with trace(ABCD)"

    checker = ClassChecker(g.classes, g.class_bounds, g.initial_degrees())
    B_pool = [(min(u, v), max(u, v)) for u in g.layers[1] for v in g.layers[2]]
    D_pool = [(min(u, v), max(u, v)) for u in g.layers[3] for v in g.layers[0]]

    used = set((min(u, v), max(u, v)) for u, v in g.edges)
    ops_B = hub_biased(
        g.n, used, g.hubs, n_ops=10, hub_bias=0.7,
        seed=seed * 13 + 1, pool=B_pool, class_check=checker,
    )
    used |= {(min(u, v), max(u, v)) for _, u, v in ops_B}
    ops_D = hub_biased(
        g.n, used, g.hubs, n_ops=10, hub_bias=0.7,
        seed=seed * 13 + 2, pool=D_pool, class_check=checker,
    )

    for i, (op, u, v) in enumerate(ops_B + ops_D):
        lp, a, b = counter._classify_edge(u, v)
        getattr(counter, op)(lp, a, b)
        expected = int(np.trace(counter.A @ counter.B @ counter.C @ counter.D))
        assert counter.total == expected, (
            f"seed={seed} step {i} ({op} layer={lp} {a},{b}): "
            f"warmup_v3={counter.total} vs trace={expected}"
        )


@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_layered_simple_lockstep_with_warmup_v3(seed: int) -> None:
    """LayeredSimpleWedgeCounter and WarmupV3Counter both count layered
    4-cycles. They must agree on every step under a B+D class-stable
    hub-biased stream.
    """
    g = layered_hub(n_per_layer=15, k_hubs=2, low_deg=2, hub_density=0.4, seed=seed)
    lc = LayeredSimpleWedgeCounter.from_layered_graph(g)
    wc = WarmupV3Counter.from_layered_graph(g)
    assert lc.count() == wc.count(), (
        f"seed={seed} initial: layered_simple={lc.count()} warmup_v3={wc.count()}"
    )

    checker = ClassChecker(g.classes, g.class_bounds, g.initial_degrees())
    B_pool = [(min(u, v), max(u, v)) for u in g.layers[1] for v in g.layers[2]]
    D_pool = [(min(u, v), max(u, v)) for u in g.layers[3] for v in g.layers[0]]
    used = set((min(u, v), max(u, v)) for u, v in g.edges)
    ops_B = hub_biased(
        g.n, used, g.hubs, n_ops=10, hub_bias=0.7,
        seed=seed * 13 + 7, pool=B_pool, class_check=checker,
    )
    used |= {(min(u, v), max(u, v)) for _, u, v in ops_B}
    ops_D = hub_biased(
        g.n, used, g.hubs, n_ops=10, hub_bias=0.7,
        seed=seed * 13 + 8, pool=D_pool, class_check=checker,
    )

    for i, (op, u, v) in enumerate(ops_B + ops_D):
        getattr(lc, op)(u, v)
        lp, a, b = wc._classify_edge(u, v)
        getattr(wc, op)(lp, a, b)
        assert lc.count() == wc.count(), (
            f"seed={seed} step {i} ({op} {u},{v}): "
            f"layered_simple={lc.count()} warmup_v3={wc.count()}"
        )


def test_simple_wedge_swapped_diverges() -> None:
    """§3.5: swapped query/update order must produce a wrong count within
    a few updates."""
    edges = _make_initial(N, P, seed=42)
    bf = BruteForceCounter(N)
    swapped = SimpleWedgeCounter(N, ordering="swapped")
    for u, v in edges:
        bf.insert(u, v)
        swapped.insert(u, v)
    ops = _make_stream(N, edges, 30, seed=42)
    diverged = False
    for op, u, v in ops:
        getattr(bf, op)(u, v)
        getattr(swapped, op)(u, v)
        if swapped.count() != bf.count():
            diverged = True
            break
    assert diverged, "swapped ordering should diverge from truth"
