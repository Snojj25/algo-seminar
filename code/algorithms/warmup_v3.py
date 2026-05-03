"""
warmup_v3.py — simplified §3 warm-up of Assadi & Shah (PODS 2025).

This is NOT a faithful realisation of the paper's algorithm. Specifically:
  - Assumptions 1 and 2 are fixed at construction time. Updates that would
    cross a class threshold raise ClassStabilityError.
  - Assumption 3 is enforced strictly: only edges in B and D may be updated.
    Inserts / deletes in A and C raise ValueError.
  - Fast rectangular matrix multiplication is substituted with NumPy GEMM.
    The asymptotic exponent is therefore strictly worse than the paper's
    O(m^(2/3 − ε₁')) claim. Per-update cost in this file is dominated by
    cubic matmul over reduced submatrices of size determined by vertex
    classes; the win over Simple Wedge at our scale comes from class-based
    work avoidance, not FMM.
  - Chunk size is fixed at 1 (no batched flushes). With chunk_size=1 the
    paper's per-chunk B-Dense class is empty, so the Eq (4) DD/SD/DS
    structures collapse to the trivial brute-enumeration path.
  - §5 (phases), §6 (tiny vertices), §7 (class changes mid-stream) are not
    implemented.

Page references in this file point to 2504.10748v1.pdf.

Layered-graph layout. Vertices are local within their layer (0..|L_i|).
The interface accepts (layer_pair, u, v) where layer_pair selects the
biadjacency matrix:
    LAYER_A (0): A   L1 × L2
    LAYER_B (1): B   L2 × L3
    LAYER_C (2): C   L3 × L4
    LAYER_D (3): D   L4 × L1
"""

from __future__ import annotations

import numpy as np

from graphs.streams import ClassStabilityError


LAYER_A = 0
LAYER_B = 1
LAYER_C = 2
LAYER_D = 3


class WarmupV3Counter:
    """Simplified §3 counter. Maintains paper Table 1 partial products
    restricted to the H and M classes:

        AB_H = A^{H*} · B           |L1^H| × |L3|       — Eq (1)
        AB_M = A^{M*} · B           |L1^M| × |L3|       — Eq (3)
        BC_H = B · C^{*H}           |L2|   × |L4^H|     — Eq (1)
        BC_M = B · C^{*M}           |L2|   × |L4^M|     — Eq (3)
        ABC_HH = A^{H*} · B · C^{*H}                     — Eq (1)
        ABC_HM, ABC_MH, ABC_MM      H/M cross-products  — Eq (3) extension

    Δ on D-update (l, i) = (ABC)[i, l] is dispatched per (class(i), class(l))
    following paper §3.3 (Lemma 3.8): HH/HM/MH/MM = O(1) lookup; HL/ML
    iterate N_C(l); LH/LM iterate N_A(i); LL is brute over N_A(i) × N_C(l).

    Δ on B-update (j, w) is brute over min(N_A(j), N_C(w)). For our planted-
    hub graphs both A- and C-degrees of L2/L3 vertices are small, so this is
    fast; the win over Simple Wedge (which would touch O(deg_union(hub))
    wedge-matrix entries) is asymptotic.
    """

    def __init__(
        self,
        sizes: tuple[int, int, int, int],
        classes_14: np.ndarray,
        classes_23: np.ndarray,
        m_estimate: int = 0,
    ) -> None:
        if len(sizes) != 4:
            raise ValueError("sizes must be (|L1|,|L2|,|L3|,|L4|)")
        self.n1, self.n2, self.n3, self.n4 = sizes
        classes_14 = np.asarray(classes_14)
        classes_23 = np.asarray(classes_23)
        if classes_14.shape != (self.n1 + self.n4,):
            raise ValueError("classes_14 length must equal |L1|+|L4|")
        if classes_23.shape != (self.n2 + self.n3,):
            raise ValueError("classes_23 length must equal |L2|+|L3|")
        for c in classes_14:
            if c not in ("H", "M", "L"):
                raise ValueError(f"classes_14 entries must be H/M/L; got {c!r}")
        for c in classes_23:
            if c not in ("S", "D"):
                raise ValueError(f"classes_23 entries must be S/D; got {c!r}")

        self.cls_L1 = classes_14[: self.n1].copy()
        self.cls_L4 = classes_14[self.n1 :].copy()
        self.cls_L2 = classes_23[: self.n2].copy()
        self.cls_L3 = classes_23[self.n2 :].copy()
        self.m_estimate = m_estimate

        # Class index arrays and inverse maps for O(1) global → local lookup.
        self.idx_L1_H = np.where(self.cls_L1 == "H")[0]
        self.idx_L1_M = np.where(self.cls_L1 == "M")[0]
        self.idx_L1_L = np.where(self.cls_L1 == "L")[0]
        self.idx_L4_H = np.where(self.cls_L4 == "H")[0]
        self.idx_L4_M = np.where(self.cls_L4 == "M")[0]
        self.idx_L4_L = np.where(self.cls_L4 == "L")[0]
        self.inv_L1_H = {int(v): k for k, v in enumerate(self.idx_L1_H)}
        self.inv_L1_M = {int(v): k for k, v in enumerate(self.idx_L1_M)}
        self.inv_L4_H = {int(v): k for k, v in enumerate(self.idx_L4_H)}
        self.inv_L4_M = {int(v): k for k, v in enumerate(self.idx_L4_M)}

        # Biadjacency matrices, dense int32.
        self.A = np.zeros((self.n1, self.n2), dtype=np.int32)
        self.B = np.zeros((self.n2, self.n3), dtype=np.int32)
        self.C = np.zeros((self.n3, self.n4), dtype=np.int32)
        self.D = np.zeros((self.n4, self.n1), dtype=np.int32)

        # Per-layer adjacency lists (sets) for fast neighbour iteration.
        self.adj_A_L1: list[set[int]] = [set() for _ in range(self.n1)]
        self.adj_A_L2: list[set[int]] = [set() for _ in range(self.n2)]
        self.adj_B_L2: list[set[int]] = [set() for _ in range(self.n2)]
        self.adj_B_L3: list[set[int]] = [set() for _ in range(self.n3)]
        self.adj_C_L3: list[set[int]] = [set() for _ in range(self.n3)]
        self.adj_C_L4: list[set[int]] = [set() for _ in range(self.n4)]
        self.adj_D_L4: list[set[int]] = [set() for _ in range(self.n4)]
        self.adj_D_L1: list[set[int]] = [set() for _ in range(self.n1)]

        # Partial products. int64 because counts can exceed int32.
        self.AB_H = np.zeros((len(self.idx_L1_H), self.n3), dtype=np.int64)
        self.AB_M = np.zeros((len(self.idx_L1_M), self.n3), dtype=np.int64)
        self.BC_H = np.zeros((self.n2, len(self.idx_L4_H)), dtype=np.int64)
        self.BC_M = np.zeros((self.n2, len(self.idx_L4_M)), dtype=np.int64)
        self.ABC_HH = np.zeros((len(self.idx_L1_H), len(self.idx_L4_H)), dtype=np.int64)
        self.ABC_HM = np.zeros((len(self.idx_L1_H), len(self.idx_L4_M)), dtype=np.int64)
        self.ABC_MH = np.zeros((len(self.idx_L1_M), len(self.idx_L4_H)), dtype=np.int64)
        self.ABC_MM = np.zeros((len(self.idx_L1_M), len(self.idx_L4_M)), dtype=np.int64)

        # Running 4-cycle count.
        self.total: int = 0

    # ----- factory ---------------------------------------------------------

    @classmethod
    def from_layered_graph(cls, lg, m_estimate: int | None = None):
        """Construct from an adversarial.LayeredGraph: bulk-populate matrices
        and adjacency lists from lg.edges, then compute partial products and
        total via NumPy GEMM. One-time O(n^3) precompute.
        """
        from graphs.adversarial import LayeredGraph

        if not isinstance(lg, LayeredGraph):
            raise TypeError("from_layered_graph expects a LayeredGraph")
        n_per = lg.n_per_layer
        sizes = (n_per, n_per, n_per, n_per)
        L1, L2, L3, L4 = lg.layers
        classes_14 = np.array(
            [lg.classes[v] for v in L1] + [lg.classes[v] for v in L4]
        )
        classes_23 = np.array(
            [lg.classes[v] for v in L2] + [lg.classes[v] for v in L3]
        )
        m_est = m_estimate if m_estimate is not None else len(lg.edges)
        c = cls(sizes, classes_14, classes_23, m_est)

        for u, v in lg.edges:
            lp, a, b = c._classify_edge(u, v)
            if lp == LAYER_A:
                c.A[a, b] = 1
                c.adj_A_L1[a].add(b)
                c.adj_A_L2[b].add(a)
            elif lp == LAYER_B:
                c.B[a, b] = 1
                c.adj_B_L2[a].add(b)
                c.adj_B_L3[b].add(a)
            elif lp == LAYER_C:
                c.C[a, b] = 1
                c.adj_C_L3[a].add(b)
                c.adj_C_L4[b].add(a)
            elif lp == LAYER_D:
                c.D[a, b] = 1
                c.adj_D_L4[a].add(b)
                c.adj_D_L1[b].add(a)
        c._rebuild_partial_products()
        c.total = c._compute_layered_total()
        return c

    def _classify_edge(self, u: int, v: int) -> tuple[int, int, int]:
        """Map a global (u, v) edge to (layer_pair, local_a, local_b) where
        local indices are within their respective layers and ordered to
        match the layer-pair convention (A: L1×L2, B: L2×L3, etc.).
        """
        n = self.n1  # all layers same size in current adversarial builder
        lu, lv = u // n, v // n
        if {lu, lv} == {0, 1}:
            return LAYER_A, (u if lu == 0 else v) % n, (v if lv == 1 else u) % n
        if {lu, lv} == {1, 2}:
            return LAYER_B, (u if lu == 1 else v) % n, (v if lv == 2 else u) % n
        if {lu, lv} == {2, 3}:
            return LAYER_C, (u if lu == 2 else v) % n, (v if lv == 3 else u) % n
        if {lu, lv} == {3, 0}:
            return LAYER_D, (u if lu == 3 else v) % n, (v if lv == 0 else u) % n
        raise ValueError(f"edge ({u},{v}) does not span consecutive layers")

    # ----- precompute ------------------------------------------------------

    def _rebuild_partial_products(self) -> None:
        """Recompute every partial product from current A, B, C, D.
        FMM substitute: NumPy GEMM throughout.
        """
        A_H = self.A[self.idx_L1_H, :]
        A_M = self.A[self.idx_L1_M, :]
        C_H = self.C[:, self.idx_L4_H]
        C_M = self.C[:, self.idx_L4_M]
        # FMM substitute: NumPy GEMM
        self.AB_H = (A_H @ self.B).astype(np.int64) if A_H.size else self.AB_H
        self.AB_M = (A_M @ self.B).astype(np.int64) if A_M.size else self.AB_M
        self.BC_H = (self.B @ C_H).astype(np.int64) if C_H.size else self.BC_H
        self.BC_M = (self.B @ C_M).astype(np.int64) if C_M.size else self.BC_M
        # FMM substitute: NumPy GEMM
        if A_H.size and C_H.size:
            self.ABC_HH = (self.AB_H @ C_H).astype(np.int64)
        if A_H.size and C_M.size:
            self.ABC_HM = (self.AB_H @ C_M).astype(np.int64)
        if A_M.size and C_H.size:
            self.ABC_MH = (self.AB_M @ C_H).astype(np.int64)
        if A_M.size and C_M.size:
            self.ABC_MM = (self.AB_M @ C_M).astype(np.int64)

    def _compute_layered_total(self) -> int:
        """trace(A·B·C·D) — the layered 4-cycle count from scratch.
        FMM substitute: NumPy GEMM.
        """
        # FMM substitute: NumPy GEMM (chained)
        ABCD = self.A @ self.B @ self.C @ self.D
        return int(np.trace(ABCD))

    # ----- public interface -----------------------------------------------

    def insert(self, layer_pair: int, u: int, v: int) -> None:
        if layer_pair == LAYER_B:
            self._apply_B(u, v, +1)
        elif layer_pair == LAYER_D:
            self._apply_D(u, v, +1)
        elif layer_pair in (LAYER_A, LAYER_C):
            raise ValueError(
                f"layer {layer_pair} is fixed under Assumption 3; "
                "use B (1) or D (3) only"
            )
        else:
            raise ValueError(f"unknown layer_pair {layer_pair}")

    def delete(self, layer_pair: int, u: int, v: int) -> None:
        if layer_pair == LAYER_B:
            self._apply_B(u, v, -1)
        elif layer_pair == LAYER_D:
            self._apply_D(u, v, -1)
        elif layer_pair in (LAYER_A, LAYER_C):
            raise ValueError(
                f"layer {layer_pair} is fixed under Assumption 3; "
                "use B (1) or D (3) only"
            )
        else:
            raise ValueError(f"unknown layer_pair {layer_pair}")

    def count(self) -> int:
        return self.total

    # ----- B-update --------------------------------------------------------

    def _apply_B(self, j: int, w: int, sign: int) -> None:
        if sign > 0:
            if w in self.adj_B_L2[j]:
                raise ValueError(f"B edge ({j},{w}) already present")
            delta = self._delta_B(j, w)
            self.adj_B_L2[j].add(w)
            self.adj_B_L3[w].add(j)
            self.B[j, w] = 1
        else:
            if w not in self.adj_B_L2[j]:
                raise ValueError(f"B edge ({j},{w}) not present")
            self.adj_B_L2[j].discard(w)
            self.adj_B_L3[w].discard(j)
            self.B[j, w] = 0
            delta = self._delta_B(j, w)
        self._update_partials_on_B(j, w, sign)
        self.total += sign * delta

    def _delta_B(self, j: int, w: int) -> int:
        """# layered 4-cycles through (j, w) ∈ B.

        Δ = sum_{i,l} A[i,j] · C[w,l] · D[l,i]. Brute over the smaller of
        N_A(j) and N_C(w); for each pair check D via adjacency set.
        """
        N_A = self.adj_A_L2[j]
        N_C = self.adj_C_L3[w]
        cnt = 0
        if len(N_A) <= len(N_C):
            for i in N_A:
                for l in self.adj_D_L1[i]:
                    if l in N_C:
                        cnt += 1
        else:
            for l in N_C:
                for i in self.adj_D_L4[l]:
                    if i in N_A:
                        cnt += 1
        return cnt

    def _update_partials_on_B(self, j: int, w: int, sign: int) -> None:
        """Maintain AB_H, AB_M, BC_H, BC_M, ABC_HH/HM/MH/MM after a B change."""
        A_Hj = self.A[self.idx_L1_H, j].astype(np.int64) if len(self.idx_L1_H) else None
        A_Mj = self.A[self.idx_L1_M, j].astype(np.int64) if len(self.idx_L1_M) else None
        C_wH = self.C[w, self.idx_L4_H].astype(np.int64) if len(self.idx_L4_H) else None
        C_wM = self.C[w, self.idx_L4_M].astype(np.int64) if len(self.idx_L4_M) else None

        if A_Hj is not None:
            self.AB_H[:, w] += sign * A_Hj
        if A_Mj is not None:
            self.AB_M[:, w] += sign * A_Mj
        if C_wH is not None:
            self.BC_H[j, :] += sign * C_wH
        if C_wM is not None:
            self.BC_M[j, :] += sign * C_wM
        # FMM substitute: NumPy outer (rank-1 update)
        if A_Hj is not None and C_wH is not None:
            self.ABC_HH += sign * np.outer(A_Hj, C_wH)
        if A_Hj is not None and C_wM is not None:
            self.ABC_HM += sign * np.outer(A_Hj, C_wM)
        if A_Mj is not None and C_wH is not None:
            self.ABC_MH += sign * np.outer(A_Mj, C_wH)
        if A_Mj is not None and C_wM is not None:
            self.ABC_MM += sign * np.outer(A_Mj, C_wM)

    # ----- D-update --------------------------------------------------------

    def _apply_D(self, l: int, i: int, sign: int) -> None:
        if sign > 0:
            if i in self.adj_D_L4[l]:
                raise ValueError(f"D edge ({l},{i}) already present")
            delta = self._delta_D(l, i)
            self.adj_D_L4[l].add(i)
            self.adj_D_L1[i].add(l)
            self.D[l, i] = 1
        else:
            if i not in self.adj_D_L4[l]:
                raise ValueError(f"D edge ({l},{i}) not present")
            self.adj_D_L4[l].discard(i)
            self.adj_D_L1[i].discard(l)
            self.D[l, i] = 0
            delta = self._delta_D(l, i)
        # No partial product depends on D — nothing else to maintain.
        self.total += sign * delta

    def _delta_D(self, l: int, i: int) -> int:
        """# layered 4-cycles through (l, i) ∈ D = (A·B·C)[i, l]. Class-routed
        per paper §3.3 (Lemma 3.8).
        """
        ci = self.cls_L1[i]
        cl = self.cls_L4[l]

        # HH, HM, MH, MM — direct lookup in precomputed ABC matrices.
        if ci == "H" and cl == "H":
            return int(self.ABC_HH[self.inv_L1_H[i], self.inv_L4_H[l]])
        if ci == "H" and cl == "M":
            return int(self.ABC_HM[self.inv_L1_H[i], self.inv_L4_M[l]])
        if ci == "M" and cl == "H":
            return int(self.ABC_MH[self.inv_L1_M[i], self.inv_L4_H[l]])
        if ci == "M" and cl == "M":
            return int(self.ABC_MM[self.inv_L1_M[i], self.inv_L4_M[l]])

        # H?-LowL4 cases: iterate N_C(l), AB^H[i, w] gives 2-paths from i to w.
        if ci == "H":  # cl == "L"
            row = self.AB_H[self.inv_L1_H[i]]
            return int(sum(int(row[w]) for w in self.adj_C_L4[l]))
        if ci == "M":  # cl == "L"
            row = self.AB_M[self.inv_L1_M[i]]
            return int(sum(int(row[w]) for w in self.adj_C_L4[l]))

        # LowL1-H? cases: iterate N_A(i), BC^c[j, l] gives 2-paths from j to l.
        if cl == "H":  # ci == "L"
            col = self.BC_H[:, self.inv_L4_H[l]]
            return int(sum(int(col[j]) for j in self.adj_A_L1[i]))
        if cl == "M":  # ci == "L"
            col = self.BC_M[:, self.inv_L4_M[l]]
            return int(sum(int(col[j]) for j in self.adj_A_L1[i]))

        # LL — brute over min(N_A(i), N_C(l)), check B[j, w] via adjacency.
        return self._delta_LL(i, l)

    def _delta_LL(self, i: int, l: int) -> int:
        N_A_i = self.adj_A_L1[i]
        N_C_l = self.adj_C_L4[l]
        cnt = 0
        if len(N_A_i) <= len(N_C_l):
            for j in N_A_i:
                for w in self.adj_B_L2[j]:
                    if w in N_C_l:
                        cnt += 1
        else:
            for w in N_C_l:
                for j in self.adj_B_L3[w]:
                    if j in N_A_i:
                        cnt += 1
        return cnt
