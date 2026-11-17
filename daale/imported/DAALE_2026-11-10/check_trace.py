import json
from pathlib import Path

runs_dir = Path(r'D:\DAALE\R-Fabric\runs')
latest_run = max(Path(r'D:\DAALE\R-Fabric\runs').glob('DD-001-*.json'), key=lambda p: p.stat().st_mtime)

with open(latest_run) as f:
    trace = json.load(f)

print('model_calls keys:', list(trace.get('model_calls', {}).keys()))

for k, v in trace.get('model_calls', {}).items():
    output = v.get('output', {})
    findings = output.get('findings', [])
    print(f'{k}: {len(findings)} findings')
    for f in findings[:3]:
        print(f'  {f.get("finding_type")} {f.get("target_id")}: {f.get("content", "")[:80]}')