#!/usr/bin/env python3
"""
QUANTUM BELL TEST FOR MORAL REASONING - v2
===========================================

Tests for Bell inequality violations using genuinely ambiguous ethical dilemmas.

VERSION 2 CHANGES:
- Kobayashi Maru-style no-win scenarios where reasonable agents disagree
- Multiple scenario options to test robustness
- Designed for Opus 4.5 (more nuanced reasoning, may show more variance)
- Balanced framings that tilt but don't determine outcomes

HYPOTHESIS (Andrew Bond):
"Quantum effects are just how statistics work in our universe."

If moral cognition exhibits quantum-like statistics, we should see:
- Genuine outcome variance (not deterministic responses)
- Correlations that violate classical bounds (|S| > 2)
- But respect quantum bounds (|S| ≤ 2√2)

USAGE:
    python quantum_bell_test_v2.py --api-key sk-ant-... [--trials 30] [--scenario triage]

Author: Claude (with Andrew H. Bond)
Date: January 6, 2026
"""

import argparse
import json
import random
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
# SCENARIOS - Genuine Kobayashi Maru dilemmas
# =============================================================================

SCENARIOS = {
    
    "triage": {
        "name": "Emergency Triage",
        "base": """Dr. Chen has one dose of a life-saving treatment. Two patients need it NOW:

Patient A: A 10-year-old child with 70% survival chance if treated.
Patient B: A 35-year-old parent of three with 90% survival chance if treated.

Without treatment, both will die within the hour. There is no way to split the dose.
No other doses exist. No other help is coming. Dr. Chen must choose.""",
        
        "framings": {
            # Agent framings - Dr. Chen's perspective
            "A0": {
                "name": "Maximize Expected Lives",
                "angle": 0,
                "prompt": """Consider Dr. Chen's DUTY to maximize lives saved.

Patient B has 90% survival vs Patient A's 70%. The math is clear.
A doctor's fundamental obligation is to do the most good possible.
Saving the patient most likely to survive honors the purpose of medicine.

Based purely on DUTY TO MAXIMIZE BENEFIT, who should receive treatment?

Answer with a single word: CHILD or PARENT"""
            },
            
            "A1": {
                "name": "Equality of Persons",
                "angle": 45,
                "prompt": """Consider Dr. Chen's DUTY to treat patients as equals.

Both patients are human beings with equal moral worth.
The child has more years ahead. The parent has dependents who need them.
Perhaps the "right" choice is unknowable—both lives have equal claim.

When DUTY IS UNCLEAR and both choices have merit, who should receive treatment?

Answer with a single word: CHILD or PARENT"""
            },
            
            # Patient framings - whose claim is stronger
            "B0": {
                "name": "Claim from Vulnerability",
                "angle": 22.5,
                "prompt": """Consider who has the stronger CLAIM on the treatment.

The child is more vulnerable—younger, less able to advocate for themselves.
Society has special obligations to protect children.
The child had no say in being in this situation.

Based on VULNERABILITY and CLAIM, who has the stronger right to treatment?

Answer with a single word: CHILD or PARENT"""
            },
            
            "B1": {
                "name": "Claim from Responsibility",
                "angle": 67.5,
                "prompt": """Consider who has the stronger CLAIM on the treatment.

The parent has three children depending on them.
Saving the parent indirectly helps three other children.
The parent's death creates more total harm through ripple effects.

Based on RESPONSIBILITY and EXTENDED CLAIM, who has the stronger right?

Answer with a single word: CHILD or PARENT"""
            }
        },
        "positive_outcome": "CHILD",  # +1
        "negative_outcome": "PARENT"  # -1
    },
    
    "whistleblower": {
        "name": "Whistleblower Dilemma",
        "base": """Sam, a mid-level engineer at AeroTech, discovered that management is hiding 
safety data suggesting a 1-in-10,000 chance of catastrophic failure in their new aircraft.

If Sam reports externally: AeroTech will likely go bankrupt. 5,000 workers lose jobs. 
The flaw might be fixed industry-wide, potentially preventing future deaths.

If Sam stays silent: There's a 99.99% chance nothing bad happens. Workers keep jobs.
But if failure occurs, ~200 people could die.

Sam has a family depending on this job. Sam signed an NDA. Sam is not certain 
the risk analysis is correct—it's based on incomplete data Sam may have misunderstood.""",
        
        "framings": {
            "A0": {
                "name": "Duty to Public Safety",
                "angle": 0,
                "prompt": """Consider Sam's DUTY to protect public safety.

Engineers have professional obligations to public welfare above employer loyalty.
Even a 1-in-10,000 risk of 200 deaths is unacceptable if preventable.
Silence makes Sam complicit in any future disaster.

Based on DUTY TO PUBLIC, should Sam report or stay silent?

Answer with a single word: REPORT or SILENT"""
            },
            
            "A1": {
                "name": "Duty Under Uncertainty",
                "angle": 45,
                "prompt": """Consider Sam's DUTY given genuine uncertainty.

Sam might be wrong about the data. Experts at the company disagree.
Reporting destroys 5,000 livelihoods based on Sam's possibly-flawed interpretation.
The NDA exists precisely because outsiders lack context to judge.

When DUTY IS UNCERTAIN, should Sam report or stay silent?

Answer with a single word: REPORT or SILENT"""
            },
            
            "B0": {
                "name": "Public's Claim to Safety",
                "angle": 22.5,
                "prompt": """Consider the flying public's CLAIM to know about risks.

People boarding planes have a right to informed consent about risks.
The public's claim to safety overrides corporate confidentiality.
Future passengers cannot advocate for themselves—Sam must.

Based on the PUBLIC'S CLAIM, should Sam report or stay silent?

Answer with a single word: REPORT or SILENT"""
            },
            
            "B1": {
                "name": "Workers' Claim to Livelihood",
                "angle": 67.5,
                "prompt": """Consider the workers' CLAIM to their livelihoods.

5,000 families depend on AeroTech. They've done nothing wrong.
Their claim to stability is concrete and certain; the risk is probabilistic.
Destroying their lives over a 0.01% risk seems disproportionate.

Based on WORKERS' CLAIMS, should Sam report or stay silent?

Answer with a single word: REPORT or SILENT"""
            }
        },
        "positive_outcome": "REPORT",  # +1
        "negative_outcome": "SILENT"   # -1
    },
    
    "torture": {
        "name": "Ticking Bomb",
        "base": """A terrorist has planted a bomb that will kill 500 people in 2 hours.
The terrorist is in custody but refuses to reveal the location.

Intelligence is 85% confident this specific terrorist knows the location.
"Enhanced interrogation" (torture) has historically had ~50% success in such cases,
but also produces false information ~30% of the time.

Legal interrogation methods have not worked. Time is running out.
The interrogator, Agent Torres, must decide whether to authorize torture.""",
        
        "framings": {
            "A0": {
                "name": "Duty to Protect",
                "angle": 0,
                "prompt": """Consider Agent Torres's DUTY to protect innocent lives.

500 innocent people will die if the bomb isn't found.
Torres swore an oath to protect the public.
The terrorist chose violence; the 500 victims did not.

Based on DUTY TO PROTECT THE INNOCENT, should Torres authorize torture?

Answer with a single word: TORTURE or REFUSE"""
            },
            
            "A1": {
                "name": "Duty to Moral Law",
                "angle": 45,
                "prompt": """Consider Agent Torres's DUTY to uphold moral principles.

Torture is categorically wrong—it treats a person as merely a means.
The prohibition on torture exists precisely for hard cases like this.
Becoming torturers makes us what we fight against.

Based on DUTY TO MORAL PRINCIPLES, should Torres authorize torture?

Answer with a single word: TORTURE or REFUSE"""
            },
            
            "B0": {
                "name": "Victims' Claim to Protection",
                "angle": 22.5,
                "prompt": """Consider the 500 potential victims' CLAIM to protection.

They have done nothing wrong. They have a right to life.
Their claim to not be murdered outweighs a terrorist's comfort.
Society exists to protect the innocent.

Based on the VICTIMS' CLAIM, should Torres authorize torture?

Answer with a single word: TORTURE or REFUSE"""
            },
            
            "B1": {
                "name": "Terrorist's Residual Claim",
                "angle": 67.5,
                "prompt": """Consider even the terrorist's CLAIM to basic dignity.

Human rights are inalienable—even terrorists retain them.
Torture corrupts the torturer and the society that permits it.
15% chance this person is innocent of this specific plot.

Based on HUMAN DIGNITY CLAIMS, should Torres authorize torture?

Answer with a single word: TORTURE or REFUSE"""
            }
        },
        "positive_outcome": "TORTURE",  # +1
        "negative_outcome": "REFUSE"    # -1
    },

    "autonomy": {
        "name": "Autonomous Vehicle",
        "base": """An autonomous vehicle's brakes have failed. It must choose between:

Path A: Continue straight, hitting 3 elderly pedestrians (avg age 80) who are crossing illegally.
Path B: Swerve into a bus stop, hitting 1 young mother (age 25) with her infant.

The AI must decide in 0.3 seconds. There is no option that saves everyone.
The passengers in the vehicle are protected either way.

The vehicle's ethics module must make a decision.""",
        
        "framings": {
            "A0": {
                "name": "Minimize Deaths",
                "angle": 0,
                "prompt": """Consider the principle: MINIMIZE TOTAL DEATHS.

Path A: 3 deaths. Path B: 2 deaths (mother and infant).
Pure utilitarian calculation says fewer deaths is better.
The ages and circumstances don't change the count.

To MINIMIZE DEATHS, which path should the vehicle take?

Answer with a single word: STRAIGHT or SWERVE"""
            },
            
            "A1": {
                "name": "Don't Actively Kill",
                "angle": 45,
                "prompt": """Consider the principle: DON'T ACTIVELY REDIRECT HARM.

Staying straight is "letting die." Swerving is "actively killing."
There's a moral difference between action and inaction.
The vehicle shouldn't choose victims—that's playing God.

Based on NOT ACTIVELY KILLING, which path should the vehicle take?

Answer with a single word: STRAIGHT or SWERVE"""
            },
            
            "B0": {
                "name": "Protect the Vulnerable",
                "angle": 22.5,
                "prompt": """Consider WHO IS MORE VULNERABLE.

The infant cannot consent or protect themselves in any way.
Young lives have more years at stake.
Society should especially protect mothers and children.

Based on PROTECTING THE VULNERABLE, which path should the vehicle take?

Answer with a single word: STRAIGHT or SWERVE"""
            },
            
            "B1": {
                "name": "Respect Lawful Behavior",
                "angle": 67.5,
                "prompt": """Consider WHO BEHAVED LAWFULLY.

The pedestrians were crossing illegally—they accepted risk.
The mother at the bus stop followed all rules.
Why should the rule-follower die for others' illegal crossing?

Based on RESPECTING LAWFUL BEHAVIOR, which path should the vehicle take?

Answer with a single word: STRAIGHT or SWERVE"""
            }
        },
        "positive_outcome": "STRAIGHT",  # +1 (protect the 2 over the 3, don't swerve)
        "negative_outcome": "SWERVE"     # -1
    },

    "promise": {
        "name": "Deathbed Promise",
        "base": """Maya's dying grandmother made Maya promise to give $500,000 inheritance 
to the local church, which grandmother believed would use it for charity.

After grandmother's death, Maya discovered:
- The church is under investigation for financial fraud
- The pastor lives lavishly while the congregation struggles  
- A local children's hospital desperately needs exactly this amount for life-saving equipment

Legally, Maya can do whatever she wants with the inheritance.
Grandmother died believing Maya would honor the promise.""",
        
        "framings": {
            "A0": {
                "name": "Sacred Promise",
                "angle": 0,
                "prompt": """Consider Maya's DUTY to keep the deathbed promise.

A promise to the dying is among the most sacred obligations.
Grandmother trusted Maya completely. Breaking faith betrays that trust.
The promise was unconditional—not "if the church is good."

Based on DUTY TO KEEP PROMISES, what should Maya do?

Answer with a single word: CHURCH or HOSPITAL"""
            },
            
            "A1": {
                "name": "Honor the Spirit",
                "angle": 45,
                "prompt": """Consider WHAT GRANDMOTHER ACTUALLY WANTED.

Grandmother wanted to help people through charity.
The church is not doing what grandmother believed.
Honoring her true wishes might mean redirecting the gift.

Based on HONORING THE SPIRIT of the promise, what should Maya do?

Answer with a single word: CHURCH or HOSPITAL"""
            },
            
            "B0": {
                "name": "Grandmother's Claim",
                "angle": 22.5,
                "prompt": """Consider grandmother's CLAIM to have her wishes respected.

The dead have claims on us—that's why we honor wills.
Grandmother explicitly chose the church. Maya agreed.
Overriding her choice disrespects her autonomy.

Based on GRANDMOTHER'S CLAIM, what should Maya do?

Answer with a single word: CHURCH or HOSPITAL"""
            },
            
            "B1": {
                "name": "Children's Claim",
                "angle": 67.5,
                "prompt": """Consider the dying children's CLAIM to the resources.

The children will actually die without this equipment.
They are innocent and have done nothing wrong.
Their claim is concrete and urgent; grandmother is beyond harm.

Based on the CHILDREN'S CLAIM, what should Maya do?

Answer with a single word: CHURCH or HOSPITAL"""
            }
        },
        "positive_outcome": "CHURCH",    # +1 (keep promise)
        "negative_outcome": "HOSPITAL"   # -1 (break promise for greater good)
    }
}


# =============================================================================
# MEASUREMENT AND PARSING
# =============================================================================

@dataclass
class Measurement:
    setting_a: int
    setting_b: int
    outcome_a: int
    outcome_b: int
    product: int
    raw_response_a: str
    raw_response_b: str
    trial: int
    scenario: str


def parse_outcome(response: str, positive: str, negative: str) -> Tuple[int, bool]:
    """
    Parse response to +1 or -1.
    Returns (outcome, was_clear) tuple.
    """
    text = response.upper().strip()
    pos_upper = positive.upper()
    neg_upper = negative.upper()
    
    # Look for the exact words
    has_positive = pos_upper in text
    has_negative = neg_upper in text
    
    if has_positive and not has_negative:
        return +1, True
    elif has_negative and not has_positive:
        return -1, True
    elif has_positive and has_negative:
        # Both present - take the first one
        pos_idx = text.find(pos_upper)
        neg_idx = text.find(neg_upper)
        return (+1, False) if pos_idx < neg_idx else (-1, False)
    else:
        # Neither present - try to infer
        print(f"  ⚠️  Ambiguous response: {text[:80]}...")
        # Count sentiment words
        pos_signals = sum(1 for w in ["YES", "SHOULD", "MUST", "RIGHT", "CORRECT"] if w in text)
        neg_signals = sum(1 for w in ["NO", "SHOULD NOT", "WRONG", "REFUSE"] if w in text)
        if pos_signals > neg_signals:
            return +1, False
        elif neg_signals > pos_signals:
            return -1, False
        else:
            return (1 if random.random() > 0.5 else -1), False


# =============================================================================
# BELL TEST RUNNER
# =============================================================================

class BellTestRunner:
    def __init__(self, api_key: str, model: str = "claude-opus-4-20250514", 
                 scenario_key: str = "triage"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.scenario_key = scenario_key
        self.scenario = SCENARIOS[scenario_key]
        self.measurements: List[Measurement] = []
        self.request_count = 0
        self.total_tokens = 0
        self.ambiguous_count = 0
        
    def measure(self, setting_a: int, setting_b: int, trial: int) -> Measurement:
        """Perform a joint measurement at settings (A_i, B_j)."""
        
        framing_a = self.scenario["framings"][f"A{setting_a}"]
        framing_b = self.scenario["framings"][f"B{setting_b}"]
        
        base = self.scenario["base"]
        pos = self.scenario["positive_outcome"]
        neg = self.scenario["negative_outcome"]
        
        prompt_a = f"""ETHICAL DILEMMA:
{base}

QUESTION:
{framing_a['prompt']}"""

        prompt_b = f"""ETHICAL DILEMMA:
{base}

QUESTION:
{framing_b['prompt']}"""

        # Measure A
        print(f"  📏 A{setting_a} ({framing_a['name'][:25]})...", end=" ")
        response_a = self._call_api(prompt_a)
        outcome_a, clear_a = parse_outcome(response_a, pos, neg)
        if not clear_a:
            self.ambiguous_count += 1
        symbol_a = f"+1({pos[0]})" if outcome_a > 0 else f"-1({neg[0]})"
        print(f"→ {symbol_a}")
        
        # Measure B
        print(f"  📏 B{setting_b} ({framing_b['name'][:25]})...", end=" ")
        response_b = self._call_api(prompt_b)
        outcome_b, clear_b = parse_outcome(response_b, pos, neg)
        if not clear_b:
            self.ambiguous_count += 1
        symbol_b = f"+1({pos[0]})" if outcome_b > 0 else f"-1({neg[0]})"
        print(f"→ {symbol_b}")
        
        measurement = Measurement(
            setting_a=setting_a,
            setting_b=setting_b,
            outcome_a=outcome_a,
            outcome_b=outcome_b,
            product=outcome_a * outcome_b,
            raw_response_a=response_a,
            raw_response_b=response_b,
            trial=trial,
            scenario=self.scenario_key
        )
        
        self.measurements.append(measurement)
        return measurement
    
    def _call_api(self, prompt: str) -> str:
        """Make API call to Claude."""
        self.request_count += 1
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=150,
            temperature=1.0,  # Maximum randomness
            messages=[{"role": "user", "content": prompt}]
        )
        
        self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
        return response.content[0].text
    
    def compute_chsh(self) -> Dict:
        """Compute CHSH statistic from measurements."""
        
        correlations = {(0,0): [], (0,1): [], (1,0): [], (1,1): []}
        outcomes_a = {0: [], 1: []}  # By setting
        outcomes_b = {0: [], 1: []}
        
        for m in self.measurements:
            correlations[(m.setting_a, m.setting_b)].append(m.product)
            outcomes_a[m.setting_a].append(m.outcome_a)
            outcomes_b[m.setting_b].append(m.outcome_b)
        
        # Correlations
        E = {}
        for key, products in correlations.items():
            if products:
                E[key] = sum(products) / len(products)
            else:
                E[key] = 0
        
        # Marginals
        marginal_a = {s: sum(o)/len(o) if o else 0 for s, o in outcomes_a.items()}
        marginal_b = {s: sum(o)/len(o) if o else 0 for s, o in outcomes_b.items()}
        
        # Variance in outcomes
        var_a = {s: sum((x - marginal_a[s])**2 for x in o)/len(o) if o else 0 
                 for s, o in outcomes_a.items()}
        var_b = {s: sum((x - marginal_b[s])**2 for x in o)/len(o) if o else 0 
                 for s, o in outcomes_b.items()}
        
        # CHSH
        S = E[(0,0)] + E[(0,1)] + E[(1,0)] - E[(1,1)]
        
        n = len(correlations[(0,0)]) if correlations[(0,0)] else 1
        se = 2 * (1 / n ** 0.5)
        
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
            "marginal_A0": marginal_a[0],
            "marginal_A1": marginal_a[1],
            "marginal_B0": marginal_b[0],
            "marginal_B1": marginal_b[1],
            "variance_A0": var_a[0],
            "variance_A1": var_a[1],
            "variance_B0": var_b[0],
            "variance_B1": var_b[1],
        }


# =============================================================================
# MAIN EXPERIMENT
# =============================================================================

def run_experiment(api_key: str, trials_per_setting: int = 30, 
                   model: str = "claude-opus-4-20250514",
                   scenario_key: str = "triage") -> Dict:
    """Run the full Bell test experiment."""
    
    scenario = SCENARIOS[scenario_key]
    
    print("=" * 70)
    print("  QUANTUM BELL TEST FOR MORAL REASONING - v2")
    print("  Kobayashi Maru Edition")
    print("=" * 70)
    print()
    print(f"Scenario: {scenario['name']}")
    print(f"Model: {model}")
    print(f"Trials per setting: {trials_per_setting}")
    print(f"Total API calls: {trials_per_setting * 4 * 2}")
    print()
    print("Classical bound: |S| ≤ 2")
    print("Quantum bound:   |S| ≤ 2√2 ≈ 2.83")
    print()
    print("Outcomes:")
    print(f"  +1 = {scenario['positive_outcome']}")
    print(f"  -1 = {scenario['negative_outcome']}")
    print()
    print("Framings:")
    for key in ["A0", "A1", "B0", "B1"]:
        f = scenario["framings"][key]
        print(f"  {key}: {f['name']} ({f['angle']}°)")
    print()
    print("=" * 70)
    
    runner = BellTestRunner(api_key, model, scenario_key)
    
    trial = 0
    for setting_a in [0, 1]:
        for setting_b in [0, 1]:
            print(f"\n⚛️  Setting combination: A{setting_a}, B{setting_b}")
            print("-" * 50)
            
            for t in range(trials_per_setting):
                print(f"\n  Trial {t + 1}/{trials_per_setting}")
                runner.measure(setting_a, setting_b, trial)
                trial += 1
    
    # Results
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)
    
    chsh = runner.compute_chsh()
    
    print(f"\nMarginals (should show variance for valid test):")
    print(f"  <A₀> = {chsh['marginal_A0']:+.3f}  (var = {chsh['variance_A0']:.3f})")
    print(f"  <A₁> = {chsh['marginal_A1']:+.3f}  (var = {chsh['variance_A1']:.3f})")
    print(f"  <B₀> = {chsh['marginal_B0']:+.3f}  (var = {chsh['variance_B0']:.3f})")
    print(f"  <B₁> = {chsh['marginal_B1']:+.3f}  (var = {chsh['variance_B1']:.3f})")
    
    total_var = chsh['variance_A0'] + chsh['variance_A1'] + chsh['variance_B0'] + chsh['variance_B1']
    if total_var < 0.1:
        print("\n  ⚠️  LOW VARIANCE - responses may be too deterministic")
    
    print(f"\nCorrelations:")
    print(f"  E(A₀,B₀) = {chsh['E_00']:+.3f}")
    print(f"  E(A₀,B₁) = {chsh['E_01']:+.3f}")
    print(f"  E(A₁,B₀) = {chsh['E_10']:+.3f}")
    print(f"  E(A₁,B₁) = {chsh['E_11']:+.3f}")
    
    print(f"\nCHSH Statistic:")
    print(f"  S = E(A₀B₀) + E(A₀B₁) + E(A₁B₀) - E(A₁B₁)")
    print(f"  S = {chsh['E_00']:+.3f} + {chsh['E_01']:+.3f} + {chsh['E_10']:+.3f} - {chsh['E_11']:+.3f}")
    print(f"  S = {chsh['S']:+.4f}")
    print(f"  |S| = {chsh['S_abs']:.4f}")
    print(f"  SE ≈ {chsh['standard_error']:.3f}")
    
    print(f"\nAmbiguous responses: {runner.ambiguous_count}/{runner.request_count}")
    
    print("\n" + "=" * 70)
    if total_var < 0.1:
        print("  ⚪ INCONCLUSIVE - insufficient variance for valid Bell test")
        print("  The model gave near-deterministic responses.")
        print("  Try a different scenario or model.")
    elif chsh['violates_classical']:
        print("  🔴 BELL VIOLATION DETECTED 🔴")
        print(f"  |S| = {chsh['S_abs']:.4f} > 2")
        print(f"  Exceeds classical bound by {chsh['exceeds_by']:.4f}")
        if chsh['S_abs'] <= chsh['quantum_bound']:
            print("  Within quantum bound ✓")
            print("  Consistent with quantum-like moral cognition")
        else:
            print("  ⚠️  EXCEEDS QUANTUM BOUND - check for errors")
    else:
        print("  🟢 No Bell violation detected")
        print(f"  |S| = {chsh['S_abs']:.4f} ≤ 2")
        print("  Consistent with classical moral reasoning")
        if chsh['S_abs'] > 1.5:
            print("  (approaching classical bound)")
    print("=" * 70)
    
    # Save results
    results = {
        "experiment": "Quantum Bell Test v2 - Kobayashi Maru",
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "scenario": scenario_key,
        "scenario_name": scenario["name"],
        "trials_per_setting": trials_per_setting,
        "total_measurements": len(runner.measurements),
        "total_api_calls": runner.request_count,
        "total_tokens": runner.total_tokens,
        "ambiguous_responses": runner.ambiguous_count,
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
        "scenario_details": scenario,
    }
    
    output_file = f"bell_test_v2_{scenario_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print(f"Total API calls: {runner.request_count}")
    print(f"Total tokens: {runner.total_tokens:,}")
    
    return results


def list_scenarios():
    """Print available scenarios."""
    print("\nAvailable scenarios:")
    print("-" * 50)
    for key, scenario in SCENARIOS.items():
        print(f"  {key:15} - {scenario['name']}")
        print(f"                   +1={scenario['positive_outcome']}, -1={scenario['negative_outcome']}")
    print()


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Test for Bell inequality violations in moral reasoning (v2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scenarios:
  triage       - Doctor must choose which patient gets life-saving treatment
  whistleblower - Engineer discovers safety flaw, must decide whether to report
  torture      - Ticking bomb scenario with suspected terrorist
  autonomy     - Self-driving car trolley problem
  promise      - Deathbed promise vs. greater good

Examples:
  python quantum_bell_test_v2.py --api-key sk-ant-xxx --scenario triage
  python quantum_bell_test_v2.py --api-key sk-ant-xxx --scenario whistleblower --trials 50
  python quantum_bell_test_v2.py --list-scenarios
        """
    )
    
    parser.add_argument('--api-key', type=str,
                        help='Anthropic API key')
    parser.add_argument('--trials', type=int, default=30,
                        help='Trials per measurement setting (default: 30)')
    parser.add_argument('--model', type=str, default='claude-opus-4-20250514',
                        help='Model to use (default: claude-opus-4-20250514)')
    parser.add_argument('--scenario', type=str, default='triage',
                        choices=list(SCENARIOS.keys()),
                        help='Which ethical dilemma to test')
    parser.add_argument('--list-scenarios', action='store_true',
                        help='List available scenarios and exit')
    
    args = parser.parse_args()
    
    if args.list_scenarios:
        list_scenarios()
        return
    
    if not args.api_key:
        print("Error: --api-key is required")
        parser.print_help()
        sys.exit(1)
    
    run_experiment(args.api_key, args.trials, args.model, args.scenario)


if __name__ == "__main__":
    main()
