import json
from pathlib import Path

runs_dir = Path(r'D:\DAALE\R-Fabric\runs')
latest_run = max(Path(r'D:\DAALE\R-Fabric\runs').glob('DD-001-*.json'), key=lambda p: p.stat().st_mtime)

with open(latest_run) as f:
    trace = json.load(f)

print('model_calls keys:', list(trace.get('model_calls', {}).keys()))

for k, v in trace.get('model_calls', {}).items():
    record = v.get('record', {})
    output = v.get('output', {})
    usage = record.get('usage', {})
    error = output.get('error', '')
    print(f'{k}: usage={usage}, error={error[:200] if error else "none"}')