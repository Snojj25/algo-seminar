"""
layered_simple_wedge.py — Simple Wedge restricted to layered 4-cycles.

This is the apples-to-apples baseline for warmup_v3: same wedge-counting
idea as paper Appendix A, but it knows it's running on a 4-layered graph and
only maintains wedges that are actually part of layered 4-cycles. In
particular it counts the same thing warmup_v3 counts (layered 4-cycles
L1-L2-L3-L4-L1, equivalently trace(A·B·C·D)), with no class-routing
machinery and no precomputed matrix products.

State:
    W_13[i, w] = number of length-2 paths from i ∈ L1 to w ∈ L3 through L2
                 = sum_j A[i, j] · B[j, w].

Per-update Δ:
    D-update (l, i): sum_{w ∈ N_C(l)} W_13[i, w]      O(deg_C(l))
    C-update (w, l): sum_{i ∈ N_D(l)} W_13[i, w]      O(deg_D(l))
    B-update (j, w): brute over N_A(j) × N_C(w)        O(deg_A(j)·deg_C(w))
    A-update (i, j): brute over N_B(j) × N_D(i)        O(deg_B(j)·deg_D(i))

W_13 maintenance:
    A insert/delete (i, j): W_13[i, w] ± 1 for w ∈ N_B(j)
    B insert/delete (j, w): W_13[i, w] ± 1 for i ∈ N_A(j)
    C and D updates: no change to W_13.

The interface accepts global vertex ids and routes by layer; this lets the
benchmark harness drop it in wherever it would have used SimpleWedgeCounter.
"""

from __future__ import annotations

import numpy as np


class LayeredSimpleWedgeCounter:
    def __init__(self, n_per_layer: int) -> None:
        n = n_per_layer
        self.n_per = n

        # Per-layer-pair adjacency lists. Local indices within each layer.
        self.adj_A_L1: list[set[int]] = [set() for _ in range(n)]
        self.adj_A_L2: list[set[int]] = [set() for _ in range(n)]
        self.adj_B_L2: list[set[int]] = [set() for _ in range(n)]
        self.adj_B_L3: list[set[int]] = [set() for _ in range(n)]
        self.adj_C_L3: list[set[int]] = [set() for _ in range(n)]
        self.adj_C_L4: list[set[int]] = [set() for _ in range(n)]
        self.adj_D_L4: list[set[int]] = [set() for _ in range(n)]
        self.adj_D_L1: list[set[int]] = [set() for _ in range(n)]

        # Edge presence matrices for fast membership tests in brute-force Δ.
        self.A = np.zeros((n, n), dtype=np.int8)
        self.B = np.zeros((n, n), dtype=np.int8)
        self.C = np.zeros((n, n), dtype=np.int8)
        self.D = np.zeros((n, n), dtype=np.int8)

        self.W_13 = np.zeros((n, n), dtype=np.int32)
        self.total: int = 0

    # ----- helpers ---------------------------------------------------------

    def _layer_pair(self, u: int, v: int) -> tuple[str, int, int]:
        n = self.n_per
        lu, lv = u // n, v // n
        au, av = u % n, v % n
        s = (min(lu, lv), max(lu, lv))
        if s == (0, 1):
            return "A", (au if lu == 0 else av), (av if lv == 1 else au)
        if s == (1, 2):
            return "B", (au if lu == 1 else av), (av if lv == 2 else au)
        if s == (2, 3):
            return "C", (au if lu == 2 else av), (av if lv == 3 else au)
        if s == (0, 3):
            return "D", (au if lu == 3 else av), (av if lv == 0 else au)
        raise ValueError(f"non-layered edge ({u},{v})")

    # ----- Δ formulas ------------------------------------------------------

    def _delta_A(self, i: int, j: int) -> int:
        cnt = 0
        for w in self.adj_B_L2[j]:
            for l in self.adj_D_L1[i]:
                if self.C[w, l]:
                    cnt += 1
        return cnt

    def _delta_B(self, j: int, w: int) -> int:
        cnt = 0
        for i in self.adj_A_L2[j]:
            for l in self.adj_C_L3[w]:
                if self.D[l, i]:
                    cnt += 1
        return cnt

    def _delta_C(self, w: int, l: int) -> int:
        col = self.W_13[:, w]
        s = 0
        for i in self.adj_D_L4[l]:
            s += int(col[i])
        return s

    def _delta_D(self, l: int, i: int) -> int:
        row = self.W_13[i]
        s = 0
        for w in self.adj_C_L4[l]:
            s += int(row[w])
        return s

    # ----- W_13 maintenance ------------------------------------------------

    def _bump_A(self, i: int, j: int, sign: int) -> None:
        # New A-edge (i, j) creates 2-paths i → j → w for each w ∈ N_B(j).
        for w in self.adj_B_L2[j]:
            self.W_13[i, w] += sign

    def _bump_B(self, j: int, w: int, sign: int) -> None:
        # New B-edge (j, w) creates 2-paths i → j → w for each i ∈ N_A(j).
        for i in self.adj_A_L2[j]:
            self.W_13[i, w] += sign

    # ----- per-layer apply -------------------------------------------------

    def _do_A(self, i: int, j: int, sign: int) -> None:
        if sign > 0:
            d = self._delta_A(i, j)
            self._bump_A(i, j, +1)
            self.A[i, j] = 1
            self.adj_A_L1[i].add(j)
            self.adj_A_L2[j].add(i)
            self.total += d
        else:
            self.A[i, j] = 0
            self.adj_A_L1[i].discard(j)
            self.adj_A_L2[j].discard(i)
            self._bump_A(i, j, -1)
            self.total -= self._delta_A(i, j)

    def _do_B(self, j: int, w: int, sign: int) -> None:
        if sign > 0:
            d = self._delta_B(j, w)
            self._bump_B(j, w, +1)
            self.B[j, w] = 1
            self.adj_B_L2[j].add(w)
            self.adj_B_L3[w].add(j)
            self.total += d
        else:
            self.B[j, w] = 0
            self.adj_B_L2[j].discard(w)
            self.adj_B_L3[w].discard(j)
            self._bump_B(j, w, -1)
            self.total -= self._delta_B(j, w)

    def _do_C(self, w: int, l: int, sign: int) -> None:
        if sign > 0:
            d = self._delta_C(w, l)
            self.C[w, l] = 1
            self.adj_C_L3[w].add(l)
            self.adj_C_L4[l].add(w)
            self.total += d
        else:
            self.C[w, l] = 0
            self.adj_C_L3[w].discard(l)
            self.adj_C_L4[l].discard(w)
            self.total -= self._delta_C(w, l)

    def _do_D(self, l: int, i: int, sign: int) -> None:
        if sign > 0:
            d = self._delta_D(l, i)
            self.D[l, i] = 1
            self.adj_D_L4[l].add(i)
            self.adj_D_L1[i].add(l)
            self.total += d
        else:
            self.D[l, i] = 0
            self.adj_D_L4[l].discard(i)
            self.adj_D_L1[i].discard(l)
            self.total -= self._delta_D(l, i)

    # ----- public interface ------------------------------------------------

    def insert(self, u: int, v: int) -> None:
        kind, a, b = self._layer_pair(u, v)
        if kind == "A":
            self._do_A(a, b, +1)
        elif kind == "B":
            self._do_B(a, b, +1)
        elif kind == "C":
            self._do_C(a, b, +1)
        else:
            self._do_D(a, b, +1)

    def delete(self, u: int, v: int) -> None:
        kind, a, b = self._layer_pair(u, v)
        if kind == "A":
            self._do_A(a, b, -1)
        elif kind == "B":
            self._do_B(a, b, -1)
        elif kind == "C":
            self._do_C(a, b, -1)
        else:
            self._do_D(a, b, -1)

    def count(self) -> int:
        return self.total

    @classmethod
    def from_layered_graph(cls, lg) -> "LayeredSimpleWedgeCounter":
        from graphs.adversarial import LayeredGraph
        if not isinstance(lg, LayeredGraph):
            raise TypeError("from_layered_graph expects a LayeredGraph")
        c = cls(lg.n_per_layer)
        for u, v in lg.edges:
            c.insert(u, v)
        return c
