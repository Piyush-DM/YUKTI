import sys
sys.path.insert(0, r'D:\DAALE\R-Fabric')
import os
from dotenv import load_dotenv
load_dotenv(r'D:\DAALE\R-Fabric\.env')
from daale.client import OpenRouterClient
from daale.prompts import build_kernel_messages
from daale.schemas import KERNEL_OUTPUT_SCHEMA
from daale.validation import validate_kernel_output
import json

load_dotenv(r'D:\DAALE\R-Fabric\.env')

with open(r'D:\DAALE\R-Fabric\cases\vendor_alpha.json') as f:
    case = json.load(f)
with open(r'D:\DAALE\R-Fabric\policies\vendor_post_technical_dd_v0_1.json') as f:
    policy = json.load(f)

client = OpenRouterClient(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    native_json_schema=True,
    timeout_seconds=180
)

messages = build_kernel_messages(
    'ANALYST',
    case,
    policy,
    prior_outputs=None,
    native_schema=True,
)

print("=== PROMPT ===")
for m in messages:
    print(f"{m['role']}: {m['content'][:500]}...")

client = OpenRouterClient(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    native_json_schema=True,
    timeout_seconds=180
)

record = client.complete_json(
    purpose='analyst',
    model='google/gemini-2.5-flash',
    messages=messages,
    schema=KERNEL_OUTPUT_SCHEMA
)

print("=== MODEL OUTPUT ===")
print(json.dumps(record.output, indent=2))

print("\n=== VALIDATION ===")
try:
    validate_kernel_output(record.output, case, policy, 'ANALYST')
    print("VALIDATION PASSED")
except Exception as e:
    print(f"VALIDATION FAILED: {e}")