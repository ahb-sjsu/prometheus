#!/usr/bin/env python3
"""
HYSTERESIS EXPERIMENT v2: Proper Methodology
=============================================

PROBLEM WITH v1:
The original experiment used two different ladders (O→L and L→O) that weren't
calibrated against each other. The "hysteresis gap" was an artifact of how
the scenarios were worded, not a real discovery about moral cognition.

SOLUTION:
Use a SINGLE set of scenarios representing a commitment spectrum, then test
whether the classification depends on the DIRECTION OF APPROACH.

TRUE HYSTERESIS means: given the SAME scenario, the classification differs
depending on whether we're "coming from" a stronger or weaker commitment state.

METHODOLOGY:
1. Create a single 7-level commitment spectrum (levels 0-6)
2. For each level, present it in two conditions:
   - ASCENDING: "Previously, the commitment was weaker. Now: [scenario]"
   - DESCENDING: "Previously, the commitment was stronger. Now: [scenario]"
3. If there's hysteresis, the same scenario will be classified as O more often
   in the ascending condition (momentum toward O) and as L more often in the
   descending condition (momentum toward L)

ALTERNATIVE APPROACH (also implemented):
Use the same scenarios but vary only the PRIMING — tell the model what the
prior state was, then ask about the current state.

Author: Claude (with Andrew H. Bond)
Date: January 2026
"""

import json
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
from collections import defaultdict
import numpy as np
from scipy import stats

class BondType(Enum):
    OBLIGATION = "O"
    LIBERTY = "L"
    
    @classmethod
    def from_string(cls, s: str) -> 'BondType':
        s = s.strip().upper()
        if 'O' in s: return cls.OBLIGATION
        if 'L' in s: return cls.LIBERTY
        raise ValueError(f"Unknown bond type: {s}")


@dataclass
class EvaluationResult:
    scenario_id: str
    bond_type: BondType
    confidence: float
    reasoning: str
    raw_response: str


# =============================================================================
# SINGLE CALIBRATED SPECTRUM
# =============================================================================

# Key design principle: ONE spectrum, described in NEUTRAL terms that don't
# presuppose direction. Each level should be interpretable independent of
# whether we're "going up" or "going down."

COMMITMENT_SPECTRUM = [
    {
        "level": 0,
        "description": "No connection",
        "scenario": "Alex and Jordan are strangers. Jordan is moving next week.",
        "expected_lean": "L",  # Clear liberty
    },
    {
        "level": 1,
        "description": "Vague social nicety",
        "scenario": "Alex said to Jordan 'Let me know if you need help with anything.' Jordan is moving next week.",
        "expected_lean": "L",  # Still liberty - just politeness
    },
    {
        "level": 2,
        "description": "Soft expression of intent",
        "scenario": "Alex told Jordan 'I could probably help you move next week.' Jordan is moving next week.",
        "expected_lean": "L?",  # Ambiguous, leaning L
    },
    {
        "level": 3,
        "description": "Statement of plan",
        "scenario": "Alex told Jordan 'I'm planning to help you move next week.' Jordan is moving next week.",
        "expected_lean": "?",  # True ambiguous middle
    },
    {
        "level": 4,
        "description": "Agreement",
        "scenario": "Alex agreed to help Jordan move next week when Jordan asked. Jordan is moving next week.",
        "expected_lean": "O?",  # Ambiguous, leaning O
    },
    {
        "level": 5,
        "description": "Explicit promise",
        "scenario": "Alex promised Jordan 'I will help you move next week.' Jordan is moving next week.",
        "expected_lean": "O",  # Clear obligation
    },
    {
        "level": 6,
        "description": "Solemn commitment with reliance",
        "scenario": "Alex gave Jordan their word and shook hands: 'I promise I'll be there to help you move.' Jordan turned down other offers of help. Jordan is moving next week.",
        "expected_lean": "O",  # Strong obligation
    },
]


# =============================================================================
# EXPERIMENT DESIGN 1: PRIMING APPROACH
# =============================================================================

class PrimingHysteresisExperiment:
    """
    Test hysteresis by presenting the SAME scenarios with different priming
    about the prior state.
    
    If hysteresis exists:
    - "Coming from O" + ambiguous scenario → more likely to stay O
    - "Coming from L" + ambiguous scenario → more likely to stay L
    """
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def create_prompt(self, scenario: str, prior_state: str) -> str:
        if prior_state == "O":
            prime = """CONTEXT: In an earlier interaction, Alex had made a clear commitment to help Jordan. 
That established obligation is the starting point. Since then, the situation has evolved.

CURRENT SITUATION:
"""
        elif prior_state == "L":
            prime = """CONTEXT: Previously, Alex had no particular obligation to help Jordan.
Alex was entirely free regarding whether to help. Since then, the situation has evolved.

CURRENT SITUATION:
"""
        else:
            prime = "SITUATION:\n"
        
        return f"""{prime}{scenario}

Based on the CURRENT situation, does Alex have a moral OBLIGATION to help Jordan move, 
or is Alex at LIBERTY (free to choose)?

Respond EXACTLY in this format:
CLASSIFICATION: O or L
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
    
    def run(self, n_trials: int = 20) -> Dict:
        """Run the priming hysteresis experiment."""
        print("\n" + "=" * 70)
        print("HYSTERESIS EXPERIMENT: PRIMING APPROACH")
        print("=" * 70)
        print("\nSame scenarios, different priming about prior state.")
        print("If hysteresis exists, prior state should bias classification.\n")
        
        results_by_level = defaultdict(lambda: {"from_O": [], "from_L": [], "neutral": []})
        
        # Test each level with both primings
        for level_info in COMMITMENT_SPECTRUM:
            level = level_info["level"]
            scenario = level_info["scenario"]
            
            print(f"Level {level}: {level_info['description']}")
            
            # Condition 1: Primed with "coming from O"
            for trial in range(n_trials):
                result = self.evaluator.evaluate(
                    {"id": f"prime_fromO_L{level}_{trial}"},
                    self.create_prompt(scenario, "O")
                )
                results_by_level[level]["from_O"].append(result)
            
            o_count_from_O = sum(1 for r in results_by_level[level]["from_O"] 
                                  if r.bond_type == BondType.OBLIGATION)
            
            # Condition 2: Primed with "coming from L"
            for trial in range(n_trials):
                result = self.evaluator.evaluate(
                    {"id": f"prime_fromL_L{level}_{trial}"},
                    self.create_prompt(scenario, "L")
                )
                results_by_level[level]["from_L"].append(result)
            
            o_count_from_L = sum(1 for r in results_by_level[level]["from_L"] 
                                  if r.bond_type == BondType.OBLIGATION)
            
            # Condition 3: Neutral (no priming) - for baseline
            for trial in range(n_trials):
                result = self.evaluator.evaluate(
                    {"id": f"prime_neutral_L{level}_{trial}"},
                    self.create_prompt(scenario, "neutral")
                )
                results_by_level[level]["neutral"].append(result)
            
            o_count_neutral = sum(1 for r in results_by_level[level]["neutral"] 
                                   if r.bond_type == BondType.OBLIGATION)
            
            print(f"  From O: P(O) = {o_count_from_O/n_trials:.0%}")
            print(f"  From L: P(O) = {o_count_from_L/n_trials:.0%}")
            print(f"  Neutral: P(O) = {o_count_neutral/n_trials:.0%}")
            
            # Test for significant difference
            if n_trials >= 10:
                contingency = [
                    [o_count_from_O, n_trials - o_count_from_O],
                    [o_count_from_L, n_trials - o_count_from_L]
                ]
                if min(contingency[0]) > 0 or min(contingency[1]) > 0:
                    chi2, p_value = stats.chi2_contingency(contingency)[:2]
                    if p_value < 0.05:
                        print(f"  *** Significant difference! χ² = {chi2:.2f}, p = {p_value:.4f}")
            print()
        
        # Analyze results
        analysis = self._analyze(results_by_level, n_trials)
        return analysis
    
    def _analyze(self, results_by_level: Dict, n_trials: int) -> Dict:
        """Analyze for hysteresis effect."""
        
        level_data = []
        total_hysteresis_effect = 0
        significant_levels = 0
        
        for level in sorted(results_by_level.keys()):
            data = results_by_level[level]
            
            p_O_from_O = sum(1 for r in data["from_O"] if r.bond_type == BondType.OBLIGATION) / n_trials
            p_O_from_L = sum(1 for r in data["from_L"] if r.bond_type == BondType.OBLIGATION) / n_trials
            p_O_neutral = sum(1 for r in data["neutral"] if r.bond_type == BondType.OBLIGATION) / n_trials
            
            # Hysteresis effect: P(O|from_O) - P(O|from_L)
            # Positive means "stickiness" - prior state biases toward itself
            hysteresis_effect = p_O_from_O - p_O_from_L
            
            # Statistical test
            o_from_O = sum(1 for r in data["from_O"] if r.bond_type == BondType.OBLIGATION)
            o_from_L = sum(1 for r in data["from_L"] if r.bond_type == BondType.OBLIGATION)
            
            try:
                contingency = [[o_from_O, n_trials - o_from_O], 
                              [o_from_L, n_trials - o_from_L]]
                chi2, p_value = stats.chi2_contingency(contingency)[:2]
            except:
                chi2, p_value = 0, 1.0
            
            level_data.append({
                "level": level,
                "description": COMMITMENT_SPECTRUM[level]["description"],
                "P_O_from_O": p_O_from_O,
                "P_O_from_L": p_O_from_L,
                "P_O_neutral": p_O_neutral,
                "hysteresis_effect": hysteresis_effect,
                "chi2": chi2,
                "p_value": p_value,
                "significant": p_value < 0.05
            })
            
            total_hysteresis_effect += hysteresis_effect
            if p_value < 0.05:
                significant_levels += 1
        
        # Overall assessment
        mean_hysteresis = total_hysteresis_effect / len(results_by_level)
        
        # Focus on ambiguous middle levels (2, 3, 4) where hysteresis should be visible
        middle_levels = [d for d in level_data if d["level"] in [2, 3, 4]]
        middle_hysteresis = np.mean([d["hysteresis_effect"] for d in middle_levels]) if middle_levels else 0
        
        print("\n" + "=" * 70)
        print("HYSTERESIS ANALYSIS")
        print("=" * 70)
        print(f"\nMean hysteresis effect (all levels): {mean_hysteresis:.3f}")
        print(f"Mean hysteresis effect (ambiguous levels 2-4): {middle_hysteresis:.3f}")
        print(f"Levels with significant priming effect: {significant_levels}/{len(results_by_level)}")
        
        if middle_hysteresis > 0.1:
            print("\n✓ HYSTERESIS DETECTED: Prior state biases classification")
            print(f"  On average, P(O|from_O) is {middle_hysteresis:.0%} higher than P(O|from_L)")
            print("  at ambiguous commitment levels.")
        elif middle_hysteresis < -0.1:
            print("\n⚠ REVERSE EFFECT: Prior state biases AWAY from itself")
            print("  This is unexpected and warrants investigation.")
        else:
            print("\n✗ NO HYSTERESIS DETECTED: Prior state does not bias classification")
        
        return {
            "test": "Priming Hysteresis",
            "level_data": level_data,
            "mean_hysteresis_effect": mean_hysteresis,
            "middle_levels_hysteresis": middle_hysteresis,
            "significant_levels": significant_levels,
            "total_levels": len(results_by_level),
            "hysteresis_detected": abs(middle_hysteresis) > 0.1 and significant_levels >= 1,
            "n_trials_per_condition": n_trials,
        }


# =============================================================================
# EXPERIMENT DESIGN 2: SEQUENTIAL APPROACH
# =============================================================================

class SequentialHysteresisExperiment:
    """
    Test hysteresis by presenting scenarios in SEQUENCE and measuring
    whether the transition point differs by direction.
    
    Ascending: Present levels 0→1→2→3→4→5→6, find where it flips to O
    Descending: Present levels 6→5→4→3→2→1→0, find where it flips to L
    
    If hysteresis exists, the ascending threshold > descending threshold
    (it takes more to CREATE an obligation than to MAINTAIN one)
    
    OR descending threshold > ascending threshold
    (it takes more to RELEASE an obligation than to CREATE one)
    """
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        
    def create_prompt(self, scenario: str, prior_scenarios: List[str], direction: str) -> str:
        if prior_scenarios:
            history = "\n".join([f"- {s}" for s in prior_scenarios[-2:]])  # Last 2 for context
            context = f"""The situation has been evolving. Recent history:
{history}

CURRENT SITUATION:
"""
        else:
            context = "SITUATION:\n"
        
        return f"""{context}{scenario}

Based on the CURRENT situation, does Alex have a moral OBLIGATION to help Jordan move,
or is Alex at LIBERTY (free to choose)?

Respond EXACTLY:
CLASSIFICATION: O or L
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
    
    def run(self, n_trials: int = 20) -> Dict:
        """Run sequential hysteresis experiment."""
        print("\n" + "=" * 70)
        print("HYSTERESIS EXPERIMENT: SEQUENTIAL APPROACH")
        print("=" * 70)
        print("\nPresent scenarios in sequence, measure transition points.\n")
        
        ascending_thresholds = []
        descending_thresholds = []
        
        for trial in range(n_trials):
            print(f"Trial {trial + 1}/{n_trials}")
            
            # Ascending: 0 → 6
            prior = []
            ascending_transitions = []
            for level_info in COMMITMENT_SPECTRUM:
                result = self.evaluator.evaluate(
                    {"id": f"seq_asc_{trial}_{level_info['level']}"},
                    self.create_prompt(level_info["scenario"], prior, "ascending")
                )
                ascending_transitions.append((level_info["level"], result.bond_type))
                prior.append(level_info["scenario"])
            
            # Find first O in ascending
            asc_threshold = None
            for level, bond in ascending_transitions:
                if bond == BondType.OBLIGATION:
                    asc_threshold = level
                    break
            if asc_threshold is None:
                asc_threshold = 7  # Never reached O
            ascending_thresholds.append(asc_threshold)
            
            # Descending: 6 → 0
            prior = []
            descending_transitions = []
            for level_info in reversed(COMMITMENT_SPECTRUM):
                result = self.evaluator.evaluate(
                    {"id": f"seq_desc_{trial}_{level_info['level']}"},
                    self.create_prompt(level_info["scenario"], prior, "descending")
                )
                descending_transitions.append((level_info["level"], result.bond_type))
                prior.append(level_info["scenario"])
            
            # Find first L in descending (going 6→0)
            desc_threshold = None
            for level, bond in descending_transitions:
                if bond == BondType.LIBERTY:
                    desc_threshold = level
                    break
            if desc_threshold is None:
                desc_threshold = -1  # Never reached L
            descending_thresholds.append(desc_threshold)
            
            print(f"  Ascending first O at: {asc_threshold}")
            print(f"  Descending first L at: {desc_threshold}")
        
        # Analysis
        mean_asc = np.mean(ascending_thresholds)
        mean_desc = np.mean(descending_thresholds)
        
        print("\n" + "=" * 70)
        print("SEQUENTIAL HYSTERESIS ANALYSIS")
        print("=" * 70)
        print(f"\nMean ascending threshold (L→O): {mean_asc:.2f}")
        print(f"Mean descending threshold (O→L): {mean_desc:.2f}")
        print(f"Hysteresis gap: {abs(mean_asc - mean_desc):.2f}")
        
        # Statistical test
        t_stat, p_value = stats.ttest_ind(ascending_thresholds, descending_thresholds)
        print(f"t-test: t = {t_stat:.2f}, p = {p_value:.4f}")
        
        if p_value < 0.05:
            if mean_asc > mean_desc:
                print("\n✓ HYSTERESIS DETECTED: Harder to CREATE obligations than RELEASE them")
            else:
                print("\n✓ HYSTERESIS DETECTED: Harder to RELEASE obligations than CREATE them")
        else:
            print("\n✗ NO SIGNIFICANT HYSTERESIS")
        
        return {
            "test": "Sequential Hysteresis",
            "ascending_thresholds": ascending_thresholds,
            "descending_thresholds": descending_thresholds,
            "mean_ascending": mean_asc,
            "mean_descending": mean_desc,
            "hysteresis_gap": abs(mean_asc - mean_desc),
            "t_statistic": t_stat,
            "p_value": p_value,
            "hysteresis_detected": p_value < 0.05,
            "direction": "CREATE > RELEASE" if mean_asc > mean_desc else "RELEASE > CREATE",
            "n_trials": n_trials,
        }


# =============================================================================
# EVALUATOR
# =============================================================================

class LLMEvaluator:
    def __init__(self, backend: str, model: str, api_key: str = None):
        self.backend = backend
        self.model = model
        self.api_key = api_key
        self.request_count = 0
        self.total_tokens = 0
    
    def evaluate(self, scenario: Dict, prompt: str) -> EvaluationResult:
        try:
            if self.backend == "anthropic":
                response = self._call_anthropic(prompt)
            elif self.backend == "simulation":
                response = self._simulate(prompt, scenario["id"])
            else:
                raise ValueError(f"Unknown backend: {self.backend}")
            
            return self._parse_response(response, scenario["id"])
        except Exception as e:
            return EvaluationResult(
                scenario_id=scenario["id"],
                bond_type=BondType.LIBERTY,
                confidence=0.0,
                reasoning=f"Error: {e}",
                raw_response=""
            )
    
    def _call_anthropic(self, prompt: str) -> str:
        import anthropic
        self.request_count += 1
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
        return response.content[0].text
    
    def _simulate(self, prompt: str, scenario_id: str) -> str:
        """Simulate with realistic hysteresis behavior for testing."""
        self.request_count += 1
        
        import hashlib
        import random
        
        # Extract level from scenario_id
        level = 3  # default middle
        for part in scenario_id.split("_"):
            if part.startswith("L") and part[1:].isdigit():
                level = int(part[1:])
                break
        
        # Base probability of O based on level
        base_p_O = level / 6.0
        
        # Add priming effect for simulation testing
        if "fromO" in scenario_id:
            base_p_O += 0.15  # Simulate hysteresis
        elif "fromL" in scenario_id:
            base_p_O -= 0.15
        
        # Clamp
        base_p_O = max(0, min(1, base_p_O))
        
        # Random draw
        bond = "O" if random.random() < base_p_O else "L"
        
        return f"CLASSIFICATION: {bond}\nCONFIDENCE: 0.8\nREASONING: Based on the commitment level."
    
    def _parse_response(self, response: str, scenario_id: str) -> EvaluationResult:
        bond_type = BondType.LIBERTY
        confidence = 0.5
        reasoning = ""
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('CLASSIFICATION:'):
                type_str = line.replace('CLASSIFICATION:', '').strip().upper()
                if 'O' in type_str:
                    bond_type = BondType.OBLIGATION
                else:
                    bond_type = BondType.LIBERTY
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.replace('CONFIDENCE:', '').strip())
                except:
                    pass
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
        
        return EvaluationResult(
            scenario_id=scenario_id,
            bond_type=bond_type,
            confidence=confidence,
            reasoning=reasoning,
            raw_response=response
        )


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Hysteresis Experiment v2: Proper Methodology",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This experiment fixes the methodological problems in v1:
1. Uses a SINGLE calibrated commitment spectrum
2. Tests hysteresis via priming (same scenario, different prior states)
3. Provides statistical tests for significance

Examples:
  python hysteresis_v2.py --backend simulation --trials 20
  python hysteresis_v2.py --backend anthropic --api-key sk-... --trials 30
        """
    )
    
    parser.add_argument('--backend', choices=['simulation', 'anthropic'],
                        default='simulation')
    parser.add_argument('--model', type=str, default='claude-sonnet-4-20250514')
    parser.add_argument('--api-key', type=str, default=None)
    parser.add_argument('--trials', type=int, default=20,
                        help='Trials per condition')
    parser.add_argument('--experiment', choices=['priming', 'sequential', 'both'],
                        default='priming', help='Which experiment to run')
    parser.add_argument('--output', type=str, default='hysteresis_v2_results.json')
    
    args = parser.parse_args()
    
    # Cost estimate
    if args.experiment == 'priming':
        n_calls = 7 * 3 * args.trials  # 7 levels × 3 conditions × trials
    elif args.experiment == 'sequential':
        n_calls = 2 * 7 * args.trials  # 2 directions × 7 levels × trials
    else:
        n_calls = (7 * 3 + 2 * 7) * args.trials
    
    est_tokens = n_calls * 300
    est_cost = est_tokens * 0.000018  # Rough Sonnet pricing
    
    print(f"Estimated API calls: {n_calls}")
    print(f"Estimated cost: ${est_cost:.2f}")
    print()
    
    evaluator = LLMEvaluator(args.backend, args.model, args.api_key)
    
    results = {"spectrum": [s["description"] for s in COMMITMENT_SPECTRUM]}
    
    if args.experiment in ['priming', 'both']:
        exp1 = PrimingHysteresisExperiment(evaluator)
        results["priming"] = exp1.run(args.trials)
    
    if args.experiment in ['sequential', 'both']:
        exp2 = SequentialHysteresisExperiment(evaluator)
        results["sequential"] = exp2.run(args.trials)
    
    results["metadata"] = {
        "total_requests": evaluator.request_count,
        "total_tokens": evaluator.total_tokens,
        "backend": args.backend,
        "model": args.model,
    }
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to {args.output}")
    print(f"Total API calls: {evaluator.request_count}")
    if evaluator.total_tokens:
        print(f"Estimated cost: ${evaluator.total_tokens * 0.000018:.2f}")


if __name__ == "__main__":
    main()
