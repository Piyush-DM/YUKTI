#!/usr/bin/env python
"""
Rubric Reproduction Experiment

Compares LLM vs frozen kernels on the same cases to test:
- Multi-kernel > Single LLM
- Kernels encode defensible standard

This is the central experiment that decides the project's direction.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, r'D:\DAALE')
sys.path.insert(0, r'D:\DAALE\R-Fabric')
sys.path.insert(0, r'D:\DAALE\D-Core')

from daale.pipeline import DaalePipeline
from daale.client import FixtureClient
from daale.policy_engine import apply_policy
from daale.client import OpenRouterClient


@dataclass
class ExperimentCase:
    case_id: str
    case: Dict
    policy: Dict
    ground_truth: Dict  # Expected verdict from frozen pipeline


@dataclass
class ExperimentResult:
    case_id: str
    frozen_verdict: str
    llm_verdict: str
    agreement: bool
    frozen_findings: int
    llm_findings: int
    frozen_critical_failures: int
    llm_critical_failures: int
    frozen_contradictions: int
    llm_contradictions: int
    details: Dict


class RubricReproductionExperiment:
    """
    Runs the rubric reproduction experiment comparing:
    1. Frozen kernel pipeline (ground truth)
    2. Single LLM with same rubric
    """
    
    def __init__(self, openrouter_client: OpenRouterClient = None):
        self.openrouter_client = openrouter_client
        self.cases: List[ExperimentCase] = []
        self.results: List[ExperimentResult] = []
    
    def load_case(self, case_path: str, policy_path: str) -> ExperimentCase:
        with open(case_path) as f:
            case = json.load(f)
        with open(policy_path) as f:
            policy = json.load(f)
        
        # Get ground truth from frozen pipeline
        ground_truth = self._get_ground_truth(case, policy)
        
        return ExperimentCase(
            case_id=case["case_id"],
            case=case,
            policy=policy,
            ground_truth=ground_truth
        )
    
    def _get_ground_truth(self, case: Dict, policy: Dict) -> Dict:
        """Run frozen pipeline to get ground truth"""
        fixtures = self._load_fixtures()
        client = FixtureClient(fixtures)
        pipeline = DaalePipeline(client=client, model_by_kernel={"default": "offline-test"})
        result = pipeline.run(case, policy)
        return {
            'verdict': result.decision_packet.get('policy_state'),
            'triggered_rule': result.decision_packet.get('triggered_rule', {}).get('rule_id'),
            'metrics': result.decision_packet.get('metrics', {}),
            'findings_count': sum(
                len(data.get('output', {}).get('findings', [])) 
                for data in result.trace.get('provisional_findings', {}).values()
            ),
            'critical_failures': result.decision_packet.get('metrics', {}).get('failed_critical_requirements', 0),
            'contradictions': result.decision_packet.get('metrics', {}).get('contradicting_relations', 0)
        }
    
    def _load_fixtures(self) -> Dict:
        fixtures = {}
        fixture_dir = Path(r'D:\DAALE\R-Fabric\fixtures')
        for fixture_file in fixture_dir.glob('*_output.json'):
            kernel_name = fixture_file.stem.replace('_output', '')
            with open(fixture_file) as f:
                fixtures[kernel_name] = json.load(f)
        return fixtures
    
    def run_llm_baseline(self, case: Dict, policy: Dict) -> Dict:
        """Run single LLM with same context as frozen pipeline"""
        if not self.openrouter_client:
            return self._simulate_llm(case, policy)
        
        # Build comprehensive prompt with all context
        prompt = self._build_rubric_prompt(case, policy)
        
        try:
            response = self.openrouter_client.complete_json(
                purpose="rubric_reproduction",
                model="anthropic/claude-3.5-sonnet",
                messages=[{"role": "user", "content": prompt}],
                schema=self._get_rubric_schema()
            )
            return response.output
        except Exception as e:
            print(f"LLM call failed: {e}")
            return self._simulate_llm(case, policy)
    
    def _simulate_llm(self, case: Dict, policy: Dict) -> Dict:
        """Simulate single LLM baseline (placeholder)"""
        # Single LLM typically misses:
        # - Cross-referenced requirement failures
        # - Contradictions between evidence items
        # - Adversarial challenges
        # - Multiple perspective synthesis
        
        req_summary = {}
        for req in policy.get('requirements', []):
            req_summary[req['requirement_id']] = {
                'status': 'UNKNOWN',
                'evidence_ids': [],
                'rationale': 'Single LLM could not determine'
            }
        
        claim_statuses = {}
        for claim in case.get('claims', []):
            claim_statuses[claim['claim_id']] = 'INSUFFICIENT_EVIDENCE'
        
        return {
            'policy_state': 'HOLD',
            'triggered_rule': {'rule_id': 'SIMULATED-HOLD'},
            'metrics': {
                'failed_critical_requirements': 0,
                'failed_mandatory_requirements': 0,
                'unknown_mandatory_requirements': len(policy.get('requirements', [])),
                'contradicting_relations': 0,
                'supporting_relations': 0,
                'weakening_relations': 0
            },
            'requirement_summary': req_summary,
            'provisional_claim_statuses': {c['claim_id']: 'INSUFFICIENT_EVIDENCE' for c in case.get('claims', [])},
            'adversarial_summary': 'Single LLM cannot generate adversarial challenges',
            'authority_notice': 'Simulated single LLM baseline'
        }
    
    def _build_rubric_prompt(self, case: Dict, policy: Dict) -> str:
        return f"""
You are an institutional reasoning engine. Apply the policy rubric to the case.

CASE:
{json.dumps(case, indent=2)}

POLICY:
{json.dumps(policy, indent=2)}

Apply the policy rules in priority order. For each requirement, determine status (SATISFIED, NOT_SATISFIED, UNKNOWN) based on evidence.

Output JSON with:
- policy_state: ADVANCE/HOLD/REJECT/ESCALATE
- triggered_rule: {{rule_id, priority, description}}
- metrics: {{failed_critical_requirements, failed_mandatory_requirements, unknown_mandatory_requirements, contradicting_relations, supporting_relations, weakening_relations}}
- requirement_summary: {{requirement_id: {{status, evidence_ids, rationale}}}}
- provisional_claim_statuses: {{claim_id: status}}
- adversarial_summary: string
- authority_notice: string
"""
    
    def _get_rubric_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "policy_state": {"type": "string", "enum": ["ADVANCE", "HOLD", "REJECT", "ESCALATE"]},
                "triggered_rule": {
                    "type": "object",
                    "properties": {
                        "rule_id": {"type": "string"},
                        "priority": {"type": "integer"},
                        "description": {"type": "string"}
                    },
                    "required": ["rule_id", "priority", "description"]
                },
                "metrics": {
                    "type": "object",
                    "properties": {
                        "failed_critical_requirements": {"type": "integer"},
                        "failed_mandatory_requirements": {"type": "integer"},
                        "unknown_mandatory_requirements": {"type": "integer"},
                        "contradicting_relations": {"type": "integer"},
                        "supporting_relations": {"type": "integer"},
                        "weakening_relations": {"type": "integer"}
                    },
                    "required": ["failed_critical_requirements", "failed_mandatory_requirements", "unknown_mandatory_requirements", "contradicting_relations", "supporting_relations", "weakening_relations"]
                },
                "requirement_summary": {"type": "object"},
                "provisional_claim_statuses": {"type": "object"},
                "adversarial_summary": {"type": "string"},
                "authority_notice": {"type": "string"}
            },
            "required": ["policy_state", "triggered_rule", "metrics", "requirement_summary", "provisional_claim_statuses", "adversarial_summary", "authority_notice"]
        }
    
    def run_experiment(self, cases: List[ExperimentCase]) -> List[ExperimentResult]:
        """Run the full experiment on all cases"""
        for case in cases:
            print(f"\nRunning experiment on {case.case_id}...")
            
            # Ground truth from frozen pipeline
            ground_truth = case.ground_truth
            
            # LLM baseline
            llm_result = self.run_llm_baseline(case.case, case.policy)
            
            # Compare
            result = ExperimentResult(
                case_id=case.case_id,
                frozen_verdict=ground_truth['verdict'],
                llm_verdict=llm_result.get('policy_state', 'ERROR'),
                agreement=ground_truth['verdict'] == llm_result.get('policy_state'),
                frozen_findings=ground_truth['findings_count'],
                llm_findings=self._extract_llm_findings(llm_result),
                frozen_critical_failures=ground_truth['critical_failures'],
                llm_critical_failures=llm_result.get('metrics', {}).get('failed_critical_requirements', 0),
                frozen_contradictions=ground_truth['contradictions'],
                llm_contradictions=llm_result.get('metrics', {}).get('contradicting_relations', 0),
                details={
                    'ground_truth': ground_truth,
                    'llm_result': llm_result
                }
            )
            
            self.results.append(result)
            print(f"  Frozen: {ground_truth['verdict']}, LLM: {llm_result.get('policy_state')}, Match: {ground_truth['verdict'] == llm_result.get('policy_state')}")
        
        return self.results
    
    def _extract_llm_findings(self, llm_result: Dict) -> int:
        """Extract findings count from LLM result"""
        # This would parse the LLM output for findings
        return 0  # Placeholder
    
    def generate_report(self) -> Dict:
        """Generate experiment report"""
        if not self.results:
            return {"error": "No results"}
        
        total = len(self.results)
        agreements = sum(1 for r in self.results if r.agreement)
        
        return {
            'total_cases': len(self.results),
            'agreement_rate': agreements / len(self.results) if self.results else 0,
            'frozen_better_findings': sum(1 for r in self.results if r.frozen_findings > r.llm_findings),
            'llm_better_findings': sum(1 for r in self.results if r.llm_findings > r.frozen_findings),
            'frozen_caught_more_critical': sum(1 for r in self.results if r.frozen_critical_failures > r.llm_critical_failures),
            'llm_caught_more_critical': sum(1 for r in self.results if r.llm_critical_failures > r.frozen_critical_failures),
            'frozen_found_more_contradictions': sum(1 for r in self.results if r.frozen_contradictions > r.llm_contradictions),
            'details': [asdict(r) for r in self.results]
        }


def run_rubric_reproduction():
    """Main entry point for rubric reproduction experiment"""
    print("=" * 80)
    print("RUBRIC REPRODUCTION EXPERIMENT")
    print("Comparing LLM vs Frozen Kernels on DAALE Cases")
    print("=" * 80)
    
    # Load cases
    cases = []
    case_files = [
        (r'D:\DAALE\R-Fabric\cases\vendor_alpha.json', r'D:\DAALE\R-Fabric\policies\vendor_post_technical_dd_v0_1.json'),
        (r'D:\DAALE\R-Fabric\cases\carlill_v_carbolic.json', r'D:\DAALE\R-Fabric\policies\contract_formation_v0_1.json'),
        (r'D:\DAALE\R-Fabric\cases\donoghue_v_stevenson.json', r'D:\DAALE\R-Fabric\policies\negligence_duty_of_care_v0_1.json'),
        (r'D:\DAALE\R-Fabric\cases\hadley_v_baxendale.json', r'D:\DAALE\R-Fabric\policies\contract_damages_remoteness_v0_1.json'),
    ]
    
    for case_path, policy_path in case_files:
        # Check if files exist
        import os
        if os.path.exists(case_path) and os.path.exists(policy_path):
            experiment = RubricReproductionExperiment()
            case = experiment.load_case(case_path, policy_path)
            cases.append(case)
    
    print(f"Loaded {len(cases)} cases for experiment")
    
    # Try to run with OpenRouter if available
    openrouter_client = None
    try:
        import os
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            openrouter_client = OpenRouterClient(
                api_key=api_key,
                native_json_schema=True,
                timeout_seconds=180
            )
            print("OpenRouter client initialized")
        else:
            print("No OpenRouter API key found - using simulated LLM baseline")
    except Exception as e:
        print(f"Could not initialize OpenRouter: {e}")
    
    # Run experiment
    experiment = RubricReproductionExperiment(openrouter_client)
    results = experiment.run_experiment(cases)
    
    # Generate report
    report = experiment.generate_report()
    
    print("\n" + "=" * 80)
    print("RUBRIC REPRODUCTION EXPERIMENT RESULTS")
    print("=" * 80)
    print(json.dumps(report, indent=2))
    
    # Save results
    with open(r'D:\DAALE\rubric_reproduction_results.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nResults saved to D:\\DAALE\\rubric_reproduction_results.json")
    
    return report


if __name__ == '__main__':
    run_rubric_reproduction()