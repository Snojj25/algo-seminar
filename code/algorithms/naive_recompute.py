"""
naive_recompute.py — recompute the 4-cycle count from the full adjacency
matrix on every update via the path-pair identity.

Derivation (closed walks of length 4 in a simple graph, all decompositions):
  trace(A^4) = 8 * c4 + 4 * sum_v binom(deg(v), 2) + 2m
where c4 is the 4-cycle count, the 2 sum binom(.) terms come from walks
u-v-u-w-u (v≠w) and u-v-w-v-u (u≠w), and 2m comes from u-v-u-v-u walks.

Let P = A @ A (length-2 walks). With diagonal zeroed (P[u,u] = deg(u)
otherwise), sum(P*P) = trace(A^4) - sum_u deg(u)^2. Substituting and using
sum_v deg(v) = 2m gives the closed form
  c4 = (sum(P*P) - 2 * sum_v binom(deg(v), 2)) / 8
which is what we compute below.
"""

from __future__ import annotations

import numpy as np


class NaiveRecomputeCounter:
    def __init__(self, n: int, dtype: type = np.int64) -> None:
        self.n = n
        self.A = np.zeros((n, n), dtype=dtype)

    def insert(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError("self-loops not allowed")
        self.A[u, v] = 1
        self.A[v, u] = 1

    def delete(self, u: int, v: int) -> None:
        self.A[u, v] = 0
        self.A[v, u] = 0

    def count(self) -> int:
        A = self.A
        # NumPy lacks BLAS for int matmul; route through float64 for the
        # heavy product (entries of P stay well under 2^53). Cast back to
        # int64 before summing to avoid accumulated rounding.
        P_f = A.astype(np.float64) @ A.astype(np.float64)
        P = np.rint(P_f).astype(np.int64)
        np.fill_diagonal(P, 0)
        deg = A.sum(axis=1).astype(np.int64)
        sq_path = int((P * P).sum())
        binom2 = int((deg * (deg - 1) // 2).sum())
        c4 = (sq_path - 2 * binom2) // 8
        return int(c4)
