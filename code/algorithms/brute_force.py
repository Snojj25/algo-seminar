"""
brute_force.py — O(n^4) 4-cycle enumeration. Correctness oracle only.

Refuses to operate for n > 50; not a baseline for any timing experiment.
"""

from __future__ import annotations


class BruteForceCounter:
    """Enumerate ordered 4-tuples of distinct vertices forming a 4-cycle.

    A 4-cycle has 8 automorphisms (4 rotations × 2 reflections), so we count
    ordered tuples (a, b, c, d) with edges {a,b}, {b,c}, {c,d}, {d,a} and
    divide by 8.
    """

    MAX_N = 50

    def __init__(self, n: int) -> None:
        if n > self.MAX_N:
            raise ValueError(
                f"BruteForceCounter refuses n={n} > {self.MAX_N}; "
                "use it only as a correctness oracle on small graphs."
            )
        self.n = n
        self.adj: list[set[int]] = [set() for _ in range(n)]

    def insert(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError("self-loops not allowed")
        self.adj[u].add(v)
        self.adj[v].add(u)

    def delete(self, u: int, v: int) -> None:
        self.adj[u].discard(v)
        self.adj[v].discard(u)

    def count(self) -> int:
        n = self.n
        adj = self.adj
        total = 0
        for a in range(n):
            Na = adj[a]
            for b in Na:
                for c in adj[b]:
                    if c == a:
                        continue
                    for d in adj[c]:
                        if d == a or d == b:
                            continue
                        if a in adj[d]:
                            total += 1
        # Each 4-cycle contributes 8 ordered tuples (4 rotations × 2 reflections).
        assert total % 8 == 0, "brute-force tuple count not divisible by 8"
        return total // 8
