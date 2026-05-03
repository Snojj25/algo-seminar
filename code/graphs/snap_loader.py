"""
snap_loader.py — load SNAP edge-list graphs.

SNAP datasets ship as gzipped edge lists. Each non-comment line is `u\tv` (or
`u v`). Vertices may be non-contiguous integer ids, so we relabel to a dense
0..n-1 range. The relabeling map is cached alongside the .npz to make
multiple runs deterministic and fast.
"""

from __future__ import annotations

import gzip
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_snap_graph(filename: str) -> tuple[int, list[tuple[int, int]]]:
    """Return (n, edges) for a SNAP-format graph file in code/data/.

    Caches a parsed .npz next to the source. Edges are simple-graph, undirected
    (u < v after relabeling).
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run code/data/download.sh to fetch."
        )
    cache = path.with_suffix(path.suffix + ".cache.npz")
    if cache.exists():
        data = np.load(cache)
        return int(data["n"]), [tuple(e) for e in data["edges"]]

    seen: set[tuple[int, int]] = set()
    relabel: dict[int, int] = {}
    edges: list[tuple[int, int]] = []
    open_fn = gzip.open if str(path).endswith(".gz") else open
    with open_fn(path, "rt") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                u, v = int(parts[0]), int(parts[1])
            except ValueError:
                continue
            if u == v:
                continue
            if u not in relabel:
                relabel[u] = len(relabel)
            if v not in relabel:
                relabel[v] = len(relabel)
            a, b = relabel[u], relabel[v]
            e = (min(a, b), max(a, b))
            if e in seen:
                continue
            seen.add(e)
            edges.append(e)
    n = len(relabel)
    np.savez_compressed(cache, n=np.array(n), edges=np.array(edges))
    return n, edges
