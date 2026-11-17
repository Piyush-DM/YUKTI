import json

with open(r'D:\DAALE\R-Fabric\runs\DD-001-20260917T160227325688Z-f546c75dd914.json') as f:
    trace = json.load(f)

print('model_calls keys:', list(trace.get('model_calls', {}).keys()))

for k, v in trace.get('model_calls', {}).items():
    record = v.get('record', {})
    output = v.get('output', {})
    usage = record.get('usage', {})
    error = output.get('error', '')
    print(f'{k}: usage={usage}, error={error[:200] if error else "none"}')