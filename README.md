# Algoritmi seminar — PODS 2025

Working plan for the group seminar in the Algorithms course at UL FRI. Group of 4. Conference of choice: **PODS 2025** (Principles of Database Systems), proceedings file `3744552.pdf` (PACMMOD Vol. 3, Issue 2, May 2025).

---

## 1. The conference at a glance

| Field | Value |
|---|---|
| Name | PODS 2025 — Principles of Database Systems |
| Host | Held jointly with SIGMOD 2025 |
| Location | Berlin, Germany |
| Dates | June 2025 (confirm exact dates from the SIGMOD/PODS 2025 website) |
| Published as | PACMMOD Vol. 3, Issue 2 (May 2025) |
| Editorial | Article 087 in the proceedings (Carmeli, Geerts, Kara, Kimelfeld) |
| Acceptance — this issue | 30 accepted / 80 submitted (37.5%) — Dec 2024 cycle |
| Acceptance — full conference | 45 accepted / 127 submitted (35.4%) — combined June + Dec 2024 cycles |
| Topics | Database theory: query languages (conjunctive, regular path, Datalog), differential privacy, streaming/sketching, graph algorithms, complexity theory, fast matrix multiplication |
| Articles in this issue | 088–117 (30 papers) |
| Proceedings URL | https://dl.acm.org/toc/pacmmod/2025/3/N2 |

---

## 2. What we have to deliver

Four distinct outputs. The essay is the big one; the others are smaller.

### 2.1 Essay ("članek") — the main deliverable

- ≤ 10 pages
- ACM SIG Proceedings (sigconf) template — `acmart-primary/samples/sample-sigconf.tex`
- Standalone paper on the **topic**, NOT a report on the source paper
- Must include a **formal proof** of correctness or complexity
- Must extend the foundational paper via at least one of:
  1. Survey of the area using the source paper's references
  2. Own thinking / improvement of results (most desired by the professor)
  3. Experimental evaluation
- Submitted on EasyChair, cross-reviewed anonymously by other groups

Reference example: `Clanek.pdf` (Funnel Heap, Brodal & Fagerberg) — note that it does not say "we read paper X and here's what it says"; it makes its own contribution to a topic and cites prior work.

### 2.2 Conference report

- Separate, shorter document (~4–6 pages)
- Must contain: topics, location, dates, # submitted, # accepted, plus 3 paper summaries
- Each summary ≤ 500 words, in our own words (no copy-paste)
- We are a single group (not double), so 3 papers, not 6
- Adds one row to the course wiki table for PODS 2025 with these columns:

| Column | Value |
|---|---|
| (i) Year | 2025 |
| (ii) # submitted | 127 conference-wide (or 80 for this issue) |
| (iii) # accepted | 45 conference-wide (or 30 for this issue) |
| (iv) URL of proceedings | https://dl.acm.org/toc/pacmmod/2025/3/N2 |
| (v) PDF of report | our compiled report file |
| (vi) Presentation file | our slides |

### 2.3 Presentation(s)

The Slovenian assignment text suggests **two separate presentations** (the phrase *"Kakor pri prvem seminarju..."* implies a first and a later seminar):

1. **Conference summary** presentation — earlier in the semester, covers the report
2. **Essay** presentation — 15 min, in the last three lecture slots, sells the foundational paper / our contribution

Use the official UL FRI CGP slide template. **Confirm with the professor** whether there is one or two separate presentations.

### 2.4 Peer reviews — individual, on EasyChair

- Done individually (not as a group)
- Use the form in `recenzije-obrazec.pdf` (six sections: Vsebina, Tok, Oblika, Dobre strani, Predlogi, Splošno + Confidence)
- Style reference: `recenzije-primer.pdf` — concrete page-level comments, framed as help to the author
- Plan ~3–4 hours per review

---

## 3. The three categories of papers (clarification)

| Category | Count | Purpose |
|---|---|---|
| **Temeljni članek** | 1 | The spine of the 10-page essay |
| **Conference-report papers** | 3 | Each gets a ≤500-word summary in the report |
| **Cited references** | ~10–20 | Background/related-work in the essay; mostly drawn from the temeljni članek's bibliography |

The 3 report papers are *of our choice* and don't have to be related to the temeljni članek. They are typically picked to span different subtopics so the report reads as a tour of the conference.

---

## 4. Selection process — three filtering rounds

This mirrors what the assignment text explicitly describes (*"prvi pregled"* → *"podrobneje pregledamo"* → *"natančno branje"*).

### Round 1 — first pass over all 30 papers

- Goal: shortlist of 5–8 candidate papers
- Depth: title + abstract + glance at intro + glance at conclusion (~5–10 min per paper)
- Distribution: ~7–8 papers per person × 4 people = full coverage in parallel
- Output: one-line note per paper (`interesting / boring / out-of-scope / maybe`) + a sentence summary
- Group meeting: combine notes, pick shortlist

### Round 2 — deeper read of the shortlist

- Goal: pick the temeljni članek
- Depth: full intro, skim technical sections, full conclusion (~30–60 min per paper)
- Distribution: assign one champion per shortlisted paper
- Each champion writes a half-page brief (problem / result / techniques / extension angles / math accessibility)
- Group meeting: 5-min pitch per champion, vote

**Selection criteria for the temeljni članek** (priority order):
1. All 4 of us are willing to spend a month on it
2. The math is accessible — we have to write a formal proof
3. Clear angle for extension (tightenable bound, alt proof, missing experiment, special case)
4. Good bibliography (we lean on it for the survey section)
5. Lies in the algorithms wheelhouse rather than pure database theory

### Round 3 — full read of the temeljni članek

- All 4 group members read it in full detail
- Different members may focus on different sections, but everyone must understand the main result

### Selecting the 3 report papers

- Done after the temeljni članek is chosen (papers we noticed in Round 1 but didn't pick)
- Pick from different subtopic areas for variety
- One champion per paper

---

## 5. Phased timeline

Rough phasing — adjust to actual deadlines.

| Phase | Duration | What happens |
|---|---|---|
| 0. Alignment | ~1 hr | All 4 read assignment + example review; agree tooling (Overleaf, shared notes); decide cadence |
| 1. First-pass review (parallel) | ~1 week | Round 1 triage of 30 papers → shortlist of 5–8 |
| 2. Detailed read + decision | ~3–4 days | Round 2; pick temeljni članek |
| 3. Conference report | ~1 week | Pick 3 report papers, write summaries + metadata, build slides |
| 4. Essay | ~3–4 weeks | Set up LaTeX, draft sections, write formal proof, iterate |
| 5. Presentation | ~1 week before talk | Build essay slides, rehearse |
| 6. Peer reviews | After submission | Each member reviews assigned essays on EasyChair |

---

## 6. Work distribution among 4 people

### For the essay (Phase 4)

| Role | Owns | Why |
|---|---|---|
| Lead / Editor | LaTeX skeleton, intro, conclusion, glue, final submission | Someone has to own coherence and EasyChair logistics |
| Background | Section 2 (survey), reference management | Reads ~10–15 references from the source paper |
| Theory | Section 3 + the formal proof | Strongest theory person; the proof is required and central |
| Contribution | Section 4 (the extension) | Whatever we agree on: tightened bound, alt proof, experiment, synthesis |

Everyone proofreads everything in the last week.

### For the conference report (Phase 3)

| Person | Owns |
|---|---|
| A | Paper 1 summary (~500 words) |
| B | Paper 2 summary (~500 words) |
| C | Paper 3 summary (~500 words) |
| D | Conference metadata page (topics, location, dates, stats) + integration & proofreading |

### For peer reviews (Phase 6)

Individual. Each member reviews whatever EasyChair assigns them.

---

## 7. Files in this repo

| File | What it is |
|---|---|
| `3744552.pdf` | PODS 2025 proceedings (631 pages, 27 MB). TOC is on pages 4–7; editorial is article 087 (page 8 onward). |
| `Clanek.pdf` | "Funnel Heap" by Brodal & Fagerberg — the example of an essay-style paper |
| `recenzije-obrazec.pdf` | Blank review form (the structure EasyChair will give you) |
| `recenzije-primer.pdf` | Two example completed reviews (one mid, one excellent) — use as style reference |
| `acmart-primary/` | ACM LaTeX class. Sigconf sample at `samples/sample-sigconf.tex` and `samples/sample-sigconf.pdf` |
| `acmart-primary/acmguide.pdf` | Full reference manual for the ACM class |

---

## 8. Open questions to resolve before starting

- **Year** — assignment text mentions "row for the year 2020"; this is almost certainly a leftover and should be the conference's actual year (2025). Confirm with the professor.
- **Submission numbers** — report 127/45 (conference-level) or 80/30 (this issue only)? Pick one and be consistent.
- **One presentation or two?** — see Section 2.3. The Slovenian text suggests two; confirm with the professor.
- **Exact deadlines** — EasyChair submission deadline, presentation slot dates, peer-review deadline. Pull these from the course page.

---

## 9. Immediate next step

**Round 1 triage** of the 30 abstracts in the proceedings — produce a one-page sortable list (title, authors, ~3-line summary, suitability note for an algorithms seminar with a required formal proof). This is the artifact the group needs to start the first meeting from.

---

## 10. Conference report tracker (F5)

The conference-report deliverable is *separate* from the essay and is currently underspecified. Fill in below.

| Slot | Paper (PODS 2025 article #) | Champion | Draft status |
|---|---|---|---|
| Summary 1 | TBD | TBD | not started |
| Summary 2 | TBD | TBD | not started |
| Summary 3 | TBD | TBD | not started |
| Conference metadata page (topics, dates, stats) | — | TBD (likely D or A) | not started |

Picking criteria (from §3): different subtopic areas for variety; ≤500 words each in own words; champions can read just abstract + intro + conclusion.

## 11. Presentation tracker (F18)

The 15-minute essay presentation at end-of-semester conference — currently has no plan.

- Slide template: official UL FRI CGP
- Owner / driver: TBD (recommended: A — Lead)
- Slide-count target: ~12 slides for 15 min (rough rule: 1 minute per slide, plus buffer)
- Goal: convince audience to *read* the paper — pitch the result, not the proofs
- Dry-run date: TBD (target ≥ 1 week before talk slot)
- Open question: is the conference-summary presentation a separate earlier seminar? (See §2.3 above.)
