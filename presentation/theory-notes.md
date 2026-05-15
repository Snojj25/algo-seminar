# Theory Notes — Counting 4-Cycles in Fully Dynamic Graphs

**Goal of this document.** Get any reader up to speed on everything the slides reference, in roughly the order the slides reference it. Self-contained: assumes only an undergraduate algorithms background (Big-O, graphs, matrices). No proofs — pointers to the paper where they live.

Read this once before the dry run. Each section maps to one or two slides.

---

## 1. The problem setting

### 1.1 Subgraph counting

Given a host graph `G = (V, E)` with `n = |V|` vertices and `m = |E|` edges, **subgraph counting** asks: how many copies of a small *pattern graph* `H` (triangle, 4-cycle, 4-clique, …) appear in `G`?

This is one of the oldest problems in algorithmic graph theory. Three motivating use cases:

- **Database query processing.** A conjunctive query whose body forms a cycle (e.g. `R(x,y) ∧ S(y,z) ∧ T(z,w) ∧ U(w,x)`) is a "cyclic join". Its answer size equals the number of copies of the corresponding cyclic pattern in the join graph.
- **Network analysis.** Counts of small motifs (triangles, 4-cycles) are clustering and structure indicators in social and biological networks.
- **Pattern detection generally.** Many algorithms reduce to "count this small thing".

### 1.2 Static vs. dynamic

In the **static** problem, `G` is fixed and we count once. In the **dynamic** problem, `G` evolves: edges are inserted and deleted over time, and after each update we want the current count.

Dynamic comes in flavours:

- **Incremental** — only insertions.
- **Decremental** — only deletions.
- **Fully dynamic** — both. *This is the strongest, and what we care about.*

### 1.3 Cost model: worst-case update time

For a dynamic algorithm we measure the time spent processing each update. Three notions of cost, from weakest to strongest:

- **Amortised** — average over a sequence of `T` updates. Some updates can be slow as long as most are fast.
- **Expected worst-case** — randomised version; we'll ignore.
- **Worst-case (deterministic)** — *every* single update finishes within the bound.

Databases want worst-case: a 1-second hiccup once every 1000 updates is a production incident, even with a great average. **All times in this talk are worst-case.**

### 1.4 The four-cycle problem

The 4-cycle (often written `C₄`) is the pattern of interest. A 4-cycle in `G` is a sequence of four distinct vertices `a-b-c-d-a` with all four edges present.

The fully-dynamic 4-cycle counting problem: maintain `#C₄(G)` exactly under edge insertions and deletions on a graph with `n` (fixed) vertices and `m` (current) edges.

---

## 2. The state of the art before 2025

### 2.1 The landscape of three patterns

| Pattern | Best worst-case update time | Reference |
|---|---|---|
| Triangle (3-cycle) | `O(√m)` | Kara–Ngo–Nikolic–Olteanu–Zhang 2020 |
| 4-clique | `O(m)` | folklore |
| **4-cycle** | **`O(m^{2/3})`** | Hanauer–Henzinger–Hua 2022 |

Triangles and 4-cliques sit at clean exponents. 4-cycles sit at a weird `2/3` exponent that nobody could budge for over a decade.

### 2.2 Why m^{2/3}? — the wedge-counting idea

A **wedge** is a 2-path: three vertices `u-x-v` with `u-x` and `x-v` edges. Wedges and 4-cycles are tightly linked: a 4-cycle through edge `(u,v)` corresponds to a length-3 path from `u` to `v` in `G \ {(u,v)}`.

The classical algorithm maintains a **wedge matrix** `W[u,v]` = the number of 2-paths between `u` and `v` whose midpoint is *low-degree*. Then when an edge `(u,v)` is inserted, the number of new 4-cycles is exactly `Δ = Σ_{w ∈ N(u)} W[w,v]` (with a correction for ordering, see paper §5.2). After computing this, `W` is updated to reflect the new edge.

**Why split high/low?** With threshold `m^{1/3}`:
- A low-degree vertex has degree `≤ m^{1/3}`. Updates through low-degree midpoints touch ≤ `m^{1/3} × m^{1/3} = m^{2/3}` entries.
- High-degree vertices are few (handshaking: there are at most `2m / m^{1/3} = 2m^{2/3}` of them). Their wedges fit in `(2m^{2/3})² = O(m^{4/3})` entries total, but per-update changes are still `O(m^{2/3})`.

So the update bound balances at `m^{2/3}` work per update. This is the **natural ceiling for combinatorial methods** working at this granularity.

### 2.3 The lower bound

Henzinger, Krinninger, Nanongkai, Saranurak 2015 showed: assuming the OMv conjecture (below), dynamic 4-cycle counting requires `Ω(m^{1/2-γ})` per update, for any constant `γ > 0`.

So there's a gap: `Ω(m^{1/2-γ})` lower bound, `O(m^{2/3})` upper bound. No combinatorial way to close it.

---

## 3. Tools you'll see on the slides

### 3.1 Fast matrix multiplication (FMM)

The **matrix multiplication exponent** `ω` is the smallest constant such that two `n × n` matrices can be multiplied in `O(n^{ω+ε})` time for every `ε > 0`. Strassen 1969 showed `ω ≤ 2.81`; the current best is **`ω < 2.371339`** (Alman–Duan–Williams 2025). It is widely conjectured that **`ω = 2`**, but nobody knows.

For *rectangular* products — multiplying an `n^a × n^b` matrix by an `n^b × n^c` matrix — write the cost as `n^{ω(a,b,c)+ε}`. At the conjectural `ω = 2`, this collapses to the trivial cost `max(a+b, b+c, a+c)` (just reading the larger pair of factors). Improved rectangular bounds are also known.

**Why FMM was thought useless in IVM.** FMM is *batched*: it multiplies two big matrices at once. Incremental view maintenance is *streaming*: edges come in one at a time. Naively, you'd have to recompute the whole product every update, which is `Ω(n^2)` just to read the matrices — far worse than `O(m^{2/3})`. Folklore conclusion: any FMM-based speedup must be amortised, and worst-case improvements must come from combinatorial techniques.

### 3.2 The OMv conjecture

The **Online Matrix-Vector multiplication** conjecture: an algorithm preprocesses an `n × n` Boolean matrix `M` in polynomial time, then receives vectors `v₁, v₂, …` one at a time and must output `M v_i` before seeing `v_{i+1}`. The conjecture: no algorithm solves this in total time `O(n^{3-γ})` for any `γ > 0`.

OMv implies the `Ω(m^{1/2-γ})` lower bound for 4-cycle counting. It also implies similar lower bounds for many dynamic problems. We don't use OMv anywhere in our proofs — it's just the source of the lower bound we cite on the landscape slide.

---

## 4. The 2025 breakthrough (Assadi–Shah)

Assadi and Shah at PODS 2025 broke the `m^{2/3}` barrier:

> **Theorem (Assadi–Shah).** There is a fully dynamic algorithm maintaining the exact 4-cycle count with worst-case update time `O(m^{2/3-ε})` for a constant `ε > 0`, using fast matrix multiplication.

With current FMM bounds, `ε ≈ 0.0098`. At the conjectural `ω = 2`, **our Lemma** gives `ε = 1/24 ≈ 0.0417`.

### 4.1 How they get around the FMM-vs-streaming problem: phases

The key idea is to organise updates into **phases** of `m^{1-δ}` consecutive updates, for a small constant `δ > 0`. During a phase, three things happen concurrently, all respecting the same per-update worst-case budget:

1. **Queries are answered using the *previous* phase's precomputed products**, combined with on-the-fly evaluation against the updates accumulated so far in the current phase.
2. **The next phase's matrix product is computed in pieces**, amortised across the `m^{1-δ}` updates of the current phase. Each update does an `O(m^{2/3-ε})` share of the work.
3. **The wedge-matrix-style bookkeeping** is maintained incrementally for the parts that don't need FMM.

By the time the phase ends, the new product is ready, and the next phase can use it as its "previous phase data". This is what reconciles batched FMM with worst-case update bounds.

### 4.2 Degree classes (more than just high/low)

Where the classical algorithm had two classes (high / low), Assadi–Shah needs three:

- **High** — degree `≥ m^{2/3-ε₁}`. There are at most `m^{1/3+ε₁}` of these.
- **Medium** — degree in `(m^{1/3+ε₁}, m^{2/3-ε₁})`.
- **Low** — degree `≤ m^{1/3+ε₁}`.

Within each, a further "Dense / Sparse" partition based on a second threshold `m^{1/3-ε₂}` (this is about how many neighbours land in each class).

The two small constants `ε₁` and `ε₂` are *parameters of the algorithm*. They have to satisfy a system of inequalities for the analysis to go through. The third parameter `ε` is the improvement in the exponent — also constrained.

### 4.3 The constraint system (Section 7 of our paper)

The analysis bound reduces to five inequalities relating `ε`, `ε₁`, `ε₂`, and `ω`:

1. **Low-Dense FMM** (Eq. 5 in Assadi–Shah): the rectangular product `A^{L*} · B_{ℓ,DD}` of shape `(2/3+2ε, 1/3-ε₁+ε₂, 1/3-ε₁+ε₂)` must fit in the chunk budget `4/3 - 2ε₁`. **This is the only ω-dependent constraint.**
2. **High-High FMM** (Eq. 2): a square-ish product on high-degree vertices. Slack at the values we use.
3. **SS/SD threshold** (Eq. 6): `3ε₁ + 2ε ≤ ε₂`. Algebraic; no FMM.
4. **Threshold ordering** (Eq. 7): `ε₁ ≤ 1/6`.
5. **Threshold ordering** (Eq. 8): `ε₁ - ε₂ ≤ 1/3`.

If `ε₁ > 0` is to be achievable, constraint 1 must have room — and this is exactly where FMM cost gives slack vs. the trivial `O(n²)` bound. Remove FMM (set `ω = 3`) and constraint 1 forces `ε₁ = 0`, collapsing the bound back to `O(m^{2/3})`.

### 4.4 Our Lemma: closed-form solution at ω = 2

We give explicit rational values satisfying all five constraints at the conjectural `ω = 2`:

> `ε₁ = 1/24`, `ε₂ = 5/24`, `ε = 1/24`.

Of the five constraints, **two bind with equality**: the Low-Dense FMM constraint (the ω-dependent one) and the SS/SD threshold. The other three have slack.

This is more informative than the existing numerical verification because it shows transparently which constraint is load-bearing: the FMM one. If you removed FMM from the algorithm, the bound would collapse. So FMM is *essential*, not just incidental.

---

## 5. The cyclic-join lens

This is our re-presentation framing — the "we open the black box" angle of the talk.

### 5.1 4-layered graphs and cyclic joins

A **4-layered graph** has vertex set `V = L₁ ∪ L₂ ∪ L₃ ∪ L₄` with edges only between consecutive layers `L_i, L_{i+1}` (and `L₄ → L₁` closing the cycle). The four edge sets are biadjacency matrices `A, B, C, D`.

A **layered 4-cycle** is a closed sequence `a → b → c → d → a` visiting one vertex per layer.

**Cyclic-join correspondence.** The four-way cyclic join `J = A ⋈ B ⋈ C ⋈ D` over the four attribute domains `L₁, …, L₄` is a database query whose answer size equals the number of layered 4-cycles. (See Slide 2 / paper Fig. 1.)

This is well-known in database theory. The reason it's useful here: it lets us describe the algorithm as a database operation, which makes the rectangular FMM step look natural — it's just a join evaluation.

### 5.2 Lifting a general graph

Given a general graph `G = (V, E)`, build a 4-layered graph `G' = (V × {1,2,3,4}, E')` by replicating each vertex four times. Each edge `(u, v) ∈ E` is lifted into **all four** biadjacency matrices `A, B, C, D`. A 4-cycle in `G` corresponds bijectively to a layered 4-cycle in `G'`.

So *every* fully dynamic 4-cycle problem on a general graph reduces to a fully dynamic layered 4-cycle problem on a 4-layered graph, with a constant-factor blow-up.

### 5.3 The update protocol

Critically, a single update `(u, v)` in `G` becomes **four** updates in `G'`, one per matrix. The *order* matters:

- **Insertion:** insert into `D`, then `C`, then `B`, then `A`.
- **Deletion:** delete from `A`, then `B`, then `C`, then `D`.
- **Query:** read off the count immediately after the `D`-update, before any subsequent `A, B, C` updates.

This protocol guarantees: at query time, the edge `(u, v)` is **present in `D` but absent from `A, B, C`**. That asymmetry is exactly what forces every length-3 walk counted by the algorithm to be a length-3 *path* (no vertex repeats) in the underlying graph. Without it, a walk could revisit `u` or `v` via the freshly written edge and the count would over-report.

### 5.4 Why this lens helps

In the cyclic-join framing:

- "Where does each matrix appear?" → directly in the biadjacency partition.
- "Where does FMM live?" → in the join evaluation step `A^{L*} · B_{ℓ,DD}`.
- "What does each ε mean?" → degree thresholds on each layer.

It makes the architecture visible. The original Assadi–Shah presentation is a 30-page tour de force; the lens compresses the load-bearing structure to a few pictures and a 5-line lemma.

---

## 6. The empirical study

### 6.1 What we built

A faithful-in-shape Python implementation of the **restricted variant** of the algorithm — the simpler version where the two matrices `A` and `C` are frozen (no updates), reducing the full algorithm to its core warm-up. Same data structures, same chunk-based maintenance, same rectangular FMM step, but **NumPy GEMM substituting for FMM**.

Why GEMM and not actual FMM? Because production FMM implementations don't exist below `ω ≈ 2.81` (Strassen). NumPy uses a cache-optimised `O(n³)` BLAS routine. The asymptotics are *worse* than the theoretical FMM, but the *shape* of where the win comes from depends on the algorithm's structural decisions (degree partitioning, chunk strategy), not on the inner matrix-multiply primitive.

### 6.2 The baseline

We compare against a **layer-aware Simple-Wedge** baseline: a clean `O(n)` wedge-counting algorithm adapted to operate on the 4-layered graph directly, maintaining a single wedge matrix `W` per layer pair.

This is the natural baseline because:

- It's what the algorithm *replaces*, structurally.
- It captures the wedge-counting idea from §2.2 without the class-routing machinery.
- It is also `O(n)` per update — fair comparison in algorithmic shape.

### 6.3 Input regimes

Four input regimes tested:

1. **Erdős–Rényi** (random, no structure).
2. **Unilateral hub** — high-degree vertices clustered on one side of the cyclic ordering.
3. **Bilateral hubs** — high-degree vertices on *both* sides (`L₁` and `L₄`).
4. **No hubs** — uniform low degree.

### 6.4 The finding

The class-routing machinery (the warm-up algorithm) beats the wedge baseline **only in the bilateral-hub regime**. On the other three, the wedge baseline matches or beats it — the routing overhead isn't worth it.

This is the structural counterpart to the algebraic feasibility result. The Lemma says "the FMM step is the load-bearing one". The experiment says "the FMM step fires when there are bilateral hubs". Same pressure point, two angles.

---

## 7. Quick reference: notation cheat sheet

- `m` = number of edges; `n` = number of vertices.
- `O(·)`, `Ω(·)` — asymptotic upper / lower bound.
- `ω` — matrix multiplication exponent; `ω(a,b,c)` — rectangular version.
- `ε`, `ε₁`, `ε₂` — small constants in the Assadi–Shah analysis.
- `δ` — phase length parameter (phases of length `m^{1-δ}`).
- `γ` — slack constant in the OMv lower bound `Ω(m^{1/2-γ})`.
- `W[u,v]` — wedge matrix entry.
- `A, B, C, D` — biadjacency matrices of the 4-layered graph.
- `L₁, …, L₄` — vertex layers.
- `A^{L*}` — the "rows of `A` indexed by low-degree vertices in `L₁`".
- `B_{ℓ,DD}` — the "Dense-Dense block of `B` in chunk `ℓ`".
- IVM — Incremental View Maintenance (database term for the dynamic-maintenance setting).
- GEMM — General Matrix Multiply (the BLAS routine NumPy calls).
- FMM — Fast Matrix Multiplication (any algorithm running in `n^{ω + o(1)}` time).
- OMv — Online Matrix-Vector multiplication.

---

## 8. Where to look in the paper

| Topic | Section in `paper/main.tex` |
|---|---|
| Problem statement | §1 (Introduction) |
| Wedge-counting idea | §5 |
| Hanauer–Henzinger–Hua | §2.3 |
| FMM/OMv background | §3.3–3.4 |
| 4-layered graph construction | §4 |
| Update protocol | §4.2 |
| Restricted variant (warm-up) | §6 |
| Constraint system + closed-form lemma | §7 |
| Phases and the full algorithm | §8 |
| Experiments | §9 |

---

## 9. Likely audience questions, with one-line answers

- *Why isn't `ω = 2` known to be true?* — Open since the 1960s. Strongest current bound is `ω < 2.371339`.
- *Doesn't `Ω(m^{1/2-γ})` mean you can't get below `m^{1/2}`?* — Right, but the gap to `m^{2/3-ε}` is still huge; nobody knows where the true bound is.
- *Is your closed-form proof using anything Assadi–Shah didn't?* — No, same five constraints. We just pick rational values that satisfy them at `ω = 2` and check by hand.
- *Why is NumPy GEMM defensible if it's not actually FMM?* — Because we're testing structural decisions about input partitioning, not the inner multiply. The shape of the win is robust to the choice of matrix kernel.
- *What's the practical takeaway?* — If your IVM workload has bilateral structural hubs on cyclic joins, the algorithm's machinery is worth it. Otherwise, a wedge-counting baseline is competitive.
