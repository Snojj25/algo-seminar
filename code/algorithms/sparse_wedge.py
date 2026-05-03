"""
sparse_wedge.py — Simple Wedge with a sparse hashmap-of-counters W.

Same algorithm and asymptotics as simple_wedge.py; W is replaced by a
defaultdict-of-Counter so memory is O(#nonzero entries). Larger constants
per access, but the only variant that fits real-world graphs in our setup.
"""

from __future__ import annotations

from collections import defaultdict


class SparseWedgeCounter:
    def __init__(self, n: int, ordering: str = "correct") -> None:
        if ordering not in ("correct", "swapped"):
            raise ValueError(f"ordering must be 'correct' or 'swapped', got {ordering!r}")
        self.n = n
        self.ordering = ordering
        self.adj: list[set[int]] = [set() for _ in range(n)]
        self.W: defaultdict[int, defaultdict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.total = 0

    def _query_delta(self, u: int, v: int) -> int:
        Wv = self.W.get(v)
        if Wv is None:
            return 0
        s = 0
        Wv_get = Wv.get
        for w in self.adj[u]:
            if w != v:
                c = Wv_get(w)
                if c:
                    s += c
        return s

    def _bump(self, a: int, b: int, sign: int) -> None:
        row = self.W[a]
        new = row[b] + sign
        if new == 0:
            del row[b]
            if not row:
                del self.W[a]
        else:
            row[b] = new

    def _apply_edge_to_W(self, u: int, v: int, sign: int) -> None:
        for w in self.adj[u]:
            if w == v:
                continue
            self._bump(w, v, sign)
            self._bump(v, w, sign)
        for w in self.adj[v]:
            if w == u:
                continue
            self._bump(w, u, sign)
            self._bump(u, w, sign)

    def insert(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError("self-loops not allowed")
        if v in self.adj[u]:
            raise ValueError(f"edge ({u},{v}) already present")

        if self.ordering == "correct":
            delta = self._query_delta(u, v)
            self._apply_edge_to_W(u, v, +1)
            self.adj[u].add(v)
            self.adj[v].add(u)
            self.total += delta
        else:
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
            self.adj[u].discard(v)
            self.adj[v].discard(u)
            self._apply_edge_to_W(u, v, -1)
            delta = self._query_delta(u, v)
            self.total -= delta
        else:
            delta = self._query_delta(u, v)
            self.adj[u].discard(v)
            self.adj[v].discard(u)
            self._apply_edge_to_W(u, v, -1)
            self.total -= delta

    def count(self) -> int:
        return self.total
