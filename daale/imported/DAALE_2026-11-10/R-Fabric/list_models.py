import requests
r = requests.get('https://openrouter.ai/api/v1/models', timeout=10)
data = r.json()
free = [m for m in data['data'] if ':free' in m['id']]
for m in free[:25]:
    print(f"{m['id']:50s}  {m.get('name','')[:50]}  ctx={m.get('context_length',0)}")