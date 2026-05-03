"""
generators.py — random-graph wrappers around networkx, returning edge lists.

All generators return (n, edges) where edges is a list of (u, v) tuples with
u < v, no duplicates, no self-loops.
"""

from __future__ import annotations

import networkx as nx


def _to_edge_list(g: nx.Graph) -> list[tuple[int, int]]:
    return [(min(u, v), max(u, v)) for u, v in g.edges()]


def erdos_renyi(n: int, p: float, seed: int) -> tuple[int, list[tuple[int, int]]]:
    g = nx.fast_gnp_random_graph(n, p, seed=seed)
    return n, _to_edge_list(g)


def erdos_renyi_density(
    n: int, gamma: float, c: float = 1.0, seed: int = 0
) -> tuple[int, list[tuple[int, int]]]:
    """ER with target m ~ c * n^gamma; sets p = c * n^(gamma - 2)."""
    if gamma >= 2.0:
        raise ValueError("gamma must be < 2 to keep p <= 1")
    p = min(1.0, c * n ** (gamma - 2.0))
    return erdos_renyi(n, p, seed)


def barabasi_albert(n: int, m: int, seed: int) -> tuple[int, list[tuple[int, int]]]:
    g = nx.barabasi_albert_graph(n, m, seed=seed)
    return n, _to_edge_list(g)


def random_regular(n: int, d: int, seed: int) -> tuple[int, list[tuple[int, int]]]:
    g = nx.random_regular_graph(d, n, seed=seed)
    return n, _to_edge_list(g)
