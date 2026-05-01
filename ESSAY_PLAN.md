# Essay plan — fully dynamic 4-cycle counting

Plan for our 10-page ACM sigconf essay based on Assadi & Shah, *An Improved Fully Dynamic Algorithm for Counting 4-Cycles in General Graphs using Fast Matrix Multiplication* (PODS 2025, article 091, arXiv 2504.10748v1, file `2504.10748v1.pdf`).

---

## 1. Locked decisions

| Decision | Value |
|---|---|
| Scope slice | **A — reduction + warm-up.** Cover §8 (general → layered), Appendix A (simple O(n)), and §3 (warm-up "A and C fixed" algorithm) in depth. Mention §5 (phases) at high level. Skip §6 and §7 entirely. |
| Own contribution | **Implementation + experiments.** Code the simple O(n) algorithm from Appendix A in Python (Go if performance forces it), benchmark against naive recompute, plot results. |
| Math density | We're comfortable; keep the FMM exponent ω(a,b,c), OMv conjecture, and the constraint system as first-class content. |
| Programming language | Python first; switch to Go only if Python is too slow to produce useful experiments. |

## 2. Scope — what is IN and what is OUT

### In scope (we own these)

- **The cyclic-join framing**: 4-cycle counting in 4-layered graphs ≡ size of `A(L₁,L₂) ⋈ B(L₂,L₃) ⋈ C(L₃,L₄) ⋈ D(L₄,L₁)`. This is the PODS-flavored framing.
- **The general → layered reduction** (paper §8): replicate V across 4 layers, run on layered graph; Claim 8.1 (3-walks = 3-paths) is provable in two paragraphs.
- **The simple O(n) algorithm** (paper Appendix A): maintain wedge counts; the pedagogical entry point and the thing we'll implement.
- **The warm-up O(m^{2/3−ε₁}) algorithm** (paper §3): vertex classes H/M/L and S/D, chunks, the data-structure table, rectangular FMM step.
- **Why FMM is critical and why the result is conceptually surprising**: any ω < 3 is *not* sufficient; we need ω < 2.5 − O(ε) (paper §5.1, Eq 9), which in particular requires ω < 2.5. 4-cliques have a combinatorial Ω(m) lower bound that *blocks* FMM speedups; 4-cycles only have Ω(m^{1/2}) which doesn't.
- **The OMv conjecture** as the source of the lower bound. Paragraph-level treatment.
- **The constraint system** (paper §3.4 Eqs 2, 5–8): state the system, verify feasibility *by hand at ω = 2* (where it reduces to checkable rationals — paper Appendix B p. 37). Cite [Bra]/[ADW+25] for the current-ω numerical case rather than reproducing it. (F11)
- **The implementation and its experimental story** (see §5 below).

### Out of scope (we mention or skip)

- The full main algorithm with phases (§5 of paper) — sketch, don't reproduce.
- §6 (tiny vertices, removing Assumption 1) — skipped.
- §7 (vertices moving between classes, removing Assumption 2) — skipped. This is most of the paper's technical depth, but it's bookkeeping, not new ideas.
- Detailed pseudocode for the warm-up's data-structure maintenance — describe in prose.
- Numeric optimization of ε to 0.0098109 / 1/24 — state the values, don't redo the constraint solver.

## 3. Section structure

Eight sections plus references. **The detailed content brief, including subsection-level breakdowns, ownership per section, figures, tables, theorem placements, and the dependency order for parallel drafting, is in [`SECTIONS.md`](./SECTIONS.md).** Use that file as the source-of-truth for scaffolding the LaTeX skeleton.

High-level summary:

1. **Introduction.** Hook, cyclic-join framing, state-of-the-art ladder (triangles tight, 4-cliques tight, 4-cycles had a gap, Assadi & Shah closed part of it), our contribution.
2. **Preliminaries.** Notation; layered graphs; FMM exponents ω and ω(a,b,c); OMv conjecture; dynamic-graph model.
3. **The cyclic-join equivalence.** General → layered reduction. **Proof 1** (Claim 8.1).
4. **A simple O(n) algorithm.** Paper Appendix A. **Proof 2** (Lemma A.1).
5. **The warm-up algorithm.** Vertex classes, chunks, data structures, the FMM step. **Proof 3** (Claim 3.6).
6. **The phases idea (sketch).** Why ω < 2.5 is required; state Theorem 1 of paper.
7. **Experiments.** The simple O(n) algorithm, implemented and benchmarked.
8. **Conclusion.** Recap, open questions.

Note: work distribution by section in `SECTIONS.md` supersedes the per-role table in §6 below — they are consistent, but `SECTIONS.md` has the granular ownership.

## 4. Formal proofs we'll include

Three proofs distributed across the essay. Order is from easy to harder:

| # | Where | Claim | Source in paper | Effort |
|---|---|---|---|---|
| 1 | §3 of essay | General → layered: 3-walks in G' = 3-paths in G | Claim 8.1 | Small (≤½ page) |
| 2 | §4 of essay | Simple algorithm correctness + O(n) update time | Lemma A.1 (+ Claims A.2, A.3) | Medium (≈¾ page) |
| 3 | §5 of essay | Warm-up: rectangular FMM step takes m^{ω(...)} time | Claim 3.6 | Medium (≈¾ page) |

Bonus material if space allows: re-derive that the constraint system (Eqs 2, 5–8) has feasible solutions — the algebra is short and shows the "complexity proof" character clearly.

## 5. The experiments — what we actually code

### 5.1 What we implement

**Algorithm 1 — Naive recompute (wedge-sum)**: on every edge update, recompute the 4-cycle count from scratch via the identity
`#4-cycles = (1/2) · Σ_v binomial(W(v), 2)`,
where `W(v)` is the number of wedges centred at `v`. Each recompute is O(n + m) to assemble W (one pass over the adjacency lists) plus O(n) to sum the binomials, giving O(n + m) per update. **Single fixed baseline; no algorithm switching across graph sizes** (F10). Brute force is used only as a tiny-graph (n ≤ 50) correctness oracle, never as the reported baseline.

**Algorithm 2 — Simple O(n)** (paper Appendix A): maintain a wedge-count matrix W[u,v] = #wedges between u and v. On edge update (u, v):
- Compute Δ(#4-cycles) = Σ_{w ∈ N(u)} W[w, v] (no correction term — paper Claim A.3 establishes correctness via the update-order rule below).
- Update W: for each w ∈ N(u), W[w, v] ± 1; symmetrically for N(v).
- **Update-order rule**: insert ⇒ query first, then update W. Delete ⇒ update W first, then query. This keeps (u,v) absent from W during the query.
- Both steps are O(n).

This is the algorithm whose correctness/complexity we prove formally in §4 of the essay.

### 5.2 Datasets

- **Synthetic Erdős–Rényi G(n, p)**: vary n ∈ {100, 500, 1000, 2000} for *both* algorithms (so timings are comparable), with three densities (m ≈ n^{1.3}, n^{1.5}, n^{1.7}). For Simple-Wedge only, also run n = 5000 to show its scaling.
- **Synthetic Barabási–Albert** (preferential attachment): one or two sizes for shape comparison.
- **Real-world graph** (Simple-Wedge only): one *small* SNAP graph such as `ca-GrQc` (n ≈ 5k, m ≈ 14k). Larger graphs like `email-Enron` (n ≈ 36k) are infeasible: the dense wedge matrix is ~5 GB at that scale (F9). Note this honestly in §7.1 of the essay.
- Update streams: random insertion-only, mixed 50/50 insert/delete (after a build-up phase).

### 5.3 What we measure

1. **Update time vs n** at fixed density. Confirm the O(n) curve for the dynamic algorithm and the O(m·n) or O(m²) curve for naive recompute.
2. **Crossover point**: at what update-stream length does maintaining the wedge matrix become cheaper than recomputing?
3. **Memory cost** of the wedge matrix (n² entries) — when does this become impractical?
4. **Sensitivity to insertion/deletion ratio**: does heavy-deletion behave differently from heavy-insertion?
5. **Sanity check**: on small graphs, verify the output of both algorithms matches at every step.

### 5.4 Deliverables from the experiment

- One figure: log-log plot of update time vs n for both algorithms across densities.
- One figure: crossover-point plot.
- One small table: real-world graph numbers.
- ≈150–300 LOC of Python in `code/` directory of the project. Keep it readable — graders may glance at it.

### 5.5 Engineering notes

- Use `numpy` for the wedge matrix (dense array). For n ≤ 5000 this is ~25M entries × 4 bytes = 100 MB, fine.
- For larger n, switch to sparse — but stay in Python first; only escape to Go if a single experiment takes >10 minutes.
- Don't bother implementing the warm-up §3 algorithm with chunks and FMM — that's a multi-week engineering project on its own and not what the seminar asks for.

## 6. Work distribution

| Role | Person | Owns |
|---|---|---|
| Lead / Editor | A | LaTeX skeleton on Overleaf, §1, §8, glue, references, EasyChair submission |
| Background | B | §2 (preliminaries), §3 (cyclic-join equivalence + Proof 1), §4 (simple algorithm + Proof 2) |
| Theory | C | §5 (warm-up algorithm + Proof 3), §6 (phases sketch), checks the math elsewhere |
| Contribution | D | The implementation and §7 (experiments). Owns `code/` directory and figures. |

Everyone reads the paper fully. Only writing ownership is split.

## 7. Reading guide

A focused order of attack on the paper:

1. **Pages 1–6** (intro): the whole story. Re-read until comfortable.
2. **Pages 6–7** (preliminaries): notation. Skim, refer back.
3. **Page 35** (Appendix A — simple algorithm): everyone groks this. It's the implementation target.
4. **Pages 7–12** (§3 warm-up): the technical centerpiece. C reads with pen and paper; everyone else reads to understand the *shape* (vertex classes, chunks, FMM step).
5. **Pages 29–30** (§8 reduction): tiny, two-paragraph proof. Read once.
6. **Pages 14–15** (§5.1 phases setup): just enough to write the §6-of-essay sketch.
7. Skim the rest. Don't read §6 or §7 of the paper unless curious.

References to read for context:
- [HHH22] (Hanauer–Henzinger–Hua): the prior O(m^{2/3}) result.
- [KNN+20]: the matching upper bound for triangles.
- [HKNS15]: the OMv lower bound.
- [AYZ97] (Alon–Yuster–Zwick): the static FMM-based cycle counting that inspires the dynamic version.

## 8. Risks (just so they're named)

- **Implementation eats the whole project.** Budget ≤ 1 week of part-time work for D. If experiments aren't producing useful plots by then, ship what we have.
- **Page count blows past 10.** Cut the §6 phases sketch first (it's a nice-to-have); cut figure captions next. Section 5 of the essay is non-negotiable.
- **Math gets opaque in §5 of essay.** Keep one walked-through claim (Claim 3.6) instead of trying to cover all of §3.2–§3.4 of the paper. The reader's takeaway should be "FMM enters here, and the constraint system has a positive solution," not full mastery.
- **The reduction in §3 of essay feels redundant after the intro.** Make the intro motivate it but not redo it; §3 is where the formal statement and proof live.

## 9. What's not in this document

- A detailed week-by-week schedule (we'll work to scope, not to a fixed timeline).
- Exact page-count allocations per section (§3 above is a structure, not a contract).
- A specific paper format for the conference report — that's covered in `README.md`.
