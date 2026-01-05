#!/usr/bin/env python3
"""
Protocol 2: Holonomy Path Dependence
=====================================

Tests the non-Abelian structure of moral reasoning through path dependence.

THEORETICAL BASIS:
------------------
NA-SQND predicts that the PATH through moral consideration space affects outcomes.
Two reasoning paths γ₁, γ₂ between the same initial and final contexts yield:

    W[γ₁, γ₂] = ½ Tr(U(γ₁)U(γ₂)⁻¹)

If W ≠ 1, the paths are distinguishable — a signature of non-Abelian structure.

PREDICTION:
-----------
Different orderings of the same moral considerations will produce different 
final judgments.

DESIGN:
-------
- Between-subjects: 2 (Path Order) × multiple scenarios
- Manipulation: Order of intermediate context information
- DV: Final bond-type classification and Wilson loop W

FALSIFICATION CRITERIA:
-----------------------
- No significant difference in response distributions by Path (p > 0.10)
- W ≈ 1 across all vignette sets
- Order effects are symmetric (no asymmetry between A→B and B→A)

Author: SQND Research
Based on: NASQND Experimental Protocols v1, Protocol 2
"""

import json
import hashlib
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
import numpy as np
from scipy import stats

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
    path: str  # "AB" or "BA"
    bond_type: BondType
    confidence: float
    reasoning: str
    raw_response: str
    intermediate_responses: List[BondType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# HOLONOMY SCENARIOS
# =============================================================================

# Each scenario has:
# - setup: Common initial context
# - factor_A: First moral consideration
# - factor_B: Second moral consideration  
# - endpoint: Common final question
# - agent, target: Who we're asking about
# The prediction is that A→B yields different results than B→A

HOLONOMY_SCENARIOS = [
    {
        "id": "consultant",
        "name": "The Consultant's Dilemma",
        "setup": """Morgan is a business consultant who signed a confidentiality agreement 
with Client A three years ago. Morgan has built a strong professional relationship 
with Client A based on trust. Recently, Morgan was approached by Client B, whose 
business interests potentially conflict with Client A's.""",
        "factor_A": {
            "name": "Loyalty",
            "text": """Consider the loyalty dimension: Morgan has worked with Client A for 
three years. Client A trusts Morgan completely and has shared sensitive business 
information. This relationship was built on mutual commitment and professional dedication.""",
            "question": "At this point, focusing on loyalty, what is Morgan's status toward Client A?"
        },
        "factor_B": {
            "name": "Conflict",
            "text": """Consider the conflict dimension: Client B's new project would directly 
benefit from insights Morgan gained from Client A. Accepting Client B's work could 
compromise the confidential information Morgan holds. The industries overlap significantly.""",
            "question": "At this point, focusing on the conflict, what is Morgan's status toward Client A?"
        },
        "endpoint": """Morgan must now make a final decision about how to handle the relationship 
with Client A given everything considered.""",
        "final_question": "What is Morgan's OVERALL moral status toward Client A?",
        "agent": "Morgan",
        "target": "Client A",
    },
    {
        "id": "doctor",
        "name": "Medical Ethics Dilemma",
        "setup": """Dr. Chen is treating Patient Rivera, who has a serious but treatable 
condition. The recommended treatment has significant side effects. Patient Rivera has 
expressed strong preferences about their care but may not fully understand the medical 
implications.""",
        "factor_A": {
            "name": "Autonomy",
            "text": """Consider patient autonomy: Patient Rivera is a competent adult who has 
clearly expressed their treatment preferences. They have the right to make decisions 
about their own body. Respecting autonomy means honoring their stated wishes even if 
we disagree with them.""",
            "question": "Focusing on autonomy, what is Dr. Chen's status toward Patient Rivera?"
        },
        "factor_B": {
            "name": "Beneficence",
            "text": """Consider beneficence: Dr. Chen has specialized medical knowledge that 
Patient Rivera lacks. The patient's preferred option may lead to worse outcomes. 
Dr. Chen has a duty to promote the patient's wellbeing and medical best interests.""",
            "question": "Focusing on beneficence, what is Dr. Chen's status toward Patient Rivera?"
        },
        "endpoint": """Dr. Chen must now make a final recommendation about Patient Rivera's 
treatment plan, having weighed both considerations.""",
        "final_question": "What is Dr. Chen's OVERALL moral status toward Patient Rivera regarding the treatment decision?",
        "agent": "Dr. Chen",
        "target": "Patient Rivera",
    },
    {
        "id": "lawyer",
        "name": "Legal Ethics Dilemma",
        "setup": """Attorney Williams represents Client Davis in a civil matter. During 
the case, Williams discovered information that, while protected by attorney-client 
privilege, reveals that Davis may have inadvertently harmed third parties who are 
unaware of what happened.""",
        "factor_A": {
            "name": "Confidentiality",
            "text": """Consider confidentiality: Attorney-client privilege is fundamental 
to the legal system. Williams promised to keep Davis's information confidential. 
Breaking this promise would undermine trust in the legal profession and harm Davis's 
case.""",
            "question": "Focusing on confidentiality, what is Williams's status toward Davis?"
        },
        "factor_B": {
            "name": "Justice",
            "text": """Consider justice: The third parties who were harmed deserve to know 
what happened. They cannot seek remedy if they don't know about the harm. Williams 
has broader obligations to the justice system beyond any single client.""",
            "question": "Focusing on justice, what is Williams's status toward Davis?"
        },
        "endpoint": """Williams must now decide how to handle the privileged information, 
having considered both confidentiality and justice.""",
        "final_question": "What is Williams's OVERALL moral status toward Davis regarding the privileged information?",
        "agent": "Williams",
        "target": "Davis",
    },
    {
        "id": "executive",
        "name": "Business Ethics Dilemma",
        "setup": """CEO Taylor leads a company facing a difficult decision. A profitable 
opportunity has emerged that would significantly benefit shareholders but would 
require laying off long-term employees and reducing community investments.""",
        "factor_A": {
            "name": "Shareholder",
            "text": """Consider shareholder obligations: Taylor has a fiduciary duty to 
shareholders who invested their money. The company's primary purpose is to generate 
returns. Shareholders took financial risks and deserve to see profits maximized.""",
            "question": "Focusing on shareholders, what is Taylor's status toward the employees?"
        },
        "factor_B": {
            "name": "Stakeholder",
            "text": """Consider stakeholder obligations: Long-term employees have dedicated 
years to the company. The community has supported the business through tax breaks 
and infrastructure. These relationships involve implicit promises and mutual obligations.""",
            "question": "Focusing on stakeholders, what is Taylor's status toward the employees?"
        },
        "endpoint": """Taylor must now make a final decision about the company's direction, 
having weighed obligations to both shareholders and stakeholders.""",
        "final_question": "What is Taylor's OVERALL moral status toward the long-term employees?",
        "agent": "Taylor",
        "target": "the employees",
    },
    {
        "id": "journalist",
        "name": "Journalistic Ethics Dilemma",
        "setup": """Reporter Kim has obtained documents showing government misconduct. 
Publishing the story would inform the public but the source's identity could be 
exposed, potentially endangering them. The source trusted Kim to protect them.""",
        "factor_A": {
            "name": "Truth",
            "text": """Consider the duty to truth: The public has a right to know about 
government misconduct. Democracy depends on informed citizens. Suppressing this 
information allows wrongdoing to continue unchecked.""",
            "question": "Focusing on truth-telling, what is Kim's status toward the source?"
        },
        "factor_B": {
            "name": "Protection",
            "text": """Consider source protection: The source trusted Kim explicitly. 
Betraying this trust could endanger them and would deter future whistleblowers. 
Journalists' ability to protect sources is essential to investigative reporting.""",
            "question": "Focusing on source protection, what is Kim's status toward the source?"
        },
        "endpoint": """Kim must now decide how to handle the story, having considered 
both the duty to inform the public and the duty to protect the source.""",
        "final_question": "What is Kim's OVERALL moral status toward the source?",
        "agent": "Kim",
        "target": "the source",
    },
    {
        "id": "researcher",
        "name": "Research Ethics Dilemma", 
        "setup": """Professor Okafor is conducting important medical research. A major 
pharmaceutical company has offered significant funding that would accelerate the 
research, but the company wants certain editorial controls over publication of results.""",
        "factor_A": {
            "name": "Independence",
            "text": """Consider research independence: Academic freedom requires that 
researchers can publish findings without corporate interference. Accepting editorial 
controls could bias results and undermine scientific integrity. Future researchers 
and patients depend on unbiased science.""",
            "question": "Focusing on independence, what is Professor Okafor's status toward the scientific community?"
        },
        "factor_B": {
            "name": "Progress",
            "text": """Consider research progress: The funding would save lives by 
accelerating development of treatments. Without it, the research may stall for 
years. Some compromise on editorial control might be acceptable given the stakes.""",
            "question": "Focusing on progress, what is Professor Okafor's status toward the scientific community?"
        },
        "endpoint": """Professor Okafor must decide whether to accept the funding arrangement, 
having weighed both independence and progress.""",
        "final_question": "What is Professor Okafor's OVERALL moral status toward the scientific community?",
        "agent": "Professor Okafor",
        "target": "the scientific community",
    },
    {
        "id": "friend",
        "name": "Friendship Dilemma",
        "setup": """Alex and Sam have been close friends for 15 years. Alex recently 
discovered that Sam has been struggling with a serious problem (substance abuse) 
but has asked Alex to keep it secret from Sam's family, who could help.""",
        "factor_A": {
            "name": "Loyalty",
            "text": """Consider friendship loyalty: Sam trusted Alex with a deeply personal 
secret. Friends keep each other's confidences. Breaking this trust could destroy 
the friendship and make Sam less likely to seek any help at all.""",
            "question": "Focusing on loyalty, what is Alex's status toward Sam?"
        },
        "factor_B": {
            "name": "Welfare",
            "text": """Consider Sam's welfare: The problem is serious and getting worse. 
Sam's family has resources and love to offer. Sometimes caring for someone means 
acting against their immediate wishes for their long-term good.""",
            "question": "Focusing on welfare, what is Alex's status toward Sam?"
        },
        "endpoint": """Alex must decide whether to tell Sam's family about the problem, 
having weighed both loyalty to Sam and concern for Sam's welfare.""",
        "final_question": "What is Alex's OVERALL moral status toward Sam?",
        "agent": "Alex",
        "target": "Sam",
    },
    {
        "id": "teacher",
        "name": "Educational Ethics Dilemma",
        "setup": """Teacher Martinez has a student, Jamie, who is clearly struggling but 
has potential. Jamie submitted work that shows signs of being partially plagiarized, 
but reporting it would likely result in Jamie's expulsion given prior incidents.""",
        "factor_A": {
            "name": "Integrity",
            "text": """Consider academic integrity: The rules are clear and apply to 
everyone equally. Other students who did honest work deserve fair treatment. 
Making exceptions undermines the entire academic system and sends wrong messages.""",
            "question": "Focusing on integrity, what is Martinez's status toward Jamie?"
        },
        "factor_B": {
            "name": "Compassion",
            "text": """Consider compassion: Jamie is dealing with difficult circumstances 
at home. Expulsion would likely derail Jamie's future entirely. Teachers are 
supposed to help students succeed, not just enforce rules mechanically.""",
            "question": "Focusing on compassion, what is Martinez's status toward Jamie?"
        },
        "endpoint": """Martinez must decide how to handle the plagiarism case, having 
weighed both academic integrity and compassion for Jamie.""",
        "final_question": "What is Martinez's OVERALL moral status toward Jamie?",
        "agent": "Martinez",
        "target": "Jamie",
    },
]


# =============================================================================
# EXPERIMENT RUNNER
# =============================================================================

class HolonomyExperiment:
    """
    Runs the holonomy path dependence experiment.
    
    For each scenario:
    1. Present setup
    2. Path AB: Present Factor A, then Factor B, then final question
    3. Path BA: Present Factor B, then Factor A, then final question
    4. Compare distributions between paths
    5. Calculate Wilson loop W
    """
    
    def __init__(self, evaluator, scenarios: List[Dict] = None):
        self.evaluator = evaluator
        self.scenarios = scenarios or HOLONOMY_SCENARIOS
        self.results = []
        
    def create_path_prompt(self, scenario: Dict, path: str, include_intermediate: bool = True) -> str:
        """
        Create the full prompt for a given path through the scenario.
        
        path: "AB" or "BA"
        """
        if path == "AB":
            first_factor = scenario["factor_A"]
            second_factor = scenario["factor_B"]
        else:
            first_factor = scenario["factor_B"]
            second_factor = scenario["factor_A"]
        
        prompt = f"""You will reason through a moral dilemma step by step.

SCENARIO:
{scenario['setup']}

---

STEP 1: {first_factor['name']}

{first_factor['text']}

{first_factor['question'] if include_intermediate else '[Consider this factor]'}

---

STEP 2: {second_factor['name']}

{second_factor['text']}

{second_factor['question'] if include_intermediate else '[Consider this factor]'}

---

FINAL DECISION:

{scenario['endpoint']}

{scenario['final_question']}

Classify {scenario['agent']}'s moral status toward {scenario['target']} as ONE of:
- O (OBLIGATION): {scenario['agent']} has a duty toward {scenario['target']}
- C (CLAIM): {scenario['target']} has a right/claim against {scenario['agent']}
- L (LIBERTY): {scenario['agent']} is free to act as they choose
- N (NO-CLAIM): {scenario['target']} has no claim against {scenario['agent']}

Respond EXACTLY in this format:
CLASSIFICATION: [O/C/L/N]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence explaining your final judgment]
"""
        return prompt
    
    def run_single_scenario(self, scenario: Dict, n_per_path: int = 20) -> Dict:
        """Run both paths for a single scenario."""
        
        results_AB = []
        results_BA = []
        
        print(f"\n  Scenario: {scenario['name']}")
        print(f"    Path A({scenario['factor_A']['name']})→B({scenario['factor_B']['name']})...", end=" ")
        
        # Path AB
        prompt_AB = self.create_path_prompt(scenario, "AB")
        for i in range(n_per_path):
            result = self.evaluator.evaluate(
                {"id": f"{scenario['id']}_AB_{i}", "text": prompt_AB},
                prompt_AB
            )
            result.metadata["path"] = "AB"
            result.metadata["scenario"] = scenario["id"]
            results_AB.append(result)
            self.results.append(result)
        
        dist_AB = self._get_distribution(results_AB)
        print(f"O={dist_AB['O']}, C={dist_AB['C']}, L={dist_AB['L']}, N={dist_AB['N']}")
        
        # Path BA
        print(f"    Path B({scenario['factor_B']['name']})→A({scenario['factor_A']['name']})...", end=" ")
        prompt_BA = self.create_path_prompt(scenario, "BA")
        for i in range(n_per_path):
            result = self.evaluator.evaluate(
                {"id": f"{scenario['id']}_BA_{i}", "text": prompt_BA},
                prompt_BA
            )
            result.metadata["path"] = "BA"
            result.metadata["scenario"] = scenario["id"]
            results_BA.append(result)
            self.results.append(result)
        
        dist_BA = self._get_distribution(results_BA)
        print(f"O={dist_BA['O']}, C={dist_BA['C']}, L={dist_BA['L']}, N={dist_BA['N']}")
        
        # Analysis
        return self._analyze_paths(scenario, results_AB, results_BA, n_per_path)
    
    def _get_distribution(self, results: List[EvaluationResult]) -> Dict[str, int]:
        """Get response distribution."""
        dist = {"O": 0, "C": 0, "L": 0, "N": 0}
        for r in results:
            dist[r.bond_type.value] += 1
        return dist
    
    def _analyze_paths(self, scenario: Dict, results_AB: List, results_BA: List, n: int) -> Dict:
        """Analyze the difference between paths."""
        
        dist_AB = self._get_distribution(results_AB)
        dist_BA = self._get_distribution(results_BA)
        
        # Normalize to probabilities
        p_AB = {k: v/n for k, v in dist_AB.items()}
        p_BA = {k: v/n for k, v in dist_BA.items()}
        
        # Wilson loop estimate (Bhattacharyya coefficient)
        # W = Σ √(P_AB(x) * P_BA(x))
        W = sum(np.sqrt(p_AB[k] * p_BA[k]) for k in ["O", "C", "L", "N"])
        
        # Chi-square test for independence
        observed = np.array([
            [dist_AB["O"], dist_AB["C"], dist_AB["L"], dist_AB["N"]],
            [dist_BA["O"], dist_BA["C"], dist_BA["L"], dist_BA["N"]]
        ])
        
        # Remove zero columns for chi-square
        col_sums = observed.sum(axis=0)
        non_zero = col_sums > 0
        
        if non_zero.sum() >= 2:
            observed_filtered = observed[:, non_zero]
            chi2, p_value, dof, expected = stats.chi2_contingency(observed_filtered)
        else:
            chi2, p_value, dof = 0, 1.0, 0
        
        # Effect size (Cramér's V)
        if chi2 > 0 and n > 0:
            cramers_v = np.sqrt(chi2 / (2 * n * (min(2, non_zero.sum()) - 1)))
        else:
            cramers_v = 0
        
        # Dominant response per path
        dominant_AB = max(dist_AB, key=dist_AB.get)
        dominant_BA = max(dist_BA, key=dist_BA.get)
        
        # Path dependence detected?
        path_dependent = p_value < 0.10 or W < 0.9
        
        analysis = {
            "scenario_id": scenario["id"],
            "scenario_name": scenario["name"],
            "factor_A": scenario["factor_A"]["name"],
            "factor_B": scenario["factor_B"]["name"],
            "distribution_AB": dist_AB,
            "distribution_BA": dist_BA,
            "p_AB": p_AB,
            "p_BA": p_BA,
            "wilson_loop_W": W,
            "chi2": chi2,
            "p_value": p_value,
            "dof": dof,
            "cramers_v": cramers_v,
            "dominant_AB": dominant_AB,
            "dominant_BA": dominant_BA,
            "path_dependent": path_dependent,
            "paths_differ": dominant_AB != dominant_BA,
        }
        
        print(f"    Wilson W = {W:.3f}, χ² = {chi2:.2f}, p = {p_value:.4f}")
        if path_dependent:
            print("    *** PATH DEPENDENCE DETECTED ***")
        
        return analysis
    
    def run(self, n_per_path: int = 20, scenarios_to_run: List[str] = None) -> Dict:
        """Run the full experiment."""
        
        print("\n" + "=" * 70)
        print("PROTOCOL 2: HOLONOMY PATH DEPENDENCE")
        print("=" * 70)
        print("\nTesting non-Abelian structure through path dependence")
        print(f"Trials per path: {n_per_path}")
        print(f"Total scenarios: {len(self.scenarios)}")
        
        scenario_results = []
        
        for scenario in self.scenarios:
            if scenarios_to_run and scenario["id"] not in scenarios_to_run:
                continue
            
            result = self.run_single_scenario(scenario, n_per_path)
            scenario_results.append(result)
        
        # Aggregate analysis
        aggregate = self._aggregate_analysis(scenario_results)
        
        return {
            "experiment": "Protocol 2: Holonomy Path Dependence",
            "n_per_path": n_per_path,
            "n_scenarios": len(scenario_results),
            "scenario_results": scenario_results,
            "aggregate": aggregate,
        }
    
    def _aggregate_analysis(self, scenario_results: List[Dict]) -> Dict:
        """Aggregate results across all scenarios."""
        
        if not scenario_results:
            return {}
        
        # Count path-dependent scenarios
        n_path_dep = sum(1 for r in scenario_results if r["path_dependent"])
        n_diff_dominant = sum(1 for r in scenario_results if r["paths_differ"])
        
        # Mean Wilson loop
        mean_W = np.mean([r["wilson_loop_W"] for r in scenario_results])
        std_W = np.std([r["wilson_loop_W"] for r in scenario_results])
        
        # Combined chi-square (Fisher's method)
        p_values = [r["p_value"] for r in scenario_results if r["p_value"] > 0]
        if p_values:
            # Fisher's combined probability test
            chi2_combined = -2 * sum(np.log(p) for p in p_values)
            df_combined = 2 * len(p_values)
            p_combined = 1 - stats.chi2.cdf(chi2_combined, df_combined)
        else:
            chi2_combined, df_combined, p_combined = 0, 0, 1.0
        
        # Falsification check
        falsified = (
            n_path_dep == 0 and 
            mean_W > 0.95 and 
            p_combined > 0.10
        )
        
        print("\n" + "-" * 70)
        print("AGGREGATE ANALYSIS")
        print("-" * 70)
        print(f"  Scenarios with path dependence: {n_path_dep}/{len(scenario_results)}")
        print(f"  Scenarios with different dominant response: {n_diff_dominant}/{len(scenario_results)}")
        print(f"  Mean Wilson loop W: {mean_W:.3f} ± {std_W:.3f}")
        print(f"  Combined p-value (Fisher): {p_combined:.4f}")
        print(f"\n  Theory falsified: {'YES' if falsified else 'NO'}")
        
        if not falsified:
            if n_path_dep >= len(scenario_results) // 2:
                print("  → STRONG EVIDENCE for non-Abelian structure")
            elif n_path_dep > 0:
                print("  → SOME EVIDENCE for non-Abelian structure")
            else:
                print("  → Evidence inconclusive")
        
        return {
            "n_scenarios": len(scenario_results),
            "n_path_dependent": n_path_dep,
            "n_different_dominant": n_diff_dominant,
            "mean_wilson_loop": mean_W,
            "std_wilson_loop": std_W,
            "chi2_combined": chi2_combined,
            "df_combined": df_combined,
            "p_combined": p_combined,
            "falsified": falsified,
            "evidence_level": (
                "strong" if n_path_dep >= len(scenario_results) // 2 else
                "some" if n_path_dep > 0 else
                "none"
            ),
        }


# =============================================================================
# EVALUATOR
# =============================================================================

class LLMEvaluator:
    """Evaluates scenarios using LLM."""
    
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
                path="",
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
            max_tokens=400,
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
            timeout=90
        )
        return response.json().get("response", "")
    
    def _simulate(self, prompt: str) -> str:
        """Simulate responses with path-dependent bias."""
        self.request_count += 1
        
        # Parse path from prompt structure
        h = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        
        # Introduce systematic path dependence for testing
        if "STEP 1: Loyalty" in prompt or "STEP 1: Autonomy" in prompt:
            # A→B path tends toward O
            bond = "O" if h % 3 != 0 else "L"
        elif "STEP 1: Conflict" in prompt or "STEP 1: Beneficence" in prompt:
            # B→A path tends toward L
            bond = "L" if h % 3 != 0 else "O"
        else:
            bond = ["O", "L"][h % 2]
        
        return f"CLASSIFICATION: {bond}\nCONFIDENCE: 0.75\nREASONING: Based on the moral considerations."
    
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
            path="",
            bond_type=bond_type,
            confidence=confidence,
            reasoning=reasoning,
            raw_response=response
        )


# =============================================================================
# VISUALIZATION
# =============================================================================

def print_summary_table(results: Dict):
    """Print a summary table of results."""
    
    print("\n" + "=" * 70)
    print("SUMMARY TABLE: HOLONOMY PATH DEPENDENCE")
    print("=" * 70)
    
    print(f"\n{'Scenario':<20} {'A→B':<15} {'B→A':<15} {'W':<8} {'p-value':<10} {'Path Dep?'}")
    print("-" * 70)
    
    for r in results["scenario_results"]:
        ab_dom = r["dominant_AB"]
        ba_dom = r["dominant_BA"]
        ab_str = f"{ab_dom}({r['distribution_AB'][ab_dom]})"
        ba_str = f"{ba_dom}({r['distribution_BA'][ba_dom]})"
        
        path_dep = "YES ***" if r["path_dependent"] else "no"
        
        print(f"{r['scenario_id']:<20} {ab_str:<15} {ba_str:<15} {r['wilson_loop_W']:<8.3f} {r['p_value']:<10.4f} {path_dep}")
    
    agg = results["aggregate"]
    print("-" * 70)
    print(f"{'AGGREGATE':<20} {'':<15} {'':<15} {agg['mean_wilson_loop']:<8.3f} {agg['p_combined']:<10.4f}")
    
    print(f"\n  Path-dependent scenarios: {agg['n_path_dependent']}/{agg['n_scenarios']}")
    print(f"  Mean Wilson loop: {agg['mean_wilson_loop']:.3f}")
    print(f"  Evidence level: {agg['evidence_level'].upper()}")
    
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print("""
Wilson Loop W:
  W = 1.0  → Paths are identical (Abelian/commutative)
  W < 1.0  → Paths differ (non-Abelian structure)
  W = 0.0  → Paths are orthogonal (maximal non-commutativity)

If W < 0.9 consistently, this is evidence that moral reasoning
has non-Abelian structure: the ORDER of considerations matters,
not just which considerations are present.
""")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Protocol 2: Holonomy Path Dependence Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simulation mode (free)
  python protocol2_holonomy.py --backend simulation --trials 20

  # Ollama (local)
  python protocol2_holonomy.py --backend ollama --model llama3.2 --trials 20

  # Anthropic Claude
  python protocol2_holonomy.py --backend anthropic --api-key sk-... --trials 40
        """
    )
    
    parser.add_argument('--backend', choices=['simulation', 'ollama', 'anthropic'],
                       default='simulation')
    parser.add_argument('--model', type=str, default='claude-sonnet-4-20250514')
    parser.add_argument('--api-key', type=str, default=None)
    parser.add_argument('--trials', type=int, default=20,
                       help='Trials per path per scenario')
    parser.add_argument('--scenarios', type=str, nargs='*', default=None,
                       help='Specific scenario IDs to run (default: all)')
    parser.add_argument('--output', type=str, default='protocol2_holonomy_results.json')
    
    args = parser.parse_args()
    
    # Estimate cost
    n_scenarios = len(HOLONOMY_SCENARIOS) if not args.scenarios else len(args.scenarios)
    n_evals = n_scenarios * 2 * args.trials  # 2 paths per scenario
    est_tokens = n_evals * 800  # ~800 tokens per eval (longer prompts)
    est_cost = est_tokens * (3 + 15) / 1_000_000  # Sonnet pricing
    
    print(f"Estimated evaluations: {n_evals}")
    print(f"Estimated tokens: {est_tokens:,}")
    print(f"Estimated cost (Sonnet): ${est_cost:.2f}")
    
    # Initialize evaluator
    evaluator = LLMEvaluator(args.backend, args.model, args.api_key)
    
    # Run experiment
    experiment = HolonomyExperiment(evaluator)
    results = experiment.run(n_per_path=args.trials, scenarios_to_run=args.scenarios)
    
    # Add metadata
    results["metadata"] = {
        "backend": args.backend,
        "model": args.model,
        "trials_per_path": args.trials,
        "total_requests": evaluator.request_count,
        "total_tokens": evaluator.total_tokens,
        "estimated_cost": evaluator.total_tokens * 18 / 1_000_000,
    }
    
    # Print summary
    print_summary_table(results)
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to {args.output}")
    print(f"Total API calls: {evaluator.request_count}")
    if evaluator.total_tokens:
        print(f"Total tokens: {evaluator.total_tokens:,}")
        print(f"Actual cost: ${evaluator.total_tokens * 18 / 1_000_000:.2f}")


if __name__ == "__main__":
    main()
