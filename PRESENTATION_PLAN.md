# Presentation Plan — Counting 4-Cycles in Fully Dynamic Graphs

**Paper:** *Counting 4-Cycles in Fully Dynamic Graphs: A Cyclic-Join Perspective*
**Setting:** mock conference at end of Algorithms seminar (UL FRI), 15 minutes, 4 speakers.
**Goal:** **sell** the paper — pitch why the problem matters and what we contribute. Not a proof walkthrough.

---

## 1. Framing

Problem-first pitch. Open with a database problem, walk through what's known, show our contribution, end on where it actually matters in practice. Audience is fellow students + the professor, so:

- define every symbol on the slide it first appears (`m`, `n`, `O(·)`, *wedge*, *4-cycle*, ω);
- treat the FMM exponent ω as "matrix multiplication cost — currently below 2.372, conjectured 2";
- no proofs on slides; the closed-form certificate appears as a small table of numbers (the *answer*), not the derivation.

## 2. Timing budget (rough — adjust at rehearsal)

| Speaker | Beat | Slides | Time |
|---|---|---|---|
| 1 | The problem & why it matters | 1–3 | 3:30 |
| 2 | State of the art & the FMM surprise | 4–6 | 3:30 |
| 3 | Our angle: cyclic-join lens + closed-form certificate | 7–9 | 3:30 |
| 4 | Experiments & takeaway | 10–12 | 3:30 |
| — | Buffer / Q&A | — | 1:00 |

One slide ≈ one minute. Title and "Thanks/Questions" slides are 10–15 s each, so the heavier middle slides can stretch.

## 3. Handoff discipline

Each speaker ends with a one-sentence **question** that the next speaker answers. This is what makes a 4-person talk feel like one talk.

- S1 → S2: *"So what's the best anyone has done?"*
- S2 → S3: *"Their proof is dense. Can we see what's really going on?"*
- S3 → S4: *"Does any of this show up in practice?"*
- S4 → close: *"Thanks — questions?"*

---

## 4. Slide-by-slide outline

### Speaker 1 — The problem (3:30, slides 1–3)

**Slide 1 — Title.**
Paper title, all 4 names, course/conference name. Read out loud, ~10 s.

**Slide 2 — The hook in one picture.**
A 4-way cyclic join `A ⋈ B ⋈ C ⋈ D` drawn as a 4-layered graph (paper Figure 1). The picture *is* the pitch: a tuple in the join = a 4-cycle in the layered graph.
Punchline: *"Maintaining this answer under inserts and deletes = counting 4-cycles in a fully dynamic graph."*

**Slide 3 — What "fully dynamic" actually demands.**
Worst-case update time, not amortized. Why this matters: databases need predictable per-update latency, not "fast on average". State the target: beat recompute-from-scratch with a per-update worst-case guarantee.

→ Hand off: *"So what's the best anyone has done?"*

### Speaker 2 — State of the art & the FMM surprise (3:30, slides 4–6)

**Slide 4 — The landscape table.**
Reuse Table 1 from the paper:

| Pattern | Best dynamic update time |
|---|---|
| Triangle | `O(√m)` |
| 4-clique | `O(m)` |
| 4-cycle | `O(m^{2/3})` |

Three patterns; two solved cleanly, one stuck at a weird exponent.

**Slide 5 — Why m^{2/3}?**
One-line intuition for wedge maintenance (Hanauer–Henzinger–Hua). Why this is the natural ceiling for combinatorial methods: low-degree / high-degree split balances at `m^{1/3}` ⇒ `m^{2/3}` work per update.

**Slide 6 — The 2025 breakthrough.**
Assadi–Shah: `O(m^{2/3-ε})` using **fast matrix multiplication**. The surprise: FMM was folklore-considered incompatible with worst-case dynamic maintenance, because batched products clash with per-update budgets. They get around this with *phases* (precompute one batch, query against the previous batch).

→ Hand off: *"Their proof is dense. Can we see what's really going on?"*

### Speaker 3 — Our contribution (3:30, slides 7–9)

**Slide 7 — A cleaner lens: cyclic joins.**
Re-present Assadi–Shah through the IVM-for-cyclic-joins view. Show the lifting picture (paper Figure 2): every general-graph update becomes 4 layered-graph updates. With this lens the architecture becomes visible — degree classes, biadjacency matrices, where each step lives.

**Slide 8 — Where the FMM step lives.**
Of the whole machinery, exactly one product carries the speedup: the rectangular `A^{L*} · B_{ℓ,DD}` in Section 7. Everything else is bookkeeping. *This* is the load-bearing line.

**Slide 9 — Closed-form feasibility at ω = 2.**
The constraint system is 5 inequalities in a handful of exponents. We give **explicit rational parameters** that satisfy them at the conjectural `ω = 2`, with `ε = 1/24`. Show the certificate as a small table of values.
Point: Assadi–Shah's feasibility argument was numerical; ours is closed-form, so we can read off *which* constraint binds at ω = 2 (the rectangular FMM one).

→ Hand off: *"Does any of this show up in practice?"*

### Speaker 4 — Experiments & takeaway (3:30, slides 10–12)

**Slide 10 — The experiment.**
Faithful-in-shape implementation of the restricted variant vs. a layer-aware **Simple-Wedge** baseline. NumPy GEMM substitutes for FMM (the asymptotics aren't what we're testing — the *shape* of where the win comes from is). Two input regimes tested. One sentence on setup.

**Slide 11 — The finding (punchline slide).**
A simple chart locating the win: the class-routing machinery pays off **where there are bilateral hubs on both sides of the cyclic ordering**. On simpler inputs the wedge baseline already captures most of the benefit.

**Slide 12 — Takeaway + open questions.**
Two angles converged here: an algebraic improvement (the closed-form certificate) and machinery that was already there to feed it well-conditioned inputs (the warm-up).
Open directions: tighter constants, other cyclic-join sizes, what the picture looks like at the real `ω ≈ 2.372`.
Close with one sentence on why this matters for IVM more broadly.

→ "Thanks — questions?"

---

## 5. Defaults baked in (push back on any of these)

1. **12 slides, not 15.** Fewer dense slides beats more sparse ones at this length. Cut ruthlessly.
2. **Every speaker ends on a question.** Forces clean handoffs and keeps the talk feeling continuous.
3. **One figure per "heavy" slide.** Reuse paper Figures 1 and 2 — they already work and are familiar from the paper.
4. **No proofs on slides.** The closed-form certificate is a *table of numbers*, not a derivation. Anyone curious reads the paper.
5. **Speaker 3 carries the contribution.** Assign the strongest "explain a constraint system" speaker to that slot.

## 6. Rehearsal checklist

- [ ] Full dry run with timer, ≥ 1 week before the slot. Target 14:00 so you have 1:00 of slack.
- [ ] Every speaker has memorized their handoff sentence.
- [ ] Slide 9 (closed-form certificate) tested with someone outside the group — if they can't follow, simplify the table.
- [ ] Slide 11 chart legible from the back of the room.
- [ ] Backup: one extra slide per speaker, hidden, ready for likely Q&A questions (esp. "but ω isn't actually 2" — Speaker 3 answers).

## 7. Open items

- Who owns which speaker slot — to be decided.
- UL FRI CGP slide template — confirm with course page; build deck in that template.
- Dry-run date — set as soon as slot date is confirmed.
