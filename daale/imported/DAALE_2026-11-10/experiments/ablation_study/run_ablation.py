#!/usr/bin/env python
"""
Ablation Study: Remove Kernels One by One to Measure Contribution

This measures each kernel's contribution to the final decision by
running the pipeline with one kernel removed at a time.
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


BASE_KERNELS = [
    "ANALYST",
    "CONTRARIAN",
    "FIRST_PRINCIPLES",
    "EXPANSIONIST",
    "OUTSIDER",
    "HISTORIAN",
]

ADVERSARY = "ADVERSARY"
ALL_KERNELS = BASE_KERNELS + [ADVERSARY]


@dataclass
class AblationResult:
    removed_kernel: str
    verdict: str
    triggered_rule: str
    metrics: Dict
    findings_count: int
    critical_failures: int
    contradictions: int
    deviation_from_baseline: Dict


class AblationStudy:
    """Runs ablation study by removing one kernel at a time"""
    
    def __init__(self):
        self.base_verdict = None
        self.base_metrics = None
        self.results: List[Dict] = []
    
    def load_case_and_policy(self, case_path: str, policy_path: str) -> tuple:
        with open(case_path) as f:
            case = json.load(f)
        with open(policy_path) as f:
            policy = json.load(f)
        return case, policy
    
    def _load_fixtures(self, excluded_kernel: str = None) -> Dict:
        fixtures = {}
        fixture_dir = Path(r'D:\DAALE\R-Fabric\fixtures')
        for fixture_file in fixture_dir.glob('*_output.json'):
            kernel_name = fixture_file.stem.replace('_output', '')
            if excluded_kernel and kernel_name.upper() == excluded_kernel.upper():
                continue
            with open(fixture_file) as f:
                fixtures[kernel_name.lower()] = json.load(f)
        return fixtures
    
    def run_pipeline(self, case: Dict, policy: Dict, fixtures: Dict) -> Dict:
        client = FixtureClient(fixtures)
        pipeline = DaalePipeline(
            client=FixtureClient(fixtures),
            model_by_kernel={"default": "offline-test"}
        )
        result = pipeline.run(case, policy)
        return {
            'verdict': result.decision_packet.get('policy_state'),
            'triggered_rule': result.decision_packet.get('triggered_rule', {}).get('rule_id'),
            'metrics': result.decision_packet.get('metrics', {}),
            'trace': result.trace
        }
    
    def run_ablation(self, case_path: str, policy_path: str) -> List[Dict]:
        """Run ablation study removing one kernel at a time"""
        
        with open(case_path) as f:
            case = json.load(f)
        with open(policy_path) as f:
            policy = json.load(f)
        
        # Baseline: all kernels
        print("Running baseline (all kernels)...")
        all_fixtures = self._load_fixtures()
        baseline = self.run_pipeline(case, policy, all_fixtures)
        self.base_verdict = baseline['verdict']
        self.base_metrics = baseline['metrics']
        
        print(f"Baseline verdict: {self.base_verdict}")
        print(f"Baseline metrics: {self.base_metrics}")
        
        # Ablate each kernel
        results = []
        for kernel in ALL_KERNELS:
            print(f"\nAblating {kernel}...")
            
            if kernel in BASE_KERNELS:
                fixtures = self._load_fixtures(excluded_kernel=kernel)
            else:
                # Adversary ablation - run without adversary
                fixtures = self._load_fixtures(excluded_kernel=ADVERSARY)
            
            try:
                result = self.run_pipeline(
                    case, policy, fixtures
                )
                
                # Calculate deviation
                deviation = {
                    'verdict_changed': result['verdict'] != self.base_verdict,
                    'critical_failures_delta': result['metrics'].get('failed_critical_requirements', 0) - self.base_metrics.get('failed_critical_requirements', 0),
                    'contradictions_delta': result['metrics'].get('contradicting_relations', 0) - self.base_metrics.get('contradicting_relations', 0),
                    'supporting_delta': result['metrics'].get('supporting_relations', 0) - self.base_metrics.get('supporting_relations', 0),
                }
                
                result_data = {
                    'removed_kernel': kernel,
                    'verdict': result['verdict'],
                    'triggered_rule': result['triggered_rule'],
                    'metrics': result['metrics'],
                    'deviation': deviation,
                    'verdict_changed': result['verdict'] != self.base_verdict
                }
                
                results.append(result_data)
                print(f"  Verdict: {result['verdict']} (baseline: {self.base_verdict}) {'CHANGED!' if result['verdict'] != self.base_verdict else ''}")
                
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append({
                    'removed_kernel': kernel,
                    'error': str(e)
                })
        
        return results
    
    def generate_report(self, results: List[Dict]) -> Dict:
        """Generate ablation study report"""
        
        kernel_impact = {}
        for r in results:
            if 'error' not in r:
                kernel = r['removed_kernel']
                kernel_impact[kernel] = {
                    'verdict_changed': r['verdict_changed'],
                    'critical_failures_delta': r['deviation']['critical_failures_delta'],
                    'contradictions_delta': r['deviation']['contradictions_delta'],
                    'supporting_delta': r['deviation']['supporting_delta']
                }
        
        # Rank kernels by impact
        impact_scores = {}
        for kernel, impact in kernel_impact.items():
            score = 0
            if impact['verdict_changed']:
                score += 100
            score += abs(impact['critical_failures_delta']) * 10
            score += abs(impact['contradictions_delta']) * 5
            score += abs(impact['supporting_delta'])
            impact_scores[kernel] = score
        
        ranked = sorted(impact_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'baseline_verdict': self.base_verdict,
            'baseline_metrics': self.base_metrics,
            'kernel_impacts': kernel_impact,
            'ranked_importance': ranked,
            'summary': {
                'kernels_that_change_verdict': sum(1 for r in self.results if r.get('verdict_changed', False)),
                'total_kernels_tested': len([r for r in self.results if 'error' not in r]),
                'most_critical_kernel': ranked[0][0] if ranked else None
            }
        }


def run_ablation_study():
    """Run complete ablation study"""
    
    case_path = r'D:\DAALE\R-Fabric\cases\vendor_alpha.json'
    policy_path = r'D:\DAALE\R-Fabric\policies\vendor_post_technical_dd_v0_1.json'
    
    print("=" * 80)
    print("ABLATION STUDY: Kernel Contribution Analysis")
    print("=" * 80)
    
    study = AblationStudy()
    results = study.run_ablation(
        r'D:\DAALE\R-Fabric\cases\vendor_alpha.json',
        r'D:\DAALE\R-Fabric\policies\vendor_post_technical_dd_v0_1.json'
    )
    
    report = study.generate_report(results)
    
    print("\n" + "=" * 80)
    print("ABLATION STUDY RESULTS")
    print("=" * 80)
    print(json.dumps(report, indent=2))
    
    # Save results
    with open(r'D:\DAALE\ablation_study_results.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nResults saved to D:\\DAALE\\ablation_study_results.json")
    
    return report


if __name__ == '__main__':
    run_ablation_study()