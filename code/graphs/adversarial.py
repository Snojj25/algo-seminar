"""
adversarial.py — planted-hub 4-layered graphs for the §3.6 headline experiment.

The construction forces Simple Wedge into its Θ(deg) worst case (whenever an
update touches a hub) while giving Warmup_v3 a chance to skip the per-neighbour
enumeration via class-based routing.

Layout:
  Vertex ids assigned contiguously per layer.
    L1 = [0,        n_per_layer)
    L2 = [n_per_layer,   2*n_per_layer)
    L3 = [2*n_per_layer, 3*n_per_layer)
    L4 = [3*n_per_layer, 4*n_per_layer)
  Edges only between consecutive layers (cyclic): L1-L2, L2-L3, L3-L4, L4-L1.
  In L1 and L2 the first `k_hubs` vertices are hubs with degree ≈ hub_target;
  remaining vertices and all of L3, L4 have degree ≈ low_deg.

Class assignment (frozen at construction; matches paper §3.4 in spirit but
relaxed to give the stream room to operate):
  L1, L4: 'H' for hubs, 'L' for low-degree.
  L2, L3: 'D' for hubs, 'S' for sparse.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class LayeredGraph:
    n: int
    n_per_layer: int
    layers: list[range]                       # 4 ranges, one per layer
    edges: list[tuple[int, int]]              # canonical u < v
    layer_pairs: list[tuple[int, int]]        # 4 pairs: (0,1),(1,2),(2,3),(3,0)
    hubs: set[int]
    classes: dict[int, str]                   # vertex -> class label
    class_bounds: dict[str, tuple[int, int]]  # class label -> (deg_lo, deg_hi)
    edge_pool: list[tuple[int, int]]          # all valid layered edges (used + unused)

    def layer_of(self, v: int) -> int:
        return v // self.n_per_layer

    def initial_degrees(self) -> dict[int, int]:
        deg: dict[int, int] = {v: 0 for v in range(self.n)}
        for u, v in self.edges:
            deg[u] += 1
            deg[v] += 1
        return deg


def _layer_edges(L_a: range, L_b: range) -> list[tuple[int, int]]:
    return [(min(u, v), max(u, v)) for u in L_a for v in L_b]


def layered_hub(
    n_per_layer: int,
    k_hubs: int,
    low_deg: int = 5,
    hub_density: float = 0.5,
    seed: int = 0,
    k_hubs_l4: int = 0,
) -> LayeredGraph:
    """Build a planted-hub layered graph.

    Hub degree per pair is round(hub_density * n_per_layer). Each hub gets that
    many random edges to the next layer. Each non-hub gets `low_deg` random
    edges to the next layer.

    Hubs are planted in L1 and L2 (the paper-§3 setup). Setting k_hubs_l4 > 0
    additionally plants L4 hubs (heavy in C toward L3) — used by §3.6.2 to
    trigger HH queries in Warmup_v3.

    Class bounds are set wide enough that streams of moderate length cannot
    push any vertex out of its class.
    """
    if k_hubs >= n_per_layer or k_hubs_l4 >= n_per_layer:
        raise ValueError("k_hubs / k_hubs_l4 must be < n_per_layer")
    rng = random.Random(seed)

    L1 = range(0, n_per_layer)
    L2 = range(n_per_layer, 2 * n_per_layer)
    L3 = range(2 * n_per_layer, 3 * n_per_layer)
    L4 = range(3 * n_per_layer, 4 * n_per_layer)
    layers = [L1, L2, L3, L4]
    layer_pairs = [(0, 1), (1, 2), (2, 3), (3, 0)]

    hub_target = max(1, round(hub_density * n_per_layer))
    if hub_target >= n_per_layer:
        hub_target = n_per_layer - 1

    hubs_L1 = set(list(L1)[:k_hubs])
    hubs_L2 = set(list(L2)[:k_hubs])
    hubs_L4 = set(list(L4)[:k_hubs_l4])
    hubs = hubs_L1 | hubs_L2 | hubs_L4

    edges_set: set[tuple[int, int]] = set()

    def _connect(u: int, neighbour_layer: range, target_deg: int) -> None:
        candidates = [w for w in neighbour_layer if w != u]
        rng.shuffle(candidates)
        added = 0
        for w in candidates:
            if added >= target_deg:
                break
            e = (min(u, w), max(u, w))
            if e in edges_set:
                continue
            edges_set.add(e)
            added += 1

    # L1 ↔ L2: hubs in L1 connect heavily to L2.
    for u in L1:
        deg = hub_target if u in hubs_L1 else low_deg
        _connect(u, L2, deg)
    # L2 ↔ L3: hubs in L2 connect heavily to L3.
    for u in L2:
        deg = hub_target if u in hubs_L2 else low_deg
        _connect(u, L3, deg)
    # L3 ↔ L4: low-degree from the L3 side; L4 hubs may add more below.
    for u in L3:
        _connect(u, L4, low_deg)
    # L4 hubs heavily connect to L3 (driving deg_C(L4 hub) high).
    for u in L4:
        if u in hubs_L4:
            _connect(u, L3, hub_target)
    # L4 ↔ L1: low-degree (closes the cycle).
    for u in L4:
        _connect(u, L1, low_deg)

    edges = sorted(edges_set)

    # Compute current degrees and choose class bounds with generous slack.
    deg: dict[int, int] = {v: 0 for v in range(4 * n_per_layer)}
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1

    classes: dict[int, str] = {}
    for v in L1:
        classes[v] = "H" if v in hubs_L1 else "L"
    for v in L2:
        classes[v] = "D" if v in hubs_L2 else "S"
    for v in L3:
        classes[v] = "S"
    for v in L4:
        classes[v] = "H" if v in hubs_L4 else "L"

    # Bounds: hubs may grow up to layer size - 1; lows have a comfortable cap.
    low_cap = max(low_deg + 50, hub_target // 4)
    hub_lo = hub_target // 2
    bounds: dict[str, tuple[int, int]] = {
        "H": (hub_lo, n_per_layer - 1),
        "L": (0, low_cap),
        "D": (hub_lo, n_per_layer - 1),
        "S": (0, low_cap),
    }
    # Sanity: every current degree fits in its class.
    for v, c in classes.items():
        lo, hi = bounds[c]
        if not (lo <= deg[v] <= hi):
            raise RuntimeError(
                f"vertex {v} class {c} has deg={deg[v]} outside bounds [{lo},{hi}]"
            )

    # Edge pool: all layered pairs (used + free) for hub_biased to draw from.
    pool: list[tuple[int, int]] = []
    pool.extend(_layer_edges(L1, L2))
    pool.extend(_layer_edges(L2, L3))
    pool.extend(_layer_edges(L3, L4))
    pool.extend(_layer_edges(L4, L1))

    return LayeredGraph(
        n=4 * n_per_layer,
        n_per_layer=n_per_layer,
        layers=layers,
        edges=edges,
        layer_pairs=layer_pairs,
        hubs=hubs,
        classes=classes,
        class_bounds=bounds,
        edge_pool=pool,
    )
