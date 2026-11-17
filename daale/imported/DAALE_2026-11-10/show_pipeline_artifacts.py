import json

# 1. COURT CASE CORPUS
print('=' * 80)
print('1. COURT CASE CORPUS')
print('=' * 80)
with open(r'D:\DAALE\R-Fabric\cases\vendor_alpha.json') as f:
    case = json.load(f)
print('Case ID: ' + case['case_id'])
print('Decision Stage: ' + case['decision_stage'])
print('Question: ' + case['decision_question'])
print('Claims: ' + str(len(case['claims'])))
for c in case['claims']:
    print('  ' + c['claim_id'] + ': ' + c['text'][:80] + '...')
print('Evidence: ' + str(len(case['evidence'])))
for e in case['evidence']:
    src = e['source']
    print('  ' + e['evidence_id'] + ': ' + e['text'][:60] + '...')
    print('    Source: ' + src['source_id'] + ' (' + src['source_type'] + ') | ' + src.get('document_id', 'N/A') + ' | p.' + str(src.get('page', 'N/A')) + ' | ' + src.get('extraction_method', 'N/A'))

print()
print('Policy:')
with open(r'D:\DAALE\R-Fabric\policies\vendor_post_technical_dd_v0_1.json') as f:
    policy = json.load(f)
print('  Policy ID: ' + policy['policy_id'])
print('  Requirements: ' + str(len(policy['requirements'])))
for r in policy['requirements']:
    print('    ' + r['requirement_id'] + ': ' + r['description'][:60] + '... (mandatory=' + str(r['mandatory']) + ', critical=' + str(r['critical']) + ')')

# 2. TEST RUN TRACE
print()
print('=' * 80)
print('2. TEST RUN TRACE (R-Fabric)')
print('=' * 80)
import glob, os
runs = glob.glob(r'D:\DAALE\R-Fabric\runs\*.json')
latest = max(runs, key=os.path.getmtime)
with open(latest) as f:
    trace = json.load(f)
print('Trace ID: ' + trace['run']['run_id'])
print('Steps:')
for step in trace['pipeline_steps']:
    print('  ' + step['step'] + ': ' + step['status'])

# 3. RESEARCH/REASONING FINDINGS (Kernel Outputs)
print()
print('=' * 80)
print('3. RESEARCH/REASONING FINDINGS (Per Kernel)')
print('=' * 80)
for kernel_id, data in trace['provisional_findings'].items():
    print()
    print('--- ' + kernel_id.upper() + ' ---')
    output = data.get('output', data)  # handle both structures
    findings = output.get('findings', [])
    print('Findings: ' + str(len(findings)))
    for f in findings[:5]:  # show first 5
        ft = f.get('finding_type', 'N/A')
        tt = f.get('target_type', 'N/A')
        tid = f.get('target_id', 'N/A')
        content = f.get('content', '')[:80]
        status = f.get('status', f.get('relation', 'N/A'))
        sev = f.get('severity', 'N/A')
        conf = f.get('confidence', 'N/A')
        print('  [' + ft + '] ' + tt + ':' + tid + ' | ' + content + '...')
        print('    status/relation=' + str(status) + ' | severity=' + str(sev) + ' | confidence=' + str(conf))
    if len(findings) > 5:
        print('  ... and ' + str(len(findings) - 5) + ' more findings')

# 4. DECISION PACKET (Policy Engine Output)
print()
print('=' * 80)
print('4. DECISION PACKET (Policy Engine Result)')
print('=' * 80)
dp = trace['decision_packet']
print('Policy State: ' + dp['policy_state'])
print('Triggered Rule: ' + dp['triggered_rule']['rule_id'] + ' (' + dp['triggered_rule']['description'] + ')')
print('Metrics:')
m = dp['metrics']
print('  Failed Critical: ' + str(m['failed_critical_requirements']) + ' -> ' + str(m['details']['failed_critical_requirement_ids']))
print('  Failed Mandatory: ' + str(m['failed_mandatory_requirements']) + ' -> ' + str(m['details']['failed_mandatory_requirement_ids']))
print('  Unknown Mandatory: ' + str(m['unknown_mandatory_requirements']) + ' -> ' + str(m['details']['unknown_mandatory_requirement_ids']))
print('  Supporting Relations: ' + str(m['supporting_relations']))
print('  Weakening Relations: ' + str(m['weakening_relations']))
print('  Contradicting Relations: ' + str(m['contradicting_relations']))
print('Claim Statuses: ' + str(dp['provisional_claim_statuses']))

# 5. RUNTIME ARTIFACTS
print()
print('=' * 80)
print('5. RUNTIME ARTIFACTS EXPOSED')
print('=' * 80)
print('R-Fabric Trace: ' + latest)
print('Trace contains:')
print('  - case, policy (input)')
print('  - model_calls: per-kernel prompt/response + usage')
print('  - provisional_findings: per-kernel structured findings')
print('  - hashes: SHA256 of all inputs/outputs')
print('  - decision_packet: deterministic policy result')
print()
# D-Core artifacts
admissions = glob.glob(r'D:\DAALE\D-Core\reports\daale\rfabric_admission\*.json')
latest_adm = max(admissions, key=os.path.getmtime) if admissions else None
if latest_adm:
    print('D-Core Admission: ' + latest_adm)
    with open(latest_adm) as f:
        adm = json.load(f)
    print('  Execution ID: ' + adm['execution_id'])
    print('  Object: ' + adm['object_id'])
    print('  Origin: ' + adm['origin'])
    print('  State: ' + adm['state'])
    print('  Gate Checks:')
    for gc in adm['gate_checks']:
        print('    ' + gc['name'] + ': ' + gc['status'] + ' - ' + gc['detail'])
    print('  Trace events: ' + str(len(adm['trace'])))
    for e in adm['trace']:
        print('    [' + str(e['sequence']) + '] ' + e['kind'] + ' - ' + e['subject'] + (' - ' + e['detail'] if e['detail'] else ''))
print()
print('Fixture Files (offline kernel outputs):')
fixtures = glob.glob(r'D:\DAALE\R-Fabric\fixtures\*.json')
for f in fixtures:
    print('  ' + os.path.basename(f))

print()
print('=' * 80)
print('COMPLETE PIPELINE: Corpus -> Test Run -> Findings -> Decision -> Artifacts')
print('=' * 80)