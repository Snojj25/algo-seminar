# Speaker Notes — 15-minute presentation

**For each slide:** the *script-in-bullets* (what to actually say), an explicit transition (how to hand off), and likely audience questions to prepare for. Time budgets are targets — rehearse with a stopwatch.

**Global tone.** This is a *pitch*. We are not proving anything live. We are selling: "this is a real problem, here is the state of the art, here is what we contribute, here is the evidence". When in doubt, cut math, keep narrative.

**Handoff discipline.** Each speaker ends with a question. The next speaker opens by answering it. This is what makes 4 voices sound like one talk.

---

## Speaker 1 — The problem (3:30)

### Slide 1 — Title (~15 s)

- Read the title and subtitle out loud.
- Introduce all four speakers by first name (or whatever names you decide).
- One sentence: *"Today we want to convince you that this paper deserves your reading time. Here's why."*
- Move on. Don't linger.

### Slide 2 — The problem in one picture (~1:30)

- Point at the picture *first*, talk *second*. The picture is the whole pitch.
- Script:
  - *"In a database, sometimes the answer to a query depends on a cyclic relation. Here are four relations, A, B, C, D, joined in a loop."*
  - *"You can read this picture as a 4-layered graph. Each relation is the set of edges between two layers."*
  - *"A single tuple in the join — one valid combination of values that satisfies all four conditions — corresponds to exactly one 4-cycle in this picture."*
  - *"So the size of this cyclic join is literally a count of 4-cycles."*
- The orange call-out (one tuple = one 4-cycle) is the punchline. Pause on it.
- Transition: *"Now imagine the database is changing — rows are being added and removed. We want the count after every change. How fast can we do that?"*

### Slide 3 — What "fully dynamic" actually demands (~1:30)

- Open with the punchline you teased: *"This is the fully dynamic 4-cycle counting problem."*
- Cover three beats:
  1. **Setting.** Edges (tuples) arrive and leave. Report the count after every one. Exact, not approximate.
  2. **Cost model.** Worst-case update time, not amortised. Read the block as written: *"the maximum work on any single update — not the average."*
  3. **Why worst-case matters.** Use the 1-second-hiccup example. Make it visceral: production engineers don't care about averages.
- Tie it back: *"So the strongest version of this problem is: beat recompute-from-scratch, with a per-update worst-case guarantee."*
- Hand off: *"So what's the best anyone has actually done?"*

### Anticipated Speaker-1 questions

- *"Why not just amortise?"* — Because databases get paged on tail latency, not average latency. Amortised bounds let outliers slip through.
- *"Why exact and not approximate?"* — Approximate algorithms exist and are useful, but the paper targets exact. Both are interesting questions; we're picking the stronger one.
- *"Doesn't a single 4-cycle pattern not generalise?"* — Cyclic joins of any even length reduce to this kind of problem; 4 is the smallest nontrivial case.

---

## Speaker 2 — State of the art & the FMM surprise (3:30)

### Slide 4 — The landscape (~1:00)

- Answer Speaker 1's question directly: *"Here's what was known."*
- Walk the table. Read the three rows out loud.
- Highlight: *"Two patterns settle at clean exponents. Triangles at root-m. 4-cliques at m. But 4-cycles are stuck at this weird two-thirds exponent."*
- One sentence: *"That two-thirds was the best bound for over a decade."*
- Don't go into the lower bound or OMv on this slide — keep it crisp.

### Slide 5 — Why m^{2/3}? (~1:30)

- Set up: *"To explain why two-thirds isn't arbitrary, here's the algorithm idea."*
- Three beats:
  1. **High/low split.** Define a wedge (2-path). Split vertices by degree at `m^{1/3}`.
  2. **Wedge matrix.** Maintain a count of low-midpoint wedges for every pair of endpoints. Each edge update touches at most `m^{1/3} × m^{1/3} = m^{2/3}` entries.
  3. **Punchline.** That's where two-thirds comes from. Combinatorial methods naturally balance here.
- If short on time, just say "high-degree and low-degree vertices balance at `m^{1/3}` — and the product is `m^{2/3}`."
- One sentence on the lower bound: *"There's a matching lower bound — OMv-conditional — that says you can't go below roughly square-root-m. So there's a gap between `m^{1/2}` and `m^{2/3}` that combinatorial tricks can't close."*

### Slide 6 — The 2025 surprise (~1:00)

- Open with the headline: *"This year, Assadi and Shah at PODS 2025 broke the two-thirds barrier."*
- State the theorem from the block. Don't read the formula — just say *"two-thirds minus a constant epsilon, using fast matrix multiplication."*
- Sell the surprise: FMM was thought useless here. Explain in 15 seconds:
  - *"FMM multiplies two big matrices at once. Dynamic algorithms get one edge at a time. These were thought incompatible."*
- One line on the trick: *"They reorganise updates into phases. During each phase, they precompute the next product in the background, while answering queries against the previous product. This is the bridge between batched FMM and per-update bounds."*
- Hand off: *"Their algorithm is dense. Can we see what's really going on?"*

### Anticipated Speaker-2 questions

- *"What is `ω` exactly?"* — Matrix multiplication exponent. Currently `< 2.371339`. Conjectured to be 2.
- *"How does Assadi-Shah avoid the FMM-vs-streaming problem?"* — Phases, as on the slide. More detail in Section 3.4 of our paper.
- *"How big is `ε`?"* — With current bounds, around 0.01. At conjectural `ω = 2`, about 0.04. Small, but it's a constant — that's what matters.

---

## Speaker 3 — Our contribution (3:30)

### Slide 7 — Cyclic-join lens (~1:00)

- Answer Speaker 2: *"Yes — and the lens is the cyclic-join view we opened with."*
- Point at the picture. Re-explain the lifting: *"Every vertex of `G` gets a copy in each layer. Every edge becomes four edges, one in each of the four biadjacency matrices."*
- Key takeaway: *"With this lens, the algorithm's architecture becomes visible. Degree classes are degree thresholds on the layers. The matrix product the algorithm computes is just a join evaluation step."*
- *"We can now point at exactly where FMM enters."*

### Slide 8 — Where the FMM step lives (~1:15)

- *"Of the whole machinery, exactly one matrix product carries the speedup."*
- Read the product `A^{L*} · B_{ℓ,DD}` out loud once. Don't dwell on the indices.
- Walk the bullet list quickly: degree classes, chunks, phases. *"All of this surrounding machinery is bookkeeping."*
- The punchline: *"It exists to feed that one FMM product a well-conditioned input — the right size, the right shape."*
- Underline: *"This is the load-bearing line. The constraint system tells us so."* Build the bridge to the next slide.

### Slide 9 — Closed-form certificate (~1:15)

- *"Assadi and Shah verified feasibility of their constraint system numerically, at the current value of `ω`. We give a closed-form solution at the conjectural optimum."*
- State the Lemma: *"Setting epsilon-one to one twenty-fourth, epsilon-two to five twenty-fourths, epsilon to one twenty-fourth — all five constraints are satisfied."*
- The two columns:
  - **Left:** five inequalities, two bind. The FMM one binds. The threshold one binds.
  - **Right:** *Why this matters.* We can read off the load-bearing constraint. It's the FMM one. Remove FMM, the bound collapses to `m^{2/3}`. So FMM is essential, not incidental.
- *"This is also an algebraic refinement: we know exactly what `epsilon` would be at conjectural `ω = 2` — one twenty-fourth, roughly 0.04."*
- Hand off: *"Theory says FMM is essential. Does this story show up in practice?"*

### Anticipated Speaker-3 questions

- *"Why bother with closed-form when numerical works?"* — Because the closed form makes the load-bearing structure transparent. We see *which* constraint binds, not just that the system is feasible.
- *"What are the three slack constraints?"* — The High-High FMM product, and two threshold-ordering inequalities. Listed in the paper §7.
- *"Is the closed-form solution unique?"* — Almost certainly no — these are inequalities, not equalities. We give *one* clean rational solution. Likely a whole polytope of feasible points.
- *"Could you go lower than `1/24`?"* — Open question; depends on whether one of the slack constraints could be made tight too.

---

## Speaker 4 — Experiments & takeaway (3:30)

### Slide 10 — Empirical setup (~1:00)

- Answer Speaker 3: *"Yes — we built a faithful implementation."*
- Walk the setup block. Three beats:
  1. **Warm-up algorithm.** The restricted variant (`A` and `C` frozen), with NumPy GEMM substituting for FMM.
  2. **Baseline.** Layer-aware Simple-Wedge — the natural wedge-counting algorithm on a 4-layered graph.
  3. **Method.** Same lifted instances, same update streams.
- **Caveat:** *"We are not testing asymptotics. NumPy GEMM is cubic, not omega. We are testing the shape of the win — which inputs make the routing machinery worth its complexity."*
- This caveat is important — the questioner will ask about it if you don't say it.

### Slide 11 — The finding (~1:30)

- Point at the chart. *"This is the punchline."*
- Walk the lines:
  - *"The simple wedge baseline grows roughly linearly with input size — slope around 0.9 in this log-log plot."*
  - *"The warm-up algorithm with FMM-shaped routing grows much more slowly — slope around 0.3."*
  - *"In this regime — bilateral hubs on both sides of the cyclic ordering — the warm-up wins clearly."*
- Then the right-column nuance:
  - *"On simpler inputs — only one-sided hubs, sparse graphs — the wedge baseline matches or beats the warm-up. The routing overhead doesn't pay off."*
- The closing point: *"So the machinery is not a generic accelerant. It locates a specific structural regime — bilateral hubs — where FMM bandwidth pays for itself."*

### Slide 12 — Takeaway (~1:00)

- Close the loop with the two-angles framing:
  - *"Algebraically: one constraint binds, and it's the FMM one."*
  - *"Empirically: one regime fires, and it's the bilateral-hub one."*
- *"Both say the same thing: the entire surrounding machinery exists to feed one well-conditioned FMM step."*
- Open directions:
  - Real `ω ≈ 2.371` rather than conjectural 2.
  - Bigger cyclic joins (5-cycles, 6-cycles, k-cycles).
  - Adaptive routing — detect bilateral-hub regimes online.
- Last line: *"More broadly, IVM for cyclic joins is a clean lens on the FMM-versus-streaming tension that lives all over dynamic algorithms."*

### Slide 13 — Thanks (~5 s)

- *"Thanks. Questions?"*
- Don't fill silence. Let the room breathe. Wait for a hand.

### Anticipated Speaker-4 questions (and full-team Q&A)

- *"How real are these experiments at scale?"* — NumPy GEMM scales fine to `n ≈ 10⁴` per layer on a laptop. Beyond that we'd need a proper FMM implementation, which doesn't exist below Strassen. The structural finding is robust within tested scales.
- *"Bilateral hubs — how often does that happen in real data?"* — Open question; we didn't sample real database workloads. Listed as an open direction.
- *"What's the gap to the lower bound?"* — `Ω(m^{1/2-γ})` vs `O(m^{2/3-ε})` with our `ε = 1/24`. Big gap. Nobody knows where the truth is.
- *"What about other cyclic patterns?"* — Same framework should adapt to cyclic joins of any even size. Open work.
- *"Is this practical today?"* — Not directly. FMM implementations don't exist below Strassen. But the framework already tells you when *combinatorial* routing helps — that's a practical takeaway.
- *"How long did the implementation take?"* — Be honest. (Update with actual answer at rehearsal time.)

---

## Logistics

### Rehearsal protocol

1. **Solo run.** Each speaker rehearses their 3:30 alone, with a timer. Target 3:15 to leave handoff slack.
2. **Pair runs.** Each consecutive pair rehearses the handoff together. Practice the question-then-answer transition until it sounds natural, not scripted.
3. **Full run.** All 4 speakers, end-to-end, with timer. Target total **14:00** to leave 1:00 of slack. Don't aim for exactly 15:00 — that's how you go over.
4. **Cold run.** Run it once in front of someone outside the group. Note where they lost the thread. Cut or rephrase that slide.

### What to do if you're running long

In order of what to cut, hardest first:

1. **Drop Slide 5** (the `m^{2/3}` intuition). Move the high/low split into one sentence on Slide 4. Saves 1:00 if you have to.
2. **Drop the right column of Slide 9** ("Why this matters"). The left column is enough.
3. **Drop the input-regime bullets on Slide 11**. Just point at the chart.

### What to do if you're running short

1. Spend more time on Slide 2 (the picture). Walk it slowly. It's the whole pitch.
2. On Slide 11, explain *one* of the curves in detail (slope, what it means).
3. Add one slide of Q&A prompts if you have a backup slide ready.

### Backup slides (optional, hidden)

If you want to be over-prepared, add these *after* the Thanks slide so they're hidden behind a final-slide bookmark:

- **B1.** The actual five inequalities of the constraint system, with one-line meanings.
- **B2.** Phases diagram (paper Fig. 3 if you make one).
- **B3.** The Simple-Wedge update pseudocode.
- **B4.** The full results plot grid (paper Figure 8 series).

You can hop to any of them via slide number in case of Q&A.
