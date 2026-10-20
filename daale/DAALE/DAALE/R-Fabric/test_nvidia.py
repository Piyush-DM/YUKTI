import sys
sys.path.insert(0, r'D:\DAALE')
from daale.client import NvidiaClient
import os
from dotenv import load_dotenv
load_dotenv()
client = NvidiaClient(api_key=os.getenv('NVIDIA_API_KEY'), max_attempts=1)
# Simple test
result = client.complete_json(
    purpose='test',
    model='nvidia/nemotron-3-ultra-550b-a55b',
    messages=[{'role': 'user', 'content': 'Return JSON: {"status": "test"}'}],
    schema={'type': 'object', 'properties': {'status': {'type': 'string'}}, 'required': ['status']}
)
print('Success:', result.output)