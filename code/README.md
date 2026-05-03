# Code — fully dynamic 4-cycle counting

Implementation and benchmark suite for the seminar essay based on
Assadi & Shah, *Improved Fully Dynamic 4-Cycle Counting via FMM*
(PODS 2025, arXiv 2504.10748). See `../EXPERIMENTS_PLAN.md` for the
binding spec.

## Layout

```
algorithms/   four counters with a common interface
graphs/       generators (ER/BA/regular), planted-hub layered, SNAP loader, streams
bench/        timing harness + memory sampling
plots/        figure generation (reads results/*.csv → figures/*.pdf)
tests/        correctness gate (lockstep agreement vs brute force)
data/         SNAP downloads, gitignored
results/      one CSV per experiment
figures/      PDFs that ../paper/main.tex pulls in
```

## Quick start

```
pip install -r requirements.txt
pytest tests/                       # correctness gate, must pass
bash run_all.sh                     # all experiments (≤ 3 hours)
```

Single experiments are invokable as modules, e.g.
`python -m bench.runner --experiment 3.6 --n 1000 --seed 0`.

Conventions: Python 3.11+, type hints on public methods, `--seed` everywhere
randomness is used, all timings via `time.perf_counter` reporting median of 5
with IQR.

## Limitations (read this before citing the numbers)

This codebase is faithful in shape to paper §3 but makes two specific concessions
that change the asymptotics. Both are fundamental honesty constraints, not budget
choices. The same prose appears in paper §7.7.

1. **NumPy GEMM substitutes for fast rectangular matrix multiplication.**
   No practical implementation of fast rectangular FMM exists at the n we test
   (Strassen needs n in the thousands to even break even with BLAS GEMM;
   rectangular fast algorithms have impractical constants). Every "fast matrix
   multiplication" call in `algorithms/warmup_v3.py` is therefore plain
   `numpy.matmul`, marked with a `# FMM substitute: NumPy GEMM` comment.
   Consequence: the per-update exponent of our `Warmup_v3` is strictly worse
   than the paper's O(m^(2/3 − ε₁')) claim. What we benchmark is "§3 with cubic
   matmul", not "§3 with FMM".

2. **Assumptions 1 and 2 are fixed by construction.**
   Vertex degree-class assignments are decided at construction time and the
   stream generator refuses any update that would push a vertex across a class
   boundary (`ClassStabilityError`). We do not implement §6 (tiny vertices)
   or §7 (vertices changing class mid-stream) of the paper, which is the
   bookkeeping that removes these assumptions.

3. **§5 phases not implemented.** Chunk size is fixed at 1 (every update
   flushes immediately).

4. **Where Warmup_v3 wins at our scale (§3.6) is from class-based work
   avoidance, not from FMM exponents.** Specifically, hub-touching updates
   skip the per-neighbour enumeration of Simple Wedge in favour of a small
   number of GEMM calls over reduced submatrices.

If the §3.6 experiment fails to produce a clear separation between Warmup_v3
and Simple Wedge on planted-hub graphs, that is itself a publishable negative
result and we report it honestly.
