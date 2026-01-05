#!/usr/bin/env python3
"""
SQND Phase Transition Experiment v2
====================================

Based on empirical findings from the fuzzer, this experiment tests a REVISED model:

OLD MODEL (SU(2) continuous rotation):
    |ψ(θ)⟩ = cos(θ/2)|O⟩ + sin(θ/2)|L⟩

NEW MODEL (Bistable σ_z eigenstates with phase transitions):
    |ψ⟩ = |O⟩  when context < T_crit  (bound state)
    |ψ⟩ = |L⟩  when context ≥ T_crit  (free state)

Key predictions:
1. SHARP TRANSITIONS at critical thresholds (not gradual)
2. HYSTERESIS - the O→L threshold may differ from L→O threshold
3. CRITICAL SLOWING - near threshold, response times/confidence may change
4. CORRELATIVE SYMMETRY - when properly framed, O↔C and L↔N should swap
5. PATH DEPENDENCE - order of threshold crossings matters (non-Abelian)

Author: SQND Research
"""

import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
from collections import defaultdict
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import argparse

# =============================================================================
# CORE DATA STRUCTURES
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
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# EXPERIMENT 1: PHASE TRANSITION DETECTION
# =============================================================================

class PhaseTransitionExperiment:
    """
    Tests for discrete phase transitions with critical threshold detection.
    
    Uses a fine-grained threshold ladder to find the exact transition point.
    Measures:
    - Critical threshold T_c
    - Transition sharpness (width)
    - Hysteresis (O→L vs L→O)
    """
    
    # Threshold levels with fine gradations around expected transition
    THRESHOLD_LADDER = [
        # Level 0-2: Clearly binding
        {"level": 0, "text": "", "expected": "O"},
        {"level": 1, "text": "Jordan thanked Alex for the commitment.", "expected": "O"},
        {"level": 2, "text": "Jordan mentioned they appreciate the help.", "expected": "O"},
        
        # Level 3-7: Transition zone (fine gradation)
        {"level": 3, "text": "Jordan said the timing might need to be flexible.", "expected": "O?"},
        {"level": 4, "text": "Jordan mentioned they might be able to manage alone.", "expected": "?"},
        {"level": 5, "text": "Jordan said 'only help if it's convenient for you'.", "expected": "?"},
        {"level": 6, "text": "Jordan found a friend who might help instead.", "expected": "?"},
        {"level": 7, "text": "Jordan said 'don't worry about it if you're busy'.", "expected": "L?"},
        
        # Level 8-10: Clearly released
        {"level": 8, "text": "Jordan explicitly said 'I release you from your promise'.", "expected": "L"},
        {"level": 9, "text": "Jordan cancelled the move entirely.", "expected": "L"},
        {"level": 10, "text": "Jordan moved last week without telling Alex.", "expected": "L"},
    ]
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
        
    def create_scenario(self, level_info: Dict, direction: str = "O_to_L") -> Dict:
        """Create a scenario at a given threshold level."""
        
        if direction == "O_to_L":
            # Start with clear obligation, add release context
            base = "Alex promised to help Jordan move next Saturday. "
            context = level_info["text"]
        else:
            # Start with no obligation, add binding context
            # (For hysteresis test)
            base = "Alex mentioned they might help Jordan move. "
            binding_texts = [
                "",
                "Jordan said 'that would be nice'.",
                "Jordan said 'I'm counting on you'.",
                "Alex said 'I promise I'll be there'.",
                "Alex gave Jordan their word and shook hands.",
            ]
            idx = min(level_info["level"], len(binding_texts) - 1)
            context = binding_texts[idx]
        
        return {
            "id": f"phase_{direction}_{level_info['level']}",
            "text": base + context,
            "level": level_info["level"],
            "direction": direction,
            "agent_a": "Alex",
            "agent_b": "Jordan",
        }
    
    def create_prompt(self, scenario: Dict) -> str:
        return f"""Analyze this moral scenario.

SCENARIO:
{scenario['text']}

What is {scenario['agent_a']}'s moral status regarding helping {scenario['agent_b']}?

Classify as ONE of:
- O (OBLIGATION): {scenario['agent_a']} has a binding duty to help
- L (LIBERTY): {scenario['agent_a']} is free to help or not

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
    
    def run(self, n_trials: int = 10) -> Dict:
        """Run the phase transition experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 1: PHASE TRANSITION DETECTION")
        print("=" * 70)
        
        results_by_level = defaultdict(list)
        
        # Test O→L direction
        print("\nTesting O→L transition (promise release)...")
        for level_info in self.THRESHOLD_LADDER:
            for trial in range(n_trials):
                scenario = self.create_scenario(level_info, "O_to_L")
                scenario["id"] = f"{scenario['id']}_{trial}"
                
                result = self.evaluator.evaluate(scenario, self.create_prompt(scenario))
                results_by_level[level_info["level"]].append(result)
                self.results.append(result)
            
            # Print progress
            l_count = sum(1 for r in results_by_level[level_info["level"]] 
                         if r.bond_type == BondType.LIBERTY)
            print(f"  Level {level_info['level']:2d}: L={l_count}/{n_trials} "
                  f"({100*l_count/n_trials:5.1f}%) | {level_info['text'][:50]}")
        
        # Analyze transition
        analysis = self._analyze_transition(results_by_level, n_trials)
        
        return analysis
    
    def _analyze_transition(self, results_by_level: Dict, n_trials: int) -> Dict:
        """Analyze the phase transition characteristics."""
        
        # Calculate P(L) at each level
        levels = sorted(results_by_level.keys())
        p_liberty = []
        confidence_by_level = []
        
        for level in levels:
            results = results_by_level[level]
            l_count = sum(1 for r in results if r.bond_type == BondType.LIBERTY)
            p_liberty.append(l_count / len(results))
            confidence_by_level.append(np.mean([r.confidence for r in results]))
        
        # Fit sigmoid to find critical threshold
        def sigmoid(x, T_c, k):
            return 1 / (1 + np.exp(-k * (x - T_c)))
        
        try:
            popt, pcov = curve_fit(sigmoid, levels, p_liberty, 
                                   p0=[5, 1], bounds=([0, 0.1], [10, 10]))
            T_c, k = popt
            transition_width = 2 / k  # Width of transition region
        except:
            T_c = np.interp(0.5, p_liberty, levels) if p_liberty[-1] > p_liberty[0] else 5
            k = 1
            transition_width = 2
        
        # Check for sharpness
        is_sharp = transition_width < 2  # Transition happens within 2 levels
        
        print(f"\n  Critical threshold T_c = {T_c:.2f}")
        print(f"  Transition width = {transition_width:.2f} levels")
        print(f"  Transition type: {'SHARP (discrete)' if is_sharp else 'GRADUAL (continuous)'}")
        
        # Check confidence dip at transition (critical slowing)
        mid_levels = [l for l in levels if abs(l - T_c) < 2]
        if mid_levels:
            mid_conf = np.mean([confidence_by_level[levels.index(l)] for l in mid_levels])
            edge_conf = np.mean([confidence_by_level[0], confidence_by_level[-1]])
            confidence_dip = edge_conf - mid_conf
            print(f"  Confidence dip at transition: {confidence_dip:.3f}")
        else:
            confidence_dip = 0
        
        return {
            "test": "Phase Transition",
            "levels": levels,
            "p_liberty": p_liberty,
            "confidence_by_level": confidence_by_level,
            "T_c": T_c,
            "transition_width": transition_width,
            "is_sharp": is_sharp,
            "confidence_dip": confidence_dip,
            "supports_discrete_model": is_sharp and transition_width < 3,
        }


# =============================================================================
# EXPERIMENT 2: HYSTERESIS
# =============================================================================

class HysteresisExperiment:
    """
    Tests for hysteresis - asymmetry between O→L and L→O transitions.
    
    If there's hysteresis, the threshold for releasing an obligation
    differs from the threshold for creating one.
    """
    
    # O→L: Start with obligation, gradually release
    O_TO_L_LADDER = [
        {"level": 0, "text": "Alex firmly promised to help Jordan move. Jordan is counting on Alex.", "start": "O"},
        {"level": 1, "text": "Alex firmly promised to help Jordan move. Jordan said it's somewhat flexible.", "start": "O"},
        {"level": 2, "text": "Alex firmly promised to help Jordan move. Jordan said help would be nice but not essential.", "start": "O"},
        {"level": 3, "text": "Alex firmly promised to help Jordan move. Jordan found backup help just in case.", "start": "O"},
        {"level": 4, "text": "Alex firmly promised to help Jordan move. Jordan said 'only if convenient'.", "start": "O"},
        {"level": 5, "text": "Alex firmly promised to help Jordan move. Jordan said 'don't worry about it'.", "start": "O"},
        {"level": 6, "text": "Alex firmly promised to help Jordan move. Jordan explicitly released Alex from the promise.", "start": "O"},
    ]
    
    # L→O: Start with no obligation, gradually bind
    L_TO_O_LADDER = [
        {"level": 0, "text": "Alex has no particular connection to Jordan. Jordan is moving next week.", "start": "L"},
        {"level": 1, "text": "Alex casually mentioned they might help Jordan move. Jordan said that would be nice.", "start": "L"},
        {"level": 2, "text": "Alex said they'd probably help Jordan move. Jordan started relying on this.", "start": "L"},
        {"level": 3, "text": "Alex agreed to help Jordan move. Jordan thanked them.", "start": "L"},
        {"level": 4, "text": "Alex promised to help Jordan move. Jordan expressed gratitude.", "start": "L"},
        {"level": 5, "text": "Alex gave their word to help Jordan move. They shook hands on it.", "start": "L"},
        {"level": 6, "text": "Alex solemnly swore to help Jordan move. Jordan is completely depending on Alex.", "start": "L"},
    ]
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def create_prompt(self, text: str) -> str:
        return f"""Analyze this moral scenario.

SCENARIO:
{text}

Does Alex have a moral OBLIGATION to help Jordan, or is Alex at LIBERTY (free to help or not)?

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
    
    def run(self, n_trials: int = 10) -> Dict:
        """Run the hysteresis experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 2: HYSTERESIS (O→L vs L→O)")
        print("=" * 70)
        
        o_to_l_results = defaultdict(list)
        l_to_o_results = defaultdict(list)
        
        # Test O→L
        print("\nTesting O→L direction (releasing obligation)...")
        for level_info in self.O_TO_L_LADDER:
            for trial in range(n_trials):
                scenario = {"id": f"hyst_OL_{level_info['level']}_{trial}", 
                           "text": level_info["text"]}
                result = self.evaluator.evaluate(scenario, self.create_prompt(level_info["text"]))
                o_to_l_results[level_info["level"]].append(result)
                self.results.append(result)
            
            l_count = sum(1 for r in o_to_l_results[level_info["level"]] 
                         if r.bond_type == BondType.LIBERTY)
            print(f"  Level {level_info['level']}: P(L) = {l_count/n_trials:.0%}")
        
        # Test L→O
        print("\nTesting L→O direction (creating obligation)...")
        for level_info in self.L_TO_O_LADDER:
            for trial in range(n_trials):
                scenario = {"id": f"hyst_LO_{level_info['level']}_{trial}",
                           "text": level_info["text"]}
                result = self.evaluator.evaluate(scenario, self.create_prompt(level_info["text"]))
                l_to_o_results[level_info["level"]].append(result)
                self.results.append(result)
            
            o_count = sum(1 for r in l_to_o_results[level_info["level"]] 
                         if r.bond_type == BondType.OBLIGATION)
            print(f"  Level {level_info['level']}: P(O) = {o_count/n_trials:.0%}")
        
        # Calculate transition points
        def find_threshold(results_dict, target_type, n):
            levels = sorted(results_dict.keys())
            probs = [sum(1 for r in results_dict[l] if r.bond_type == target_type) / n 
                    for l in levels]
            # Find where prob crosses 0.5
            for i in range(len(probs) - 1):
                if probs[i] < 0.5 <= probs[i+1] or probs[i] >= 0.5 > probs[i+1]:
                    return levels[i] + (0.5 - probs[i]) / (probs[i+1] - probs[i])
            return levels[-1] if probs[-1] >= 0.5 else levels[0]
        
        T_c_release = find_threshold(o_to_l_results, BondType.LIBERTY, n_trials)
        T_c_bind = find_threshold(l_to_o_results, BondType.OBLIGATION, n_trials)
        
        hysteresis = abs(T_c_release - T_c_bind)
        
        print(f"\n  T_c (O→L, release): {T_c_release:.2f}")
        print(f"  T_c (L→O, bind): {T_c_bind:.2f}")
        print(f"  Hysteresis gap: {hysteresis:.2f}")
        print(f"  Hysteresis detected: {'YES' if hysteresis > 0.5 else 'NO'}")
        
        return {
            "test": "Hysteresis",
            "T_c_release": T_c_release,
            "T_c_bind": T_c_bind,
            "hysteresis_gap": hysteresis,
            "has_hysteresis": hysteresis > 0.5,
        }


# =============================================================================
# EXPERIMENT 3: CORRELATIVE SYMMETRY (REDESIGNED)
# =============================================================================

class CorrelativeSymmetryExperiment:
    """
    Tests Hohfeldian correlative symmetry with EXPLICIT perspective framing.
    
    The key insight: we must ask about the SAME relationship from different
    perspectives, not just swap agent names.
    
    If Alex has OBLIGATION toward Jordan, then Jordan has CLAIM against Alex.
    If Alex has LIBERTY regarding Jordan, then Jordan has NO-CLAIM against Alex.
    """
    
    SCENARIOS = [
        {
            "id": "debt",
            "a_perspective": "Alex borrowed $100 from Jordan last month and promised to repay it this week.",
            "b_perspective": "Jordan lent $100 to Alex last month. Alex promised to repay it this week.",
            "a_question": "What is Alex's moral status regarding the money?",
            "b_question": "What is Jordan's moral status regarding the money?",
            "expected_a": "O",  # Alex has Obligation
            "expected_b": "C",  # Jordan has Claim
        },
        {
            "id": "promise",
            "a_perspective": "Alex promised to drive Jordan to the airport tomorrow morning.",
            "b_perspective": "Jordan received a promise from Alex to be driven to the airport tomorrow morning.",
            "a_question": "What is Alex's moral status regarding driving Jordan?",
            "b_question": "What is Jordan's moral status regarding being driven by Alex?",
            "expected_a": "O",
            "expected_b": "C",
        },
        {
            "id": "no_duty",
            "a_perspective": "Alex is a stranger who happens to be walking past Jordan's house.",
            "b_perspective": "Jordan is at home. A stranger named Alex is walking past on the sidewalk.",
            "a_question": "What is Alex's moral status regarding helping Jordan with yard work?",
            "b_question": "What is Jordan's moral status regarding getting help from Alex with yard work?",
            "expected_a": "L",  # Alex has Liberty
            "expected_b": "N",  # Jordan has No-claim
        },
        {
            "id": "released",
            "a_perspective": "Alex had promised to help Jordan, but Jordan explicitly said 'I release you from your promise, don't worry about it.'",
            "b_perspective": "Jordan explicitly released Alex from a previous promise, saying 'don't worry about it.'",
            "a_question": "What is Alex's moral status regarding the original promise?",
            "b_question": "What is Jordan's moral status regarding Alex's original promise?",
            "expected_a": "L",
            "expected_b": "N",
        },
        {
            "id": "professional",
            "a_perspective": "Dr. Alex is the assigned physician for patient Jordan in the hospital.",
            "b_perspective": "Jordan is a patient in the hospital. Dr. Alex has been assigned as their physician.",
            "a_question": "What is Dr. Alex's moral status regarding providing medical care?",
            "b_question": "What is Jordan's moral status regarding receiving medical care from Dr. Alex?",
            "expected_a": "O",
            "expected_b": "C",
        },
    ]
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def create_prompt_a(self, scenario: Dict) -> str:
        return f"""Analyze this moral scenario from {scenario['id'].upper()}'s perspective.

SCENARIO:
{scenario['a_perspective']}

QUESTION: {scenario['a_question']}

Classify as ONE of:
- O (OBLIGATION): Alex has a duty/must do this
- L (LIBERTY): Alex is free/permitted, no duty either way

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
    
    def create_prompt_b(self, scenario: Dict) -> str:
        return f"""Analyze this moral scenario from {scenario['id'].upper()}'s perspective.

SCENARIO:
{scenario['b_perspective']}

QUESTION: {scenario['b_question']}

Classify as ONE of:
- C (CLAIM): Jordan has a right/can demand this
- N (NO-CLAIM): Jordan has no right to demand this

Respond EXACTLY:
CLASSIFICATION: [C/N]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
    
    def run(self, n_trials: int = 10) -> Dict:
        """Run the correlative symmetry experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 3: CORRELATIVE SYMMETRY")
        print("=" * 70)
        print("\nTesting: O↔C and L↔N correlative pairs")
        
        symmetry_results = []
        
        for scenario in self.SCENARIOS:
            a_results = []
            b_results = []
            
            for trial in range(n_trials):
                # Evaluate A's perspective
                scenario_a = {"id": f"sym_{scenario['id']}_A_{trial}", "text": scenario['a_perspective']}
                result_a = self.evaluator.evaluate(scenario_a, self.create_prompt_a(scenario))
                a_results.append(result_a)
                
                # Evaluate B's perspective
                scenario_b = {"id": f"sym_{scenario['id']}_B_{trial}", "text": scenario['b_perspective']}
                result_b = self.evaluator.evaluate(scenario_b, self.create_prompt_b(scenario))
                b_results.append(result_b)
                
                self.results.extend([result_a, result_b])
            
            # Check symmetry
            # O should pair with C, L should pair with N
            correct_pairs = 0
            for ra, rb in zip(a_results, b_results):
                if ra.bond_type == BondType.OBLIGATION and rb.bond_type == BondType.CLAIM:
                    correct_pairs += 1
                elif ra.bond_type == BondType.LIBERTY and rb.bond_type == BondType.NO_CLAIM:
                    correct_pairs += 1
            
            symmetry_rate = correct_pairs / n_trials
            
            # Get modal responses
            a_mode = max(set(r.bond_type for r in a_results), 
                        key=lambda x: sum(1 for r in a_results if r.bond_type == x))
            b_mode = max(set(r.bond_type for r in b_results),
                        key=lambda x: sum(1 for r in b_results if r.bond_type == x))
            
            result = {
                "scenario": scenario['id'],
                "expected": f"{scenario['expected_a']}↔{scenario['expected_b']}",
                "observed": f"{a_mode.value}↔{b_mode.value}",
                "symmetry_rate": symmetry_rate,
                "correct": (a_mode.value == scenario['expected_a'] and 
                           b_mode.value == scenario['expected_b']),
            }
            symmetry_results.append(result)
            
            status = "✓" if result['correct'] else "✗"
            print(f"  {scenario['id']:12s}: expected {result['expected']}, "
                  f"got {result['observed']}, symmetry={symmetry_rate:.0%} {status}")
        
        overall_symmetry = np.mean([r['symmetry_rate'] for r in symmetry_results])
        correct_count = sum(1 for r in symmetry_results if r['correct'])
        
        print(f"\n  Overall symmetry rate: {overall_symmetry:.1%}")
        print(f"  Correct predictions: {correct_count}/{len(symmetry_results)}")
        
        return {
            "test": "Correlative Symmetry",
            "results": symmetry_results,
            "overall_symmetry_rate": overall_symmetry,
            "correct_predictions": correct_count,
            "total_scenarios": len(symmetry_results),
            "supports_hohfeldian": overall_symmetry > 0.7,
        }


# =============================================================================
# EXPERIMENT 4: PATH DEPENDENCE (NON-ABELIAN)
# =============================================================================

class PathDependenceExperiment:
    """
    Tests for non-Abelian structure through path dependence.
    
    Uses morally significant context modifications that might not commute.
    """
    
    BASE_SCENARIO = "Alex and Jordan are business partners with equal stakes in a project."
    
    MODIFIER_PAIRS = [
        {
            "id": "trust_harm",
            "A": "Jordan discovered that Alex had been secretly negotiating with a competitor.",
            "B": "Alex discovered that the project was failing and would cost both of them money.",
            "question": "Does Alex have an obligation to continue supporting the partnership?",
        },
        {
            "id": "apology_damage",
            "A": "Alex sincerely apologized for a past mistake that hurt Jordan.",
            "B": "Despite good intentions, Alex's actions caused significant financial loss to Jordan.",
            "question": "Does Alex have an obligation to compensate Jordan?",
        },
        {
            "id": "emergency_betrayal",
            "A": "Alex was dealing with a serious family emergency.",
            "B": "Alex broke a critical promise to Jordan.",
            "question": "Does Alex have an obligation to make amends to Jordan?",
        },
        {
            "id": "forgiveness_pattern",
            "A": "Jordan forgave Alex for a previous transgression.",
            "B": "Alex repeated similar behavior after being forgiven.",
            "question": "Does Alex have an obligation to change their behavior?",
        },
    ]
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def create_prompt(self, base: str, mods: List[str], question: str) -> str:
        context = base + " " + " ".join(mods)
        return f"""Analyze this moral scenario.

SCENARIO:
{context}

QUESTION: {question}

Classify as ONE of:
- O (OBLIGATION): Alex has a binding duty
- L (LIBERTY): Alex is free, no duty

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
"""
    
    def run(self, n_trials: int = 15) -> Dict:
        """Run the path dependence experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 4: PATH DEPENDENCE (NON-ABELIAN)")
        print("=" * 70)
        print("\nTesting if order of context matters (A→B vs B→A)")
        
        path_results = []
        
        for pair in self.MODIFIER_PAIRS:
            ab_results = []
            ba_results = []
            
            for trial in range(n_trials):
                # Path A→B
                prompt_ab = self.create_prompt(
                    self.BASE_SCENARIO, 
                    [pair["A"], pair["B"]], 
                    pair["question"]
                )
                scenario_ab = {"id": f"path_{pair['id']}_AB_{trial}", "text": ""}
                result_ab = self.evaluator.evaluate(scenario_ab, prompt_ab)
                ab_results.append(result_ab)
                
                # Path B→A
                prompt_ba = self.create_prompt(
                    self.BASE_SCENARIO,
                    [pair["B"], pair["A"]],
                    pair["question"]
                )
                scenario_ba = {"id": f"path_{pair['id']}_BA_{trial}", "text": ""}
                result_ba = self.evaluator.evaluate(scenario_ba, prompt_ba)
                ba_results.append(result_ba)
                
                self.results.extend([result_ab, result_ba])
            
            # Calculate distribution difference
            ab_o = sum(1 for r in ab_results if r.bond_type == BondType.OBLIGATION)
            ba_o = sum(1 for r in ba_results if r.bond_type == BondType.OBLIGATION)
            
            # Chi-square test
            contingency = np.array([[ab_o, n_trials - ab_o], 
                                   [ba_o, n_trials - ba_o]])
            if contingency.min() > 0:
                chi2, p = stats.chi2_contingency(contingency)[:2]
            else:
                chi2, p = 0, 1.0
            
            path_dependent = p < 0.1  # Use p < 0.1 for this exploratory test
            
            result = {
                "pair": pair["id"],
                "AB_obligation": ab_o / n_trials,
                "BA_obligation": ba_o / n_trials,
                "difference": abs(ab_o - ba_o) / n_trials,
                "chi2": chi2,
                "p_value": p,
                "path_dependent": path_dependent,
            }
            path_results.append(result)
            
            status = "PATH DEP!" if path_dependent else ""
            print(f"  {pair['id']:20s}: A→B: {ab_o/n_trials:.0%} O, "
                  f"B→A: {ba_o/n_trials:.0%} O, Δ={result['difference']:.0%} {status}")
        
        n_path_dep = sum(1 for r in path_results if r['path_dependent'])
        
        print(f"\n  Path-dependent pairs: {n_path_dep}/{len(path_results)}")
        
        return {
            "test": "Path Dependence",
            "results": path_results,
            "n_path_dependent": n_path_dep,
            "total_pairs": len(path_results),
            "supports_non_abelian": n_path_dep >= 2,
        }


# =============================================================================
# EXPERIMENT 5: CRITICAL FLUCTUATIONS
# =============================================================================

class CriticalFluctuationsExperiment:
    """
    Tests for critical fluctuations near the phase transition.
    
    Near a critical point, we expect:
    1. Increased response variability
    2. Decreased confidence
    3. Longer/more complex reasoning
    """
    
    # Scenarios at different distances from critical threshold
    SCENARIOS = [
        {"distance": -3, "text": "Alex solemnly promised to help Jordan. Jordan is completely depending on Alex."},
        {"distance": -2, "text": "Alex promised to help Jordan move. Jordan thanked them."},
        {"distance": -1, "text": "Alex agreed to help Jordan move. Jordan seems to expect it."},
        {"distance": 0, "text": "Alex said they'd try to help Jordan move, but made no firm promise."},  # Critical
        {"distance": 1, "text": "Alex mentioned they might help Jordan move if they're free."},
        {"distance": 2, "text": "Alex casually said they could possibly help Jordan move."},
        {"distance": 3, "text": "Alex and Jordan are strangers. Jordan is moving this weekend."},
    ]
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.results = []
    
    def create_prompt(self, text: str) -> str:
        return f"""Analyze this moral scenario carefully.

SCENARIO:
{text}

Does Alex have a moral OBLIGATION to help Jordan, or is Alex at LIBERTY?

Respond EXACTLY:
CLASSIFICATION: [O/L]
CONFIDENCE: [0.0-1.0]
REASONING: [your detailed reasoning]
"""
    
    def run(self, n_trials: int = 20) -> Dict:
        """Run the critical fluctuations experiment."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 5: CRITICAL FLUCTUATIONS")
        print("=" * 70)
        print("\nMeasuring variability and confidence near transition...")
        
        results_by_distance = defaultdict(list)
        
        for scenario in self.SCENARIOS:
            for trial in range(n_trials):
                s = {"id": f"crit_{scenario['distance']}_{trial}", 
                     "text": scenario["text"]}
                result = self.evaluator.evaluate(s, self.create_prompt(scenario["text"]))
                results_by_distance[scenario["distance"]].append(result)
                self.results.append(result)
        
        # Analyze
        analysis = []
        for distance in sorted(results_by_distance.keys()):
            results = results_by_distance[distance]
            
            # Response variability (entropy)
            o_count = sum(1 for r in results if r.bond_type == BondType.OBLIGATION)
            p_o = o_count / len(results)
            if 0 < p_o < 1:
                entropy = -p_o * np.log2(p_o) - (1-p_o) * np.log2(1-p_o)
            else:
                entropy = 0
            
            # Confidence
            mean_conf = np.mean([r.confidence for r in results])
            std_conf = np.std([r.confidence for r in results])
            
            # Reasoning length (proxy for complexity)
            mean_reasoning_len = np.mean([len(r.reasoning) for r in results])
            
            analysis.append({
                "distance": distance,
                "p_obligation": p_o,
                "entropy": entropy,
                "mean_confidence": mean_conf,
                "std_confidence": std_conf,
                "mean_reasoning_length": mean_reasoning_len,
            })
            
            print(f"  d={distance:+d}: P(O)={p_o:.0%}, entropy={entropy:.2f}, "
                  f"conf={mean_conf:.2f}±{std_conf:.2f}")
        
        # Check if entropy peaks near d=0
        entropies = [a["entropy"] for a in analysis]
        distances = [a["distance"] for a in analysis]
        max_entropy_dist = distances[np.argmax(entropies)]
        
        print(f"\n  Max entropy at distance: {max_entropy_dist}")
        print(f"  Critical fluctuations: {'DETECTED' if abs(max_entropy_dist) <= 1 else 'NOT CLEAR'}")
        
        return {
            "test": "Critical Fluctuations",
            "analysis": analysis,
            "max_entropy_distance": max_entropy_dist,
            "critical_fluctuations_detected": abs(max_entropy_dist) <= 1,
        }


# =============================================================================
# EVALUATOR
# =============================================================================

class LLMEvaluator:
    """Unified evaluator for all experiments."""
    
    def __init__(self, backend: str, model: str, api_key: str = None):
        self.backend = backend
        self.model = model
        self.api_key = api_key
        self.request_count = 0
        self.total_tokens = 0
        
    def evaluate(self, scenario: Dict, prompt: str) -> EvaluationResult:
        """Evaluate a scenario with the given prompt."""
        
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
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=60
        )
        return response.json().get("response", "")
    
    def _simulate(self, prompt: str) -> str:
        """Simple simulation for testing."""
        self.request_count += 1
        # Hash-based deterministic response
        h = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        bond = "O" if "promise" in prompt.lower() or "owe" in prompt.lower() else "L"
        if "release" in prompt.lower() or "no" in prompt.lower():
            bond = "L"
        return f"CLASSIFICATION: {bond}\nCONFIDENCE: 0.8\nREASONING: Based on the scenario."
    
    def _parse_response(self, response: str, scenario_id: str) -> EvaluationResult:
        bond_type = BondType.LIBERTY
        confidence = 0.5
        reasoning = ""
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('CLASSIFICATION:'):
                type_str = line.replace('CLASSIFICATION:', '').strip()
                for char in type_str.upper():
                    if char in 'OCLN':
                        try:
                            bond_type = BondType.from_string(char)
                            break
                        except:
                            pass
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

def run_all_experiments(evaluator: LLMEvaluator, n_trials: int = 10) -> Dict:
    """Run all experiments."""
    
    print("=" * 70)
    print("SQND PHASE TRANSITION EXPERIMENTS v2")
    print("=" * 70)
    print(f"\nBackend: {evaluator.backend}")
    print(f"Model: {evaluator.model}")
    print(f"Trials per condition: {n_trials}")
    
    results = {}
    
    # Experiment 1: Phase Transition
    exp1 = PhaseTransitionExperiment(evaluator)
    results["phase_transition"] = exp1.run(n_trials)
    
    # Experiment 2: Hysteresis
    exp2 = HysteresisExperiment(evaluator)
    results["hysteresis"] = exp2.run(n_trials)
    
    # Experiment 3: Correlative Symmetry
    exp3 = CorrelativeSymmetryExperiment(evaluator)
    results["correlative_symmetry"] = exp3.run(n_trials)
    
    # Experiment 4: Path Dependence
    exp4 = PathDependenceExperiment(evaluator)
    results["path_dependence"] = exp4.run(n_trials)
    
    # Experiment 5: Critical Fluctuations
    exp5 = CriticalFluctuationsExperiment(evaluator)
    results["critical_fluctuations"] = exp5.run(n_trials)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│                    REVISED SQND MODEL TESTS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. DISCRETE PHASE TRANSITION                                        │
│     Sharp transition: {'✓ YES' if results['phase_transition']['is_sharp'] else '✗ NO':>10}                              │
│     Critical threshold T_c: {results['phase_transition']['T_c']:>5.2f}                              │
│                                                                      │
│  2. HYSTERESIS                                                       │
│     Detected: {'✓ YES' if results['hysteresis']['has_hysteresis'] else '✗ NO':>10}                                      │
│     Gap (O→L vs L→O): {results['hysteresis']['hysteresis_gap']:>5.2f}                                  │
│                                                                      │
│  3. CORRELATIVE SYMMETRY                                             │
│     O↔C, L↔N pairing: {results['correlative_symmetry']['overall_symmetry_rate']:>5.1%}                                 │
│     Supports Hohfeldian: {'✓ YES' if results['correlative_symmetry']['supports_hohfeldian'] else '✗ NO':>10}                         │
│                                                                      │
│  4. PATH DEPENDENCE (Non-Abelian)                                    │
│     Pairs with path dependence: {results['path_dependence']['n_path_dependent']}/{results['path_dependence']['total_pairs']}                              │
│     Supports non-Abelian: {'✓ YES' if results['path_dependence']['supports_non_abelian'] else '✗ NO':>10}                          │
│                                                                      │
│  5. CRITICAL FLUCTUATIONS                                            │
│     Max entropy near threshold: {'✓ YES' if results['critical_fluctuations']['critical_fluctuations_detected'] else '✗ NO':>10}                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
""")
    
    results["metadata"] = {
        "total_requests": evaluator.request_count,
        "total_tokens": evaluator.total_tokens,
        "estimated_cost": evaluator.total_tokens * 0.000003 + evaluator.total_tokens * 0.000015,
    }
    
    print(f"\nTotal API calls: {evaluator.request_count}")
    print(f"Total tokens: {evaluator.total_tokens}")
    print(f"Estimated cost: ${results['metadata']['estimated_cost']:.2f}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="SQND Phase Transition Experiments v2")
    parser.add_argument('--backend', choices=['simulation', 'ollama', 'anthropic'],
                       default='simulation')
    parser.add_argument('--model', type=str, default='claude-sonnet-4-20250514')
    parser.add_argument('--api-key', type=str, default=None)
    parser.add_argument('--trials', type=int, default=10,
                       help='Trials per condition')
    parser.add_argument('--output', type=str, default='phase_transition_results.json')
    
    args = parser.parse_args()
    
    evaluator = LLMEvaluator(args.backend, args.model, args.api_key)
    results = run_all_experiments(evaluator, args.trials)
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
