import sys
sys.path.insert(0, r'D:\DAALE\R-Fabric')
import os
from dotenv import load_dotenv
load_dotenv(r'D:\DAALE\R-Fabric\.env')
from daale.client import OpenRouterClient
import json

models_to_test = [
    'nvidia/nemotron-3-super-120b-a12b:free',
    'nvidia/nemotron-3-ultra-550b-a55b:free',
    'nvidia/nemotron-3.5-lightning:free',
]

for model in models_to_test:
    print(f"\n=== Testing {model} ===")
    client = OpenRouterClient(
        api_key=os.getenv('OPENROUTER_API_KEY'),
        native_json_schema=True,
        timeout_seconds=180
    )
    try:
        record = client.complete_json(
            purpose='test',
            model=model,
            messages=[{'role': 'user', 'content': 'Return JSON: {"test": "value"}'}],
            schema={'type': 'object', 'properties': {'test': {'type': 'string'}}, 'required': ['test'], 'additionalProperties': False}
        )
        print(f'  Success! Output: {record.output}')
        print(f'  Usage: {record.usage}')
        break
    except Exception as e:
        print(f'  Failed: {e}')
        continue