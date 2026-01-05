#!/usr/bin/env python3
"""
Stratified Gauge Theory Exploration Suite
==========================================

Experimental framework for validating the stratified non-Abelian gauge theory
of moral reasoning.

Key experiments:
1. Gate Identification - Map the semantic trigger lexicon
2. Trigger Compositionality - Test Z₂ × Z₂ structure (X² = 1)
3. Stratum Crossing - Test semidirect product (trigger × context interaction)
4. Concordance-Holonomy Correlation - Verify D₄ structure
5. Hysteresis Mapping - Measure asymmetric potential across scenarios

Author: SQND Research
"""

import json
import hashlib
import argparse
from dataclasses import dataclass
from typing import Dict
from enum import Enum
from collections import defaultdict
import numpy as np

# =============================================================================
# CORE STRUCTURES
# =============================================================================

class BondType(Enum):
    OBLIGATION = "O"
    CLAIM = "C"
    LIBERTY = "L"
    NO_CLAIM = "N"
    
    @classmethod
    def from_string(cls, s: str) -> 'BondType':
        s = s.strip().upper()
        for char in s:
            if char == 'O': return cls.OBLIGATION
            if char == 'C': return cls.CLAIM
            if char == 'L': return cls.LIBERTY
            if char == 'N': return cls.NO_CLAIM
        raise ValueError(f"Unknown bond type: {s}")


@dataclass
class EvaluationResult:
    scenario_id: str
    bond_type: BondType
    confidence: float
    reasoning: str
    raw_response: str


# =============================================================================
# EXPERIMENT 1: GATE IDENTIFICATION
# =============================================================================

class GateIdentificationExperiment:
    """
    Maps the semantic trigger lexicon by testing candidate phrases
    against baseline scenarios.
    
    Tests the prediction: Triggers produce bimodal (0% or 100%) distributions.
    """
    
    # Base scenarios that start with clear O or L
    BASES = {
        "promise_O": {
            "text": "Alex firmly promised to help Jordan move this Saturday. Jordan is counting on this help and has made no other arrangements.",
            "initial_state": "O",
            "agent": "Alex",
            "target": "Jordan",
            "action": "helping with the move",
        },
        "no_relation_L": {
            "text": "Alex and Jordan are strangers who happen to live in the same neighborhood. Jordan is moving this weekend.",
            "initial_state": "L",
            "agent": "Alex",
            "target": "Jordan",
            "action": "helping with the move",
        },
    }
    
    # Candidate triggers to test
    CANDIDATE_TRIGGERS = {
        # Expected X-class (O↔L) - Release direction
        "release_explicit": [
            "Jordan explicitly said 'I release you from your promise.'",
            "Jordan told Alex 'You are no longer obligated to help.'",
            "Jordan formally released Alex from any commitment.",
        ],
        "release_implicit": [
            "Jordan said 'only if it's convenient for you.'",
            "Jordan mentioned 'no pressure at all.'",
            "Jordan said 'only help if you want to.'",
        ],
        "release_weak": [
            "Jordan said 'don't worry about it if you're busy.'",
            "Jordan mentioned 'it's okay if you can't make it.'",
            "Jordan said 'I'll understand if something comes up.'",
        ],
        
        # Expected X-class (O↔L) - Binding direction
        "bind_explicit": [
            "Alex said 'I promise I will be there.'",
            "Alex gave Jordan their solemn word.",
            "Alex swore they would help no matter what.",
        ],
        "bind_implicit": [
            "Alex said 'you can count on me.'",
            "Alex assured Jordan 'I'll definitely be there.'",
            "Alex told Jordan 'I won't let you down.'",
        ],
        
        # Expected NULL-class (no effect)
        "circumstantial": [
            "Jordan mentioned they found a friend who might help.",
            "The weather forecast shows it might rain Saturday.",
            "Jordan said the move is less urgent than initially thought.",
        ],
        "ambiguous": [
            "Jordan said 'the timing is flexible.'",
            "Alex mentioned they have other commitments that day.",
            "Jordan's landlord extended the deadline by a week.",
        ],
    }
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def create_prompt(self, base: Dict, trigger: str) -> str:
        """Create prompt with base + trigger."""
        scenario = f"{base['text']} {trigger}"
        
        return f"""Analyze this moral scenario.

SCENARIO:
{scenario}

What is {base['agent']}'s moral status regarding {base['action']}?

Classify as ONE of:
- O (OBLIGATION): {base['agent']} has a duty to help
- L (LIBERTY): {base['agent']} is free to help or not

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
    
    def run(self, n_trials: int = 10) -> Dict:
        """Run gate identification experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 1: GATE IDENTIFICATION")
        print("=" * 70)
        print("\nMapping semantic trigger lexicon...")
        
        trigger_effects = {}
        
        for trigger_class, triggers in self.CANDIDATE_TRIGGERS.items():
            print(f"\n  Testing class: {trigger_class}")
            
            for trigger in triggers:
                trigger_short = trigger[:40] + "..." if len(trigger) > 40 else trigger
                
                # Test from O baseline
                base_O = self.BASES["promise_O"]
                o_results = []
                for i in range(n_trials):
                    prompt = self.create_prompt(base_O, trigger)
                    result = self.evaluator.evaluate(
                        {"id": f"gate_{trigger_class}_{i}_O", "text": ""},
                        prompt
                    )
                    o_results.append(result)
                    self.results.append(result)
                
                # Test from L baseline
                base_L = self.BASES["no_relation_L"]
                l_results = []
                for i in range(n_trials):
                    prompt = self.create_prompt(base_L, trigger)
                    result = self.evaluator.evaluate(
                        {"id": f"gate_{trigger_class}_{i}_L", "text": ""},
                        prompt
                    )
                    l_results.append(result)
                    self.results.append(result)
                
                # Analyze
                p_L_from_O = sum(1 for r in o_results if r.bond_type == BondType.LIBERTY) / n_trials
                p_O_from_L = sum(1 for r in l_results if r.bond_type == BondType.OBLIGATION) / n_trials
                
                # Determine gate type
                if p_L_from_O > 0.8:
                    gate_type = "X (O→L)"
                    strength = p_L_from_O
                elif p_O_from_L > 0.8:
                    gate_type = "X† (L→O)"
                    strength = p_O_from_L
                elif p_L_from_O > 0.3 or p_O_from_L > 0.3:
                    gate_type = "PARTIAL"
                    strength = max(p_L_from_O, p_O_from_L)
                else:
                    gate_type = "NULL"
                    strength = 0
                
                trigger_effects[trigger] = {
                    "class": trigger_class,
                    "gate_type": gate_type,
                    "strength": strength,
                    "p_L_from_O": p_L_from_O,
                    "p_O_from_L": p_O_from_L,
                }
                
                print(f"    {trigger_short}: {gate_type} (α={strength:.2f})")
        
        # Summarize
        self._print_summary(trigger_effects)
        
        return {
            "experiment": "Gate Identification",
            "trigger_effects": trigger_effects,
            "n_trials": n_trials,
        }
    
    def _print_summary(self, effects: Dict):
        """Print summary of gate identification."""
        print("\n" + "-" * 70)
        print("GATE LEXICON SUMMARY")
        print("-" * 70)
        
        by_type = defaultdict(list)
        for trigger, data in effects.items():
            by_type[data["gate_type"]].append((trigger[:30], data["strength"]))
        
        for gate_type in ["X (O→L)", "X† (L→O)", "PARTIAL", "NULL"]:
            if gate_type in by_type:
                print(f"\n  {gate_type}:")
                for trigger, strength in sorted(by_type[gate_type], key=lambda x: -x[1]):
                    print(f"    {trigger}... (α={strength:.2f})")


# =============================================================================
# EXPERIMENT 2: TRIGGER COMPOSITIONALITY
# =============================================================================

class TriggerCompositionalityExperiment:
    """
    Tests the Z₂ × Z₂ structure prediction: X² = 1 (same-class triggers cancel).
    
    If two release triggers are applied, they should cancel out (return to O).
    """
    
    BASE_SCENARIO = "Alex firmly promised to help Jordan move this Saturday."
    
    COMPOSITIONS = [
        {
            "id": "double_release",
            "triggers": [
                "Jordan said 'I release you from your promise.'",
                "Jordan then said 'Actually, I take back that release - I still need your help.'"
            ],
            "prediction": "O",  # Release + anti-release = identity
        },
        {
            "id": "release_confirm_release",
            "triggers": [
                "Jordan said 'I release you from your promise.'",
                "Jordan confirmed 'Yes, you're definitely released.'"
            ],
            "prediction": "L",  # Release + release = release (idempotent)
        },
        {
            "id": "double_bind",
            "triggers": [
                "Alex said 'I promise to help.'",
                "Alex then said 'Just kidding, I'm not actually committed.'"
            ],
            "prediction": "L",  # Bind + anti-bind from L baseline
        },
        {
            "id": "triple_release",
            "triggers": [
                "Jordan said 'I release you.'",
                "Jordan said 'Actually no, please come.'",
                "Jordan said 'Never mind, you're released again.'"
            ],
            "prediction": "L",  # X · X · X = X
        },
    ]
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def run(self, n_trials: int = 15) -> Dict:
        """Run compositionality experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 2: TRIGGER COMPOSITIONALITY")
        print("=" * 70)
        print("\nTesting Z₂ × Z₂ structure (X² = 1)...")
        
        composition_results = []
        
        for comp in self.COMPOSITIONS:
            print(f"\n  Testing: {comp['id']}")
            
            # Build full scenario
            full_scenario = self.BASE_SCENARIO + " " + " ".join(comp["triggers"])
            
            results = []
            for i in range(n_trials):
                prompt = f"""Analyze this moral scenario.

SCENARIO:
{full_scenario}

After all of these statements, what is Alex's FINAL moral status regarding helping Jordan?

Classify as ONE of:
- O (OBLIGATION): Alex has a duty to help
- L (LIBERTY): Alex is free to help or not

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
                result = self.evaluator.evaluate(
                    {"id": f"comp_{comp['id']}_{i}", "text": ""},
                    prompt
                )
                results.append(result)
                self.results.append(result)
            
            # Analyze
            predicted = comp["prediction"]
            actual_dist = {
                "O": sum(1 for r in results if r.bond_type == BondType.OBLIGATION),
                "L": sum(1 for r in results if r.bond_type == BondType.LIBERTY),
            }
            actual_mode = "O" if actual_dist["O"] > actual_dist["L"] else "L"
            correct = actual_mode == predicted
            
            comp_result = {
                "id": comp["id"],
                "predicted": predicted,
                "actual_distribution": actual_dist,
                "actual_mode": actual_mode,
                "correct": correct,
            }
            composition_results.append(comp_result)
            
            status = "✓" if correct else "✗"
            print(f"    Predicted: {predicted}, Actual: {actual_mode} "
                  f"(O={actual_dist['O']}, L={actual_dist['L']}) {status}")
        
        # Summary
        n_correct = sum(1 for r in composition_results if r["correct"])
        print(f"\n  Correct predictions: {n_correct}/{len(composition_results)}")
        
        return {
            "experiment": "Trigger Compositionality",
            "results": composition_results,
            "n_correct": n_correct,
            "n_total": len(composition_results),
            "supports_z2z2": n_correct >= len(composition_results) - 1,
        }


# =============================================================================
# EXPERIMENT 3: STRATUM CROSSING
# =============================================================================

class StratumCrossingExperiment:
    """
    Tests semidirect product structure: trigger effect depends on active context.
    
    The same trigger should have different effects depending on which
    contextual frame is active.
    """
    
    CONTEXTS = {
        "loyalty_first": {
            "text": "Consider the loyalty dimension: Alex has known Jordan for 10 years. They've been through difficult times together.",
            "name": "Loyalty",
        },
        "autonomy_first": {
            "text": "Consider the autonomy dimension: Alex has their own life and priorities. They have the right to make their own choices.",
            "name": "Autonomy",
        },
    }
    
    TRIGGER = "Jordan said 'only if it's convenient for you.'"
    
    BASE = "Alex promised to help Jordan move."
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def run(self, n_trials: int = 20) -> Dict:
        """Run stratum crossing experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 3: STRATUM CROSSING")
        print("=" * 70)
        print("\nTesting semidirect product structure...")
        print(f"Trigger: '{self.TRIGGER}'")
        
        context_results = {}
        
        for ctx_id, context in self.CONTEXTS.items():
            print(f"\n  Context: {context['name']}")
            
            # Trigger before context
            results_before = []
            for i in range(n_trials):
                prompt = f"""Analyze this moral scenario step by step.

SCENARIO:
{self.BASE}

STEP 1: {self.TRIGGER}

STEP 2: {context['text']}

What is Alex's FINAL moral status regarding helping Jordan?

Classify as ONE of:
- O (OBLIGATION): Alex has a duty to help
- L (LIBERTY): Alex is free to help or not

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
                result = self.evaluator.evaluate(
                    {"id": f"strat_{ctx_id}_before_{i}", "text": ""},
                    prompt
                )
                results_before.append(result)
                self.results.append(result)
            
            # Trigger after context
            results_after = []
            for i in range(n_trials):
                prompt = f"""Analyze this moral scenario step by step.

SCENARIO:
{self.BASE}

STEP 1: {context['text']}

STEP 2: {self.TRIGGER}

What is Alex's FINAL moral status regarding helping Jordan?

Classify as ONE of:
- O (OBLIGATION): Alex has a duty to help
- L (LIBERTY): Alex is free to help or not

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
                result = self.evaluator.evaluate(
                    {"id": f"strat_{ctx_id}_after_{i}", "text": ""},
                    prompt
                )
                results_after.append(result)
                self.results.append(result)
            
            # Analyze
            p_L_before = sum(1 for r in results_before if r.bond_type == BondType.LIBERTY) / n_trials
            p_L_after = sum(1 for r in results_after if r.bond_type == BondType.LIBERTY) / n_trials
            
            context_results[ctx_id] = {
                "context": context["name"],
                "p_L_trigger_before_context": p_L_before,
                "p_L_trigger_after_context": p_L_after,
                "difference": abs(p_L_after - p_L_before),
            }
            
            print(f"    Trigger BEFORE context: P(L) = {p_L_before:.0%}")
            print(f"    Trigger AFTER context:  P(L) = {p_L_after:.0%}")
            print(f"    Difference: {abs(p_L_after - p_L_before):.0%}")
        
        # Cross-context comparison
        print("\n  Cross-stratum interaction test:")
        loyalty_diff = context_results["loyalty_first"]["difference"]
        autonomy_diff = context_results["autonomy_first"]["difference"]
        
        # If semidirect product holds, different contexts should produce different
        # interaction patterns with the same trigger
        ctx_diffs = [r["p_L_trigger_after_context"] for r in context_results.values()]
        context_matters = max(ctx_diffs) - min(ctx_diffs) > 0.15
        
        print(f"    Context modulates trigger effect: {'YES' if context_matters else 'NO'}")
        
        return {
            "experiment": "Stratum Crossing",
            "results": context_results,
            "context_matters": context_matters,
            "supports_semidirect": context_matters,
        }


# =============================================================================
# EXPERIMENT 4: CONCORDANCE-HOLONOMY CORRELATION
# =============================================================================

class ConcordanceHolonomyExperiment:
    """
    Tests the prediction: Path dependence occurs iff contextual factors oppose.
    
    Concordant factors (both → same bond type) should commute.
    Discordant factors (→ different bond types) should not commute.
    """
    
    SCENARIOS = [
        {
            "id": "concordant_OO",
            "name": "Both factors reinforce O",
            "base": "Alex is a doctor treating patient Jordan.",
            "factor_A": {
                "name": "Care",
                "text": "Dr. Alex has a professional duty of care to their patients.",
            },
            "factor_B": {
                "name": "Commitment",
                "text": "Alex explicitly took on Jordan's case and promised to see it through.",
            },
            "predicted_holonomy": "LOW",  # Both → O, should commute
        },
        {
            "id": "concordant_LL",
            "name": "Both factors reinforce L",
            "base": "Alex is a bystander who witnessed Jordan drop their wallet.",
            "factor_A": {
                "name": "Autonomy",
                "text": "Alex has no relationship with Jordan and no duty to strangers.",
            },
            "factor_B": {
                "name": "Circumstances",
                "text": "The wallet is already being picked up by someone else.",
            },
            "predicted_holonomy": "LOW",  # Both → L, should commute
        },
        {
            "id": "discordant_OL",
            "name": "Factors oppose (O vs L)",
            "base": "Alex is a consultant with confidential information about Jordan's competitor.",
            "factor_A": {
                "name": "Loyalty",
                "text": "Alex has worked with the competitor for years and owes them confidentiality.",
            },
            "factor_B": {
                "name": "Opportunity",
                "text": "Jordan is offering a much better contract if Alex shares the information.",
            },
            "predicted_holonomy": "HIGH",  # Opposing, should not commute
        },
        {
            "id": "discordant_LO",
            "name": "Factors oppose (L vs O)",
            "base": "Alex found evidence of their company's wrongdoing.",
            "factor_A": {
                "name": "Self-preservation",
                "text": "Whistleblowing could destroy Alex's career and family stability.",
            },
            "factor_B": {
                "name": "Public duty",
                "text": "The public has a right to know about safety violations.",
            },
            "predicted_holonomy": "HIGH",  # Opposing, should not commute
        },
    ]
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def run(self, n_trials: int = 15) -> Dict:
        """Run concordance-holonomy experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 4: CONCORDANCE-HOLONOMY CORRELATION")
        print("=" * 70)
        print("\nTesting: Commutation ↔ Concordance correlation...")
        
        scenario_results = []
        
        for scenario in self.SCENARIOS:
            print(f"\n  {scenario['id']}: {scenario['name']}")
            
            # Path A→B
            results_AB = []
            for i in range(n_trials):
                prompt = f"""Analyze this moral scenario.

SCENARIO:
{scenario['base']}

First, consider: {scenario['factor_A']['text']}

Then, consider: {scenario['factor_B']['text']}

What is Alex's FINAL moral status?

Classify as ONE of:
- O (OBLIGATION): Alex has a duty
- L (LIBERTY): Alex is free to choose

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
                result = self.evaluator.evaluate(
                    {"id": f"conc_{scenario['id']}_AB_{i}", "text": ""},
                    prompt
                )
                results_AB.append(result)
                self.results.append(result)
            
            # Path B→A
            results_BA = []
            for i in range(n_trials):
                prompt = f"""Analyze this moral scenario.

SCENARIO:
{scenario['base']}

First, consider: {scenario['factor_B']['text']}

Then, consider: {scenario['factor_A']['text']}

What is Alex's FINAL moral status?

Classify as ONE of:
- O (OBLIGATION): Alex has a duty
- L (LIBERTY): Alex is free to choose

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
                result = self.evaluator.evaluate(
                    {"id": f"conc_{scenario['id']}_BA_{i}", "text": ""},
                    prompt
                )
                results_BA.append(result)
                self.results.append(result)
            
            # Calculate Wilson loop
            p_AB = {
                "O": sum(1 for r in results_AB if r.bond_type == BondType.OBLIGATION) / n_trials,
                "L": sum(1 for r in results_AB if r.bond_type == BondType.LIBERTY) / n_trials,
            }
            p_BA = {
                "O": sum(1 for r in results_BA if r.bond_type == BondType.OBLIGATION) / n_trials,
                "L": sum(1 for r in results_BA if r.bond_type == BondType.LIBERTY) / n_trials,
            }
            
            W = np.sqrt(p_AB["O"] * p_BA["O"]) + np.sqrt(p_AB["L"] * p_BA["L"])
            
            # Determine holonomy level
            if W > 0.9:
                observed_holonomy = "LOW"
            elif W > 0.7:
                observed_holonomy = "MEDIUM"
            else:
                observed_holonomy = "HIGH"
            
            predicted = scenario["predicted_holonomy"]
            match = observed_holonomy == predicted or (
                predicted == "LOW" and observed_holonomy in ["LOW", "MEDIUM"]
            ) or (
                predicted == "HIGH" and observed_holonomy in ["HIGH", "MEDIUM"]
            )
            
            result = {
                "id": scenario["id"],
                "predicted_holonomy": predicted,
                "observed_holonomy": observed_holonomy,
                "wilson_loop": W,
                "p_AB": p_AB,
                "p_BA": p_BA,
                "match": match,
            }
            scenario_results.append(result)
            
            status = "✓" if match else "✗"
            print(f"    W = {W:.3f} → {observed_holonomy} (predicted: {predicted}) {status}")
        
        # Summary
        n_match = sum(1 for r in scenario_results if r["match"])
        
        # Correlation test
        concordant_W = [r["wilson_loop"] for r in scenario_results 
                       if "concordant" in r["id"]]
        discordant_W = [r["wilson_loop"] for r in scenario_results 
                       if "discordant" in r["id"]]
        
        if concordant_W and discordant_W:
            mean_conc = np.mean(concordant_W)
            mean_disc = np.mean(discordant_W)
            diff = mean_conc - mean_disc
            
            print(f"\n  Mean W (concordant): {mean_conc:.3f}")
            print(f"  Mean W (discordant): {mean_disc:.3f}")
            print(f"  Difference: {diff:.3f}")
            print(f"  Prediction correct: {diff > 0}")
        
        return {
            "experiment": "Concordance-Holonomy Correlation",
            "results": scenario_results,
            "n_match": n_match,
            "n_total": len(scenario_results),
            "supports_D4": n_match >= len(scenario_results) - 1,
        }


# =============================================================================
# EXPERIMENT 5: HYSTERESIS ASYMMETRY
# =============================================================================

class HysteresisAsymmetryExperiment:
    """
    Tests universality of hysteresis across different scenario types.
    
    Prediction: O→L requires stronger intervention than L→O in all cases.
    """
    
    SCENARIO_PAIRS = [
        {
            "id": "promise",
            "O_start": "Alex firmly promised to help Jordan move.",
            "L_start": "Alex mentioned they might be free to help Jordan move.",
            "release_levels": [
                "",  # Baseline
                "Jordan said 'only if convenient.'",
                "Jordan said 'I release you from the promise.'",
            ],
            "bind_levels": [
                "",  # Baseline
                "Jordan said 'I'm counting on you.'",
                "Alex said 'I give you my word.'",
            ],
        },
        {
            "id": "debt",
            "O_start": "Alex owes Jordan $100 from a loan last month.",
            "L_start": "Alex has $100 that they might give to Jordan as a gift.",
            "release_levels": [
                "",
                "Jordan said 'pay when you can.'",
                "Jordan said 'consider it forgiven.'",
            ],
            "bind_levels": [
                "",
                "Jordan reminded Alex about the money.",
                "Alex signed a written IOU.",
            ],
        },
        {
            "id": "professional",
            "O_start": "Dr. Alex is the assigned physician for patient Jordan.",
            "L_start": "Dr. Alex is off-duty when patient Jordan arrives at the ER.",
            "release_levels": [
                "",
                "Jordan requested a different doctor.",
                "Jordan transferred their care to a new physician.",
            ],
            "bind_levels": [
                "",
                "No other doctor is available.",
                "Alex formally took on Jordan's case.",
            ],
        },
    ]
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def run(self, n_trials: int = 10) -> Dict:
        """Run hysteresis asymmetry experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 5: HYSTERESIS ASYMMETRY")
        print("=" * 70)
        print("\nTesting universal asymmetry: O→L harder than L→O...")
        
        hysteresis_results = []
        
        for pair in self.SCENARIO_PAIRS:
            print(f"\n  Scenario: {pair['id']}")
            
            # O→L direction
            o_to_l = []
            for level, release in enumerate(pair["release_levels"]):
                scenario = f"{pair['O_start']} {release}"
                l_count = 0
                
                for i in range(n_trials):
                    prompt = f"""Analyze this moral scenario.

SCENARIO:
{scenario}

What is Alex's moral status?

Classify as ONE of:
- O (OBLIGATION): Alex has a duty
- L (LIBERTY): Alex is free

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
                    result = self.evaluator.evaluate(
                        {"id": f"hyst_{pair['id']}_OL_{level}_{i}", "text": ""},
                        prompt
                    )
                    if result.bond_type == BondType.LIBERTY:
                        l_count += 1
                    self.results.append(result)
                
                o_to_l.append(l_count / n_trials)
            
            # L→O direction
            l_to_o = []
            for level, bind in enumerate(pair["bind_levels"]):
                scenario = f"{pair['L_start']} {bind}"
                o_count = 0
                
                for i in range(n_trials):
                    prompt = f"""Analyze this moral scenario.

SCENARIO:
{scenario}

What is Alex's moral status?

Classify as ONE of:
- O (OBLIGATION): Alex has a duty
- L (LIBERTY): Alex is free

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
                    result = self.evaluator.evaluate(
                        {"id": f"hyst_{pair['id']}_LO_{level}_{i}", "text": ""},
                        prompt
                    )
                    if result.bond_type == BondType.OBLIGATION:
                        o_count += 1
                    self.results.append(result)
                
                l_to_o.append(o_count / n_trials)
            
            # Find transition points
            def find_transition(probs):
                for i, p in enumerate(probs):
                    if p >= 0.5:
                        return i + (0.5 - probs[i-1]) / (p - probs[i-1]) if i > 0 else 0
                return len(probs)
            
            t_release = find_transition(o_to_l)
            t_bind = find_transition(l_to_o)
            gap = t_release - t_bind
            
            result = {
                "id": pair["id"],
                "o_to_l_curve": o_to_l,
                "l_to_o_curve": l_to_o,
                "t_release": t_release,
                "t_bind": t_bind,
                "gap": gap,
                "has_hysteresis": gap > 0,
            }
            hysteresis_results.append(result)
            
            print(f"    O→L: {[f'{p:.0%}' for p in o_to_l]} → T_c = {t_release:.2f}")
            print(f"    L→O: {[f'{p:.0%}' for p in l_to_o]} → T_c = {t_bind:.2f}")
            print(f"    Gap: {gap:.2f} {'(HYSTERESIS)' if gap > 0 else ''}")
        
        # Summary
        n_hysteresis = sum(1 for r in hysteresis_results if r["has_hysteresis"])
        mean_gap = np.mean([r["gap"] for r in hysteresis_results])
        
        print(f"\n  Scenarios with hysteresis: {n_hysteresis}/{len(hysteresis_results)}")
        print(f"  Mean gap: {mean_gap:.2f}")
        print(f"  Universal hysteresis: {'YES' if n_hysteresis == len(hysteresis_results) else 'NO'}")
        
        return {
            "experiment": "Hysteresis Asymmetry",
            "results": hysteresis_results,
            "n_hysteresis": n_hysteresis,
            "n_total": len(hysteresis_results),
            "mean_gap": mean_gap,
            "universal": n_hysteresis == len(hysteresis_results),
        }


# =============================================================================
# EVALUATOR
# =============================================================================

class LLMEvaluator:
    """Unified evaluator."""
    
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
            elif self.backend == "ollama":
                response = self._call_ollama(prompt)
            else:
                response = self._simulate(prompt)
            
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
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
        return response.content[0].text
    
    def _call_ollama(self, prompt: str) -> str:
        import requests
        self.request_count += 1
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=60
        )
        return resp.json().get("response", "")
    
    def _simulate(self, prompt: str) -> str:
        self.request_count += 1
        h = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        
        # Simulate based on keywords
        if "release" in prompt.lower() or "convenient" in prompt.lower():
            bond = "L"
        elif "promise" in prompt.lower() or "owe" in prompt.lower():
            bond = "O"
        else:
            bond = ["O", "L"][h % 2]
        
        return f"CLASSIFICATION: {bond}\nCONFIDENCE: 0.8\nREASONING: Based on scenario."
    
    def _parse_response(self, response: str, scenario_id: str) -> EvaluationResult:
        bond_type = BondType.LIBERTY
        confidence = 0.5
        reasoning = ""
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('CLASSIFICATION:'):
                for char in line.upper():
                    if char in 'OCLN':
                        bond_type = BondType.from_string(char)
                        break
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.replace('CONFIDENCE:', '').strip())
                except:
                    pass
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
        
        return EvaluationResult(scenario_id, bond_type, confidence, reasoning, response)


# =============================================================================
# MAIN
# =============================================================================

def run_exploration_suite(evaluator: LLMEvaluator, n_trials: int = 10) -> Dict:
    """Run the full exploration suite."""
    
    print("=" * 70)
    print("STRATIFIED GAUGE THEORY EXPLORATION SUITE")
    print("=" * 70)
    
    results = {}
    
    # Experiment 1: Gate Identification
    exp1 = GateIdentificationExperiment(evaluator)
    results["gate_identification"] = exp1.run(n_trials)
    
    # Experiment 2: Trigger Compositionality
    exp2 = TriggerCompositionalityExperiment(evaluator)
    results["compositionality"] = exp2.run(n_trials)
    
    # Experiment 3: Stratum Crossing
    exp3 = StratumCrossingExperiment(evaluator)
    results["stratum_crossing"] = exp3.run(n_trials)
    
    # Experiment 4: Concordance-Holonomy
    exp4 = ConcordanceHolonomyExperiment(evaluator)
    results["concordance_holonomy"] = exp4.run(n_trials)
    
    # Experiment 5: Hysteresis Asymmetry
    exp5 = HysteresisAsymmetryExperiment(evaluator)
    results["hysteresis"] = exp5.run(n_trials)
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY: STRATIFIED GAUGE THEORY SUPPORT")
    print("=" * 70)
    
    print(f"""
    ┌────────────────────────────────────────────────────────────────────┐
    │  Component                    Test                    Status       │
    ├────────────────────────────────────────────────────────────────────┤
    │  G₁ ≅ Z₂ × Z₂                 Compositionality        {'PASS' if results['compositionality']['supports_z2z2'] else 'FAIL'}         │
    │  G₂ ≅ D₄                      Concordance-Holonomy    {'PASS' if results['concordance_holonomy']['supports_D4'] else 'FAIL'}         │
    │  Semidirect Product           Stratum Crossing        {'PASS' if results['stratum_crossing']['supports_semidirect'] else 'FAIL'}         │
    │  Asymmetric Potential         Hysteresis             {'PASS' if results['hysteresis']['universal'] else 'PARTIAL'}      │
    │  Discrete Gates               Gate Identification     TBD          │
    └────────────────────────────────────────────────────────────────────┘
    """)
    
    results["metadata"] = {
        "total_requests": evaluator.request_count,
        "total_tokens": evaluator.total_tokens,
    }
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Stratified Gauge Theory Exploration")
    parser.add_argument('--backend', choices=['simulation', 'ollama', 'anthropic'],
                       default='simulation')
    parser.add_argument('--model', type=str, default='claude-sonnet-4-20250514')
    parser.add_argument('--api-key', type=str, default=None)
    parser.add_argument('--trials', type=int, default=10)
    parser.add_argument('--output', type=str, default='stratified_gauge_results.json')
    
    args = parser.parse_args()
    
    evaluator = LLMEvaluator(args.backend, args.model, args.api_key)
    results = run_exploration_suite(evaluator, args.trials)
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to {args.output}")
    print(f"Total API calls: {evaluator.request_count}")


if __name__ == "__main__":
    main()
