"""
simple_wedge.py — paper Appendix A (Assadi & Shah, PODS 2025).

Maintain the dense wedge matrix W[a, b] = number of length-2 walks (=
common neighbours) between a and b. On each edge update, the change in
the 4-cycle count is computable in O(deg(u) + deg(v)) by summing one row
of W over the neighbours of an endpoint. Correctness depends on the
update-order rule:
  insert: query first (W still pre-update), then update W, then add edge.
  delete: remove edge first, update W, then query.
Both orderings keep the modified edge (u, v) absent from W during the
query, so the wedge counts exclude paths that traverse the moving edge.
"""

from __future__ import annotations

import numpy as np


class SimpleWedgeCounter:
    def __init__(
        self,
        n: int,
        ordering: str = "correct",
        dtype: type = np.int32,
    ) -> None:
        if ordering not in ("correct", "swapped"):
            raise ValueError(f"ordering must be 'correct' or 'swapped', got {ordering!r}")
        self.n = n
        self.ordering = ordering
        self.adj: list[set[int]] = [set() for _ in range(n)]
        self.W = np.zeros((n, n), dtype=dtype)
        self.total = 0

    def _query_delta(self, u: int, v: int) -> int:
        # Count 4-cycles through (u, v): for each w in N(u) \ {v},
        # W[w, v] counts paths w-?-v of length 2; each such path closes
        # to a 4-cycle u-w-?-v-u via the (u,v) edge.
        W = self.W
        s = 0
        for w in self.adj[u]:
            if w != v:
                s += int(W[w, v])
        return s

    def _apply_edge_to_W(self, u: int, v: int, sign: int) -> None:
        # Edge (u, v) creates length-2 paths through u (for each neighbour
        # of u other than v, ending at v) and through v symmetrically.
        W = self.W
        for w in self.adj[u]:
            if w == v:
                continue
            W[w, v] += sign
            W[v, w] += sign
        for w in self.adj[v]:
            if w == u:
                continue
            W[w, u] += sign
            W[u, w] += sign

    def insert(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError("self-loops not allowed")
        if v in self.adj[u]:
            raise ValueError(f"edge ({u},{v}) already present")

        if self.ordering == "correct":
            # Query before W update; adj[u] does not yet contain v.
            delta = self._query_delta(u, v)
            self._apply_edge_to_W(u, v, +1)
            self.adj[u].add(v)
            self.adj[v].add(u)
            self.total += delta
        else:  # swapped — pedagogically wrong, used in §3.5 experiment
            self._apply_edge_to_W(u, v, +1)
            self.adj[u].add(v)
            self.adj[v].add(u)
            delta = self._query_delta(u, v)
            self.total += delta

    def delete(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError("self-loops not allowed")
        if v not in self.adj[u]:
            raise ValueError(f"edge ({u},{v}) not present")

        if self.ordering == "correct":
            # Remove edge first, decrement W using the new adjacency
            # (mirror of insert), then query.
            self.adj[u].discard(v)
            self.adj[v].discard(u)
            self._apply_edge_to_W(u, v, -1)
            delta = self._query_delta(u, v)
            self.total -= delta
        else:  # swapped — wrong
            delta = self._query_delta(u, v)
            self.adj[u].discard(v)
            self.adj[v].discard(u)
            self._apply_edge_to_W(u, v, -1)
            self.total -= delta

    def count(self) -> int:
        return self.total
