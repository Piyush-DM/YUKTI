import requests

r = requests.get('https://openrouter.ai/api/v1/models', headers={'Authorization': 'Bearer sk-or-v1-<REDACTED>'}, timeout=30)
data = r.json()
for m in data['data']:
    if 'free' in m['id']:
        pricing = m.get('pricing', {})
        prompt_cost = pricing.get('prompt', '?')
        completion = pricing.get('completion', '?')
        tier = m.get('access_tier', '?')
        print(f'{m["id"]:50s} tier={m.get("access_tier", "?")} in={m.get("pricing", {}).get("prompt", "?")} out={m.get("pricing", {}).get("completion", "?")}')