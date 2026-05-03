#!/usr/bin/env bash
# Download SNAP datasets used in EXPERIMENTS_PLAN.md §3.4.
# Idempotent: re-running is a no-op if files exist.

set -euo pipefail

cd "$(dirname "$0")"

declare -a FILES=(
    "https://snap.stanford.edu/data/ca-GrQc.txt.gz"
    "https://snap.stanford.edu/data/ca-HepTh.txt.gz"
    "https://snap.stanford.edu/data/email-Enron.txt.gz"
)

for url in "${FILES[@]}"; do
    fname=$(basename "$url")
    if [[ -f "$fname" ]]; then
        echo "have $fname"
        continue
    fi
    echo "fetching $fname"
    curl -fsSL "$url" -o "$fname"
done

echo "done"
