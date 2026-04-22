#!/usr/bin/env python3
from pathlib import Path
import re
import sys

log_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('out/adc_sim.log')
text = log_path.read_text()

assert 'TB TIMEOUT' not in text, 'Simulation timed out'
assert 'TB FAIL' not in text, 'TB reported failure'
assert 'ERROR:' not in text, 'Found mismatch markers in log'

m = re.search(r'TB PASS: (\d+) frames verified', text)
assert m, 'PASS banner not found'
frames = int(m.group(1))
assert frames >= 24, f'Expected >=24 verified frames, got {frames}'

print(f'ADC validation PASS: {frames} frames verified from {log_path}')
