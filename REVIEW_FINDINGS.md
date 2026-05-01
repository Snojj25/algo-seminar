# Review findings

Synthesis of four adversarial reviews (three Claude agents + Codex CLI) on `ESSAY_PLAN.md`, `SECTIONS.md`, `paper/main.tex`. Findings are deduplicated and triaged.

Reviewers: **R1** = math/correctness · **R2** = scope/feasibility · **R3** = assignment alignment · **CX** = Codex CLI external.

---

## Critical (correctness or assignment-flunking) — must fix

### F1 — "Walks" vs "paths" in Theorem 1 statement
Reviewers: R1, CX.
Paper Claim 8.1 states "walks of length 3 in G' = paths of length 3 in G". `SECTIONS.md` §3.3 mistakenly says "layered 3-paths" on the LHS, which makes the claim vacuous. `paper/main.tex` got it right.

### F2 — Bogus "correction term" / W[v,v] in Algorithm 1
Reviewers: R1, CX.
`ESSAY_PLAN.md` §5.1 and `SECTIONS.md` §4.1 mention `Δ = Σ W[w,v] − W[v,v]·[wedge correction]`. The paper's Claim A.3 uses no such correction — correctness comes from the update-order rule (query-then-update on insert; update-then-query on delete) which keeps (u,v) absent from W during the query.

### F3 — D→C→B→A insertion order and query-after-D timing missing from setup
Reviewers: R1, CX.
The reduction's correctness depends critically on the layered-graph update protocol: insertions go D→C→B→A; queries answered immediately after the D update; deletions reverse. `SECTIONS.md` §3.2 mentions ordering but does not state that queries happen after the D update specifically. Without this, the proof of F1 fails.

### F4 — Plan reads as a paper-report, not a topic essay
Reviewers: R3.
Title "An Exposition of...", every theorem tagged "(= Claim X of paper)", roadmap says "self-contained exposition of three components of the paper's argument". This is exactly the failure mode the professor warns against in `recenzije-obrazec.pdf` p.3. Compare the Funnel Heap paper (`Clanek.pdf`), which presents *its own* construction.

### F5 — Conference-report deliverable absent from essay-track plan
Reviewers: R3.
`README.md` mentions it but neither `ESSAY_PLAN.md` nor `SECTIONS.md` track it: no candidate papers, no champions, no draft summaries. This is a separately-graded deliverable.

### F6 — EasyChair anonymity not configured
Reviewers: R3.
`paper/main.tex` line 9 uses `\documentclass[sigconf,nonacm]`. The `anonymous,review` options are commented as a swap-before-submission note. Authors are real-looking placeholders. Will be forgotten.

---

## High (quality or feasibility) — should fix

### F7 — Page budget already over
Reviewers: R2, CX.
`SECTIONS.md` page targets sum to 10.5 body pages; the empty scaffold already burns ~30% of the budget on structure. References at full size add another ~0.7 page. ESSAY_PLAN.md's proposed cuts ("figure captions") don't free meaningful space.

### F8 — §5 is structurally impossible at 3 pages
Reviewers: R2, R3, CX.
6 subsections + Table 2 + Lemma 3 + Theorem 4 + 9-row data-structure walkthrough + database gloss + query case analysis. Even the empty scaffold has §5 spilling across pages. Needs a real scope cut.

### F9 — Experiment plan: dense wedge matrix at email-Enron scale is infeasible
Reviewers: R2, CX.
At n=36k a dense W matrix is ~5 GB. Naive-Recompute at n=5000 with m≈n^1.7 is minutes per update in Python — 1000-update sweep is hours per cell. Plan is incoherent at the planned scales.

### F10 — Baseline algorithm not specified — three different ones implied
Reviewers: R1, CX.
`ESSAY_PLAN.md` §5.1: "AYZ approach", "or wedge-sum", "or brute force". These are different algorithms with different complexities; the experiment cannot have a stable baseline.

### F11 — "Re-derive constraint system cleanly" is wishful
Reviewers: R1.
Paper Appendix B uses the [Bra] complexity-term-balancer with rectangular-FMM bounds from [ADW+25]. Students cannot reproduce ε₁=0.04201965 by hand. Plan promises to re-derive in `ESSAY_PLAN.md` §2.

### F12 — Three formal proofs are routine, not "interesting" formal proofs
Reviewers: R3.
Claim 8.1 (2 paragraphs of distinctness arguments), Lemma A.1 (1-liner), Claim 3.6 (dimension bookkeeping). The example-essay rubric praises "lastni premislek in razširili problem" — an actual extension. The current proofs may not satisfy the assignment's "formalni dokaz" expectation in spirit.

### F13 — ω < 2.5 vs ω < 2.5 − O(ε) is mis-stated
Reviewers: R1.
The paper says δ > 0 requires ω < 2.5 − O(ε) — strict inequality with ε slack. The plan's "ω < 2.5" headline is necessary but not sufficient. `ESSAY_PLAN.md` §2 and `SECTIONS.md` abstract bullet say it incorrectly.

### F14 — Theorem 1 of paper is restated prominently though we don't prove it
Reviewers: CX.
`paper/main.tex` Theorem 5 reproduces Theorem 1 of the paper as if it's a result we deliver. Reviewer can fairly say we prove only fragments while claiming the full theorem.

### F15 — Survey draws only from the source paper's bibliography
Reviewers: R3.
All 13 cite-keys are pulled from Assadi–Shah's references with the same usage. Assignment requires "pregled področja izbranega članka", which implies external reading.

### F16 — Own contribution is weak per the example-essay rubric
Reviewers: R3.
The implementation is a textbook 30-line algorithm benchmark. The rubric praises "dodali svoj premislek in razširili problem" — actual problem extension. Need a real intellectual contribution beyond running numpy.

---

## Medium — worth a one-line fix or note

| # | Issue | Reviewer |
|---|---|---|
| F17 | PODS/database angle treated as one paragraph in §1.2 then forgotten | R3 |
| F18 | 15-minute presentation has no owner/plan | R3 |
| F19 | Algorithm 1 has potential issue if N(u) includes v at delete-time | R1 |
| F20 | Work distribution: B owns 3 sections + 2 proofs; serial-blocks C on §5 | R2 |
| F21 | Figure 2 (lifting diagram) has no tool/owner/timeline | R2 |
| F22 | Reference-counting policy (refs inside or outside 10 pages?) undefined | R2 |
| F23 | `\fmm` macro defined but never used in `main.tex` | R1 |
| F24 | ε used in essay §1 Table 1 without prior definition | R1 |
| F25 | Five theorem-class boxes is heavy for 10 pages | R2 |
| F26 | Naive-Recompute "AYZ" framing is technically wrong (AYZ is a static FMM algorithm, not what one runs to recompute) | R1, CX |

---

## Triage decisions

**To implement now in this session:**
- F1, F2, F3 — correctness fixes to the planning docs
- F4 — drop "= Claim X of paper" tags; retitle; reframe roadmap
- F6 — make `anonymous,review` the default class option; strip placeholder names to a separate non-anon build
- F7+F8 — make a real cut: drop essay §6 entirely, fold a one-paragraph phases note into §5 closing or §8
- F10 — commit to one specific baseline algorithm
- F11, F13 — fix the math wording
- F14 — explicitly say "we prove fragments; Theorem 1 of [paper] is the assembly we don't reproduce"
- F23, F24 — small LaTeX hygiene

**To flag for the team but not implement (decisions they need to make):**
- F5, F18 — the conference report and presentation are separate trackers; add stubs in `README.md`
- F12, F16 — strengthening contribution. Recommend promoting the constraint-system feasibility check (verify ω=2 case by hand) as a fourth/replacement proof; team decides.
- F15 — external references must be read by team members.
- F20 — work distribution rebalance — team decides.

**Defer (not blocking):**
- F17, F19, F21, F22, F25, F26 — track in this doc; revisit during drafting.
