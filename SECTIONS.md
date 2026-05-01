# Section-by-section scope

Detailed content brief for each section of the essay. Designed so we can scaffold a LaTeX skeleton from this directly, then each section's owner fills in prose against the bullet list.

ACM sigconf is two-column, ~600 words per page. Targets below are guidance, not contracts.

Source paper: Assadi & Shah, *An Improved Fully Dynamic Algorithm for Counting 4-Cycles in General Graphs using Fast Matrix Multiplication*, PODS 2025 (file `2504.10748v1.pdf`). Citations like "paper §3" refer to the source paper; "essay §3" refers to a section of our essay.

---

## Work distribution (by section)

Updated after F7/F8: dropped standalone §6, folded its content into §5.7. Re-budgeted to ~9 body pages + 1 page references.

| Section | Owner | Page target | Why this owner |
|---|---|---|---|
| §1 Introduction | A — Lead | ~1.25 | Sets the framing and our angle; integrates with §8 |
| §2 Preliminaries | B — Background | ~0.75 | Pure exposition of definitions and tools |
| §3 Cyclic-join equivalence | B — Background | ~1 | Database-theory framing + Proof 1 |
| §4 Simple O(n) algorithm | B — Background | ~1.25 | Pedagogical, accessible; Proof 2; bridges to harder material |
| §5 Warm-up algorithm (incl. §5.7 phases sketch) | C — Theory | ~3 | Technical core; Proof 3; the FMM step + phases sketch |
| §7 Experiments | D — Contribution | ~1.5 | Owns implementation in `code/` and figures |
| §8 Conclusion | A — Lead | ~0.5 | Symmetric with §1; pulls together threads |

A also owns: Overleaf setup, abstract, references, glue, EasyChair submission.
D also owns: all code under `code/`, raw data, plot scripts.
B and C also pair-review each other since their sections build on each other.

---

## How paper references work in this document

Below each subsection you'll see a **Paper map** entry pointing to the corresponding location(s) in `2504.10748v1.pdf`. Page numbers refer to the printed numbers on the body of the paper (page 1 = first page of body text after the title and ToC). Section numbers like "paper §3.2" refer to the source paper's sections.

Quick page index of the source paper:

| Paper section | Pages | Key items |
|---|---|---|
| Title + Abstract | 1 | Theorem 1 stated in abstract |
| §1 Introduction | 1–6 | Theorem 1 (p. 2), Theorem 2 (p. 3), database framing (p. 1), lower-bound discussion (p. 2), "Our Techniques" (p. 3–5), Related Work (p. 5–6) |
| §2 Preliminaries | 6–7 | §2.1 Notation (p. 6), Fast Matrix Multiplication paragraph (p. 6), Figure 1 (p. 7), §2.2 Equivalent Queries (p. 7) |
| §3 Warm-up: A and C fixed | 7–12 | §3.1 Setup + Assumptions 1–3 (p. 7–8), Lemma 3.1 (p. 8), Table 1 + §3.2 Data Structures (p. 9), Claims 3.3–3.7 + Eqs (1)–(6) (p. 9–10), Figure 2 + §3.3 Queries (p. 11), Lemma 3.8 (p. 11–12), §3.4 Constraints + Eqs (7)–(8) (p. 12) |
| §4 Setup for the Main Algorithm | 12–14 | Theorem 2 restated (p. 13), main-algorithm vertex classes (p. 13), Eqs (9)–(11) (p. 13–14) |
| §5 Main Algorithm | 14–19 | High-level idea + Lemma 5.1 (p. 14), §5.1 Phases + ω < 2.5 observation (p. 15), Table 2 + §5.2 Data Structures (p. 15), Eqs (12)–(15) + Claims 5.3–5.6 (p. 16–17), Figure 3 (p. 17), §5.3 Queries + Lemma 5.7 + Claims 5.8–5.9 (p. 17–18), §5.4 Pseudocode + Algorithms 1–3 (p. 19) |
| §6 Tiny Vertices (out of scope) | 20–23 | Skipped in our essay |
| §7 Vertex Class Transitions (out of scope) | 23–29 | Skipped in our essay |
| §8 General → Layered | 29–30 | Theorem 1 reproved (p. 29), Claim 8.1 + proof (p. 30) |
| References | 31–34 | — |
| Appendix A: Simple Algorithm | 35 | Lemma A.1, Claims A.2 and A.3 |
| Appendix B: Verifying Constraints | 35–37 | Numeric verification of ε, ε₁, ε₂, δ |

---

## Front matter

### Title (working)

> An Exposition of Fully Dynamic 4-Cycle Counting via Fast Matrix Multiplication, with an Empirical Study of the Wedge-Maintenance Baseline

(Shorten before submission; this is just descriptive.)

### Authors

Four authors, alphabetical, with UL FRI affiliation. Anonymized for EasyChair submission per the assignment.

### Abstract (~150 words, ~1 paragraph)

**Owner**: A.

**Paper map**: paper's abstract is on the title page (p. 1). It is a useful template for tone but not for content — our abstract describes our essay's contribution, not the paper's contribution.

**Content arc**:
1. One sentence: subgraph counting in fully dynamic graphs, framed as IVM for cyclic joins.
2. State of the art: triangles tight at O(√m); 4-cliques tight at O(m); 4-cycles long believed at O(m^{2/3}).
3. Assadi & Shah's result: the O(m^{2/3}) barrier is breakable via fast matrix multiplication, achieving O(m^{2/3−ε}) for some constant ε > 0.
4. What this essay does: self-contained exposition of (a) the reduction from general to layered graphs, (b) the simple O(n) algorithm as a baseline, and (c) the warm-up algorithm where two of the four matrices are fixed; with three formal proofs.
5. Empirical complement: implementation and benchmarking of the simple O(n) algorithm against naive recomputation.

### Keywords / CCS concepts

ACM CCS concepts (these are mandatory for sigconf >2 pages):
- *Theory of computation → Dynamic graph algorithms*
- *Theory of computation → Streaming, sublinear and near linear time algorithms*
- *Information systems → Database query processing*

Author keywords: *fully dynamic algorithms; subgraph counting; 4-cycles; fast matrix multiplication; incremental view maintenance; cyclic joins.*

---

## §1 Introduction (~1.5 pages, owner A)

**Goal**: motivate the problem, state where the field stands, and announce what the essay does.

### §1.1 Subgraph counting and dynamic graphs (~½ page)

**Paper map**: §1 paragraph 1, p. 1 (general motivation, applications cited via [RPS+21, COJT+11, MSOI+02, SMS+20]). Definition of fully dynamic model: §1, p. 1, paragraph "In the dynamic model...".

- Open with: counting small subgraphs (triangles, 4-cycles) is fundamental in graph algorithms with applications across social-network analysis, computational biology, and database query processing. Cite [RPS+21], [SMS+20], [MSOI+02].
- Define the *fully dynamic* model in one sentence: graph receives a stream of edge insertions and deletions; after each update, the algorithm must output the current count.
- The optimization target is *worst-case update time* over all updates.

### §1.2 The cyclic-join framing (~⅓ page)

**Paper map**: §1, p. 1, paragraph "Subgraph counting has many applications in database theory..." through "...example of the connection between joins and layered graphs can be found in Figure 1." Figure 1 is on p. 7 (in §2.2). Also §1, p. 2, paragraph "In this paper, we are interested in counting 4-cycles in the fully dynamic model. We can equivalently state the problem as follows..."

- Counting 4-cycles in *4-layered* graphs is exactly the size of the cyclic join `J = A(L₁,L₂) ⋈ B(L₂,L₃) ⋈ C(L₃,L₄) ⋈ D(L₄,L₁)`. This is why the paper sits at PODS.
- Cite [NRR14], [NPRR18], [KNN+20] for context.
- Forward-reference: §3 makes this equivalence precise and proves general → layered.
- **Figure 1** here: a small 4-layered graph, with relations A, B, C, D shown as edges, and one layered 4-cycle highlighted. Adapt from paper Fig 1.

### §1.3 The state of the art — a ladder of results (~⅓ page)

**Paper map**: §1, p. 2, the paragraphs starting "We are interested in 4-cycles because..." through the end of "Question: What is the worst-case update time...". Specifically:
- Triangle bounds: §1, p. 2, "3-cycle (triangle) counting in the dynamic model has an upper bound of O(√m) [KNN+20]. There is also a conditional lower bound of Ω(m^{1/2−γ})..."
- 4-clique bounds: §1, p. 2, "[HHH22] also studied the problem of counting 4-cliques showing that the folklore upper bound of O(m) for the update time is tight..."
- 4-cycles state-of-the-art before this paper: §1, p. 2, "However, the bounds for graphs on 4 vertices are not well understood. In particular, 4-cycle counting in the dynamic model has an upper bound of O(m^{2/3}) [HHH22]..."

Present as a small table.

- Triangles (3-cycle): upper bound O(√m) [KNN+20], conditional lower bound Ω(m^{1/2−γ}) under OMv [HKNS15]. Tight.
- 4-cliques: upper bound O(m) folklore, lower bound Ω(m^{1−γ}) under combinatorial 4-clique conjecture [HHH22]. Tight (for combinatorial algorithms).
- 4-cycles: upper bound O(m^{2/3}) [HHH22]. Lower bound Ω(m^{1/2−γ}) [HKNS15] under OMv. **Gap** between m^{1/2} and m^{2/3}.
- **Table 1** here: this ladder, three rows × three columns (problem, upper, lower).

### §1.4 The Assadi–Shah result and what makes it surprising (~¼ page)

**Paper map**:
- Theorem 1 statement: §1, p. 2, "Theorem 1." (also restated on p. 29 at the start of §8).
- Surprise commentary: §1, p. 2, paragraph "This approach crucially relies on fast matrix multiplication, and we only get an improvement when ω < 2.5. This is very surprising because any upper bound on ω better than 3 like Strassen's algorithm is not sufficient."
- 4-clique vs 4-cycle distinction: §1, p. 2, "Existing Lower Bounds." paragraph.
- IVM-with-FMM observation: §1, p. 3, "This is the first result to demonstrate that fast matrix multiplication can be leveraged to achieve a speedup in join size estimation problems in dynamic graphs..." through "This insight could potentially inspire a new class of IVM algorithms."
- Worst-case (not amortized) emphasis: §1, p. 3, "It is also important to note that we get a worst-case bound on the update-time and not an amortized bound."

- They give an O(m^{2/3−ε}) worst-case algorithm for 4-cycles using *fast (rectangular) matrix multiplication* (FMM).
- With current ω = 2.371339, ε ≈ 0.0098. With ω = 2, ε = 1/24.
- The conceptual surprise: FMM was widely believed not to help in dynamic settings — Strassen-type algorithms need both matrices upfront. This result is a counter-example.
- The 4-clique vs 4-cycle distinction: 4-clique's combinatorial Ω(m) lower bound *blocks* FMM speedups; 4-cycle's only Ω(m^{1/2}) (OMv) lower bound does not.

### §1.5 What this essay does (~¼ page)

**Paper map**: no direct equivalent — this is our own framing of the slice we cover (paper §1, §2, §3, §8, Appendix A in depth; §4, §5 lightly; §6, §7 omitted).

- Self-contained exposition of three components of the paper's argument:
  1. The general → layered graph reduction (§3).
  2. The simple O(n) baseline algorithm (§4).
  3. The warm-up O(m^{2/3−ε₁}) algorithm under the assumption that A and C are fixed (§5).
- A high-level sketch of how phases lift the warm-up to the full result (§6).
- Three formal proofs distributed across §3, §4, §5.
- An empirical complement: Python implementation of the simple algorithm benchmarked against naive recomputation (§7).
- We do not reproduce §6 (tiny vertices) or §7 (vertices changing classes) of the source paper — these are bookkeeping rather than new ideas, and would not fit in 10 pages.

**Citations used in §1**: [RPS+21], [SMS+20], [MSOI+02], [NRR14], [NPRR18], [KNN+20], [HKNS15], [HHH22], paper itself.

---

## §2 Preliminaries (~1 page, owner B)

**Goal**: nail down the notation and tools needed for the rest of the essay. Dense, no narrative.

### §2.1 Graphs and subgraph notation

**Paper map**: §2.1 Notation, p. 6, paragraphs 1–5 (definitions of n, m, deg, N(v), k-path, k-cycle, 4-layered graph, layered 4-cycle).

- G = (V, E), n = |V|, m = |E|. Simple, undirected, unweighted, no self-loops.
- deg(v), N(v).
- *k-path*: sequence of k+1 distinct vertices with consecutive edges. k=2 is a *wedge*.
- *k-cycle*: closed k-path.
- A *k-layered graph* is G = (V, E) with V = L₁ ∪ ⋯ ∪ Lₖ, each Lᵢ independent, edges only between consecutive layers (and between Lₖ and L₁ for cyclic). For us, k = 4.
- A *layered 4-cycle* has one vertex in each layer.

### §2.2 Dynamic graph model

**Paper map**: §1, p. 1, paragraph "In the dynamic model, the pattern graph H is fixed and known apriori..." (this is where the model is defined; the paper does not have a dedicated preliminaries subsection for it). Worst-case vs amortized is also emphasized in §1, p. 3, "It is also important to note that we get a worst-case bound on the update-time and not an amortized bound."

- Update sequence u₁, u₂, …; each uᵢ is `insert(e)` or `delete(e)`.
- After update i, output the count of 4-cycles in the current graph Gᵢ.
- *Worst-case update time*: max over all updates and all states.
- (Distinction from amortized — note that paper achieves *worst-case*, which is harder.)

### §2.3 Fast matrix multiplication

**Paper map**: §2.1, p. 6, the bold-headed paragraph "**Fast Matrix Multiplication.**" defines ω and ω(a,b,c) and cites [ADW+25] for the current best square ω = 2.371339 and improved rectangular bounds.

- ω: square FMM exponent. Two n×n matrices multiplied in O(n^ω) time. Current best ω ≈ 2.371339 [ADW+25]; conjectured optimal ω = 2.
- ω(a, b, c): rectangular FMM exponent. n^a × n^b times n^b × n^c in time n^{ω(a,b,c)}.
- "Combinatorial" algorithms exclude these algebraic identity tricks; they have ω = 3 effectively.

### §2.4 The OMv conjecture (~⅓ paragraph)

**Paper map**:
- First mention: §1, p. 1, "There is also a conditional lower bound of approximately Ω(m^{1/2}) for the update time by Henzinger, Krinninger, Nanongkai, and Saranurak (STOC 15) under the OMv conjecture..."
- "Existing Lower Bounds" paragraph: §1, p. 2, explains why OMv blocks combinatorial improvements but does *not* block FMM-based ones. Source for our explanation that OMv goes through boolean matrix-vector products.

- Online Matrix-Vector multiplication conjecture [HKNS15]: pre-process an n×n boolean matrix M; answer a stream of queries Mvᵢ for boolean vectors vᵢ; conjecture says total time is Ω(n^{3−γ}) for any γ > 0.
- Implication: dynamic problems reduce *to* OMv → conditional Ω(m^{1/2−γ}) lower bounds for triangle and 4-cycle update.
- Note: OMv conjecture does *not* preclude FMM-based algorithms, since reductions go through the boolean *matrix-vector product*, which doesn't admit a Strassen-like speedup.

**Citations used in §2**: [ADW+25], [HKNS15].

---

## §3 The cyclic-join equivalence (~1 page, owner B)

**Goal**: precisely state and prove the equivalence between 4-cycle counting in general graphs and in 4-layered graphs (cyclic joins). **Proof 1.**

### §3.1 Joins as layered graphs

**Paper map**:
- Database-theoretic setup: §1, p. 1, paragraph "Subgraph counting has many applications in database theory..." through "...example of the connection between joins and layered graphs can be found in Figure 1."
- Concrete worked example for triangles: §1, p. 1, "Specifically, the problem of finding the number of elements in a cyclic join of size k is equivalent to counting the number of k-cycles in k-layered graphs..."
- 4-cycle ↔ 4-way cyclic join: §1, p. 2, "In this paper, we are interested in counting 4-cycles in the fully dynamic model. We can equivalently state the problem as follows: Given four binary relations A(L₁, L₂), B(L₂, L₃), C(L₃, L₄), and D(L₄, L₁)..."
- Layered-graph definition: §2.1, p. 6, paragraph defining 4-layered graphs.
- Figure example: Figure 1 on p. 7 shows a small instance.

- Let A(L₁,L₂), B(L₂,L₃), C(L₃,L₄), D(L₄,L₁) be binary relations.
- Build a 4-layered graph G' where each layer Lᵢ is the active domain of attribute Lᵢ; edge (a,b) ∈ E(G') iff (a,b) is a tuple in the relation between consecutive layers.
- *Lemma 3.1 (informal):* |J| = number of layered 4-cycles in G'. (Cite paper §1; one-paragraph argument.)

### §3.2 Lifting a general graph to a 4-layered graph

**Paper map**: §8, p. 29–30, paragraphs 1–2 ("We solve this problem by creating a layered graph G'..." and "The first thing we address is that when an edge update (u, v) arrives in the graph, it corresponds to 4 updates in the layered graph G'. If the update is an insertion, we insert the edge in D then C then B and then in A and if it is a deletion, we delete edges in the reverse order.").

- Given general graph G = (V, E), construct G' = (V', E') with V' = V × {1,2,3,4}, copies of V in each layer.
- An edge (u, v) ∈ E becomes 4 edges in G' between consecutive layers (and L₄ ↔ L₁ closure).
- *Update protocol* (load-bearing for the proof — F3):
  - **Insert**: insert into D first, then C, then B, then A.
  - **Delete**: remove from A first, then B, C; D is removed last.
  - **Query**: the count of new 4-cycles in G is read off after the D update only — i.e. between the D operation and the next of A/B/C. This guarantees that during a query, the edge (u,v) is present in D but absent from A, B, C.

### §3.3 Theorem (Claim 8.1) and proof

**Paper map**: §8, p. 30. Statement and proof of Claim 8.1: "The number of walks of length 3 from u ∈ L₁ to v ∈ L₄ in the layered graph is equal to the number of paths of length 3 from u to v in the general graph." Proof spans p. 30 ("All 3-paths in the general graph from u to v exist in the constructed layered graph..." through "Thus, all the vertices are distinct and u, x, y, v is a path."). The wrap-up "Claim 8.1 along with Theorem 2 proves Theorem 1" is also on p. 30.

> **Theorem 1 (essay).** *In the construction above, the number of length-3 **walks** from u ∈ L₁ to v ∈ L₄ in G' equals the number of length-3 paths from u to v in the original graph G.*

(Note: LHS is *walks*, not paths. The point of the theorem is that under the update protocol below, walks coincide with paths. Saying "paths = paths" makes the claim vacuous. — F1.)

**Proof.** Two-paragraph argument from paper §8:
- Forward direction is immediate: any path u, x, y, v in G lifts to a layered walk in G'.
- Reverse direction: a layered *walk* u, x, y, v in G' uses one vertex per layer. Show all are distinct.
  - x ≠ u (no self-loops in the lifted graph).
  - x ≠ v: edge (u,v) is not present in A, B, C at query time (by the insert/delete ordering above). Hence x cannot equal v in the relevant data structure.
  - Symmetric arguments for y.
  - x ≠ y by no-self-loops.
- All four vertices distinct ⇒ this walk is a path in G. ∎

This is **Proof 1** of the essay.

### §3.4 Consequence

**Paper map**: §1, p. 3, "We will show in Section 8 that the problem of dynamically maintaining the number of 4-cycles in general graphs is equivalent to dynamically maintaining the number of layered 4-cycles in 4-layered graphs..." Also §2.2 Equivalent Queries, p. 7, paragraph 1 ("After every update to the simple graph, the query we have to answer is the exact total number (count) of distinct 4-cycles in the current graph. We will show in Section 8 that this problem is equivalent in general and layered graphs, so we will just focus on layered graphs.").

- It suffices, for the rest of the essay, to design an algorithm for layered 4-cycle counting on 4-layered graphs.
- Forward-reference §4 (simple algorithm) and §5 (warm-up) which work on 4-layered graphs.

**Figures**: **Figure 2** — the lifting construction, V replicated across 4 layers, an edge (u,v) shown as 4 lifted edges. Adapt from paper notation.

**Citations used in §3**: paper §8 (we re-prove), [HHH22] (they also use this trick).

---

## §4 A simple O(n) algorithm (~1.25 pages, owner B)

**Goal**: present and fully prove a simple wedge-maintenance algorithm. Establishes a baseline and motivates why we want better. **Proof 2.** This is also the algorithm we implement in §7.

### §4.1 The wedge-counting idea (~⅓ page)

**Paper map**:
- Idea introduced in §1, p. 3, "Our Techniques" section: "We count the number of cycles through the new edge update by finding the number of 3-paths between the endpoints of the edge update. In the simple algorithm (Appendix A), we do this by storing a data structure for the number of 2-paths (paths with 2 edges also called wedges) between all pairs of vertices."
- Algorithm itself: Appendix A, p. 35 ("In this section, we give a very simple algorithm to maintain the total number of 4-cycles in a fully dynamic general graph with worst-case update time O(n) where n is the number of vertices in the graph.").

- Number of 4-cycles through new edge (u,v) = number of 3-paths from u to v.
- Number of 3-paths from u to v = Σ_{w ∈ N(u)} W[w, v], where W[w, v] = #wedges between w and v.
- The sum gives 3-*walks*; under the update-order protocol below, every counted walk is a path (no correction term needed — F2).
- So we maintain a wedge-count matrix W and queries are an inner-product over N(u).

### §4.2 The algorithm (Algorithm 1)

**Paper map**: Appendix A, p. 35, the prose description following Lemma A.1 statement: "We will do this by counting the number of 4-cycles through every new edge update. The idea is to maintain the number of wedges i.e. two-paths between every pair of vertices..." through "...we need to be careful about whether we update the data structures first or answer the queries first. The data structures for the wedges should not have the current edge (u, v) as part of their paths. To make this happen we answer the query first during an edge insertion and update the data structures first during an edge deletion."

```
On insert(u, v):                        # query then update
    Δ = 0
    for w in N(u):  Δ += W[w, v]
    cycle_count += Δ                    # new 4-cycles
    for w in N(u):  W[w, v] += 1; W[v, w] += 1
    for w in N(v):  W[w, u] += 1; W[u, w] += 1
    add (u, v) to E

On delete(u, v):                        # update then query
    remove (u, v) from E
    for w in N(u):  W[w, v] -= 1; W[v, w] -= 1
    for w in N(v):  W[w, u] -= 1; W[u, w] -= 1
    Δ = 0
    for w in N(u):  Δ += W[w, v]
    cycle_count -= Δ
```

- Subtle correctness point: insertion queries before updating W (so W doesn't include the new edge); deletion updates first (so W doesn't include the removed edge during the count).

### §4.3 Lemma A.1 — correctness and complexity

**Paper map**: Appendix A, p. 35.
- Lemma A.1 statement: top of p. 35.
- Claim A.2 (wedge-matrix maintenance is O(n)): p. 35, with one-paragraph proof.
- Claim A.3 (counting 4-cycles through new edge is O(n)): p. 35, proof argues that the candidate 3-walks u, w, x, v are paths because (u, v) is not present in W (by the order-of-operations rule) and no-self-loop arguments rule out coincident vertices.

> **Lemma 1 (essay = Lemma A.1 paper).** *The algorithm above maintains the exact 4-cycle count of any fully dynamic graph in worst-case update time O(n).*

**Proof.** Two parts.
1. *Maintenance time* (Claim A.2 of paper): each update iterates over N(u) ∪ N(v), at most 2n vertices. O(n).
2. *Counting through new edge* (Claim A.3 of paper):
   - The Δ computed is Σ_{w ∈ N(u)} W[w, v].
   - For a fixed w, W[w, v] counts wedges w − x − v.
   - So Σ counts u − w − x − v walks. We must show all such walks are paths (distinct vertices).
   - u, v distinct (graph is simple).
   - w ≠ u, v: (u, v) edge case ruled out by the order-of-operations above.
   - x ≠ w, v by no-self-loops; x ≠ u because (u, v) is the new edge, not an edge to u somewhere else.
3. Combine: each update is O(n). ∎

This is **Proof 2** of the essay.

### §4.4 Why O(n) isn't good enough

**Paper map**: §1, p. 3, end of "Our Techniques" introductory paragraph: "This gives a worst-case update time of O(n). We now want to get the update time purely as a function of m, the number of edges. The goal is to minimize the worst-case update time over all edge updates. This might be slightly tricky because we want the update time to be purely a function of m, the current number of edges in the graph, but m changes with every insertion or deletion. Thus, the goal is to come up with an algorithm with a worst-case update time of O(m^x) with the smallest possible value of x."

- For sparse graphs m = O(n), the O(n) bound matches the worst case (you might have to touch every vertex on a single update).
- For denser graphs n² = ω(m), the bound is loose; we'd hope for sub-n.
- Memory: W is n² entries — fine for n ≤ 5000, problematic for n in the millions.
- This motivates the HHH22 O(m^{2/3}) result and the Assadi–Shah improvement.

**Citations used in §4**: paper Appendix A.

---

## §5 The warm-up algorithm (~3 pages, owner C)

**Goal**: present the key technical content of the paper at a level a reader can follow. Demonstrate where FMM enters. **Proof 3.**

### §5.1 Setup and assumptions (~⅓ page)

**Paper map**:
- §3 opening, p. 7: "In this section, we give an algorithm for counting 4-cycles in a 4-layered graph under a few assumptions."
- §3.1 Setup, p. 7: "We let the worst-case update time be O(m^{2/3−ε₁}) and we will show we can get ε₁ > 0 to be a constant."
- Assumptions 1, 2, 3: §3.1, p. 8: "Assumption 1. The number of vertices in each layer is n ≤ m^{2/3+2ε}." "Assumption 2. The vertices do not change classes throughout the algorithm." "Assumption 3. There are no edge updates in A and C i.e. the only edge updates are in B, D."
- Lemma 3.1 statement: §3.1, p. 8: "Theorem 2 holds under Assumption 1, Assumption 2, and Assumption 3."

- We assume edge updates only in B and D (matrices A and C are fixed).
- Assumption 1 of paper: number of vertices in each layer is n ≤ m^{2/3+2ε}. (Removed in paper §6 — out of scope for us.)
- Assumption 2 of paper: vertices don't change degree class during the algorithm. (Removed in paper §7 — out of scope for us.)
- Goal under these assumptions: O(m^{2/3−ε₁}) update time for some constant ε₁ > 0.
- *Lemma (statement only)*: under assumptions 1, 2, 3 (here Assumption 3 = updates restricted to B, D), the algorithm achieves O(m^{2/3−ε₁}).

### §5.2 Vertex degree classes (~⅓ page)

**Paper map**:
- H/M/L definitions for L₁ and L₄: §3.1, p. 8, bullet list "**High** (H): degree between m^{2/3−ε₁} and n.", "**Medium** (M): degree between m^{1/3+ε₁} and 2m^{2/3−ε₁}.", "**Low** (L): degree between 0 and 2m^{1/3+ε₁}."
- S/D definitions for L₂ and L₃: §3.1, p. 8, paragraph "The edge updates to B are divided into chunks of size m^{2/3−ε₁} called B₁, B₂, …Bᵢ. For a chunk Bᵢ, vertices in L₂ and L₃ with degree in Bᵢ at most m^{1/3−ε₂} are in **Sparse** (S) and degree in Bᵢ at least m^{1/3−ε₂} are in **Dense** (D)."
- Notation conventions A^{H*}, A^{M*}, etc.: §3.1, p. 8, paragraph "We use superscripts to talk about a submatrix of a matrix by restricting the vertices in different layers..."
- Contrast with HHH22's two classes (motivation for three): §1, p. 4, "Algorithm of Previous Work" paragraph (HHH22 used high + low only); the paper's "Our Algorithm" paragraph that follows (p. 4) introduces high + medium + low.

- Vertices in L₁ (similarly L₄) partitioned by degree in A (resp. C):
  - **High** (H): degree in [m^{2/3−ε₁}, n].
  - **Medium** (M): degree in [m^{1/3+ε₁}, 2m^{2/3−ε₁}].
  - **Low** (L): degree in [0, 2m^{1/3+ε₁}].
- For each chunk Bᵢ (next sub-section), vertices in L₂ (similarly L₃) are split:
  - **Sparse** (S): chunk-degree at most m^{1/3−ε₂}.
  - **Dense** (D): chunk-degree at least m^{1/3−ε₂}.
- Why these classes? Different data structures cost different amounts to maintain; the partition lets us bound each.
- One sentence on the contrast with HHH22's two classes (high/low) — we have three for L₁,L₄ to enable the FMM step.

### §5.3 Chunks and lazy maintenance (~⅓ page)

**Paper map**:
- Chunk definition: §3.1, p. 8, paragraph "The edge updates to B are divided into chunks of size m^{2/3−ε₁} called B₁, B₂, …Bᵢ."
- Eager vs amortized maintenance: §3.2, p. 9, paragraph "We maintain some data structures on the fly as the updates arrive and show that the update time is O(m^{2/3−ε₁}). For the remaining data structures, we compute them for the previous chunk when the updates of the next chunk arrive."
- Lemma 3.2 (worst-case time accounting): §3.2, p. 9, "The worst-case update time for all the data structures we store is O(m^{2/3−ε₁}) during an edge update and O(m^{4/3−2ε₁}) if it is being updated during the insertion of a chunk."
- Lazy evaluation for in-progress chunks: §3.3, p. 11, paragraph "We first describe the procedure of lazy evaluation that we use for chunks Bᵢ and Bᵢ₊₁..."
- Subtlety about edges inserted then deleted across chunks (the "negative edge" trick): §3.3, p. 12, paragraph "We make a brief remark here that will be addressed now and will not be mentioned for the remainder of the paper..."

- Updates to B partitioned into *chunks* B₁, B₂, … of size m^{2/3−ε₁}.
- Some data structures are maintained eagerly per update (the cheap ones, O(m^{1/3+ε₁}) per update).
- Other data structures (the expensive ones, requiring FMM) are computed for chunk Bᵢ during the m^{2/3−ε₁} updates of chunk Bᵢ₊₁.
- Lazy evaluation: while inside chunk Bᵢ₊₁, queries are answered by combining (a) finished data for B<ᵢ₊₁, (b) eager data for Bᵢ₊₁ in progress.

### §5.4 Data structures (~⅓ page)

**Paper map**:
- Table 1 of paper (data structures by class for the warm-up): §3.2, p. 9.
- High-vertex data structures and Eq (1): §3.2, p. 9, "Data Structures for High vertices.": A^{H*}·B<ᵢ, A^{H*}·B<ᵢ·C^{*H}, B<ᵢ·C^{*H}.
- Claim 3.3 (cost of maintaining A^{H*}·Bᵢ on the fly): §3.2, p. 9.
- Claim 3.4 (cost of multiplying (A^{H*}·Bᵢ) with C^{*H}): §3.2, p. 9, with Eq (2) on p. 10 giving the resulting constraint.
- Medium-vertex data structures and Eq (3): §3.2, p. 10, "Data Structures for Medium vertices."
- Claim 3.5 (cost for medium): §3.2, p. 10.
- Low-vertex data structures and Eq (4): §3.2, p. 10, "Data Structures for Low vertices."
- Claim 3.6 (the rectangular-FMM step) and resulting Eq (5): §3.2, p. 10.
- Claim 3.7 (cost of the alternative iteration A^{L*}·B_{i,SS} and A^{L*}·B_{i,SD}) and Eq (6): §3.2, p. 10.
- Lemma 3.2 wrap-up: §3.2, p. 11, paragraph "Proof of Lemma 3.2. Claims 3.3 to 3.7 together prove the statement..."

- We list the data structures by class (Table 2 of essay, adapted from paper Table 1):

| Vertex class | Data structures stored |
|---|---|
| **High** in L₁/L₄ | A^{H*}·B<ᵢ ;  A^{H*}·B<ᵢ·C^{*H} ;  B<ᵢ·C^{*H} |
| **Medium** in L₁/L₄ | A^{M*}·B<ᵢ ;  B<ᵢ·C^{*M} |
| **Low** in L₁/L₄ | A^{L*}·B<ᵢ,DD ;  A^{L*}·B<ᵢ,SS ;  A^{L*}·B<ᵢ,SD ;  B<ᵢ,DD·C^{*L} ;  B<ᵢ,SS·C^{*L} ;  B<ᵢ,DS·C^{*L} |

- Each data structure encodes the count of 3-paths between two layers through certain vertex classes.
- *Lemma 2 (= Lemma 3.2 paper, statement only):* the worst-case time to update all these data structures is O(m^{2/3−ε₁}) per update, plus O(m^{4/3−2ε₁}) per chunk transition (amortized to O(m^{2/3−ε₁}) per update inside a chunk).

### §5.5 Worked example: the FMM step (Claim 3.6) (~⅔ page)

**Paper map**:
- Claim 3.6 statement and proof: §3.2, p. 10, "Computing A^{L*}·B_{i,DD} can be done in time m^{ω(2/3+2ε, 1/3−ε₁+ε₂, 1/3−ε₁+ε₂)}." Followed by Eq (5) the resulting constraint.
- Database-terminology gloss for these matrix-product data structures: §3.2, p. 9 (the paragraph after Lemma 3.2 starting "Consider one of these data structures, for instance A^{H*}B<ᵢ. It can be expressed in database terminology as follows: We start with the binary relation A and select the tuples where the first attribute corresponds to a high-degree vertex in L₁..."); the same idea applies to A^{L*}·B_{i,DD}.
- Numeric solution of the constraint system (ε₁ = 0.04201965, ε₂ = 0.14568075 with current ω, ε = 0.0098109): §3.4, p. 12, paragraph "Solving all these constraints (Eq (2) and (5) to (8)) gives us ε₁ = 0.04201965 and ε₂ = 0.14568075 when ε = 0.0098109."
- Verification of the numbers: Appendix B, p. 36–37, "Algorithm where A, C are fixed with current best bounds on the rectangular matrix multiplication exponents."

- Pick the most illuminating data structure: A^{L*}·B_i,DD.
- Dimension analysis:
  - A^{L*} is m^{2/3+2ε} rows (vertices in L₁) × m^{1/3−ε₁+ε₂} cols (dense vertices in L₂ within Bᵢ).
  - B_i,DD is m^{1/3−ε₁+ε₂} × m^{1/3−ε₁+ε₂}.
- Use rectangular FMM: time m^{ω(2/3+2ε, 1/3−ε₁+ε₂, 1/3−ε₁+ε₂)}.

> **Theorem 2 (essay, = Claim 3.6 paper).** *Computing the matrix product A^{L\*}·B_{i,DD} can be done in time m^{ω(2/3+2ε, 1/3−ε₁+ε₂, 1/3−ε₁+ε₂)}.*

**Proof.**
- Argue that A^{L*} has at most m^{2/3+2ε} non-zero rows (Assumption 1) and m^{1/3−ε₁+ε₂} non-zero columns (one column per dense vertex in L₂ in Bᵢ).
- Same for B_i,DD's two dimensions.
- Apply rectangular FMM. ∎

This is **Proof 3** of the essay.

- Constraint Eq (5) of paper: the cost m^{ω(...)} must be ≤ m^{4/3−2ε₁} (the chunk-transition budget):

ω(2/3 + 2ε, 1/3 − ε₁ + ε₂, 1/3 − ε₁ + ε₂) ≤ 4/3 − 2ε₁.

- This is what *forces* the existence of ε₁ > 0: with current ω(·,·,·) bounds [ADW+25], the inequality has a feasible solution at ε₁ = 0.04201965, ε₂ = 0.14568075, ε = 0.0098109. Cite paper Appendix B.

### §5.6 Pulling it together (~⅓ page)

**Paper map**:
- Query case analysis: §3.3 Queries, p. 11–12. Lemma 3.8 ("All types of queries can be answered in worst-case time O(m^{2/3−ε₁}).") with Cases 1 (HH), 2 (HM, ML, HL, MM), and 3 (LL). Figure 2 on p. 11 illustrates an HM query.
- Constraints summary: §3.4 Constraints, p. 12, Eqs (7), (8) and the discussion of the full system.
- Why ε₁ ≥ ε is needed: §3.4, p. 12, "We need this because we use this algorithm as a subroutine in our main algorithm which has update time O(m^{2/3−ε})."

- State the warm-up theorem informally: the data structures maintain enough information to answer (u, v) queries in O(m^{2/3−ε₁}), via case analysis on whether u and v are H, M, or L. The eight resulting cases are listed in paper §3.3 — we summarize but don't reproduce.
- Transition into §5.7 (the phases sketch — replaces former standalone §6, F8).

### §5.7 From warm-up to the full theorem (sketch, ~⅓ page)

**Paper map**: paper §5 "High Level Idea" p. 14; §5.1 Phases p. 15; §1 p. 2 (the surprise); §1 p. 2 (Theorem 1 statement); §8 p. 29 (restatement). Eq (9) on p. 13.

This subsection replaces the previously planned standalone §6 (F8 — page-budget cut). One paragraph covering:

- *Why the warm-up is not enough*: aggregation A^{L*}·B<ᵢ,DD = A^{L*}·B<ᵢ−1,DD + A^{L*}·Bᵢ,DD requires A fixed; breaks once A receives updates.
- *Phases*: paper introduces phases of size m^{1−δ}; during phase j+1, FMM products are precomputed for the now-frozen phase j. Eq (9): 1 − δ ≥ (2ω + 1)·ε + (ω − 1)·2/3.
- *Why ω < 2.5 − O(ε) is required* (F13 — note the "− O(ε)" slack, not bare "ω < 2.5"). Strassen (ω ≈ 2.81) is insufficient. This is the conceptual surprise.
- *Restate Theorem 1 of the paper* — but explicitly say that the full proof (paper §5 phases + paper §6 tiny vertices + paper §7 class transitions + paper §8 reduction) is beyond scope; our formal contribution is the three proofs in §3, §4, §5.5 (F14).

**Citations used**: paper §4–§5; [Str69]; [ADW+25].

---

## §7 Experiments (~1.5 pages, owner D)

**Goal**: empirically validate the simple O(n) algorithm against naive recomputation, find crossover points, demonstrate practical considerations.

### §7.1 Experimental setup (~¼ page)

**Paper map**: the algorithm we implement is from Appendix A, p. 35 (full algorithm description and pseudocode-equivalent prose). The paper itself has no experimental section — this is entirely our contribution. The naive recompute baseline is folklore (see [AYZ97] for the static FMM-based version, but we use the simpler combinatorial wedge-sum approach for fairness).

- Implementation: Python 3.11 + NumPy. Code in `code/` of the project.
- Hardware: state CPU, RAM (one line).
- Algorithms compared (one fixed baseline — F10):
  - **Simple-Wedge**: paper Appendix A, our implementation, $O(n)$ per update.
  - **Naive-Recompute (wedge-sum)**: at each update, recompute $\#4\text{-cycles} = \tfrac{1}{2} \sum_v \binom{W(v)}{2}$ from scratch in $O(n+m)$ per update. Brute force is used only as a tiny-graph correctness oracle (n ≤ 50), never as a reported baseline.
- Datasets (sizes capped per F9):
  - **Erdős–Rényi** G(n, p): n ∈ {200, 500, 1000, 2000} for both algorithms, three densities each. n = 5000 is run for **Simple-Wedge only** (Naive-Recompute infeasible at that scale in Python).
  - **Barabási–Albert**: 1–2 sizes for shape contrast.
  - **Real-world** (Simple-Wedge only): one *small* SNAP graph, e.g., `ca-GrQc` (n ≈ 5k, m ≈ 14k). Larger graphs (`email-Enron`, etc.) need a sparse wedge representation we do not implement.
- Update streams: random insertion-only, mixed 50/50 insert/delete (after a build-up phase).

### §7.2 Methodology and metrics (~¼ page)

**Paper map**: no paper map — entirely our methodology choices.

- Build the graph by streaming inserts; warm cache with a few hundred no-op queries.
- Measure: median per-update time over 1000 updates (use median, not mean, because of GC pauses).
- Memory peak via `tracemalloc` or `/usr/bin/time -v`.
- Cross-check: on small graphs (n ≤ 100), compare counts after every update; abort on mismatch. This catches off-by-one bugs in the corner cases of §4.2.

### §7.3 Results (~¾ page)

**Paper map**: no paper map — our experimental results.

- **Figure 3** (essay-internal numbering): log-log plot, update time (y) vs n (x), one line per (algorithm, density). Show clear O(n) scaling for Simple-Wedge and steeper scaling for Naive-Recompute.
- **Figure 4**: crossover analysis. For a fixed graph size, plot total time vs number of updates for both algorithms. Crossover point = where lines cross.
- **Table 3**: real-world graph numbers. Columns: dataset, n, m, simple-wedge avg/median update time, recompute equivalent. Memory peak for Simple-Wedge.
- Discussion (~one paragraph): note that Simple-Wedge wins quickly on dense graphs (where m ≈ n²) and more slowly on sparse graphs (where m ≈ n). Naive-Recompute is competitive when the update stream is short.

### §7.4 Connection to theoretical results (~¼ page)

**Paper map**: bound comparisons reference §1, p. 3 (the O(m^{2/3−ε}) and Ω(m^{1/2}) bounds for 4-cycles). The qualitative point that the FMM-based algorithm is impractical to implement but theoretically important is implicit in the paper's framing throughout §1 and §5.

- Caveat: we *do not* implement the warm-up §3 algorithm — that would require chunked maintenance and rectangular FMM, which is a multi-week engineering project. Our experiment is on Simple-Wedge (the O(n) baseline).
- What our experiment confirms empirically:
  - Dynamic maintenance is dramatically faster than recomputation on long update streams.
  - The O(n) update bound is loose for sparse graphs but tight for dense ones — matches theoretical expectation.
- What our experiment cannot tell us about: the constant-factor practicality of Assadi–Shah's FMM-based algorithm. That's an open empirical question worth flagging.

**Citations used in §7**: SNAP dataset reference; paper Appendix A for the algorithm.

---

## §8 Conclusion (~0.5 page, owner A)

**Goal**: pull threads together, restate what we did, name open questions.

### §8.1 What we did (one paragraph)

**Paper map**: no paper map — our own synthesis.

- Restated the 4-cycle counting problem as IVM for cyclic joins.
- Proved the general → layered reduction (Proof 1).
- Presented and proved the simple O(n) baseline (Proof 2).
- Walked through the warm-up algorithm where A, C are fixed, demonstrating the FMM step (Proof 3).
- Sketched how phases lift the warm-up to the full O(m^{2/3−ε}) result.
- Implemented and benchmarked the simple algorithm.

### §8.2 Open questions (one paragraph)

**Paper map**:
- The lower-bound gap (Ω(m^{1/2−γ}) vs the new O(m^{2/3−ε})): §1, p. 2, "Existing Lower Bounds." paragraph: "we do not rule out a combinatorial lower bound of Ω(m^{2/3}) for the update time for maintaining the number of 4-cycles in a fully dynamic graph."
- IVM-with-FMM as an open direction: §1, p. 3, "This is the first result to demonstrate that fast matrix multiplication can be leveraged to achieve a speedup in join size estimation problems in dynamic graphs..." through "This insight could potentially inspire a new class of IVM algorithms."

- The gap between O(m^{2/3−ε}) (upper) and Ω(m^{1/2−γ}) (lower) for 4-cycles. Where does the true bound sit?
- Other IVM problems where FMM might break "natural" barriers — k-cycle counting for k > 4? Path counting?
- Practical implementations of Assadi–Shah's algorithm — does the FMM constant kill the asymptotic improvement on realistic graph sizes?

**Citations used in §8**: paper itself, possibly [HHH22] for k-vertex pattern context.

---

## References plan

Estimated 12–18 citations. Recommended core list:

| Cite key | Paper | Used in |
|---|---|---|
| AssadiShah25 | The temeljni članek | throughout |
| HHH22 | Hanauer–Henzinger–Hua, prior O(m^{2/3}) | §1, §4, §5 |
| KNN+20 | Triangle upper bound O(√m) | §1, §2 |
| HKNS15 | OMv conjecture, lower bounds | §1, §2 |
| ADW+25 | Current ω = 2.371339 | §2, §5 |
| AYZ97 | Static FMM cycle counting | §1, §5 |
| Str69 | Strassen | §6 |
| NRR14 | Worst-case optimal joins (context) | §1, §3 |
| NPRR18 | WCO joins | §1, §3 |
| RPS+21 | Subgraph counting survey | §1 |
| SMS+20 | Graph processing survey | §1 |
| MSOI+02 | Network motifs | §1 |
| SNAP | Stanford SNAP datasets | §7 |

Add 2–4 more as needed during writing.

---

## Figures and tables, consolidated

| ID | Type | Where | What it shows | Adapted from paper | Owner |
|---|---|---|---|---|---|
| Fig 1 | Diagram | §1.2 | A small 4-layered graph with relations A,B,C,D, one cycle highlighted | paper Figure 1, p. 7 | A |
| Tab 1 | Table | §1.3 | Ladder of dynamic subgraph counting bounds (3-cycle, 4-cycle, 4-clique) | distilled from §1, p. 2 of paper | A |
| Fig 2 | Diagram | §3.2 | General → layered lifting construction | new — illustrates §8 reduction (paper p. 29–30) | B |
| Tab 2 | Table | §5.4 | Data structures by vertex class (H/M/L) | paper Table 1, p. 9 | C |
| Fig 3 | Plot | §7.3 | Update time vs n, log-log, per algorithm × density | new — our experiment | D |
| Fig 4 | Plot | §7.3 | Crossover analysis (total time vs #updates) | new — our experiment | D |
| Tab 3 | Table | §7.3 | Real-world graph experiment numbers | new — our experiment | D |

---

## Theorem environments to declare in LaTeX

```
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{claim}[theorem]{Claim}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
```

Numbered objects (essay-local):
- Theorem 1 (essay): general → layered (= Claim 8.1 of paper, p. 30). §3.3 of essay.
- Lemma 1 (essay): simple algorithm correctness/complexity (= Lemma A.1 of paper, p. 35). §4.3 of essay.
- Theorem 2 (essay): FMM step (= Claim 3.6 of paper, p. 10). §5.5 of essay.
- Lemma 2 (essay, statement only): warm-up data-structure update times (= Lemma 3.2 of paper, p. 9). §5.4 of essay.

---

## Section dependency map (so we can write in parallel)

```
§1 ──depends-on──► §2, §3, §4, §5, §6, §7  (intro is written last)
§2 ──standalone
§3 ──depends-on──► §2
§4 ──depends-on──► §2
§5 ──depends-on──► §2, §3, §4
§6 ──depends-on──► §5
§7 ──depends-on──► §4 (uses simple algorithm)
§8 ──depends-on──► §5, §6, §7
```

So the natural drafting order is: §2 → §3, §4 (parallel) → §5 → §6, §7 (parallel) → §1, §8 (last).
