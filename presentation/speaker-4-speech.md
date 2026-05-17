# Speaker 4 — Spoken Script (Slides 11–14)

> The actual words to say. Target total time: **~3:30**. Stage directions in `[brackets]`. Emphasis in **bold**. Pauses marked with `//`.
>
> Read this out loud at least twice before the dry run. Anything you can't say smoothly, rewrite — don't memorize a stumble.

---

## Slide 11 — Implementation and empirical setup (~60 s)

`[Take the handoff from Speaker 3 without missing a beat.]`

> "Yes — we built a faithful implementation, // and we tested exactly the question theory just asked: // **on which inputs is the surrounding machinery actually worth its complexity?**"

`[Step to the slide. Brief beat.]`

> "Three components, all in Python."

> "First — the **algorithm**. A faithful Python implementation of the structure from the paper. // Concretely, three things make it work.
>
> // The graph is **split into four layers** — one copy of each vertex per role it plays in a 4-cycle. Edges then become matrices between consecutive layers, and a 4-cycle in the original graph is just a path that walks all four layers and closes back to the start.
>
> // Vertices are then sorted by **degree** — hubs in one class, low-degree vertices in another — because the algorithm routes work very differently for each.
>
> // And the central piece: a **matrix-multiplication step** that pre-computes the product over the hub class. // Once that table exists, an update between two hubs is answered with a **single lookup** — constant time, regardless of how big the graph is. // *That* is where the speedup comes from."

> "Second — a **baseline**. The natural simpler approach: wedge counting on the same four-layered graph, without the class-routing machinery. Same problem, same inputs, no clever bookkeeping."

> "Third — a **test harness**. // The whole reason we built this: the algorithm's advantage depends on the **structure** of the graph — so we needed a way to dial that structure on demand. // The harness lets us generate the same problem with very different shapes: random graphs, // hubs concentrated on one side of the cycle, // hubs on **both** sides, // or uniform low-degree with no hubs at all. // Then we run both algorithms on each shape, and see where the structural advantage actually appears."

> "Both algorithms run on **identical graphs**, **identical update streams**. The comparison is honest."

`[Slow down here. This is the caveat. Look up from the slide.]`

> "One important caveat. // The paper's headline claim is **asymptotic** — it says: as graphs get very large, the cost per update grows more slowly than the old barrier. // Proving that requires **fast matrix multiplication** — a theoretical multiply with exponent below 2.371. // **No such implementation actually exists** — NumPy uses cubic matrix multiplication, the same as schoolbook. // So we can't reproduce the asymptotic claim, and we don't try. // What we *can* test is something different: // even **without** fast matrix multiplication, does the algorithm's structural design — the class partitioning, the routing, the precomputed tables — produce a measurable advantage? // And if so, **on which graphs**? // That's the question."

**Time check: ~60 s. Move on.**

---

## Slide 12 — Where the algorithm wins (~90 s)

`[Step toward the plot. Don't speak for ~1 second. Let them look.]`

> "This is the punchline of the experiment."

`[Trace the RED line with your finger, left to right.]`

> "In this regime — **bilateral high-degree**, hubs on both sides of the cycle — the new algorithm grows much more slowly than the baseline. // Slope around **0.3** for the new algorithm, slope around **0.9** for the fair baseline. // The gap **opens** as the input grows. // At our largest size, the new algorithm is roughly **five times faster** than the fair baseline."

`[Now turn to the three small cycle diagrams on the right.]`

> "But the headline number isn't the whole story — the regime matters. We tested three structures."

`[Point at "bilateral".]`

> "**Bilateral** — hubs on opposite sides of the cycle — the new algorithm wins. This is the plot you're looking at."

`[Point at "unilateral".]`

> "**Unilateral** — hubs on one side only — the baseline matches it. The extra machinery doesn't pay off."

`[Point at "no hubs".]`

> "**No hubs** — uniform low-degree — the baseline actually does slightly better. The routing overhead becomes pure overhead."

`[Step back. Bring it home — slow, deliberate.]`

> "So the algorithm is **not a generic accelerant**. // It targets a **specific structural regime** — bilateral hubs — // where fast matrix multiplication, or here its structural shadow, is genuinely worth setting up."

**Time check: ~2:30 cumulative. Move on.**

---

## Slide 13 — Takeaway (~60 s)

`[Pause. Make eye contact across the room before the first line. This is the payoff.]`

> "Two perspectives converge on the same conclusion."

`[One beat.]`

> "**Theoretical** — // from Speaker 3's analysis: of five inequalities in the constraint system, **only one binds** — the fast matrix multiplication step. That one step is load-bearing.
>
> **Empirical** — // from our experiments: of four input regimes we tested, **only one fires** — bilateral high-degree. That one regime is where the machinery earns its keep."

> "Both indicate the same thing: // the surrounding machinery exists to support **one well-conditioned matrix multiplication**. // Same statement, in two languages."

`[Brief pause, then transition.]`

> "Three open directions.
>
> **Larger cycles** — extend the lens beyond 4-cycles to general k-cycles.
>
> **Online detection** of the bilateral regime — a meta-algorithm that routes to the new algorithm when the structure is there, falls back to the baseline when it isn't.
>
> **Closed-form analysis at current matrix-multiplication exponents** — not just the conjectural limit `omega = 2`, but at the best known bound today."

`[Closing line — slow it down. Don't rush this.]`

> "More broadly, // this is a clean lens on the tension between **bulk** computation and **streaming** computation in dynamic data systems."

**Time check: ~3:30 cumulative.**

---

## Slide 14 — Thanks (~5 s)

> "Thank you. // Questions?"

`[STOP. Hands relaxed. Don't fill the silence — wait for someone to raise a hand.]`

---

## Quick delivery notes

- **Three things to land**, in order of priority:
  1. **"NumPy GEMM, not real FMM"** — say it on slide 11. This is the honest caveat. Don't skip it.
  2. **"Slope 0.3 versus 0.9"** — the single most defensible number. Memorize it.
  3. **The two-angle paragraph on slide 13** — theory and empirics saying the same thing. This is the talk's payoff. Do not rush it.

- **Things NOT to do**:
  - Don't dwell on the *blue* line on the plot (general Simple Wedge) — it's only there for visual scale. Real comparison is **red vs. green**.
  - Don't claim "we implemented Assadi–Shah" — we implemented their §3 warm-up. If asked, say so.
  - Don't read the slide. The audience can read. Speak *around* it: emphasis, story, gesture.
  - Don't list the open directions and trail off. Each one is a short sentence with a verb. Land each one cleanly.

- **If you go over time**, cut from:
  - The three-regime walk on slide 12 (keep "bilateral wins"; drop the unilateral/no-hubs detail — that's Q&A material).
  - The open directions on slide 13 (you can drop "closed-form analysis at current exponents" — keep the first two).
  - **Never cut** the caveat on slide 11 or the two-angle paragraph on slide 13.

- **Handoff line from Speaker 3** (so you're ready):
  > *"Theory says fast matrix multiplication is load-bearing. Does that story actually show up in practice?"*
  >
  > Your first words: *"Yes — we built a faithful implementation, and we tested exactly the question theory just asked."*
