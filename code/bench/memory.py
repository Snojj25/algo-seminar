"""
memory.py — peak RSS and resident-memory probes for the §3.3 memory-cliff
experiment. Uses psutil; falls back to resource.getrusage on POSIX if psutil
is unavailable.
"""

from __future__ import annotations

import gc
import os


def current_rss_mb() -> float:
    try:
        import psutil

        return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    except ImportError:
        import resource

        rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS: ru_maxrss is in bytes; Linux: kilobytes.
        if os.uname().sysname == "Darwin":
            return rss_kb / 1024 / 1024
        return rss_kb / 1024


def measure_build_memory(build_fn) -> tuple[float, float, object]:
    """Run build_fn() and report (rss_before_mb, rss_peak_mb, result).

    Forces a GC before and after to make the deltas meaningful.
    """
    gc.collect()
    before = current_rss_mb()
    result = build_fn()
    gc.collect()
    peak = current_rss_mb()
    return before, peak, result
