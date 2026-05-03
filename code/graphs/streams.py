"""
streams.py — update streams over a fixed vertex set.

A stream is an iterable of operations (op, u, v) where op ∈ {"insert", "delete"}.
Streams are pure data; the runner applies them to all counters in lockstep.
"""

from __future__ import annotations

import random
from typing import Iterable


Op = tuple[str, int, int]


class ClassStabilityError(RuntimeError):
    """Raised when a stream operation would push a vertex across a class boundary."""


def insert_only(
    n: int,
    existing: Iterable[tuple[int, int]],
    n_ops: int,
    seed: int,
    pool: Iterable[tuple[int, int]] | None = None,
) -> list[Op]:
    """Sample n_ops insertions of new edges. If `pool` is given, draw from it
    (used for layered graphs where only certain pairs are valid). Otherwise
    draw from the complement of `existing` over the full vertex set.
    """
    rng = random.Random(seed)
    used = {(min(u, v), max(u, v)) for u, v in existing}
    ops: list[Op] = []

    if pool is not None:
        candidates = [e for e in pool if e not in used]
        rng.shuffle(candidates)
        if len(candidates) < n_ops:
            raise ValueError(
                f"pool exhausted: requested {n_ops} insertions, only "
                f"{len(candidates)} unused candidates available"
            )
        for u, v in candidates[:n_ops]:
            ops.append(("insert", u, v))
            used.add((u, v))
        return ops

    # Full vertex-set sampling with rejection.
    tries = 0
    while len(ops) < n_ops:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        e = (min(u, v), max(u, v))
        if e in used:
            tries += 1
            if tries > 100 * n_ops:
                raise RuntimeError("too many rejections; graph may be near-complete")
            continue
        used.add(e)
        ops.append(("insert", e[0], e[1]))
    return ops


def mixed(
    n: int,
    existing: Iterable[tuple[int, int]],
    n_ops: int,
    insert_frac: float,
    seed: int,
) -> list[Op]:
    """Random mix of insert/delete. State is tracked locally so we never
    insert an existing edge or delete a missing one. Approximate fractions.
    """
    rng = random.Random(seed)
    edges = {(min(u, v), max(u, v)) for u, v in existing}
    ops: list[Op] = []
    while len(ops) < n_ops:
        do_insert = rng.random() < insert_frac
        if do_insert:
            u, v = rng.randrange(n), rng.randrange(n)
            if u == v:
                continue
            e = (min(u, v), max(u, v))
            if e in edges:
                continue
            edges.add(e)
            ops.append(("insert", e[0], e[1]))
        else:
            if not edges:
                continue
            e = rng.choice(list(edges))
            edges.discard(e)
            ops.append(("delete", e[0], e[1]))
    return ops


def hub_biased(
    n: int,
    existing: Iterable[tuple[int, int]],
    hubs: Iterable[int],
    n_ops: int,
    hub_bias: float,
    seed: int,
    pool: Iterable[tuple[int, int]] | None = None,
    class_check: "ClassChecker | None" = None,
) -> list[Op]:
    """Insertion-only stream where each operation touches a hub vertex with
    probability hub_bias. Edges drawn from `pool` (if provided) or the full
    complement. If `class_check` is given, every produced operation is
    validated to keep all vertex classes stable.
    """
    rng = random.Random(seed)
    hubs_set = set(hubs)
    used = {(min(u, v), max(u, v)) for u, v in existing}

    if pool is None:
        all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    else:
        all_pairs = [(min(u, v), max(u, v)) for u, v in pool]

    hub_pool = [e for e in all_pairs if (e[0] in hubs_set or e[1] in hubs_set) and e not in used]
    nonhub_pool = [e for e in all_pairs if e[0] not in hubs_set and e[1] not in hubs_set and e not in used]
    rng.shuffle(hub_pool)
    rng.shuffle(nonhub_pool)

    ops: list[Op] = []
    hub_i = 0
    nonhub_i = 0

    def _next_from(pool_list: list, idx: int) -> tuple[tuple[int, int] | None, int]:
        while idx < len(pool_list):
            cand = pool_list[idx]
            idx += 1
            if cand in used:
                continue
            if class_check is not None and not class_check.allows_insert(*cand):
                continue
            return cand, idx
        return None, idx

    while len(ops) < n_ops:
        prefer_hub = rng.random() < hub_bias
        if prefer_hub:
            cand, hub_i = _next_from(hub_pool, hub_i)
            if cand is None:
                cand, nonhub_i = _next_from(nonhub_pool, nonhub_i)
        else:
            cand, nonhub_i = _next_from(nonhub_pool, nonhub_i)
            if cand is None:
                cand, hub_i = _next_from(hub_pool, hub_i)
        if cand is None:
            raise RuntimeError(
                f"hub_biased stream exhausted at {len(ops)}/{n_ops} ops "
                "(class-stability or edge-pool constraints too tight)"
            )
        used.add(cand)
        if class_check is not None:
            class_check.apply_insert(*cand)
        ops.append(("insert", cand[0], cand[1]))
    return ops


class ClassChecker:
    """Tracks current degrees and refuses operations that cross class
    thresholds. Used by hub_biased to filter the stream and by Warmup_v3 to
    enforce Assumption 1+2 at update time.

    classes: dict vertex -> class label (e.g. 'H', 'M', 'L', 'S', 'D').
    bounds:  dict class label -> (min_deg, max_deg) inclusive bounds.
    """

    def __init__(
        self,
        classes: dict[int, str],
        bounds: dict[str, tuple[int, int]],
        initial_degrees: dict[int, int],
    ) -> None:
        self.classes = classes
        self.bounds = bounds
        self.deg = dict(initial_degrees)
        for v, c in classes.items():
            d = self.deg.get(v, 0)
            lo, hi = bounds[c]
            if not (lo <= d <= hi):
                raise ClassStabilityError(
                    f"vertex {v} (class {c}) starts with deg={d}, "
                    f"outside bounds [{lo},{hi}]"
                )

    def _bounds_for(self, v: int) -> tuple[int, int]:
        return self.bounds[self.classes[v]]

    def allows_insert(self, u: int, v: int) -> bool:
        for x in (u, v):
            lo, hi = self._bounds_for(x)
            if self.deg.get(x, 0) + 1 > hi:
                return False
        return True

    def allows_delete(self, u: int, v: int) -> bool:
        for x in (u, v):
            lo, hi = self._bounds_for(x)
            if self.deg.get(x, 0) - 1 < lo:
                return False
        return True

    def apply_insert(self, u: int, v: int) -> None:
        if not self.allows_insert(u, v):
            raise ClassStabilityError(
                f"insert ({u},{v}) would push a vertex across a class boundary"
            )
        self.deg[u] = self.deg.get(u, 0) + 1
        self.deg[v] = self.deg.get(v, 0) + 1

    def apply_delete(self, u: int, v: int) -> None:
        if not self.allows_delete(u, v):
            raise ClassStabilityError(
                f"delete ({u},{v}) would push a vertex across a class boundary"
            )
        self.deg[u] -= 1
        self.deg[v] -= 1
