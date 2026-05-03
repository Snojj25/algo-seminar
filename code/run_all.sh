#!/usr/bin/env bash
# Reproduce every CSV and PDF deliverable from a clean checkout.
# EXPERIMENTS_PLAN.md §6.2 budget: ≤ 3 hours on a recent laptop, hard ceiling
# of 10 minutes per experiment cell (enforced inside bench/runner.py).

set -euo pipefail

cd "$(dirname "$0")"

echo "==> tests"
python3 -m pytest tests/ -q

echo "==> downloading SNAP datasets (idempotent)"
bash data/download.sh

echo "==> experiment 3.0 already validated by tests/"

for exp in 3.5 3.1 3.2 3.3 3.4 3.6 3.6.1 3.7; do
    echo "==> experiment $exp"
    python3 -m bench.runner --experiment "$exp"
done

echo "==> rendering figures"
python3 -m plots.figures

echo "done"
