#!/usr/bin/env python3
import re
import sys
from pathlib import Path

log_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('out/sim.log')

lines = log_path.read_text().splitlines()
pat = re.compile(r"\[(\d+) ns\] rst_n=(\d) count=(\d+)")
records = []
for l in lines:
    m = pat.search(l)
    if m:
        t, r, c = map(int, m.groups())
        records.append((t, r, c))

assert records, f'No simulation records found in {log_path}'

# Every posedge is 10ns apart.
for (t0, _, _), (t1, _, _) in zip(records, records[1:]):
    assert t1 - t0 == 10000, f'Clock spacing mismatch: {t0}->{t1}'

# Before reset release (rst_n=0), count remains 0.
for t, r, c in records:
    if r == 0:
        assert c == 0, f'Count not reset at {t}ns'

# After rst_n goes high, count increments by 1 on each posedge.
post = [(t, c) for t, r, c in records if r == 1]
for (_, c0), (t1, c1) in zip(post, post[1:]):
    assert c1 == (c0 + 1) % 16, f'Count increment mismatch at {t1}ns: {c0}->{c1}'

# Ensure rollover is present in the captured window.
assert any(c0 == 15 and c1 == 0 for (_, c0), (_, c1) in zip(post, post[1:])), (
    'Rollover 15->0 not observed; simulation window may be too short.'
)

print(f'Timing validation passed using {log_path}: counter increments every 10ns and rollover is observed.')
