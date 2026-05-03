# Experiments plan — fully dynamic 4-cycle counting

Spec for the implementation + benchmark phase. Self-contained; hand to a coding agent and they should be able to execute end-to-end. Source paper: Assadi & Shah, PODS 2025, *Improved Fully Dynamic 4-Cycle Counting via FMM* (arXiv 2504.10748, file `paper/2504.10748v1.pdf`). We implement two baselines (Naive, Simple Wedge), a sparse-hashmap extension of Simple Wedge, **and a simplified version of the paper's §3 warm-up algorithm**. The §5 phase machinery and the §6/§7 bookkeeping that removes the paper's two simplifying assumptions are out of scope.

---

## 0. The story we're telling — read this first

The paper has four algorithms in increasing complexity:

1. **Naive recompute** — O(n^ω) or O(nm) per update via path-pair matrix.
2. **Simple Wedge** (paper Appendix A) — O(deg(u)+deg(v)) ≤ O(n) per update, O(n²) memory.
3. **Warm-up §3** — O(m^{2/3 − ε₁'}) per update worst-case, using vertex classes + rectangular FMM.
4. **Main §5** — O(m^{2/3 − ε₁}) per update, ε₁ ≈ 0.042; phases on top of (3).

We implement (1), (2), and **a faithful but simplified version of (3)**. "Simplified" means two specific concessions — neither hidden, both stated in the paper §7 prose:

- **Assumptions 1 and 2 fixed by construction.** Vertex degree-class assignments are decided at construction time and the stream generator refuses any update that would change them. We do not implement §6/§7 of the paper, which is the bookkeeping that removes these assumptions.
- **NumPy `@` substitutes for fast rectangular matrix multiplication.** No practical implementation of fast rectangular FMM exists at the n we test (Strassen needs n in the thousands to even break even with BLAS GEMM; rectangular fast algorithms have impractical constants). This is a fundamental honesty constraint, not a budget choice. We document this exactly once in `code/README.md` and once in paper §7.7.

What this lets us measure:

- (a) Empirical asymptotic curves for Naive and Simple on Erdős–Rényi, with fitted slopes — confirms textbook theory.
- (b) **The regime where the §3 warm-up wins**: graphs with hub vertices, where Simple degrades to its O(n) worst case and §3's vertex-class machinery delivers a real speedup *even with cubic matmul*. The win at our scale comes from avoiding O(n) per-update enumeration of a hub's neighborhood, not from FMM exponents.
- (c) Crossover analysis: at what stream length does maintaining a wedge matrix beat from-scratch?
- (d) Memory cliff and the sparse-hashmap rescue on real-world graphs.
- (e) Update-order rule correctness for Simple Wedge.

What this does **not** let us measure (and we say so):

- The paper's actual headline gain m^{2/3} → m^{2/3 − ε₁}. With NumPy matmul, our Warmup_v3 has a strictly worse exponent than paper §3's claim; what we benchmark is "§3 with cubic matmul", not "§3 with FMM".
- Behaviour under streams that change vertex degree classes.
- The phase machinery (§5).

The headline experiment is §3.6 (Warmup_v3 vs Simple on adversarial graphs). Everything else is supporting evidence. If §3.6 fails to produce a clear separation, that is itself a publishable negative result — we report it honestly.

---

## 1. Algorithms (binding specs)

All four counters expose the same interface (Warmup_v3 has a richer constructor — see §1.4):

```python
class Counter:
    def __init__(self, n: int, **kwargs) -> None: ...
    def insert(self, u: int, v: int) -> None: ...
    def delete(self, u: int, v: int) -> None: ...
    def count(self) -> int: ...
```

### 1.1 Naive Recompute (`naive_recompute.py`)

State: adjacency lists only. On every update, apply the change, then recompute via the path-pair identity:

```
P = A @ A                            # length-2 path matrix, n×n
np.fill_diagonal(P, 0)
deg = A.sum(axis=1)
n_c4 = (np.sum(P*P) - 2*np.sum(deg*(deg-1)//2)) // 8
```

Equivalently `#C4 = (1/2) [Σ_{u<w} P[u,w]² − Σ_v binom(deg(v),2)]`. The deg-binom term subtracts paths u→v→u (which P counts as `deg(v)` length-2 paths). Implementer: comment the derivation in 3 lines and unit-test against brute force on n=20.

Per-update cost: O(n^ω) via NumPy GEMM (dense) for n ≤ 2000; switch to `scipy.sparse` matmul above that.

### 1.2 Simple Wedge (`simple_wedge.py`) — paper Appendix A

State: adjacency lists + dense `W: np.ndarray[int32]` of shape `(n, n)`, where `W[a,b]` = current count of length-2 paths from `a` to `b`. `W[a,a]` is irrelevant; keep it 0.

`insert(u, v)`:
1. **Query first** (W still pre-update): `delta = sum(W[w, v] for w in adj[u] if w != v)`.
2. Update `W`: for each `w ∈ adj[u], w ≠ v`: `W[w, v] += 1; W[v, w] += 1`. Symmetrically for `adj[v]` updating `W[w, u]; W[u, w]`.
3. Append edge to adjacency.
4. `total += delta`.

`delete(u, v)`:
1. Remove edge from adjacency first.
2. **Update W**: decrement using new adjacency (mirror image of insert step 2).
3. **Then query**: `delta = sum(W[w, v] for w in adj[u])`.
4. `total -= delta`.

Expose the order rule as `--ordering={correct,swapped}` for experiment §3.5.

Per-update cost: O(deg(u) + deg(v)).

### 1.3 Sparse Wedge (`sparse_wedge.py`) — our small extension

Same algorithm, replace `W` with `defaultdict(Counter)`. Memory: O(#nonzero W entries). Same asymptotics, larger constants. The only variant that runs on `email-Enron`-scale graphs in our setup.

### 1.4 Warm-up §3 (`warmup_v3.py`) — the paper's algorithm, simplified

Implements the algorithm of paper §3 (pages 7–13 of `2504.10748v1.pdf`) under fixed Assumptions 1+2. **The implementer must read paper §3 directly; this section gives the interface, the simplifying contract, and the substitutions, not the full algorithm.**

Operates on the **4-layered model**: a graph G with layers L₁, L₂, L₃, L₄ and biadjacency matrices `A: L₁×L₂`, `B: L₂×L₃`, `C: L₃×L₄`, `D: L₄×L₁`. A query returns `trace(A B C D)`, the count of length-4 cycles in G.

```python
class WarmupV3Counter:
    def __init__(
        self,
        sizes: tuple[int, int, int, int],   # |L1|, |L2|, |L3|, |L4|
        classes_14: np.ndarray,             # length |L1|+|L4|; values in {'H','M','L'}
        classes_23: np.ndarray,             # length |L2|+|L3|; values in {'S','D'}
        m_estimate: int,                    # used to pick degree thresholds
    ) -> None: ...

    def insert(self, layer_pair: int, u: int, v: int) -> None: ...
    def delete(self, layer_pair: int, u: int, v: int) -> None: ...
    def count(self) -> int: ...
```

Vertex classes are passed in fixed at construction. **Updates that would change a vertex's class (i.e. push its degree across a threshold) raise `ClassStabilityError`.** This is how Assumptions 1+2 are encoded; we generate streams that respect them.

Threshold defaults (from paper §3.4 with ω=2 substitution; tweak when you read §3.4 carefully):
- L₁/L₄ split: H if deg ≥ m^{2/3}; M if m^{1/3} ≤ deg < m^{2/3}; L if deg < m^{1/3}.
- L₂/L₃ split: D if deg ≥ m^{1/2}; S otherwise.

Per-update logic — paper §3.2/3.3, with these exact substitutions:

- Replace every "fast (rectangular) matrix multiplication" call with `numpy.matmul` (or `numpy.einsum` for tensor-style contractions). Mark each such call with a `# FMM substitute: NumPy GEMM` comment and a citation to the paper page.
- Maintain the **data-structure table** (paper Table 2). Implementer: in `WarmupV3Counter.__init__`, enumerate every entry of that table as a named instance attribute with a one-line comment pointing to its row in paper Table 2. This makes the maintenance code traceable to the paper.
- The chunk-based batched updates from paper §3.3: for our purposes, set `chunk_size = 1` (every update flushes immediately). This sacrifices some asymptotic refinement but is dramatically simpler and still demonstrates the vertex-class win.

Honesty docstring at the top of the file (mandatory):

```python
"""
warmup_v3.py — simplified §3 warm-up of Assadi & Shah (PODS 2025).

This is NOT a faithful realisation of the paper's algorithm. Specifically:
  - Assumptions 1 and 2 are fixed at construction time. Updates that would
    cross a class threshold raise ClassStabilityError.
  - Fast rectangular matrix multiplication is substituted with NumPy GEMM.
    The asymptotic exponent is therefore strictly worse than the paper's
    O(m^(2/3 − ε₁')) claim. Per-update cost in this file is dominated by
    cubic matmul over reduced submatrices of size determined by vertex
    classes; the win over Simple Wedge at our scale comes from class-based
    work avoidance, not FMM.
  - Chunk size is fixed at 1 (no batched flushes).
  - §5 (phases), §6 (tiny vertices), §7 (class changes mid-stream) are not
    implemented.

Page references in this file point to 2504.10748v1.pdf.
"""
```

LOC budget: target 400–600. If the file grows past 800, the implementer is over-fitting to the paper — flag and re-scope, do not silently expand.

### 1.5 Brute Force (`brute_force.py`)

O(n⁴) enumeration over 4-tuples / 8 to dedupe rotations and reflections. Refuses for n > 50. Correctness oracle in `tests/`.

---

## 2. Code layout

```
code/
├── algorithms/
│   ├── naive_recompute.py
│   ├── simple_wedge.py
│   ├── sparse_wedge.py
│   ├── warmup_v3.py            # paper §3, simplified, NumPy-GEMM-as-FMM
│   └── brute_force.py
├── graphs/
│   ├── generators.py           # ER, BA, random regular wrappers
│   ├── adversarial.py          # NEW — planted-hub, layered-hub-bipartite
│   ├── snap_loader.py          # parse SNAP edge-list .txt; cache as .npz
│   └── streams.py              # insert-only, mixed, hub-driven, class-stable
├── bench/
│   ├── runner.py               # single-cell timing harness; emits one CSV row
│   └── memory.py               # peak-RSS sampling
├── plots/
│   └── figures.py              # reads results/*.csv, writes figures/*.pdf
├── tests/
│   └── test_correctness.py     # all four counters in lockstep
├── data/                       # SNAP downloads, gitignored
├── results/                    # one CSV per experiment
├── figures/                    # PDFs that ../paper/main.tex pulls in
├── run_all.sh
├── requirements.txt            # numpy, scipy, networkx, matplotlib, pytest
└── README.md                   # includes the honesty/limitations block
```

Conventions: Python 3.11+, type hints on public methods, `--seed` everywhere randomness is used, all timings via `time.perf_counter` reporting median of 5 with IQR, every script invokable as a module (`python -m bench.runner …`).

---

## 3. Experiments

Run order: 3.0 (correctness gate) → 3.5 (order rule) → 3.1, 3.2, 3.3 in parallel → 3.4 → **3.6 (the headline)**.

Shipping priority if time runs short: 3.0, 3.1, 3.6 are non-negotiable. Drop in this order: 3.7 → 3.4 (real-world) → 3.3 (memory) → 3.2 (crossover) → 3.5.

### 3.0 Correctness gate

`pytest tests/`. 100 random seeds. For each: generate a random graph (general, n=20, p=0.2 for Naive/Simple/Sparse; layered with n_per_layer=15 and class-stable stream for Warmup_v3), build a length-100 update stream, run all relevant counters in lockstep, assert agreement at every step. Must pass before any timing experiment runs.

### 3.1 Asymptotic curves on ER (Figure 5)

**Question**: do empirical update times match O(n^ω) for Naive and O(deg) for Simple?

- Algorithms: Naive, Simple Wedge.
- Graphs: ER G(n, p) with `p = c · n^{γ−2}` so m ≈ n^γ. Densities γ ∈ {1.3, 1.5, 1.7}.
- Sizes: n ∈ {200, 500, 1000, 2000, 5000}. Naive may time out at n=5000; mark and continue.
- Workload: pre-build to 50% density, then 200 insertions, report median per-update time.
- Plot: log-log time vs n, 6 curves. Fit lines, report slopes.
- Acceptance: Simple slope ≈ γ−1 ± 0.3; Naive slope close to ω ≈ 2.4 (or sparse-matmul complexity).

### 3.2 Crossover (Figure 6)

**Question**: how long must an update stream be before maintaining the wedge matrix beats recomputing each time?

- Fixed graph: ER, n=1000, m=n^1.5 ≈ 31600.
- Stream lengths K ∈ {1, 10, 100, 1000, 10000, 100000}.
- Strategies: A = Naive recompute; B = Simple Wedge with one-shot O(n²) build cost amortised over K.
- Plot: total wall-clock vs K, log-log. Mark crossover K*.

### 3.3 Memory cliff (Figure 7)

**Question**: at what n does dense W become infeasible? Does sparse rescue it?

- Algorithms: Simple Wedge, Sparse Wedge.
- Graphs: ER with `p = 5/n` (sparse, m ≈ 2.5n).
- Sizes: n ∈ {1k, 2k, 5k, 10k, 20k, 50k}.
- Measure: peak RSS after building W on the full graph.
- Plot: peak memory vs n, two curves; annotate where dense exceeds 4 GB.

### 3.4 Real-world graphs (Table 3)

**Question**: throughput on actual graphs.

- Algorithm: Sparse Wedge only.
- Graphs: SNAP `ca-GrQc` (n=5242), `ca-HepTh` (n≈9877), `email-Enron` (n≈36692, attempt; OOM is a finding).
- Workload: hold out 10% of edges; run insert-only stream on top of the 90% pre-built.
- Report: n, m, throughput, peak memory, final count. Cross-check `ca-GrQc` against an offline NetworkX 4-cycle count.

### 3.5 Update-order rule (one number in §7.6)

**Question**: does swapping query/update order break correctness?

- Algorithm: Simple Wedge with `--ordering=swapped`.
- Graph: n=30, ER p=0.3, 50-update stream.
- Plot or sentence: cumulative absolute count error vs update index; swapped diverges within ~5 updates, correct stays at 0.

### 3.6 NEW — Warmup_v3 vs Simple Wedge on adversarial graphs (Figure 8) — *the headline*

**Question**: on graphs designed to force Simple Wedge into its O(n)-per-update worst case, does the §3 warm-up (with cubic NumPy matmul standing in for FMM) actually win in wall-clock terms?

- Algorithms: Simple Wedge, Warmup_v3.
- Graphs: **planted-hub layered graphs** generated by `graphs/adversarial.py::layered_hub(n_per_layer, k_hubs, p_low, seed)`. Construction:
  - 4 layers of `n_per_layer` vertices each.
  - In each of L₁ and L₂, plant `k_hubs` hub vertices with degree Θ(n) toward the next layer.
  - Remaining vertices have low degree (≈ 5).
  - Class assignments computed once at graph build and frozen.
- Workload: 200 insertions, of which ≥75% touch a hub vertex (`streams.hub_biased(graph, hub_bias=0.75)`). Stream is constrained to never push a vertex across a class boundary; generator asserts this on every step.
- Sizes: n_per_layer ∈ {200, 500, 1000, 2000}; k_hubs = 5.
- Measure: median per-update time, both algorithms.
- Plot: log-log per-update time vs n_per_layer, two curves. Expectation: Simple scales as Θ(n) (its worst case); Warmup_v3 scales sub-linearly because hub-touching updates use the matmul-batched class path rather than per-neighbor enumeration.
- Acceptance: a visible separation at n=2000 — Warmup_v3 ≥ 2× faster than Simple. Anything weaker is published as a *negative result* with the caveat about cubic matmul.

#### 3.6.1 Robustness sub-experiment

Rerun Warmup_v3 vs Simple on the ER graphs of §3.1, fixed n=1000, three densities. Expect Simple to win because ER has no hubs and Warmup_v3 carries matmul overhead. **Honest reporting; this matters as much as 3.6 itself.**

### 3.7 Stretch (only if 3.0–3.6 land with time to spare)

- Sweep `k_hubs` at fixed `n_per_layer`: at what hub count does §3 break even?
- BA preferential-attachment graph: does its natural skew put us in §3's regime?
- Profile breakdown of Warmup_v3: matmul vs class bookkeeping vs adjacency.

---

## 4. Datasets

| Source | Generator / file | Sizes | Used in |
|---|---|---|---|
| Erdős–Rényi | `networkx.erdos_renyi_graph` | n ∈ [200, 50k] | §3.1, §3.3, §3.6.1 |
| **Planted-hub layered** | **`adversarial.layered_hub`** | **n ∈ [200, 2000], k=5** | **§3.6 (headline)** |
| Barabási–Albert | `networkx.barabasi_albert_graph` | n=5000 | §3.7 |
| SNAP `ca-GrQc` | edge list | n=5242 | §3.4 |
| SNAP `ca-HepTh` | edge list | n≈9877 | §3.4 |
| SNAP `email-Enron` | edge list | n≈36692 | §3.4 |

Download via `code/data/download.sh`; cache locally; re-running is a no-op.

---

## 5. Deliverables to the paper

| ID | Content | Source | Goes into paper section |
|---|---|---|---|
| Fig 5 | log-log update-time vs n, Naive + Simple, fitted slopes | §3.1 | §7.2 |
| Fig 6 | total time vs stream length K, crossover marked | §3.2 | §7.3 |
| Fig 7 | peak memory vs n, dense + sparse | §3.3 | §7.4 |
| Tab 3 | real-world results | §3.4 | §7.5 |
| One number | swapped-order divergence index | §3.5 | §7.6 |
| **Fig 8** | **Warmup_v3 vs Simple on planted-hub graphs** | **§3.6** | **§7.7 (new headline subsection)** |

Paper structure note: a new §7.7 ("Where the paper's algorithm wins — and the FMM caveat") is needed. Flag this when integrating; current paper has §7.1–§7.6.

---

## 6. Acceptance criteria

1. `pytest tests/` passes with all four counters in lockstep.
2. `bash run_all.sh` reproduces every CSV and PDF from a clean checkout in ≤ 3 hours on a recent laptop. Hard ceiling per cell: 10 minutes; cells exceeding it are marked `TIMEOUT` in the CSV.
3. ≤ 1000 LOC total across `algorithms/`, `graphs/`, `bench/`, `plots/`. `warmup_v3.py` ≤ 600 LOC; if it grows past 800 the implementer must re-scope and ask, not silently expand.
4. Every parameter is a CLI flag or a `config.yaml` entry. No magic constants in `__main__` blocks.
5. `figures/` outputs are deterministic given a seed.
6. **Honesty block** in `code/README.md`: a labelled "Limitations" section listing (a) NumPy-as-FMM, (b) Assumptions 1+2 fixed by construction, (c) §5 phases and §6/§7 not implemented, (d) at our n, the §3.6 win comes from class-based work avoidance, not FMM exponents. The same prose appears in paper §7.7.

---

## 7. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Warmup_v3 implementation eats the whole budget | Time-box: 5 working days for runnable + correct. If not running by day 5, fall back to baseline-only plan (drop §3.6, paper §7.7), document loudly. |
| Cubic matmul overhead dominates and Warmup_v3 loses on adversarial graphs too | Publishable as a *negative result*: "with cubic matmul standing in for FMM at n ≤ 2000, vertex-class savings are absorbed by GEMM constants." Reframe §7.7 around this finding. |
| Class-stability constraint silently violated | `streams.py` asserts on every update that no class would change; raises `ClassStabilityError` immediately. |
| Implementer over-engineers Warmup_v3 chasing the paper's full result | Hard limit: 800 LOC. Past that, stop and ask. |
| `email-Enron` OOMs everywhere | Document the failure mode; do not rescue. |

---

## 8. Out of scope — do not implement

- The full §5 main algorithm (phases, deeper class structure, ε₁ optimisation).
- §6 (tiny vertices) and §7 (class changes mid-stream) of the paper.
- Real fast rectangular matrix multiplication (no Strassen, no asymptotic-FMM library, no GPU FMM tricks).
- The general → layered reduction at runtime; we work in the layered model directly. Document the reduction in the paper without coding it.
- Refactors for "clean architecture". Code is read once.

If something seems missing or under-specified, **ask before inventing**. Default: pick the simpler option, document it in `code/README.md`, move on.
