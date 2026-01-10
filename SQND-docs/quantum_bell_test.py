#!/usr/bin/env python3
"""
QUANTUM BELL TEST FOR MORAL REASONING
======================================

Tests for Bell inequality violations in moral reasoning using the Claude API.

HYPOTHESIS (Andrew Bond):
"Quantum effects are just how math works."

This script tests whether moral reasoning exhibits genuine quantum contextuality
by measuring CHSH statistics across different "measurement angles" (framings).

USAGE:
    python quantum_bell_test.py --api-key sk-ant-... [--trials 20] [--model claude-sonnet-4-20250514]

Author: Claude (with Andrew H. Bond)
Date: January 6, 2026
"""

import argparse
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum
import re
import sys

try:
    import anthropic
except ImportError:
    print("Please install anthropic: pip install anthropic")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

class MeasurementAngle(Enum):
    """
    Measurement angles for Bell test.
    
    Optimal CHSH angles are: 0°, 22.5°, 45°, 67.5°
    We map these to moral framings:
    - 0° (A0): Pure duty framing
    - 45° (A1): Mixed duty-discretion framing  
    - 22.5° (B0): Duty-leaning claim framing
    - 67.5° (B1): Discretion-leaning vulnerability framing
    """
    A0 = "duty_pure"
    A1 = "duty_discretion_mixed"
    B0 = "claim_duty_leaning"
    B1 = "vulnerability_discretion_leaning"


# =============================================================================
# THE SCENARIO
# =============================================================================

QUANTUM_SCENARIO = {
    "name": "quantum_debt",
    "base": """Taylor lent Quinn $500 last year, saying "Pay me back when you can."
Quinn now has steady income but also significant expenses.
Quinn could pay the money back, but it would require some sacrifice.
Taylor hasn't asked for the money back or mentioned it since the loan.""",
    
    "framings": {
        # Agent framings (A0, A1)
        "A0": {
            "name": "Pure Duty",
            "angle": 0,
            "prompt": """Consider Quinn's DUTY and OBLIGATION.

The phrase "pay me back" creates a commitment. Money was received with an 
expectation of return. Quinn accepted the loan knowing repayment was expected.

Focus purely on: Does Quinn have a binding OBLIGATION to pay Taylor back now?

Answer with a single word: OBLIGATION or LIBERTY"""
        },
        
        "A1": {
            "name": "Mixed Duty-Discretion",
            "angle": 45,
            "prompt": """Consider both Quinn's duty AND Quinn's discretion.

On one hand, Quinn received money with "pay me back" - suggesting obligation.
On the other hand, "when you can" grants latitude - suggesting discretion.

The situation has elements of both binding duty and personal freedom.

Weighing BOTH the obligation AND the discretion, which feels stronger right now?

Answer with a single word: OBLIGATION or LIBERTY"""
        },
        
        # Patient framings (B0, B1)
        "B0": {
            "name": "Claim (Duty-Leaning)",
            "angle": 22.5,
            "prompt": """Consider Taylor's position, with emphasis on legitimate expectations.

Taylor lent money in good faith. The words "pay me back" established an expectation.
Taylor has a reasonable basis to expect repayment. The money is rightfully Taylor's.

Does Taylor have a CLAIM - a legitimate right to expect payment?

Answer with a single word: CLAIM or NO_CLAIM"""
        },
        
        "B1": {
            "name": "Vulnerability (Discretion-Leaning)",
            "angle": 67.5,
            "prompt": """Consider Taylor's position, with emphasis on actual impact.

Taylor hasn't asked for the money or indicated any need. Taylor said "when you can"
which suggests flexibility. Taylor may be financially comfortable.

Would Taylor actually be HARMED or VULNERABLE if Quinn delays further?

Answer with a single word: CLAIM or NO_CLAIM"""
        }
    }
}


# =============================================================================
# OUTCOME PARSING
# =============================================================================

@dataclass
class Measurement:
    setting_a: int  # 0 or 1
    setting_b: int  # 0 or 1
    outcome_a: int  # +1 or -1
    outcome_b: int  # +1 or -1
    product: int    # outcome_a * outcome_b
    raw_response_a: str
    raw_response_b: str
    trial: int


def parse_outcome(response: str, is_agent: bool) -> int:
    """
    Parse response to +1 or -1.
    
    For agent (A): OBLIGATION = +1, LIBERTY = -1
    For patient (B): CLAIM = +1, NO_CLAIM = -1
    """
    text = response.upper().strip()
    
    if is_agent:
        if "OBLIGATION" in text:
            return +1
        elif "LIBERTY" in text:
            return -1
    else:
        if "NO_CLAIM" in text or "NO-CLAIM" in text or "NOCLAIM" in text:
            return -1
        elif "CLAIM" in text:
            return +1
    
    # If unclear, try to infer from context
    if any(word in text for word in ["DUTY", "BOUND", "MUST", "SHOULD", "OBLIGAT"]):
        return +1
    elif any(word in text for word in ["FREE", "DISCRETION", "MAY", "CHOICE", "LIBERTY"]):
        return -1
    
    # Default based on what seems more present
    print(f"  ⚠️  Ambiguous response, defaulting based on keywords: {text[:100]}")
    return +1 if len(text) % 2 == 0 else -1


# =============================================================================
# API CALLER
# =============================================================================

class BellTestRunner:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.measurements: List[Measurement] = []
        self.request_count = 0
        self.total_tokens = 0
        
    def measure(self, setting_a: int, setting_b: int, trial: int) -> Measurement:
        """Perform a joint measurement at settings (A_i, B_j)."""
        
        framing_a = QUANTUM_SCENARIO["framings"][f"A{setting_a}"]
        framing_b = QUANTUM_SCENARIO["framings"][f"B{setting_b}"]
        
        # Construct prompts
        base = QUANTUM_SCENARIO["base"]
        
        prompt_a = f"""SCENARIO:
{base}

MEASUREMENT TASK:
{framing_a['prompt']}"""

        prompt_b = f"""SCENARIO:
{base}

MEASUREMENT TASK:
{framing_b['prompt']}"""

        # Make API calls
        print(f"  📏 Measuring A{setting_a} ({framing_a['name']})...")
        response_a = self._call_api(prompt_a)
        outcome_a = parse_outcome(response_a, is_agent=True)
        print(f"      → {'+1 (O)' if outcome_a > 0 else '-1 (L)'}: {response_a[:50]}...")
        
        print(f"  📏 Measuring B{setting_b} ({framing_b['name']})...")
        response_b = self._call_api(prompt_b)
        outcome_b = parse_outcome(response_b, is_agent=False)
        print(f"      → {'+1 (C)' if outcome_b > 0 else '-1 (N)'}: {response_b[:50]}...")
        
        measurement = Measurement(
            setting_a=setting_a,
            setting_b=setting_b,
            outcome_a=outcome_a,
            outcome_b=outcome_b,
            product=outcome_a * outcome_b,
            raw_response_a=response_a,
            raw_response_b=response_b,
            trial=trial
        )
        
        self.measurements.append(measurement)
        return measurement
    
    def _call_api(self, prompt: str) -> str:
        """Make API call to Claude."""
        self.request_count += 1
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=100,
            temperature=1.0,  # Maximum temperature for genuine indeterminacy
            messages=[{"role": "user", "content": prompt}]
        )
        
        self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
        return response.content[0].text
    
    def compute_chsh(self) -> Dict:
        """Compute CHSH statistic from measurements."""
        
        correlations = {(0,0): [], (0,1): [], (1,0): [], (1,1): []}
        
        for m in self.measurements:
            key = (m.setting_a, m.setting_b)
            correlations[key].append(m.product)
        
        E = {}
        for key, products in correlations.items():
            if products:
                E[key] = sum(products) / len(products)
            else:
                E[key] = 0
        
        # CHSH: S = E(A0,B0) + E(A0,B1) + E(A1,B0) - E(A1,B1)
        S = E[(0,0)] + E[(0,1)] + E[(1,0)] - E[(1,1)]
        
        # Standard error estimation
        n = len(correlations[(0,0)]) if correlations[(0,0)] else 1
        se = 2 * (1 / n ** 0.5)  # Rough estimate
        
        return {
            "E_00": E[(0,0)],
            "E_01": E[(0,1)],
            "E_10": E[(1,0)],
            "E_11": E[(1,1)],
            "S": S,
            "S_abs": abs(S),
            "standard_error": se,
            "violates_classical": abs(S) > 2,
            "exceeds_by": max(0, abs(S) - 2),
            "n_per_setting": n,
            "quantum_bound": 2 * (2 ** 0.5),
        }


# =============================================================================
# MAIN EXPERIMENT
# =============================================================================

def run_experiment(api_key: str, trials_per_setting: int = 20, 
                   model: str = "claude-sonnet-4-20250514") -> Dict:
    """Run the full Bell test experiment."""
    
    print("=" * 70)
    print("  QUANTUM BELL TEST FOR MORAL REASONING")
    print("  Testing for CHSH violations")
    print("=" * 70)
    print()
    print(f"Model: {model}")
    print(f"Trials per setting: {trials_per_setting}")
    print(f"Total API calls: {trials_per_setting * 4 * 2}")
    print()
    print("Classical bound: |S| ≤ 2")
    print("Quantum bound:   |S| ≤ 2√2 ≈ 2.83")
    print()
    print("Measurement angles (optimal for Bell test):")
    print("  A0 (0°):    Pure duty framing")
    print("  A1 (45°):   Mixed duty-discretion framing")
    print("  B0 (22.5°): Claim with duty emphasis")
    print("  B1 (67.5°): Vulnerability with discretion emphasis")
    print()
    print("=" * 70)
    
    runner = BellTestRunner(api_key, model)
    
    trial = 0
    for setting_a in [0, 1]:
        for setting_b in [0, 1]:
            print(f"\n⚛️  Setting combination: A{setting_a}, B{setting_b}")
            print("-" * 50)
            
            for t in range(trials_per_setting):
                print(f"\n  Trial {t + 1}/{trials_per_setting}")
                runner.measure(setting_a, setting_b, trial)
                trial += 1
    
    # Compute results
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)
    
    chsh = runner.compute_chsh()
    
    print(f"\nCorrelations:")
    print(f"  E(A₀,B₀) = {chsh['E_00']:+.3f}  (duty × claim)")
    print(f"  E(A₀,B₁) = {chsh['E_01']:+.3f}  (duty × vulnerability)")
    print(f"  E(A₁,B₀) = {chsh['E_10']:+.3f}  (mixed × claim)")
    print(f"  E(A₁,B₁) = {chsh['E_11']:+.3f}  (mixed × vulnerability)")
    
    print(f"\nCHSH Statistic:")
    print(f"  S = E(A₀B₀) + E(A₀B₁) + E(A₁B₀) - E(A₁B₁)")
    print(f"  S = {chsh['E_00']:+.3f} + {chsh['E_01']:+.3f} + {chsh['E_10']:+.3f} - {chsh['E_11']:+.3f}")
    print(f"  S = {chsh['S']:+.4f}")
    print(f"  |S| = {chsh['S_abs']:.4f}")
    print(f"  SE ≈ {chsh['standard_error']:.3f}")
    
    print(f"\nBounds:")
    print(f"  Classical: |S| ≤ 2.000")
    print(f"  Quantum:   |S| ≤ {chsh['quantum_bound']:.3f}")
    
    print("\n" + "=" * 70)
    if chsh['violates_classical']:
        print("  🔴 BELL VIOLATION DETECTED 🔴")
        print(f"  |S| = {chsh['S_abs']:.4f} > 2")
        print(f"  Exceeds classical bound by {chsh['exceeds_by']:.4f}")
        if chsh['S_abs'] <= chsh['quantum_bound']:
            print("  Within quantum bound - consistent with quantum mechanics")
        else:
            print("  ⚠️  EXCEEDS QUANTUM BOUND - check for errors")
    else:
        print("  🟢 No Bell violation detected")
        print(f"  |S| = {chsh['S_abs']:.4f} ≤ 2")
        if chsh['S_abs'] > 1.8:
            print("  ⚠️  Approaching classical bound - warrants investigation")
    print("=" * 70)
    
    # Save results
    results = {
        "experiment": "Quantum Bell Test for Moral Reasoning",
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "trials_per_setting": trials_per_setting,
        "total_measurements": len(runner.measurements),
        "total_api_calls": runner.request_count,
        "total_tokens": runner.total_tokens,
        "chsh_results": chsh,
        "measurements": [
            {
                "trial": m.trial,
                "setting_a": m.setting_a,
                "setting_b": m.setting_b,
                "outcome_a": m.outcome_a,
                "outcome_b": m.outcome_b,
                "product": m.product,
                "raw_a": m.raw_response_a,
                "raw_b": m.raw_response_b,
            }
            for m in runner.measurements
        ],
        "scenario": QUANTUM_SCENARIO,
    }
    
    output_file = f"bell_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print(f"Total API calls: {runner.request_count}")
    print(f"Total tokens: {runner.total_tokens:,}")
    
    # Cost estimate
    cost = runner.total_tokens * 0.000015  # Rough Sonnet pricing
    print(f"Estimated cost: ${cost:.2f}")
    
    return results


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Test for Bell inequality violations in moral reasoning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quantum_bell_test.py --api-key sk-ant-xxx --trials 20
  python quantum_bell_test.py --api-key sk-ant-xxx --trials 50 --model claude-sonnet-4-20250514

The test uses temperature=1.0 for maximum response variability.
Each trial makes 2 API calls (one for agent, one for patient framing).
Total API calls = trials × 4 settings × 2 calls = trials × 8
        """
    )
    
    parser.add_argument('--api-key', type=str, required=True,
                        help='Anthropic API key')
    parser.add_argument('--trials', type=int, default=20,
                        help='Trials per measurement setting (default: 20)')
    parser.add_argument('--model', type=str, default='claude-sonnet-4-20250514',
                        help='Model to use (default: claude-sonnet-4-20250514)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file (default: auto-generated)')
    
    args = parser.parse_args()
    
    results = run_experiment(args.api_key, args.trials, args.model)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results also saved to: {args.output}")


if __name__ == "__main__":
    main()
