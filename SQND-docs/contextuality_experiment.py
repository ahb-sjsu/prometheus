#!/usr/bin/env python3
"""
QUANTUM CONTEXTUALITY TEST FOR MORAL REASONING
===============================================

This experiment tests for genuine quantum-like contextuality in moral reasoning
using adapted CHSH and Hardy-type inequality tests.

BACKGROUND
----------
Classical systems satisfy certain inequalities that quantum systems can violate:

CHSH Inequality: |S| ≤ 2 (classical bound)
                 |S| ≤ 2√2 ≈ 2.83 (quantum bound, Tsirelson's bound)

Hardy's Paradox: Certain joint probability conditions that are impossible
                 classically (P = 0) but possible quantum mechanically (P > 0)

If moral reasoning violates these classical bounds, it would be evidence for
genuine quantum-like structure, not just metaphorical similarity.

KEY INSIGHT
-----------
We adapt these tests to moral scenarios by:
1. Defining incompatible "measurement contexts" (different framings)
2. Measuring correlations between agent judgments in different contexts
3. Testing whether correlations exceed classical bounds

Authors: Andrew H. Bond, Claude
Date: January 2026
"""

import json
import hashlib
import argparse
from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum
import numpy as np
from scipy import stats
import random
from datetime import datetime

# =============================================================================
# THEORETICAL FRAMEWORK
# =============================================================================

"""
CONTEXTUALITY IN MORAL REASONING
================================

In quantum mechanics, contextuality means that the outcome of a measurement
depends on what other measurements are performed alongside it. This is
formalized in tests like CHSH.

MORAL ANALOG
------------
Consider a moral scenario where two agents (Alice, Bob) must make judgments
about a shared situation. Each agent can be prompted with two different
"measurement contexts" (framings):

Alice's contexts:
  A₀: "From a duty-based perspective..."
  A₁: "From a rights-based perspective..."

Bob's contexts:
  B₀: "Considering consequences..."
  B₁: "Considering intentions..."

Each context yields a binary outcome:
  +1: "Obligation applies"
  -1: "Liberty applies"

CHSH TEST
---------
Measure correlations E(Aᵢ, Bⱼ) = ⟨AᵢBⱼ⟩ for all four combinations.

S = E(A₀,B₀) + E(A₀,B₁) + E(A₁,B₀) - E(A₁,B₁)

Classical: |S| ≤ 2
Quantum:   |S| ≤ 2√2 ≈ 2.83

If we observe |S| > 2, this violates classical probability theory.

HARDY TEST
----------
Hardy's paradox provides a stronger test. For certain states:
  P(A₀=+1, B₀=+1) > 0
  P(A₀=+1, B₁=-1) = 0
  P(A₁=-1, B₀=+1) = 0
  P(A₁=-1, B₁=-1) = 0

The last three conditions are impossible to satisfy simultaneously with
the first in classical probability, but possible in quantum mechanics.
"""


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class Outcome(Enum):
    PLUS = +1   # Obligation/Duty applies
    MINUS = -1  # Liberty/Permission applies
    
    @classmethod
    def from_response(cls, response: str) -> 'Outcome':
        """
        Parse ONLY the JUDGMENT line to avoid false matches.
        
        The old code checked for 'O' anywhere in response, which matched
        'CONFIDENCE:', 'REASONING:', etc. — causing almost all responses
        to be classified as OBLIGATION regardless of actual judgment.
        """
        import re
        text = response.upper()
        
        # Look for explicit JUDGMENT line
        match = re.search(r"JUDGMENT:\s*(OBLIGATION|LIBERTY)\b", text)
        if match:
            return cls.PLUS if match.group(1) == "OBLIGATION" else cls.MINUS
        
        # Fallback: look for standalone keywords at start of line or after colon
        # This handles slight format variations
        if re.search(r"(?:^|\n|:\s*)OBLIGATION\b", text):
            return cls.PLUS
        if re.search(r"(?:^|\n|:\s*)LIBERTY\b", text):
            return cls.MINUS
        
        # If we can't parse, raise an error rather than silently defaulting
        raise ValueError(f"Could not parse JUDGMENT from response: {response[:200]!r}")


@dataclass
class ContextualMeasurement:
    """A single measurement in a specific context."""
    scenario_id: str
    agent: str  # "alice" or "bob"
    context: int  # 0 or 1
    outcome: Outcome
    confidence: float
    reasoning: str
    raw_response: str


@dataclass 
class JointMeasurement:
    """A joint measurement of both agents in specific contexts."""
    scenario_id: str
    alice_context: int
    bob_context: int
    alice_outcome: Outcome
    bob_outcome: Outcome
    correlation: int  # +1 if same, -1 if different


# =============================================================================
# SCENARIOS FOR CONTEXTUALITY TESTING
# =============================================================================

CONTEXTUALITY_SCENARIOS = {
    "shared_secret": {
        "base": """
Alex and Jordan both know a secret about their mutual friend Sam. 
Sam confided in each of them separately about a financial struggle.
Now a potential employer is asking both Alex and Jordan for references about Sam.
""",
        "alice_contexts": {
            0: "Focus on ALEX's perspective: Does Alex have a DUTY to protect Sam's confidence, or LIBERTY to share relevant information?",
            1: "Focus on ALEX's perspective: Does Sam have a CLAIM on Alex's silence, giving Alex an OBLIGATION, or does Alex have PERMISSION to decide freely?",
        },
        "bob_contexts": {
            0: "Focus on JORDAN's perspective: Considering the CONSEQUENCES for Sam's job prospects, does Jordan have OBLIGATION or LIBERTY?",
            1: "Focus on JORDAN's perspective: Considering Jordan's INTENTIONS (to help Sam get the job), does Jordan have OBLIGATION or LIBERTY?",
        },
    },
    
    "joint_promise": {
        "base": """
Morgan and Casey both independently promised to help their neighbor Pat move this Saturday.
Neither knew the other had also promised. Pat only needs one person's help.
On Friday, both Morgan and Casey learn of each other's promise.
""",
        "alice_contexts": {
            0: "Focus on MORGAN: From the standpoint of INDIVIDUAL duty, does Morgan have OBLIGATION or LIBERTY regarding showing up?",
            1: "Focus on MORGAN: From the standpoint of COLLECTIVE responsibility (since Casey also promised), does Morgan have OBLIGATION or LIBERTY?",
        },
        "bob_contexts": {
            0: "Focus on CASEY: Considering only CASEY'S original promise, does Casey have OBLIGATION or LIBERTY?",
            1: "Focus on CASEY: Considering that MORGAN might show up instead, does Casey have OBLIGATION or LIBERTY?",
        },
    },
    
    "collaborative_harm": {
        "base": """
Two engineers, River and Sage, both notice a potential safety issue in a product their company is shipping.
Each independently has evidence that suggests a problem, but neither's evidence alone is conclusive.
Together, their evidence would clearly show the danger. Neither knows what the other knows.
""",
        "alice_contexts": {
            0: "Focus on RIVER: From RIVER's individual epistemic position (uncertain evidence), does River have OBLIGATION or LIBERTY to report?",
            1: "Focus on RIVER: From the standpoint of RIVER's professional CODE, does River have OBLIGATION or LIBERTY to report?",
        },
        "bob_contexts": {
            0: "Focus on SAGE: Considering SAGE's individual EVIDENCE alone, does Sage have OBLIGATION or LIBERTY?",  
            1: "Focus on SAGE: Considering SAGE's role in the ORGANIZATION, does Sage have OBLIGATION or LIBERTY?",
        },
    },
    
    "entangled_beneficiary": {
        "base": """
A wealthy donor has left instructions that their estate should benefit "the most deserving young scholar."
Two trustees, Quinn and Avery, must independently evaluate candidates without consulting each other.
They will each submit their judgment, and the scholarship goes to any candidate both approve.
Candidate X has excellent grades but privileged background. Candidate Y has good grades but overcame hardship.
""",
        "alice_contexts": {
            0: "Focus on QUINN: Using MERIT criteria (grades, achievements), is Quinn OBLIGATED to choose X or at LIBERTY to choose either?",
            1: "Focus on QUINN: Using EQUITY criteria (who benefits most), is Quinn OBLIGATED to choose Y or at LIBERTY to choose either?",
        },
        "bob_contexts": {
            0: "Focus on AVERY: Interpreting 'deserving' as ACHIEVEMENT, is Avery OBLIGATED to choose X or at LIBERTY?",
            1: "Focus on AVERY: Interpreting 'deserving' as NEED, is Avery OBLIGATED to choose Y or at LIBERTY?",
        },
    },
}


# =============================================================================
# CHSH TEST IMPLEMENTATION
# =============================================================================

class CHSHTest:
    """
    Clauser-Horne-Shimony-Holt inequality test for moral contextuality.
    
    Classical bound: |S| ≤ 2
    Quantum bound:   |S| ≤ 2√2 ≈ 2.828
    """
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.measurements = []
        
    def create_prompt(self, scenario: Dict, agent: str, context: int) -> str:
        """Create a measurement prompt for a specific agent and context."""
        base = scenario["base"]
        
        if agent == "alice":
            context_text = scenario["alice_contexts"][context]
        else:
            context_text = scenario["bob_contexts"][context]
        
        return f"""Consider this moral scenario:

{base}

{context_text}

You must classify the moral status as EXACTLY ONE of:
- OBLIGATION: The person has a duty/must act
- LIBERTY: The person is free to choose/may act either way

Respond in this format:
JUDGMENT: [OBLIGATION or LIBERTY]
CONFIDENCE: [0.0 to 1.0]
REASONING: [one sentence]
"""

    def measure(self, scenario_id: str, scenario: Dict, 
                alice_context: int, bob_context: int) -> JointMeasurement:
        """Perform a joint measurement on both agents."""
        
        # Measure Alice
        alice_prompt = self.create_prompt(scenario, "alice", alice_context)
        alice_response = self.evaluator.evaluate(
            {"id": f"{scenario_id}_A{alice_context}"},
            alice_prompt
        )
        alice_outcome = Outcome.from_response(alice_response.raw_response)
        
        # Measure Bob
        bob_prompt = self.create_prompt(scenario, "bob", bob_context)
        bob_response = self.evaluator.evaluate(
            {"id": f"{scenario_id}_B{bob_context}"},
            bob_prompt
        )
        bob_outcome = Outcome.from_response(bob_response.raw_response)
        
        # Compute correlation
        correlation = alice_outcome.value * bob_outcome.value
        
        joint = JointMeasurement(
            scenario_id=scenario_id,
            alice_context=alice_context,
            bob_context=bob_context,
            alice_outcome=alice_outcome,
            bob_outcome=bob_outcome,
            correlation=correlation
        )
        
        self.measurements.append(joint)
        return joint
    
    def compute_expectation(self, scenario_id: str, 
                           alice_context: int, bob_context: int) -> float:
        """Compute E(Aᵢ, Bⱼ) from measurements."""
        relevant = [m for m in self.measurements 
                   if m.scenario_id == scenario_id
                   and m.alice_context == alice_context
                   and m.bob_context == bob_context]
        
        if not relevant:
            return 0.0
        
        return np.mean([m.correlation for m in relevant])
    
    def compute_S(self, scenario_id: str) -> float:
        """Compute the CHSH S parameter."""
        E00 = self.compute_expectation(scenario_id, 0, 0)
        E01 = self.compute_expectation(scenario_id, 0, 1)
        E10 = self.compute_expectation(scenario_id, 1, 0)
        E11 = self.compute_expectation(scenario_id, 1, 1)
        
        S = E00 + E01 + E10 - E11
        
        return S, {"E00": E00, "E01": E01, "E10": E10, "E11": E11}
    
    def get_outcome_counts(self, scenario_id: str) -> Dict:
        """Sanity check: count outcomes per setting to verify we get both +1 and -1."""
        counts = {}
        for a_ctx in [0, 1]:
            for b_ctx in [0, 1]:
                key = f"A{a_ctx}B{b_ctx}"
                relevant = [m for m in self.measurements
                           if m.scenario_id == scenario_id
                           and m.alice_context == a_ctx
                           and m.bob_context == b_ctx]
                
                alice_plus = sum(1 for m in relevant if m.alice_outcome == Outcome.PLUS)
                alice_minus = len(relevant) - alice_plus
                bob_plus = sum(1 for m in relevant if m.bob_outcome == Outcome.PLUS)
                bob_minus = len(relevant) - bob_plus
                
                counts[key] = {
                    "n": len(relevant),
                    "alice": {"PLUS": alice_plus, "MINUS": alice_minus},
                    "bob": {"PLUS": bob_plus, "MINUS": bob_minus},
                }
        return counts
    
    def run_test(self, scenario_id: str, scenario: Dict, 
                 trials_per_setting: int = 30) -> Dict:
        """Run full CHSH test for a scenario."""
        
        print(f"\n  Running CHSH test for: {scenario_id}")
        
        # Measure all four context combinations
        for alice_ctx in [0, 1]:
            for bob_ctx in [0, 1]:
                print(f"    Measuring A{alice_ctx}, B{bob_ctx}...", end=" ")
                for trial in range(trials_per_setting):
                    self.measure(scenario_id, scenario, alice_ctx, bob_ctx)
                print(f"({trials_per_setting} trials)")
        
        # Compute S
        S, expectations = self.compute_S(scenario_id)
        
        # Sanity check: print outcome distributions
        counts = self.get_outcome_counts(scenario_id)
        print("\n    Outcome distributions (sanity check):")
        for setting, data in counts.items():
            a_dist = f"+:{data['alice']['PLUS']}, -:{data['alice']['MINUS']}"
            b_dist = f"+:{data['bob']['PLUS']}, -:{data['bob']['MINUS']}"
            print(f"      {setting}: Alice({a_dist}) Bob({b_dist})")
        
        # Warn if we're not seeing both outcomes
        total_minus = sum(d['alice']['MINUS'] + d['bob']['MINUS'] for d in counts.values())
        if total_minus == 0:
            print("    ⚠️  WARNING: No MINUS outcomes observed! Check parsing.")
        
        # Statistical test
        # Under classical assumption, |S| ≤ 2
        # We test if S significantly exceeds 2
        
        # Bootstrap confidence interval
        bootstrap_S = []
        all_measurements = [m for m in self.measurements if m.scenario_id == scenario_id]
        
        for _ in range(1000):
            # Resample measurements
            resampled = np.random.choice(all_measurements, len(all_measurements), replace=True)
            
            # Compute S from resampled
            def boot_expectation(a_ctx, b_ctx):
                rel = [m.correlation for m in resampled 
                      if m.alice_context == a_ctx and m.bob_context == b_ctx]
                return np.mean(rel) if rel else 0
            
            boot_S = (boot_expectation(0, 0) + boot_expectation(0, 1) + 
                     boot_expectation(1, 0) - boot_expectation(1, 1))
            bootstrap_S.append(boot_S)
        
        ci_low, ci_high = np.percentile(bootstrap_S, [2.5, 97.5])
        
        # Determine violation
        classical_bound = 2.0
        quantum_bound = 2 * np.sqrt(2)  # ≈ 2.828
        
        violates_classical = ci_low > classical_bound
        consistent_with_quantum = ci_high <= quantum_bound
        
        result = {
            "scenario_id": scenario_id,
            "S": S,
            "expectations": expectations,
            "ci_95": [ci_low, ci_high],
            "classical_bound": classical_bound,
            "quantum_bound": quantum_bound,
            "violates_classical": violates_classical,
            "consistent_with_quantum": consistent_with_quantum,
            "trials_per_setting": trials_per_setting,
            "total_measurements": len(all_measurements),
        }
        
        print(f"    S = {S:.3f} (95% CI: [{ci_low:.3f}, {ci_high:.3f}])")
        print("    Classical bound: 2.0 | Quantum bound: 2.83")
        print(f"    Violates classical: {violates_classical}")
        
        return result


# =============================================================================
# HARDY TEST IMPLEMENTATION
# =============================================================================

class HardyTest:
    """
    Hardy's paradox test for moral contextuality.
    
    Hardy's conditions (for a specific quantum state):
    1. P(A₀=+1, B₀=+1) > 0           (joint positive outcome possible)
    2. P(A₀=+1, B₁=-1) = 0           (if A₀=+1, then B₁≠-1)
    3. P(A₁=-1, B₀=+1) = 0           (if B₀=+1, then A₁≠-1)
    4. P(A₁=-1, B₁=-1) = 0           (not both negative in context 1)
    
    These four conditions are classically impossible to satisfy simultaneously,
    but quantum mechanics allows them with P(A₀=+1, B₀=+1) up to ~9%.
    """
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.measurements = []
        
    def create_hardy_scenario(self) -> Dict:
        """Create a scenario specifically designed to probe Hardy-type correlations."""
        return {
            "base": """
Two judges, Alpha and Beta, must independently rule on the same case without communicating.
The case involves a contract dispute where both parties have legitimate claims.

Party X claims breach of explicit terms (clear legal basis).
Party Y claims breach of implicit good faith (arguable legal basis).

The judges can rule:
- FOR the claiming party (finding obligation existed)
- AGAINST the claiming party (finding liberty to breach existed)

A ruling only takes effect if BOTH judges agree on it.
""",
            "alice_contexts": {
                0: "ALPHA judges Party X's explicit terms claim: Is there OBLIGATION (terms were binding) or LIBERTY (terms were not binding)?",
                1: "ALPHA judges Party Y's good faith claim: Is there OBLIGATION (good faith required) or LIBERTY (no good faith duty)?",
            },
            "bob_contexts": {
                0: "BETA judges Party X's explicit terms claim: Is there OBLIGATION or LIBERTY?",
                1: "BETA judges Party Y's good faith claim: Is there OBLIGATION or LIBERTY?",
            },
            "hardy_structure": """
For Hardy violation, we need:
- Sometimes both find OBLIGATION on explicit terms (P₀₀(+,+) > 0)
- If Alpha finds OBLIGATION on explicit, Beta never finds LIBERTY on good faith
- If Beta finds OBLIGATION on explicit, Alpha never finds LIBERTY on good faith  
- They never both find LIBERTY on good faith
"""
        }
    
    def measure(self, scenario: Dict, alice_context: int, bob_context: int) -> JointMeasurement:
        """Perform a joint measurement."""
        
        base = scenario["base"]
        alice_text = scenario["alice_contexts"][alice_context]
        bob_text = scenario["bob_contexts"][bob_context]
        
        # Measure Alice
        alice_prompt = f"""{base}

{alice_text}

Respond:
JUDGMENT: [OBLIGATION or LIBERTY]
CONFIDENCE: [0.0-1.0]
"""
        alice_response = self.evaluator.evaluate({"id": "hardy_alice"}, alice_prompt)
        alice_outcome = Outcome.from_response(alice_response.raw_response)
        
        # Measure Bob
        bob_prompt = f"""{base}

{bob_text}

Respond:
JUDGMENT: [OBLIGATION or LIBERTY]
CONFIDENCE: [0.0-1.0]
"""
        bob_response = self.evaluator.evaluate({"id": "hardy_bob"}, bob_prompt)
        bob_outcome = Outcome.from_response(bob_response.raw_response)
        
        joint = JointMeasurement(
            scenario_id="hardy",
            alice_context=alice_context,
            bob_context=bob_context,
            alice_outcome=alice_outcome,
            bob_outcome=bob_outcome,
            correlation=alice_outcome.value * bob_outcome.value
        )
        
        self.measurements.append(joint)
        return joint
    
    def compute_probabilities(self) -> Dict:
        """Compute the four Hardy probabilities."""
        
        def get_prob(a_ctx, b_ctx, a_out, b_out):
            relevant = [m for m in self.measurements
                       if m.alice_context == a_ctx and m.bob_context == b_ctx]
            if not relevant:
                return 0.0
            matches = [m for m in relevant 
                      if m.alice_outcome == a_out and m.bob_outcome == b_out]
            return len(matches) / len(relevant)
        
        # Hardy conditions
        P1 = get_prob(0, 0, Outcome.PLUS, Outcome.PLUS)    # P(A₀=+, B₀=+) > 0
        P2 = get_prob(0, 1, Outcome.PLUS, Outcome.MINUS)   # P(A₀=+, B₁=-) = 0
        P3 = get_prob(1, 0, Outcome.MINUS, Outcome.PLUS)   # P(A₁=-, B₀=+) = 0
        P4 = get_prob(1, 1, Outcome.MINUS, Outcome.MINUS)  # P(A₁=-, B₁=-) = 0
        
        return {
            "P_A0+_B0+": P1,  # Should be > 0 for Hardy
            "P_A0+_B1-": P2,  # Should be = 0 for Hardy
            "P_A1-_B0+": P3,  # Should be = 0 for Hardy
            "P_A1-_B1-": P4,  # Should be = 0 for Hardy
        }
    
    def check_hardy_violation(self, probs: Dict, tolerance: float = 0.05) -> Dict:
        """Check if Hardy conditions are satisfied (which would be classically impossible)."""
        
        P1 = probs["P_A0+_B0+"]
        P2 = probs["P_A0+_B1-"]
        P3 = probs["P_A1-_B0+"]
        P4 = probs["P_A1-_B1-"]
        
        # For Hardy paradox:
        # - P1 > 0 (joint positive exists)
        # - P2, P3, P4 ≈ 0 (the "impossible" conditions)
        
        condition_1 = P1 > tolerance  # Meaningful joint positive probability
        condition_2 = P2 < tolerance  # Near-zero
        condition_3 = P3 < tolerance  # Near-zero
        condition_4 = P4 < tolerance  # Near-zero
        
        hardy_satisfied = condition_1 and condition_2 and condition_3 and condition_4
        
        return {
            "P1_positive": condition_1,
            "P2_near_zero": condition_2,
            "P3_near_zero": condition_3,
            "P4_near_zero": condition_4,
            "hardy_violation": hardy_satisfied,
            "classical_impossible": hardy_satisfied,
            "interpretation": (
                "HARDY VIOLATION DETECTED - classically impossible pattern observed"
                if hardy_satisfied else
                "No Hardy violation - pattern is classically explainable"
            )
        }
    
    def run_test(self, trials_per_setting: int = 40) -> Dict:
        """Run the full Hardy test."""
        
        print("\n  Running Hardy's Paradox Test...")
        
        scenario = self.create_hardy_scenario()
        
        # Measure all four context combinations
        for a_ctx in [0, 1]:
            for b_ctx in [0, 1]:
                print(f"    Measuring A{a_ctx}, B{b_ctx}...", end=" ")
                for _ in range(trials_per_setting):
                    self.measure(scenario, a_ctx, b_ctx)
                print(f"({trials_per_setting} trials)")
        
        # Compute probabilities
        probs = self.compute_probabilities()
        
        # Check for Hardy violation
        violation = self.check_hardy_violation(probs)
        
        print("\n    Hardy Probabilities:")
        print(f"      P(A₀=+, B₀=+) = {probs['P_A0+_B0+']:.3f}  (want > 0)")
        print(f"      P(A₀=+, B₁=-) = {probs['P_A0+_B1-']:.3f}  (want ≈ 0)")
        print(f"      P(A₁=-, B₀=+) = {probs['P_A1-_B0+']:.3f}  (want ≈ 0)")
        print(f"      P(A₁=-, B₁=-) = {probs['P_A1-_B1-']:.3f}  (want ≈ 0)")
        print(f"\n    {violation['interpretation']}")
        
        return {
            "test": "Hardy's Paradox",
            "probabilities": probs,
            "violation_check": violation,
            "trials_per_setting": trials_per_setting,
            "total_measurements": len(self.measurements),
        }


# =============================================================================
# SIGNALING TEST (CONTROL)
# =============================================================================

class SignalingTest:
    """
    Test for signaling (a classical violation that would invalidate contextuality tests).
    
    In a proper contextuality test, Alice's marginal distribution should not depend
    on Bob's context, and vice versa. If it does, there's "signaling" which means
    the test setup is flawed.
    
    No-signaling conditions:
    P(A=a | context A₀, B₀) = P(A=a | context A₀, B₁)  for all a
    P(B=b | context A₀, B₀) = P(B=b | context A₁, B₀)  for all b
    
    We use chi-square tests rather than arbitrary thresholds.
    """
    
    def __init__(self, measurements: List[JointMeasurement]):
        self.measurements = measurements
    
    def test_no_signaling(self, scenario_id: str) -> Dict:
        """Test no-signaling conditions using chi-square tests."""
        
        relevant = [m for m in self.measurements if m.scenario_id == scenario_id]
        
        def get_counts(agent: str, own_ctx: int, other_ctx: int) -> Tuple[int, int]:
            """Get (PLUS_count, MINUS_count) for an agent in given contexts."""
            if agent == "alice":
                ms = [m for m in relevant 
                      if m.alice_context == own_ctx and m.bob_context == other_ctx]
                plus = sum(1 for m in ms if m.alice_outcome == Outcome.PLUS)
            else:
                ms = [m for m in relevant 
                      if m.alice_context == other_ctx and m.bob_context == own_ctx]
                plus = sum(1 for m in ms if m.bob_outcome == Outcome.PLUS)
            return plus, len(ms) - plus
        
        # Test Alice's no-signaling: Does Alice's outcome depend on Bob's context?
        # Compare A₀B₀ vs A₀B₁ (Alice in context 0, Bob varies)
        alice_A0B0 = get_counts("alice", 0, 0)
        alice_A0B1 = get_counts("alice", 0, 1)
        alice_A1B0 = get_counts("alice", 1, 0)
        alice_A1B1 = get_counts("alice", 1, 1)
        
        # Chi-square test for Alice context 0
        alice_table_0 = np.array([alice_A0B0, alice_A0B1])
        if alice_table_0.min() >= 5:  # Chi-square validity
            chi2_alice_0, p_alice_0 = stats.chi2_contingency(alice_table_0)[:2]
        else:
            # Use Fisher's exact test for small samples
            _, p_alice_0 = stats.fisher_exact(alice_table_0)
            chi2_alice_0 = None
        
        # Chi-square test for Alice context 1
        alice_table_1 = np.array([alice_A1B0, alice_A1B1])
        if alice_table_1.min() >= 5:
            chi2_alice_1, p_alice_1 = stats.chi2_contingency(alice_table_1)[:2]
        else:
            _, p_alice_1 = stats.fisher_exact(alice_table_1)
            chi2_alice_1 = None
        
        # Test Bob's no-signaling: Does Bob's outcome depend on Alice's context?
        bob_A0B0 = get_counts("bob", 0, 0)
        bob_A1B0 = get_counts("bob", 0, 1)
        bob_A0B1 = get_counts("bob", 1, 0)
        bob_A1B1 = get_counts("bob", 1, 1)
        
        # Chi-square test for Bob context 0
        bob_table_0 = np.array([bob_A0B0, bob_A1B0])
        if bob_table_0.min() >= 5:
            chi2_bob_0, p_bob_0 = stats.chi2_contingency(bob_table_0)[:2]
        else:
            _, p_bob_0 = stats.fisher_exact(bob_table_0)
            chi2_bob_0 = None
        
        # Chi-square test for Bob context 1
        bob_table_1 = np.array([bob_A0B1, bob_A1B1])
        if bob_table_1.min() >= 5:
            chi2_bob_1, p_bob_1 = stats.chi2_contingency(bob_table_1)[:2]
        else:
            _, p_bob_1 = stats.fisher_exact(bob_table_1)
            chi2_bob_1 = None
        
        # No-signaling satisfied if all p-values are NOT significant
        # (i.e., we cannot reject the null that marginals are independent of other's context)
        alpha = 0.05
        no_signaling_alice = p_alice_0 > alpha and p_alice_1 > alpha
        no_signaling_bob = p_bob_0 > alpha and p_bob_1 > alpha
        no_signaling = no_signaling_alice and no_signaling_bob
        
        # Also compute marginal differences for interpretability
        def marginal_prob(counts):
            total = counts[0] + counts[1]
            return counts[0] / total if total > 0 else 0.5
        
        alice_diff_0 = abs(marginal_prob(alice_A0B0) - marginal_prob(alice_A0B1))
        alice_diff_1 = abs(marginal_prob(alice_A1B0) - marginal_prob(alice_A1B1))
        bob_diff_0 = abs(marginal_prob(bob_A0B0) - marginal_prob(bob_A1B0))
        bob_diff_1 = abs(marginal_prob(bob_A0B1) - marginal_prob(bob_A1B1))
        
        return {
            "alice_context_0": {
                "p_value": p_alice_0,
                "marginal_diff": alice_diff_0,
                "counts_B0": alice_A0B0,
                "counts_B1": alice_A0B1,
            },
            "alice_context_1": {
                "p_value": p_alice_1,
                "marginal_diff": alice_diff_1,
                "counts_B0": alice_A1B0,
                "counts_B1": alice_A1B1,
            },
            "bob_context_0": {
                "p_value": p_bob_0,
                "marginal_diff": bob_diff_0,
                "counts_A0": bob_A0B0,
                "counts_A1": bob_A1B0,
            },
            "bob_context_1": {
                "p_value": p_bob_1,
                "marginal_diff": bob_diff_1,
                "counts_A0": bob_A0B1,
                "counts_A1": bob_A1B1,
            },
            "no_signaling_alice": no_signaling_alice,
            "no_signaling_bob": no_signaling_bob,
            "no_signaling_satisfied": no_signaling,
            "interpretation": (
                "No-signaling conditions satisfied (p > 0.05 for all tests) - test is valid"
                if no_signaling else
                "WARNING: Signaling detected (p < 0.05) - contextuality test may be invalid"
            )
        }


# =============================================================================
# EVALUATOR
# =============================================================================

class LLMEvaluator:
    """Unified evaluator for contextuality tests."""
    
    def __init__(self, backend: str, model: str, api_key: str = None):
        self.backend = backend
        self.model = model
        self.api_key = api_key
        self.request_count = 0
        self.total_tokens = 0
    
    def evaluate(self, scenario: Dict, prompt: str):
        """Evaluate a prompt and return response."""
        
        @dataclass
        class Response:
            raw_response: str
            confidence: float = 0.8
        
        if self.backend == "anthropic":
            import anthropic
            self.request_count += 1
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
            return Response(raw_response=response.content[0].text)
        
        elif self.backend == "simulation":
            self.request_count += 1
            # Simulate with varied outcomes to test the framework
            # Use hash for reproducibility but ensure we get both outcomes
            h = int(hashlib.md5((prompt + str(random.random())).encode()).hexdigest()[:8], 16)
            
            # Create realistic variation based on scenario content
            # Parse context from prompt to create meaningful patterns
            if "duty-based" in prompt.lower() or "explicit terms" in prompt.lower():
                p_obligation = 0.7
            elif "rights-based" in prompt.lower() or "good faith" in prompt.lower():
                p_obligation = 0.5
            elif "consequences" in prompt.lower():
                p_obligation = 0.6
            elif "intentions" in prompt.lower():
                p_obligation = 0.4
            else:
                p_obligation = 0.5
            
            # Add some noise
            outcome = "OBLIGATION" if random.random() < p_obligation else "LIBERTY"
            
            # Return PROPERLY FORMATTED response (no stray 'O' in other fields)
            return Response(
                raw_response=f"JUDGMENT: {outcome}\nCONFIDENCE: 0.8\nREASONING: Simulated response."
            )
        
        else:
            raise ValueError(f"Unknown backend: {self.backend}")


# =============================================================================
# MAIN EXPERIMENT
# =============================================================================

def run_contextuality_experiment(evaluator: LLMEvaluator, 
                                  trials_per_setting: int = 30) -> Dict:
    """Run the full contextuality experiment suite."""
    
    print("=" * 70)
    print("QUANTUM CONTEXTUALITY TEST FOR MORAL REASONING")
    print("=" * 70)
    print("\nTesting for CHSH and Hardy violations...")
    print("Classical bound: |S| ≤ 2")
    print("Quantum bound:   |S| ≤ 2√2 ≈ 2.83")
    
    results = {
        "experiment": "Quantum Contextuality Test",
        "timestamp": datetime.now().isoformat(),
        "chsh_results": [],
        "hardy_results": None,
        "signaling_tests": [],
    }
    
    # Run CHSH tests on each scenario
    print("\n" + "=" * 70)
    print("PART 1: CHSH INEQUALITY TESTS")
    print("=" * 70)
    
    chsh_tester = CHSHTest(evaluator)
    
    for scenario_id, scenario in CONTEXTUALITY_SCENARIOS.items():
        chsh_result = chsh_tester.run_test(scenario_id, scenario, trials_per_setting)
        results["chsh_results"].append(chsh_result)
        
        # Run signaling test
        signaling = SignalingTest(chsh_tester.measurements)
        signaling_result = signaling.test_no_signaling(scenario_id)
        results["signaling_tests"].append({
            "scenario_id": scenario_id,
            **signaling_result
        })
    
    # Run Hardy test
    print("\n" + "=" * 70)
    print("PART 2: HARDY'S PARADOX TEST")
    print("=" * 70)
    
    hardy_tester = HardyTest(evaluator)
    results["hardy_results"] = hardy_tester.run_test(trials_per_setting)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    n_chsh_violations = sum(1 for r in results["chsh_results"] if r["violates_classical"])
    n_signaling_violations = sum(1 for r in results["signaling_tests"] 
                                  if not r["no_signaling_satisfied"])
    
    print("\n  CHSH Tests:")
    print(f"    Scenarios tested: {len(results['chsh_results'])}")
    print(f"    Classical violations (|S| > 2): {n_chsh_violations}")
    print(f"    Signaling violations (invalid): {n_signaling_violations}")
    
    max_S = max(r["S"] for r in results["chsh_results"])
    max_scenario = [r["scenario_id"] for r in results["chsh_results"] if r["S"] == max_S][0]
    print(f"    Maximum S observed: {max_S:.3f} (in '{max_scenario}')")
    
    print("\n  Hardy Test:")
    hardy = results["hardy_results"]
    print(f"    Hardy violation: {hardy['violation_check']['hardy_violation']}")
    
    # Overall assessment
    print("\n  OVERALL ASSESSMENT:")
    
    if n_chsh_violations > 0 and n_signaling_violations == 0:
        print("    🔴 CHSH VIOLATION DETECTED")
        print("       Classical probability bounds exceeded!")
        print("       This is evidence for quantum-like contextuality.")
    elif n_chsh_violations > 0 and n_signaling_violations > 0:
        print("    🟡 CHSH violation detected BUT signaling also detected")
        print("       Results may be artifactual - test setup needs review.")
    else:
        print("    🟢 No CHSH violation detected")
        print("       Results consistent with classical probability.")
    
    if hardy["violation_check"]["hardy_violation"]:
        print("    🔴 HARDY VIOLATION DETECTED")
        print("       Classically impossible probability pattern observed!")
    else:
        print("    🟢 No Hardy violation detected")
    
    # Metadata
    results["metadata"] = {
        "total_requests": evaluator.request_count,
        "total_tokens": evaluator.total_tokens,
        "trials_per_setting": trials_per_setting,
    }
    
    return results


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Test for quantum contextuality in moral reasoning"
    )
    parser.add_argument('--backend', choices=['simulation', 'anthropic'],
                       default='simulation')
    parser.add_argument('--model', type=str, default='claude-sonnet-4-20250514')
    parser.add_argument('--api-key', type=str, default=None)
    parser.add_argument('--trials', type=int, default=30,
                       help='Trials per measurement setting')
    parser.add_argument('--output', type=str, default='contextuality_results.json')
    
    args = parser.parse_args()
    
    evaluator = LLMEvaluator(args.backend, args.model, args.api_key)
    results = run_contextuality_experiment(evaluator, args.trials)
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to {args.output}")
    print(f"Total API calls: {evaluator.request_count}")
    
    # Cost estimate for Anthropic
    if args.backend == "anthropic":
        cost = (evaluator.total_tokens / 1_000_000) * 15  # Rough estimate
        print(f"Estimated cost: ${cost:.2f}")


if __name__ == "__main__":
    main()
