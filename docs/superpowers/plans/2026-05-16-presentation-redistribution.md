# Presentation Speaker Redistribution (Approach A) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Realign the 4-speaker division of the 4-cycle counting presentation to a balanced 3-3-3-3 content-frame split, and bring `presentation/speaker-notes.md` back in sync with the current `presentation/slides.tex`. The slide deck is final and is not edited.

**Architecture:** Two-file edit. `speaker-notes.md` is fully rewritten to (a) match the actual 13 frames in `slides.tex`, (b) reassign frames per Approach A, and (c) preserve the "each speaker hands off with a question, the next answers it" handoff discipline. `theory-notes.md` gets a single new section at the top mapping each speaker to the theory sections they own — the body of theory-notes is left intact as shared reference material.

**Tech Stack:** Markdown only. No code. No slide edits.

**Approach A — final frame assignments:**

| Speaker | Frames in `slides.tex` | Total content frames | Target time |
|---|---|---|---|
| 1 | 1 (title) + 2 (motivating query) + 3 (dynamic setting) + 4 (landscape table) | 3 + title | ~3:35 |
| 2 | 5 (where m^{2/3} comes from) + 6 (Assadi–Shah) + 7 (why MM) | 3 | ~3:30 |
| 3 | 8 (cyclic-join lens) + 9 (scaffolding) + 10 (FMM essential) | 3 | ~3:30 |
| 4 | 11 (empirical) + 12 (bilateral wins) + 13 (takeaway) + 14 (thanks) | 3 + thanks | ~3:35 |

Total target: **~14:10**, leaving slack on a 15-min budget.

**Key changes from the existing `speaker-notes.md`:**

1. Slide 4 (landscape table) moves **from Speaker 2 to Speaker 1**.
2. Slide 7 (why MM) — has no existing entry; **new content** under Speaker 2.
3. Old "Slide 9 — Closed-form certificate" referencing `ε₁=1/24, ε₂=5/24` does not match the actual slide 10. Replaced with notes for the actual slide 10 ("FMM is essential, not incidental"). The `1/24` numerical material stays available as Q&A backup, sourced from `theory-notes.md`.
4. Handoff lines between speakers are rewritten for the new boundaries.

---

### Task 1: Rewrite Speaker 1 section of speaker-notes.md

**Files:**
- Modify: `presentation/speaker-notes.md` — replace the "## Speaker 1" section (currently covers slides 1–3, ending before "## Speaker 2") with the content below.

- [ ] **Step 1: Replace the Speaker 1 section**

Replace from the line `## Speaker 1 — The problem (3:30)` through (and not including) the line `## Speaker 2 — State of the art & the FMM surprise (3:30)` with:

```markdown
## Speaker 1 — Frame the problem (3:35)

Owns slides **1–4**: title, motivating query, fully dynamic setting, landscape table.

### Slide 1 — Title (~15 s)

- Read the title and subtitle out loud.
- Introduce all four speakers by first name.
- One line: *"We want to convince you in 15 minutes that this paper deserves your reading time. Here's why."*
- Move on. Don't linger.

### Slide 2 — A motivating query (~1:20)

- Point at the picture *first*, talk *second*.
- Script:
  - *"Four accounts. `a` pays `b`, `b` pays `c`, `c` pays `d`, `d` pays back to `a`. The red arrows trace a 4-cycle in the transaction graph — a classic fraud-detection pattern."*
  - *"Formally this is a cyclic conjunctive query: four relations joined in a loop. The answer size is the number of 4-cycles."*
  - *"The same shape shows up in citation loops, mutual-follow communities, recommendation cycles."*
- Punchline (the alerted line on the slide): *"And the underlying graph is constantly evolving."*
- In-speaker transition to slide 3: *"What does it mean for the algorithm if the graph keeps changing?"*

### Slide 3 — The fully dynamic setting (~1:00)

- *"Every new transaction is an edge insertion. Some are reversed — deletions. After every single update, we report the exact 4-cycle count."*
- *"Recomputing from scratch on a large graph is prohibitively slow."*
- Read the block: *"We measure the slowest update — not the average."*
- Drive the worst-case point home with the 1-second-hiccup framing: a single bad update is a production incident even if the mean is fine.
- Close: *"Target: beat recompute-from-scratch under a per-update worst-case guarantee."*
- In-speaker transition to slide 4: *"How well does the literature do?"*

### Slide 4 — The landscape (~1:00)

- *"Three small patterns. Three best-known worst-case per-update bounds."*
- Walk the table once, top to bottom:
  - *"Triangles — root-m. Clean exponent."*
  - *"4-cliques — linear in m. Clean exponent."*
  - *"4-cycles — m to the two-thirds. Weird exponent."*
- *"That `m^{2/3}` was the best known for over a decade."*
- Do NOT explain *why* 2/3 here — that's Speaker 2's first slide.
- **Hand off to Speaker 2:** *"So why are 4-cycles stuck at two-thirds — and what changed?"*

### Anticipated Speaker-1 questions

- *"Why not amortise?"* — Databases get paged on tail latency, not means. Amortised bounds let outliers slip through.
- *"Why exact, not approximate?"* — Approximate algorithms exist and are useful; the paper targets exact, the stronger version.
- *"Why 4-cycles and not just 4-cliques or triangles?"* — 4 is the smallest non-trivial cyclic conjunctive query. Cyclic joins of any even length reduce to this kind of problem.
- *"Why does the landscape table not show the lower bound?"* — Mentioned in Speaker 2's section. Quick answer if asked early: `Ω(m^{1/2-γ})` under OMv.

```

- [ ] **Step 2: Verify the edit**

Open `presentation/speaker-notes.md`, scroll to Speaker 1, confirm:
- Slide numbering goes 1 → 2 → 3 → 4 (NOT stopping at 3).
- Final handoff line is *"So why are 4-cycles stuck at two-thirds — and what changed?"*
- No remaining `m^{2/3}` *explanation* in Speaker 1's section — only the fact that the bound exists.

---

### Task 2: Rewrite Speaker 2 section of speaker-notes.md

**Files:**
- Modify: `presentation/speaker-notes.md` — replace the "## Speaker 2" section.

- [ ] **Step 1: Replace the Speaker 2 section**

Replace from `## Speaker 2 — State of the art & the FMM surprise (3:30)` through (and not including) `## Speaker 3` with:

```markdown
## Speaker 2 — Prior art and the FMM bridge (3:30)

Owns slides **5–7**: where `m^{2/3}` comes from, the 2025 Assadi–Shah result, why matrix multiplication is the right tool.

### Slide 5 — Where m^{2/3} comes from (~1:20)

- Answer Speaker 1 directly: *"Two-thirds isn't arbitrary. It comes from a degree-class balance."*
- Three beats, using the diagram on the right of the slide:
  1. *"Few high-degree vertices — banks, large merchants. Each is expensive to process."*
  2. *"Many low-degree vertices — most accounts. Each is cheap."*
  3. *"Split at threshold `m^{1/3}`. Updates touching low-low pairs cost `m^{1/3} × m^{1/3} = m^{2/3}`. High vertices balance at the same exponent."*
- Punchline: *"This is the natural ceiling for any combinatorial algorithm processing one edge at a time."*
- If time, add one sentence on the lower bound: *"There's a matching OMv-conditional lower bound at roughly square-root-m. So there's a gap between `m^{1/2}` and `m^{2/3}` that combinatorial methods can't close."*

### Slide 6 — The 2025 result of Assadi and Shah (~1:10)

- Headline: *"Last year, at PODS 2025, Assadi and Shah broke the two-thirds wall: `m^{2/3 - ε}` for a constant `ε > 0`."*
- Don't read the exponent formula; just say *"two-thirds minus a small constant."*
- Sell the surprise: *"The ingredient is fast matrix multiplication — which everyone thought was useless here."*
- 15-second explanation of why FMM seemed useless:
  - *"FMM is bulk — multiply two big matrices at once."*
  - *"Dynamic problems are streaming — edges arrive one at a time."*
  - *"Folklore said these are incompatible."*
- Read the block: *"Their reconciliation is phases. During each phase, queries are answered against a precomputed product, while the next product is being assembled in the background, amortised across the phase. At the phase boundary, the products swap."*
- In-speaker transition to slide 7: *"OK — but why does matrix multiplication even fit a 4-cycle problem in the first place?"*

### Slide 7 — Why matrix multiplication? (~1:00)

- Point at the diagram on the left. *"Look at one 4-cycle as two 2-hop paths sharing the same endpoints."*
- The two coloured paths: *"`1 → 2 → 3` plus `1 → 4 → 3`. Two 2-hop paths with the same endpoints — that's one 4-cycle."*
- The reduction: *"So counting 4-cycles becomes: for every pair `(u, v)`, how many 2-hop paths connect them?"*
- *"The answer is a table indexed by pairs — one entry per pair of vertices."*
- Punchline (the alerted line on the slide): *"Computing that table is exactly a matrix multiplication. That's where MM enters."*
- *"Assadi and Shah use FAST matrix multiplication for this step. That is where the asymptotic speedup comes from."*
- **Hand off to Speaker 3:** *"OK, but the whole algorithm is much more than one matrix product. What does it actually look like?"*

### Anticipated Speaker-2 questions

- *"What is `ω` exactly?"* — Matrix multiplication exponent. Current best `< 2.371339`. Conjectured to be 2.
- *"How big is `ε`?"* — Tiny but constant. With current `ω`, about 0.01. At `ω = 2`, about `1/24 ≈ 0.04` (see theory-notes §4.4).
- *"How exactly do phases avoid the FMM-vs-streaming problem?"* — Updates are batched into phases of `m^{1-δ}` updates. The next product is precomputed in the background. Q&A backup in theory-notes §4.1.
- *"How is FMM different from regular MM?"* — FMM achieves `n^{ω}` with `ω < 3`. Regular schoolbook is `n^3`. Strassen 1969 was the first sub-cubic.

```

- [ ] **Step 2: Verify the edit**

Confirm:
- Speaker 2's section now contains exactly three slides (5, 6, 7).
- Slide 7 ("Why MM?") is new — does not exist in the pre-edit speaker-notes.
- The final handoff line is *"OK, but the whole algorithm is much more than one matrix product. What does it actually look like?"*
- The opener answers Speaker 1's question about why 2/3 is special.

---

### Task 3: Rewrite Speaker 3 section of speaker-notes.md

**Files:**
- Modify: `presentation/speaker-notes.md` — replace the "## Speaker 3" section.

- [ ] **Step 1: Replace the Speaker 3 section**

Replace from `## Speaker 3 — Our contribution (3:30)` through (and not including) `## Speaker 4` with:

```markdown
## Speaker 3 — Our contribution (3:30)

Owns slides **8–10**: the cyclic-join lens, the scaffolding around the MM step, the load-bearing argument.

### Slide 8 — The cyclic-join lens (~1:20)

- Answer Speaker 2: *"Yes — and the cleanest way to see it is the cyclic-join lens."*
- Point at the layered diagram on the left.
- Explain the lifting:
  - *"Each vertex of a 4-cycle plays one of four roles — position 1, 2, 3, or 4."*
  - *"Layer `L_i` collects every vertex viewed as a candidate for role `i`. Conceptually, four copies of the vertex set."*
  - *"Matrix `A` is the edges between role-1 and role-2 candidates. Matrix `B` is between role-2 and role-3."*
- The product: *"Then `A · B` counts, for each pair of role-1 and role-3 vertices, the number of role-2 intermediates — exactly the TOP HALF of slide 7's 4-cycle."*
- Punchline: *"Fast matrix multiplication evaluates this product strictly faster than naive — the shortcut that breaks `m^{2/3}`."*
- Optional: *"The whole algorithm sits inside this 4-layered picture: degree classes are thresholds on the layers, chunks are blocks of `B`, phases re-shuffle the precomputed product."*

### Slide 9 — One MM step, supported by scaffolding (~1:10)

- *"We've located the MM step. But a fundamental tension remains."*
- Read the block: *"FMM is bulk — needs two complete matrices at once. The problem is streaming — edges come one at a time."*
- The alerted line on the slide: *"Every remaining component of the algorithm exists to bridge that gap."*
- Walk the bullet list quickly — one line each:
  - *"Degree partitioning controls matrix size and shape so the FMM input is well-conditioned."*
  - *"Chunked maintenance amortises the bulk MM cost across many updates."*
  - *"Phases keep a precomputed product ready while the next is being assembled."*
- Closing line: *"All of this complexity serves one purpose — render a bulk matrix multiplication compatible with a streaming workload."*

### Slide 10 — FMM is essential, not incidental (~1:00)

- *"Could the speedup come from a different part of the machinery? We verified it cannot."*
- *"We analysed the constraint system at the conjectural optimum — the best possible matrix-multiplication exponent."*
- Read the block as written: *"Remove the fast matrix multiplication step and the entire speedup vanishes; the bound collapses back to the prior `m^{2/3}`."*
- Closing line: *"FMM is the load-bearing step. Everything around it exists to make FMM usable in a streaming setting."*
- **Hand off to Speaker 4:** *"Theory says FMM is load-bearing. Does that story actually show up in practice?"*

### Anticipated Speaker-3 questions

- *"What does 'analysed the constraint system at the conjectural optimum' actually mean?"* — Five inequalities relate `ε`, `ε₁`, `ε₂`, `ω`. At `ω = 2` we have a closed-form solution `ε₁ = 1/24, ε₂ = 5/24, ε = 1/24`, two constraints binding — the FMM one and the SS/SD threshold. Detail in theory-notes §4.3–4.4.
- *"Which constraint binds?"* — The Low-Dense FMM constraint (the only `ω`-dependent one). That's the load-bearing argument.
- *"Why bother with closed-form when numerical works?"* — Numerical verification tells you the system is feasible. Closed-form tells you *which* constraint binds, which is what makes the "FMM is load-bearing" claim sharp.
- *"What's `ε` at current `ω`?"* — Around 0.01. The `1/24 ≈ 0.04` is at the conjectural `ω = 2`.
- *"Are there other feasible points?"* — Almost certainly yes — the constraints are inequalities, not equalities. We just give one clean rational solution.

```

- [ ] **Step 2: Verify the edit**

Confirm:
- Speaker 3's section contains exactly three slides (8, 9, 10).
- Slide 8 opens by answering Speaker 2's handoff question.
- The `1/24` numerical content is preserved in Q&A, NOT in the body of slide 10's script (slide 10 doesn't show the numbers — only that the constraint system was analysed).
- Slide 10's body reads the slide's block verbatim where indicated.

---

### Task 4: Rewrite Speaker 4 section of speaker-notes.md

**Files:**
- Modify: `presentation/speaker-notes.md` — replace the "## Speaker 4" section.

- [ ] **Step 1: Replace the Speaker 4 section**

Replace from `## Speaker 4 — Experiments & takeaway (3:30)` through (and not including) `## Logistics` with:

```markdown
## Speaker 4 — Experiments and takeaway (3:35)

Owns slides **11–13** + thanks: empirical setup, the bilateral-hub finding, takeaway, thanks.

### Slide 11 — Implementation and empirical setup (~1:00)

- Answer Speaker 3: *"Yes — we built a faithful implementation and tested it."*
- Three components, walk the bullet list:
  - *"Algorithm — a faithful Python implementation of the new algorithm's structure: four layers, degree thresholds, chunked update maintenance, and the central matrix-multiplication step."*
  - *"Baseline — the natural simpler approach: wedge-counting on the same four-layered graph, without the class-routing machinery."*
  - *"Test harness — a graph generator with controllable structure: random, one-sided high-degree, two-sided high-degree, or uniformly low-degree."*
- *"Both algorithms run on identical graphs and identical update streams."*
- **Crucial caveat** — say this out loud: *"We're not testing asymptotics. NumPy GEMM is cubic, not `n^ω`. We're testing the SHAPE of the win — which inputs make the surrounding machinery worth its complexity."*

### Slide 12 — Where the algorithm wins: bilateral high-degree structure (~1:30)

- *"This is the punchline of the experiment."*
- Point at the plot on the left first, then walk the diagram on the right.
- The plot: *"In this regime, the new algorithm grows much more slowly than the baseline. The gap opens as the input grows."*
- Walk the three cycle diagrams on the right:
  - *"Bilateral — high-degree vertices on opposite sides of the cycle — new algorithm wins. Check mark."*
  - *"Unilateral — high-degree on one side only — baseline matches."*
  - *"No hubs — uniformly low degree — baseline matches."*
- Close: *"The algorithm is not a generic accelerant. It targets a specific structural regime where fast matrix multiplication is worth setting up."*

### Slide 13 — Takeaway (~1:00)

- Close the loop with the two-angles framing:
  - *"Theoretical — one step is load-bearing: the fast matrix multiplication."*
  - *"Empirical — one regime requires the machinery: bilateral high-degree."*
- *"Both indicate the surrounding machinery exists to support one well-conditioned matrix multiplication."*
- Open directions (read the bullets):
  - *"Larger cycles — `k`-cycles beyond 4."*
  - *"Online detection of the bilateral regime, with fallback to the baseline."*
  - *"Closed-form analysis at current matrix-multiplication exponents."*
- Closing line: *"More broadly, a clean lens on the tension between bulk and streaming computation in dynamic data systems."*

### Slide 14 — Thanks (~5 s)

- *"Thank you. Questions?"*
- Don't fill silence. Wait for a hand.

### Anticipated Speaker-4 questions (and team-wide Q&A)

- *"How real are these results at scale?"* — NumPy GEMM handles `n ≈ 10⁴` per layer on a laptop. Beyond that, a real FMM implementation is needed — and one doesn't exist below Strassen. The structural finding is robust within tested scales.
- *"Bilateral hubs — how often does that happen in real data?"* — Open question. We didn't sample real database workloads. Listed as an open direction.
- *"What's the gap to the lower bound?"* — `Ω(m^{1/2-γ})` vs `O(m^{2/3-ε})` with `ε = 1/24`. Big gap. Nobody knows where the truth is.
- *"What about other cyclic patterns?"* — Same framework should adapt to cyclic joins of any even size. Open work.
- *"Is this practical today?"* — Not directly — FMM implementations don't exist below Strassen. The framework already tells you when *combinatorial* routing helps; that's the practical takeaway.
- *"Why is NumPy GEMM defensible if it isn't real FMM?"* — Because we're testing structural routing decisions, not the inner multiply. The shape of the win is robust to the matrix kernel.

```

- [ ] **Step 2: Verify the edit**

Confirm:
- Speaker 4's section contains exactly slides 11, 12, 13, 14 (thanks).
- The "NumPy GEMM, not real FMM" caveat appears explicitly in slide 11's script.
- Slide 12's script walks the three diagram options (bilateral / unilateral / no hubs) in the order the slide shows them.

---

### Task 5: Update the Logistics section of speaker-notes.md

**Files:**
- Modify: `presentation/speaker-notes.md` — replace the "## Logistics" section.

The existing cut-list references slide numbers from the pre-edit numbering (e.g. "Drop Slide 5" was the `m^{2/3}` slide — same number, fine; "Drop right column of Slide 9" referred to a no-longer-existing closed-form slide). Refresh.

- [ ] **Step 1: Replace the Logistics section**

Replace from `## Logistics` to end of file with:

```markdown
## Logistics

### Rehearsal protocol

1. **Solo run.** Each speaker rehearses their ~3:30 alone, with a timer. Target 3:15 to leave handoff slack.
2. **Pair runs.** Each consecutive pair rehearses the handoff together: one ends with a question, the next opens by answering it. Do this until it sounds natural, not scripted.
3. **Full run.** All 4 speakers, end-to-end, with timer. Target total **14:00** to leave 1:00 of slack. Don't aim for exactly 15:00 — that's how you go over.
4. **Cold run.** Run it once in front of someone outside the group. Note where they lost the thread. Cut or rephrase the slide they lost you on.

### What to do if you're running long

In priority order — cut the costliest first:

1. **Compress Slide 5** (`m^{2/3}` intuition). Drop to a single sentence: *"`m^{2/3}` is the balance of a degree-class threshold at `m^{1/3}`; that's the natural combinatorial ceiling."* Saves ~45 s.
2. **Drop the optional lower-bound aside on Slide 5.** Saves ~10 s.
3. **Compress Slide 9's bullet list** (degree partitioning / chunked maintenance / phases) to one sentence: *"Three pieces around the MM step, all in service of feeding it a well-conditioned input."* Saves ~30 s.
4. **Compress Slide 12.** Just point at the chart and at the bilateral diagram. Skip the unilateral/no-hub walk-through.

### What to do if you're running short

1. Spend more time on Slide 2 (the picture). Walk the cyclic join slowly. It's the whole pitch.
2. On Slide 7 (Why MM?), spell out the 2-hop-path reduction with the audience step-by-step.
3. On Slide 12, walk one curve of the plot in detail (slope, what it means).

### Backup slides (optional, hidden)

If you want to be over-prepared, prepare these on paper or as hidden slides after Thanks:

- **B1.** The five inequalities of the constraint system with one-line meanings (theory-notes §4.3).
- **B2.** The phases diagram (theory-notes §4.1).
- **B3.** The Simple-Wedge update pseudocode (theory-notes §6.2).
- **B4.** The full results plot grid (paper Figure 8 series).

You can hop to any of them via slide number in case of Q&A.
```

- [ ] **Step 2: Verify the edit**

Confirm:
- The "cut" list references slide numbers that exist in the current `slides.tex` (slides 5, 9, 12 — all valid).
- The "no Slide 9 closed-form" cut from the old version is gone.
- File ends cleanly with the Backup slides section.

---

### Task 6: Add a speaker–theory mapping preamble to theory-notes.md

**Files:**
- Modify: `presentation/theory-notes.md` — insert a new section between the existing intro paragraph and section "## 1. The problem setting".

- [ ] **Step 1: Insert the speaker–theory mapping**

After the line `Read this once before the dry run. Each section maps to one or two slides.` and before the `---` separator preceding `## 1. The problem setting`, insert:

```markdown

### Per-speaker reading priorities

Each speaker should fully digest their own column. The other columns are nice-to-have for Q&A.

| Speaker | Must read | Useful for Q&A |
|---|---|---|
| 1 (slides 1–4) | §1 (problem setting), §2.1 (landscape table) | §2.3 (lower bound), §7 (notation) |
| 2 (slides 5–7) | §2.2 (where `m^{2/3}` comes from), §3.1–3.2 (FMM, OMv), §4.1 (phases) | §4.2–4.3 (degree classes, constraint system) |
| 3 (slides 8–10) | §5 (cyclic-join lens), §4.2–4.4 (degree classes, constraints, closed-form) | §4.1 (phases), §3.1 (FMM) |
| 4 (slides 11–13) | §6 (empirical study), §9 (likely audience questions) | §5.4 (why the lens helps), §4.4 (closed form, for Q&A) |

Sections not listed for any speaker are general background everyone benefits from skimming once.

```

- [ ] **Step 2: Verify the edit**

Confirm:
- New section is between the intro and `## 1. The problem setting`.
- Each speaker has at least one "must read" entry.
- All section numbers referenced (`§1`, `§2.1`, …) exist in the current `theory-notes.md` body.

---

### Task 7: Final cross-check — read top-to-bottom

- [ ] **Step 1: Re-open both files and read end-to-end**

Open `presentation/speaker-notes.md` and `presentation/theory-notes.md`. Verify:

1. `speaker-notes.md` has exactly four `## Speaker N` sections, in order 1, 2, 3, 4.
2. Slide numbers in `speaker-notes.md` go 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 — no gaps, no duplicates.
3. Each speaker's *final* line is a handoff question that the next speaker's *first* slide answers (except Speaker 4, which closes with thanks).
4. No reference to a "closed-form certificate" slide (it doesn't exist in `slides.tex`).
5. The numerical `1/24, 5/24` material appears only in Q&A and in `theory-notes.md`, never in the body of any slide script.
6. `theory-notes.md` has the new "Per-speaker reading priorities" table.

- [ ] **Step 2: Time check**

Sum the time budgets in `speaker-notes.md`:

- Speaker 1: 15 + 80 + 60 + 60 = 215 s = 3:35
- Speaker 2: 80 + 70 + 60 = 210 s = 3:30
- Speaker 3: 80 + 70 + 60 = 210 s = 3:30
- Speaker 4: 60 + 90 + 60 + 5 = 215 s = 3:35

Total: ~14:10. Within the 15:00 budget with ~50 s of slack. Per-speaker spread is 3:30–3:35 (within the user's 3–5 minute requirement).

If any number drifted during the edits, recompute and either trim a beat or relax the per-slide target.

---

### Task 8: Ask about committing

- [ ] **Step 1: Ask the user**

Per the user's hard rule on commits (see global `CLAUDE.md`), do NOT commit. Use `AskUserQuestion` with an explicit options-show-the-commit-message form to propose committing the two updated files (and the plan doc) as one commit. If denied, leave the working tree dirty and let the user handle it.

---

## Self-Review (run before handing off)

**Spec coverage.** The user asked for: (a) 4 sections for 4 speakers, (b) each speaker can prep their part separately with light context only, (c) each speaker talks 3–5 minutes. Tasks 1–4 cover (a); Task 6 (the per-speaker theory mapping) supports (b); Task 7 step 2 validates (c).

**Placeholder scan.** No "TBD", "TODO", "fill in later" anywhere. Each script step has actual speakable content.

**Type consistency.** Slide numbers are consistent with `slides.tex` frame order. Speaker numbers 1–4 are consistent throughout. The two-angles framing ("theoretical / empirical → one binding constraint / one firing regime") is consistent between Speaker 3's slide 10 and Speaker 4's slide 13.

**Out of scope (per user instruction).** `presentation/slides.tex` is NOT edited. No LaTeX changes. No `.pdf` regeneration steps.
