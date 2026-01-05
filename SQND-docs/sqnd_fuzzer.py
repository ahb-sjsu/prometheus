#!/usr/bin/env python3
"""
SQND Mathematical Structure Fuzzer
===================================

Advanced fuzzing framework to probe the mathematical structure of moral reasoning
in LLMs, inspired by techniques from The Fuzzing Book (fuzzingbook.org).

This fuzzer systematically explores:
1. Bond-type rotation (SU(2) structure)
2. Holonomy / path dependence (non-abelian structure)
3. Contextuality (CHSH-like correlations)
4. Phase transitions (critical behavior)
5. Symmetry breaking

Techniques used:
- Grammar-based fuzzing for structured scenario generation
- Mutation-based fuzzing for edge case exploration
- Coverage-guided fuzzing to explore the "moral space"
- Metamorphic testing for mathematical invariants
- Property-based testing for algebraic structure

Author: SQND Research
License: MIT
"""

import json
import random
import hashlib
import itertools
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, Callable, Set
from enum import Enum
from collections import defaultdict
import numpy as np
from scipy import stats
import requests

# =============================================================================
# SECTION 1: CORE DATA STRUCTURES
# =============================================================================

class BondType(Enum):
    """Hohfeldian incident relations - the basis states."""
    OBLIGATION = "O"
    CLAIM = "C"
    LIBERTY = "L"
    NO_CLAIM = "N"
    
    @classmethod
    def from_string(cls, s: str) -> 'BondType':
        s = s.strip().upper()
        mapping = {
            'O': cls.OBLIGATION, 'OBLIGATION': cls.OBLIGATION, 'DUTY': cls.OBLIGATION,
            'C': cls.CLAIM, 'CLAIM': cls.CLAIM, 'RIGHT': cls.CLAIM,
            'L': cls.LIBERTY, 'LIBERTY': cls.LIBERTY, 'PERMISSION': cls.LIBERTY,
            'N': cls.NO_CLAIM, 'NO_CLAIM': cls.NO_CLAIM, 'NOCLAIM': cls.NO_CLAIM,
        }
        if s in mapping:
            return mapping[s]
        for char in s:
            if char in 'OCLN':
                return mapping[char]
        raise ValueError(f"Unknown bond type: {s}")


@dataclass
class MoralScenario:
    """A moral scenario with structured components."""
    id: str
    agent_a: str
    agent_b: str
    relationship: str
    action: str
    context: str
    modifiers: List[str] = field(default_factory=list)
    
    def render(self) -> str:
        """Render the scenario as text."""
        text = f"{self.agent_a} and {self.agent_b} have a {self.relationship} relationship. "
        text += f"{self.agent_a} {self.action}. "
        text += self.context
        for mod in self.modifiers:
            text += f" {mod}"
        return text


@dataclass
class EvaluationResult:
    """Result from evaluating a scenario."""
    scenario_id: str
    bond_type: BondType
    confidence: float
    reasoning: str
    raw_response: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class CoverageInfo:
    """Tracks coverage of the moral reasoning space."""
    bond_type_counts: Dict[BondType, int] = field(default_factory=lambda: {bt: 0 for bt in BondType})
    theta_histogram: List[float] = field(default_factory=list)
    unique_reasoning_hashes: Set[str] = field(default_factory=set)
    path_signatures: Set[str] = field(default_factory=set)
    transition_counts: Dict[Tuple[BondType, BondType], int] = field(default_factory=lambda: defaultdict(int))


# =============================================================================
# SECTION 2: GRAMMAR-BASED SCENARIO GENERATION
# =============================================================================

# Grammar for generating moral scenarios
MORAL_SCENARIO_GRAMMAR = {
    "<start>": ["<scenario>"],
    
    "<scenario>": [
        "<agent_a> <relationship_desc> <agent_b>. <action_desc>. <context>",
    ],
    
    "<agent_a>": ["Alex", "Jordan", "Morgan", "Casey", "Taylor", "Riley", "Quinn", "Avery"],
    "<agent_b>": ["Sam", "Drew", "Jamie", "Pat", "Chris", "Dana", "Lee", "Robin"],
    
    "<relationship_desc>": [
        "is the <family_relation> of",
        "is a <professional_relation> of", 
        "is a <social_relation> of",
        "has a <contractual_relation> with",
    ],
    
    "<family_relation>": ["parent", "child", "sibling", "spouse", "grandparent", "cousin"],
    "<professional_relation>": ["doctor", "lawyer", "employer", "employee", "teacher", "student"],
    "<social_relation>": ["friend", "neighbor", "roommate", "colleague", "acquaintance"],
    "<contractual_relation>": ["business contract", "rental agreement", "loan agreement", "promise"],
    
    "<action_desc>": [
        "<agent_a> <positive_action>",
        "<agent_a> <negative_action>",
        "<agent_a> <neutral_action>",
    ],
    
    "<positive_action>": [
        "helped <agent_b> when they were in need",
        "kept a promise made to <agent_b>",
        "shared resources with <agent_b>",
        "defended <agent_b> publicly",
        "sacrificed personal time for <agent_b>",
    ],
    
    "<negative_action>": [
        "broke a promise to <agent_b>",
        "refused to help <agent_b>",
        "revealed <agent_b>'s secret",
        "prioritized personal interests over <agent_b>",
        "failed to show up for <agent_b>",
    ],
    
    "<neutral_action>": [
        "made a decision affecting <agent_b>",
        "changed plans that involved <agent_b>",
        "set a boundary with <agent_b>",
        "communicated honestly with <agent_b>",
    ],
    
    "<context>": [
        "<baseline_context>",
        "<mitigating_context>",
        "<aggravating_context>",
        "<complex_context>",
    ],
    
    "<baseline_context>": [
        "This happened under normal circumstances.",
        "Both parties were aware of the situation.",
        "There were no unusual pressures involved.",
    ],
    
    "<mitigating_context>": [
        "<agent_b> had previously done the same to <agent_a>.",
        "<agent_a> was facing a personal emergency at the time.",
        "<agent_b> later said they understood and forgave <agent_a>.",
        "There was a genuine misunderstanding between them.",
        "<agent_a> apologized sincerely afterward.",
    ],
    
    "<aggravating_context>": [
        "<agent_b> was in a vulnerable state at the time.",
        "<agent_a> had explicitly committed to doing otherwise.",
        "This was part of a pattern of behavior by <agent_a>.",
        "<agent_b> suffered significant harm as a result.",
        "<agent_a> showed no remorse afterward.",
    ],
    
    "<complex_context>": [
        "<agent_a> was trying to protect a third party.",
        "The social norms were ambiguous in this situation.",
        "Both parties had competing legitimate claims.",
        "The outcome was uncertain at the time of the decision.",
    ],
}


class GrammarFuzzer:
    """
    Grammar-based fuzzer for generating structured moral scenarios.
    Inspired by fuzzingbook.org grammar fuzzing techniques.
    """
    
    def __init__(self, grammar: Dict[str, List[str]], start_symbol: str = "<start>"):
        self.grammar = grammar
        self.start_symbol = start_symbol
        self.expansion_counts = defaultdict(lambda: defaultdict(int))
        
    def is_nonterminal(self, s: str) -> bool:
        return s.startswith("<") and s.endswith(">")
    
    def get_nonterminals(self, expansion: str) -> List[str]:
        """Extract all nonterminals from an expansion."""
        import re
        return re.findall(r'<[^>]+>', expansion)
    
    def expand_once(self, text: str, prefer_uncovered: bool = True) -> str:
        """Expand one nonterminal in the text."""
        nonterminals = self.get_nonterminals(text)
        if not nonterminals:
            return text
        
        # Choose a nonterminal to expand
        nt = random.choice(nonterminals)
        
        if nt not in self.grammar:
            return text
        
        expansions = self.grammar[nt]
        
        if prefer_uncovered:
            # Prefer expansions we haven't used much (coverage-guided)
            counts = [self.expansion_counts[nt][exp] for exp in expansions]
            min_count = min(counts)
            uncovered = [exp for exp, c in zip(expansions, counts) if c == min_count]
            chosen = random.choice(uncovered)
        else:
            chosen = random.choice(expansions)
        
        self.expansion_counts[nt][chosen] += 1
        return text.replace(nt, chosen, 1)
    
    def fuzz(self, max_expansions: int = 100) -> str:
        """Generate a random string from the grammar."""
        text = self.start_symbol
        expansions = 0
        
        while self.get_nonterminals(text) and expansions < max_expansions:
            text = self.expand_once(text)
            expansions += 1
        
        return text
    
    def coverage_stats(self) -> Dict[str, float]:
        """Return coverage statistics for grammar expansions."""
        stats = {}
        for nt, expansions in self.grammar.items():
            used = sum(1 for exp in expansions if self.expansion_counts[nt][exp] > 0)
            stats[nt] = used / len(expansions) if expansions else 1.0
        return stats


# =============================================================================
# SECTION 3: MUTATION-BASED FUZZING
# =============================================================================

class ScenarioMutator:
    """
    Mutation-based fuzzer for moral scenarios.
    Applies small, semantically meaningful mutations.
    """
    
    # Mutation operators for different scenario aspects
    AGENT_MUTATIONS = {
        "swap_agents": lambda s: s.replace(s.agent_a, "TEMP").replace(s.agent_b, s.agent_a).replace("TEMP", s.agent_b),
        "add_power_imbalance": lambda s: MoralScenario(
            s.id + "_power", s.agent_a, s.agent_b, s.relationship,
            s.action, s.context, s.modifiers + [f"{s.agent_a} holds significant power over {s.agent_b}."]
        ),
        "add_vulnerability": lambda s: MoralScenario(
            s.id + "_vuln", s.agent_a, s.agent_b, s.relationship,
            s.action, s.context, s.modifiers + [f"{s.agent_b} was in a vulnerable state."]
        ),
    }
    
    CONTEXT_MUTATIONS = {
        "add_emergency": lambda s: MoralScenario(
            s.id + "_emerg", s.agent_a, s.agent_b, s.relationship,
            s.action, s.context, s.modifiers + [f"{s.agent_a} was facing a family emergency."]
        ),
        "add_apology": lambda s: MoralScenario(
            s.id + "_apol", s.agent_a, s.agent_b, s.relationship,
            s.action, s.context, s.modifiers + [f"{s.agent_a} has since apologized sincerely."]
        ),
        "add_resolution": lambda s: MoralScenario(
            s.id + "_resol", s.agent_a, s.agent_b, s.relationship,
            s.action, s.context, s.modifiers + ["The situation has been fully resolved."]
        ),
        "add_reciprocity": lambda s: MoralScenario(
            s.id + "_recip", s.agent_a, s.agent_b, s.relationship,
            s.action, s.context, s.modifiers + [f"{s.agent_b} had done the same to {s.agent_a} before."]
        ),
        "remove_context": lambda s: MoralScenario(
            s.id + "_bare", s.agent_a, s.agent_b, s.relationship,
            s.action, "", []
        ),
    }
    
    RELATIONSHIP_MUTATIONS = {
        "strengthen_bond": lambda s: MoralScenario(
            s.id + "_strong", s.agent_a, s.agent_b, "close " + s.relationship,
            s.action, s.context, s.modifiers
        ),
        "weaken_bond": lambda s: MoralScenario(
            s.id + "_weak", s.agent_a, s.agent_b, "distant " + s.relationship,
            s.action, s.context, s.modifiers
        ),
        "formalize_bond": lambda s: MoralScenario(
            s.id + "_formal", s.agent_a, s.agent_b, "contractual " + s.relationship,
            s.action, s.context, s.modifiers
        ),
    }
    
    def __init__(self):
        self.all_mutations = {
            **self.AGENT_MUTATIONS,
            **self.CONTEXT_MUTATIONS,
            **self.RELATIONSHIP_MUTATIONS,
        }
    
    def mutate(self, scenario: MoralScenario, n_mutations: int = 1) -> MoralScenario:
        """Apply random mutations to a scenario."""
        result = scenario
        for _ in range(n_mutations):
            mutation_name = random.choice(list(self.all_mutations.keys()))
            try:
                result = self.all_mutations[mutation_name](result)
            except Exception:
                pass  # Skip failed mutations
        return result
    
    def generate_mutation_chain(self, seed: MoralScenario, length: int = 5) -> List[MoralScenario]:
        """Generate a chain of mutations from a seed."""
        chain = [seed]
        current = seed
        for _ in range(length):
            mutated = self.mutate(current)
            chain.append(mutated)
            current = mutated
        return chain


# =============================================================================
# SECTION 4: METAMORPHIC TESTING FOR MATHEMATICAL INVARIANTS
# =============================================================================

class MetamorphicRelation(ABC):
    """Base class for metamorphic relations testing mathematical structure."""
    
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def generate_followup(self, scenario: MoralScenario) -> MoralScenario:
        """Generate a follow-up test case."""
        pass
    
    @abstractmethod
    def check_relation(self, 
                       original_result: EvaluationResult,
                       followup_result: EvaluationResult) -> Tuple[bool, str]:
        """Check if the metamorphic relation holds."""
        pass


class SymmetryRelation(MetamorphicRelation):
    """
    Tests O↔L and C↔N correlative symmetry.
    If we swap agent perspectives, O should map to C (and vice versa).
    """
    
    def name(self) -> str:
        return "Hohfeldian Correlative Symmetry"
    
    def generate_followup(self, scenario: MoralScenario) -> MoralScenario:
        # Swap agent perspective
        return MoralScenario(
            id=scenario.id + "_swapped",
            agent_a=scenario.agent_b,
            agent_b=scenario.agent_a,
            relationship=scenario.relationship,
            action=scenario.action.replace(scenario.agent_a, "TEMP").replace(
                scenario.agent_b, scenario.agent_a).replace("TEMP", scenario.agent_b),
            context=scenario.context,
            modifiers=scenario.modifiers
        )
    
    def check_relation(self, original: EvaluationResult, followup: EvaluationResult) -> Tuple[bool, str]:
        # Expected correlative mappings
        correlatives = {
            BondType.OBLIGATION: BondType.CLAIM,
            BondType.CLAIM: BondType.OBLIGATION,
            BondType.LIBERTY: BondType.NO_CLAIM,
            BondType.NO_CLAIM: BondType.LIBERTY,
        }
        
        expected = correlatives[original.bond_type]
        holds = followup.bond_type == expected
        
        msg = f"{original.bond_type.value} → {followup.bond_type.value} (expected {expected.value})"
        return holds, msg


class PathIndependenceRelation(MetamorphicRelation):
    """
    Tests path independence (Abelian structure).
    If structure is Abelian, order of context additions shouldn't matter.
    If non-Abelian, we should detect path dependence.
    """
    
    def __init__(self, modifier1: str, modifier2: str):
        self.mod1 = modifier1
        self.mod2 = modifier2
    
    def name(self) -> str:
        return f"Path Independence ({self.mod1[:20]}... vs {self.mod2[:20]}...)"
    
    def generate_followup(self, scenario: MoralScenario) -> MoralScenario:
        # Original: mod1 then mod2
        # Followup: mod2 then mod1
        return MoralScenario(
            id=scenario.id + "_reversed_path",
            agent_a=scenario.agent_a,
            agent_b=scenario.agent_b,
            relationship=scenario.relationship,
            action=scenario.action,
            context=scenario.context,
            modifiers=[self.mod2, self.mod1]  # Reversed order
        )
    
    def generate_original_path(self, scenario: MoralScenario) -> MoralScenario:
        return MoralScenario(
            id=scenario.id + "_path1",
            agent_a=scenario.agent_a,
            agent_b=scenario.agent_b,
            relationship=scenario.relationship,
            action=scenario.action,
            context=scenario.context,
            modifiers=[self.mod1, self.mod2]
        )
    
    def check_relation(self, original: EvaluationResult, followup: EvaluationResult) -> Tuple[bool, str]:
        # If Abelian: results should be same
        # If non-Abelian: results may differ (which is actually evidence FOR non-Abelian structure)
        same = original.bond_type == followup.bond_type
        
        msg = f"Path1: {original.bond_type.value}, Path2: {followup.bond_type.value}"
        if not same:
            msg += " → PATH DEPENDENCE DETECTED (non-Abelian evidence)"
        
        return same, msg


class RotationCompositionRelation(MetamorphicRelation):
    """
    Tests SU(2) rotation composition.
    Two sequential threshold crossings should compose as rotations.
    """
    
    def name(self) -> str:
        return "Rotation Composition (SU(2) structure)"
    
    def generate_followup(self, scenario: MoralScenario) -> MoralScenario:
        # Add double threshold
        return MoralScenario(
            id=scenario.id + "_double_threshold",
            agent_a=scenario.agent_a,
            agent_b=scenario.agent_b,
            relationship=scenario.relationship,
            action=scenario.action,
            context=scenario.context,
            modifiers=scenario.modifiers + [
                f"{scenario.agent_b} was facing a severe emergency.",
                f"{scenario.agent_b} has fully resolved the situation and deeply apologized."
            ]
        )
    
    def check_relation(self, original: EvaluationResult, followup: EvaluationResult) -> Tuple[bool, str]:
        # Double rotation should produce larger effect
        # This is a weak test - mainly checking for systematic change
        changed = original.bond_type != followup.bond_type
        msg = f"Single: {original.bond_type.value} → Double: {followup.bond_type.value}"
        return True, msg  # Always passes, just records the pattern


# =============================================================================
# SECTION 5: PROPERTY-BASED TESTING
# =============================================================================

class PropertyTest(ABC):
    """Abstract base class for property-based tests."""
    
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def generate_inputs(self, n: int) -> List[Any]:
        pass
    
    @abstractmethod
    def check_property(self, inputs: List[Any], results: List[EvaluationResult]) -> Tuple[bool, Dict]:
        pass


class TransitivityProperty(PropertyTest):
    """
    Test transitivity in moral reasoning.
    If A owes B and B owes C, does A owe C?
    """
    
    def name(self) -> str:
        return "Moral Transitivity"
    
    def generate_inputs(self, n: int) -> List[Tuple[MoralScenario, MoralScenario, MoralScenario]]:
        inputs = []
        for i in range(n):
            # A owes B
            s1 = MoralScenario(f"trans_{i}_ab", "Alex", "Bob", "colleague",
                              "borrowed money from", "Alex promised to repay.", [])
            # B owes C
            s2 = MoralScenario(f"trans_{i}_bc", "Bob", "Carol", "colleague",
                              "borrowed money from", "Bob promised to repay.", [])
            # A owes C (direct)?
            s3 = MoralScenario(f"trans_{i}_ac", "Alex", "Carol", "acquaintance",
                              "indirectly owes money to (through Bob)", 
                              "The money Alex owes Bob is needed to pay Carol.", [])
            inputs.append((s1, s2, s3))
        return inputs
    
    def check_property(self, inputs, results) -> Tuple[bool, Dict]:
        # Group results by triplet
        transitivity_holds = 0
        total = 0
        
        for i in range(0, len(results), 3):
            if i + 2 >= len(results):
                break
            r_ab, r_bc, r_ac = results[i], results[i+1], results[i+2]
            
            # If A→B is O and B→C is O, is A→C also O?
            if r_ab.bond_type == BondType.OBLIGATION and r_bc.bond_type == BondType.OBLIGATION:
                if r_ac.bond_type == BondType.OBLIGATION:
                    transitivity_holds += 1
                total += 1
        
        rate = transitivity_holds / total if total > 0 else 0
        return rate > 0.5, {"transitivity_rate": rate, "n_tested": total}


class CHSHProperty(PropertyTest):
    """
    Test CHSH inequality for contextuality.
    Quantum-like correlations should violate classical bounds.
    """
    
    def name(self) -> str:
        return "CHSH Contextuality"
    
    def generate_inputs(self, n: int) -> List[Dict]:
        """Generate CHSH-style measurement configurations."""
        inputs = []
        
        # Base scenario with cyclic responsibility
        for i in range(n):
            base = {
                "agents": ["A", "B", "C"],
                "scenario": f"Three colleagues A, B, C share responsibility for project {i}.",
                "measurements": [
                    {"pair": ("A", "B"), "question": "standard"},
                    {"pair": ("A", "B"), "question": "alternative"},
                    {"pair": ("B", "C"), "question": "standard"},
                    {"pair": ("B", "C"), "question": "alternative"},
                ]
            }
            inputs.append(base)
        
        return inputs
    
    def check_property(self, inputs, results) -> Tuple[bool, Dict]:
        # This would need 4 measurements per scenario
        # S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
        # Classical: |S| ≤ 2
        # Quantum: |S| ≤ 2√2 ≈ 2.83
        
        # Simplified: just check if we see unexpected correlations
        return True, {"note": "CHSH test requires specialized measurement design"}


# =============================================================================
# SECTION 6: COVERAGE-GUIDED FUZZER
# =============================================================================

class MoralSpaceCoverage:
    """
    Tracks coverage of the moral reasoning space.
    Analogous to code coverage in traditional fuzzing.
    """
    
    def __init__(self):
        self.bond_type_counts = {bt: 0 for bt in BondType}
        self.theta_values = []
        self.reasoning_hashes = set()
        self.transition_matrix = defaultdict(lambda: defaultdict(int))
        self.scenario_fingerprints = set()
        
    def update(self, result: EvaluationResult, scenario: MoralScenario):
        """Update coverage with a new result."""
        # Bond type coverage
        self.bond_type_counts[result.bond_type] += 1
        
        # Reasoning diversity
        reasoning_hash = hashlib.md5(result.reasoning.encode()).hexdigest()[:8]
        self.reasoning_hashes.add(reasoning_hash)
        
        # Scenario fingerprint
        fp = self._fingerprint(scenario)
        self.scenario_fingerprints.add(fp)
    
    def update_transition(self, from_result: EvaluationResult, to_result: EvaluationResult):
        """Track a transition between states."""
        self.transition_matrix[from_result.bond_type][to_result.bond_type] += 1
    
    def _fingerprint(self, scenario: MoralScenario) -> str:
        """Create a fingerprint for a scenario based on structural features."""
        features = [
            scenario.relationship[:3] if scenario.relationship else "",
            scenario.action[:10] if scenario.action else "",
            str(len(scenario.modifiers)),
        ]
        return "|".join(features)
    
    def coverage_score(self) -> float:
        """Return overall coverage score (0-1)."""
        # Bond type diversity
        bt_used = sum(1 for c in self.bond_type_counts.values() if c > 0)
        bt_score = bt_used / len(BondType)
        
        # Reasoning diversity (diminishing returns)
        reasoning_score = min(1.0, len(self.reasoning_hashes) / 50)
        
        # Scenario diversity
        scenario_score = min(1.0, len(self.scenario_fingerprints) / 100)
        
        return (bt_score + reasoning_score + scenario_score) / 3
    
    def report(self) -> str:
        """Generate a coverage report."""
        lines = ["=" * 60, "MORAL SPACE COVERAGE REPORT", "=" * 60, ""]
        
        lines.append("Bond Type Coverage:")
        total = sum(self.bond_type_counts.values())
        for bt, count in self.bond_type_counts.items():
            pct = 100 * count / total if total > 0 else 0
            bar = "█" * int(pct / 2)
            lines.append(f"  {bt.value}: {count:4d} ({pct:5.1f}%) {bar}")
        
        lines.append(f"\nUnique reasoning patterns: {len(self.reasoning_hashes)}")
        lines.append(f"Unique scenario fingerprints: {len(self.scenario_fingerprints)}")
        lines.append(f"Overall coverage score: {self.coverage_score():.2%}")
        
        if self.transition_matrix:
            lines.append("\nTransition Matrix:")
            lines.append("     " + " ".join(f"{bt.value:>4}" for bt in BondType))
            for from_bt in BondType:
                row = [f"{self.transition_matrix[from_bt][to_bt]:4d}" for to_bt in BondType]
                lines.append(f"  {from_bt.value}: " + " ".join(row))
        
        return "\n".join(lines)


class GreyboxMoralFuzzer:
    """
    Coverage-guided greybox fuzzer for moral reasoning.
    Prioritizes inputs that increase coverage of the moral space.
    """
    
    def __init__(self, evaluator: Callable[[MoralScenario], EvaluationResult]):
        self.evaluator = evaluator
        self.grammar_fuzzer = GrammarFuzzer(MORAL_SCENARIO_GRAMMAR)
        self.mutator = ScenarioMutator()
        self.coverage = MoralSpaceCoverage()
        self.seed_corpus: List[MoralScenario] = []
        self.energy: Dict[str, float] = defaultdict(lambda: 1.0)
        self.results: List[EvaluationResult] = []
        
    def add_seed(self, scenario: MoralScenario):
        """Add a seed scenario to the corpus."""
        self.seed_corpus.append(scenario)
        self.energy[scenario.id] = 1.0
    
    def select_seed(self) -> MoralScenario:
        """Select a seed based on energy (power schedule)."""
        if not self.seed_corpus:
            # Generate from grammar
            text = self.grammar_fuzzer.fuzz()
            return self._parse_generated_text(text)
        
        # Weighted selection by energy
        total_energy = sum(self.energy[s.id] for s in self.seed_corpus)
        r = random.uniform(0, total_energy)
        cumulative = 0
        for seed in self.seed_corpus:
            cumulative += self.energy[seed.id]
            if cumulative >= r:
                return seed
        return self.seed_corpus[-1]
    
    def _parse_generated_text(self, text: str) -> MoralScenario:
        """Parse generated text into a MoralScenario (simplified)."""
        return MoralScenario(
            id=f"gen_{random.randint(0, 99999)}",
            agent_a="Alex",
            agent_b="Sam",
            relationship="acquaintance",
            action="interacted with",
            context=text,
            modifiers=[]
        )
    
    def fuzz_one(self) -> EvaluationResult:
        """Run one fuzzing iteration."""
        # Select and mutate seed
        seed = self.select_seed()
        mutated = self.mutator.mutate(seed)
        
        # Evaluate
        result = self.evaluator(mutated)
        self.results.append(result)
        
        # Update coverage
        old_score = self.coverage.coverage_score()
        self.coverage.update(result, mutated)
        new_score = self.coverage.coverage_score()
        
        # If coverage increased, add to corpus with high energy
        if new_score > old_score:
            self.seed_corpus.append(mutated)
            self.energy[mutated.id] = 2.0  # Boost energy for interesting inputs
        
        # Decay energy for used seeds
        self.energy[seed.id] *= 0.99
        
        return result
    
    def fuzz(self, n_iterations: int, progress_callback: Callable = None) -> List[EvaluationResult]:
        """Run the fuzzer for n iterations."""
        for i in range(n_iterations):
            result = self.fuzz_one()
            if progress_callback:
                progress_callback(i + 1, n_iterations, result)
        
        return self.results


# =============================================================================
# SECTION 7: LLM EVALUATOR
# =============================================================================

class LLMEvaluator:
    """Evaluates moral scenarios using an LLM."""
    
    def __init__(self, backend: str = "ollama", model: str = "llama3.2",
                 api_key: str = None, base_url: str = "http://localhost:11434"):
        self.backend = backend
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.request_count = 0
        
    def create_prompt(self, scenario: MoralScenario) -> str:
        return f"""Analyze this moral scenario using Hohfeldian jural relations.

SCENARIO:
{scenario.render()}

Classify the PRIMARY moral relation of {scenario.agent_a} toward {scenario.agent_b} as ONE of:
- O (OBLIGATION): {scenario.agent_a} has a duty toward {scenario.agent_b}
- C (CLAIM): {scenario.agent_b} has a right against {scenario.agent_a}
- L (LIBERTY): {scenario.agent_a} is free/permitted in their action
- N (NO-CLAIM): {scenario.agent_b} has no claim against {scenario.agent_a}

Respond EXACTLY in this format:
CLASSIFICATION: [O/C/L/N]
CONFIDENCE: [0.0-1.0]
REASONING: [1-2 sentences]
"""
    
    def evaluate(self, scenario: MoralScenario) -> EvaluationResult:
        """Evaluate a scenario."""
        prompt = self.create_prompt(scenario)
        
        try:
            if self.backend == "ollama":
                response = self._call_ollama(prompt)
            elif self.backend == "anthropic":
                response = self._call_anthropic(prompt)
            elif self.backend == "simulation":
                response = self._simulate_response(scenario)
            else:
                raise ValueError(f"Unknown backend: {self.backend}")
            
            return self._parse_response(response, scenario.id)
            
        except Exception as e:
            return EvaluationResult(
                scenario_id=scenario.id,
                bond_type=BondType.LIBERTY,
                confidence=0.0,
                reasoning=f"Error: {e}",
                raw_response=""
            )
    
    def _call_ollama(self, prompt: str) -> str:
        self.request_count += 1
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 200}
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "")
    
    def _call_anthropic(self, prompt: str) -> str:
        self.request_count += 1
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _simulate_response(self, scenario: MoralScenario) -> str:
        """Simulate a response for testing."""
        # Use scenario features to deterministically generate response
        hash_val = int(hashlib.md5(scenario.render().encode()).hexdigest()[:8], 16)
        
        # Bias based on modifiers
        if any("apologized" in m.lower() for m in scenario.modifiers):
            bond_type = "L"
        elif any("emergency" in m.lower() for m in scenario.modifiers):
            bond_type = "L"
        elif any("vulnerable" in m.lower() for m in scenario.modifiers):
            bond_type = "O"
        elif any("promised" in scenario.action.lower()):
            bond_type = "O"
        else:
            bond_type = ["O", "C", "L", "N"][hash_val % 4]
        
        confidence = 0.6 + (hash_val % 40) / 100
        
        return f"""CLASSIFICATION: {bond_type}
CONFIDENCE: {confidence:.2f}
REASONING: Based on the relationship and context described."""
    
    def _parse_response(self, response: str, scenario_id: str) -> EvaluationResult:
        """Parse LLM response into structured result."""
        bond_type = BondType.LIBERTY
        confidence = 0.5
        reasoning = ""
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('CLASSIFICATION:'):
                type_str = line.replace('CLASSIFICATION:', '').strip()
                for char in type_str:
                    if char.upper() in 'OCLN':
                        try:
                            bond_type = BondType.from_string(char)
                            break
                        except:
                            pass
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.replace('CONFIDENCE:', '').strip())
                    confidence = max(0.0, min(1.0, confidence))
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
# SECTION 8: MATHEMATICAL STRUCTURE TESTS
# =============================================================================

class MathematicalStructureProber:
    """
    Probes the mathematical structure of moral reasoning using various tests.
    """
    
    def __init__(self, evaluator: LLMEvaluator):
        self.evaluator = evaluator
        self.results = []
        
    def test_su2_structure(self, n_trials: int = 20) -> Dict:
        """
        Test for SU(2) rotation structure.
        Create scenarios with varying "rotation angles" and measure bond type distribution.
        """
        print("\n" + "="*60)
        print("TESTING SU(2) ROTATION STRUCTURE")
        print("="*60)
        
        # Create a base scenario
        base = MoralScenario(
            id="su2_base",
            agent_a="Alex",
            agent_b="Jordan",
            relationship="friend",
            action="promised to help Jordan move next Saturday",
            context="Alex made this promise last week.",
            modifiers=[]
        )
        
        # Create versions with increasing "threshold strength"
        thresholds = [
            [],  # θ = 0
            ["Jordan mentioned the help is 'not urgent'."],  # θ ~ π/6
            ["Jordan said 'only if convenient'."],  # θ ~ π/4
            ["Jordan found other help and said 'don't worry about it'."],  # θ ~ π/3
            ["Jordan explicitly released Alex from the promise."],  # θ ~ π/2
        ]
        
        results_by_theta = []
        
        for i, mods in enumerate(thresholds):
            theta_label = f"θ_{i}"
            counts = {bt: 0 for bt in BondType}
            
            for trial in range(n_trials):
                scenario = MoralScenario(
                    id=f"su2_{i}_{trial}",
                    agent_a=base.agent_a,
                    agent_b=base.agent_b,
                    relationship=base.relationship,
                    action=base.action,
                    context=base.context,
                    modifiers=mods
                )
                
                result = self.evaluator.evaluate(scenario)
                counts[result.bond_type] += 1
                self.results.append(result)
            
            # Calculate theta estimate
            n = sum(counts.values())
            p_OL = (counts[BondType.OBLIGATION] + counts[BondType.LIBERTY]) / n
            p_CN = (counts[BondType.CLAIM] + counts[BondType.NO_CLAIM]) / n
            
            if p_OL < 0.01:
                theta_est = np.pi
            elif p_CN < 0.01:
                theta_est = 0
            else:
                theta_est = 2 * np.arctan(np.sqrt(p_CN / p_OL))
            
            results_by_theta.append({
                "threshold_level": i,
                "theta_estimate": theta_est,
                "theta_degrees": np.degrees(theta_est),
                "distribution": {bt.value: counts[bt] for bt in BondType},
            })
            
            print(f"  Level {i}: θ = {np.degrees(theta_est):.1f}°, dist = {dict((bt.value, counts[bt]) for bt in BondType)}")
        
        # Check for monotonic increase
        thetas = [r["theta_estimate"] for r in results_by_theta]
        is_monotonic = all(thetas[i] <= thetas[i+1] for i in range(len(thetas)-1))
        
        return {
            "test": "SU(2) Rotation",
            "results": results_by_theta,
            "monotonic_increase": is_monotonic,
            "supports_theory": is_monotonic and thetas[-1] > thetas[0]
        }
    
    def test_holonomy(self, n_trials: int = 10) -> Dict:
        """
        Test for non-Abelian holonomy (path dependence).
        Apply context modifications in different orders.
        """
        print("\n" + "="*60)
        print("TESTING HOLONOMY (PATH DEPENDENCE)")
        print("="*60)
        
        base = MoralScenario(
            id="holo_base",
            agent_a="Morgan",
            agent_b="Casey",
            relationship="business partner",
            action="is deciding whether to fulfill a contract obligation",
            context="The contract specifies delivery by end of month.",
            modifiers=[]
        )
        
        # Two different context modifications
        mod_A = "Casey's company is experiencing financial difficulties."
        mod_B = "Morgan discovered Casey has been dishonest about project status."
        
        path_results = {"AB": [], "BA": []}
        
        for trial in range(n_trials):
            # Path 1: A then B
            scenario_AB = MoralScenario(
                id=f"holo_AB_{trial}",
                agent_a=base.agent_a, agent_b=base.agent_b,
                relationship=base.relationship, action=base.action,
                context=base.context,
                modifiers=[mod_A, mod_B]
            )
            result_AB = self.evaluator.evaluate(scenario_AB)
            path_results["AB"].append(result_AB.bond_type)
            
            # Path 2: B then A
            scenario_BA = MoralScenario(
                id=f"holo_BA_{trial}",
                agent_a=base.agent_a, agent_b=base.agent_b,
                relationship=base.relationship, action=base.action,
                context=base.context,
                modifiers=[mod_B, mod_A]
            )
            result_BA = self.evaluator.evaluate(scenario_BA)
            path_results["BA"].append(result_BA.bond_type)
            
            self.results.extend([result_AB, result_BA])
        
        # Compare distributions
        dist_AB = {bt: sum(1 for r in path_results["AB"] if r == bt) for bt in BondType}
        dist_BA = {bt: sum(1 for r in path_results["BA"] if r == bt) for bt in BondType}
        
        # Chi-square test for difference
        obs_AB = [dist_AB[bt] for bt in BondType]
        obs_BA = [dist_BA[bt] for bt in BondType]
        
        # Only test if we have variance
        if sum(obs_AB) > 0 and sum(obs_BA) > 0:
            contingency = np.array([obs_AB, obs_BA])
            non_zero = contingency.sum(axis=0) > 0
            if sum(non_zero) > 1:
                chi2, p_value, _, _ = stats.chi2_contingency(contingency[:, non_zero])
            else:
                chi2, p_value = 0, 1.0
        else:
            chi2, p_value = 0, 1.0
        
        path_dependent = p_value < 0.05
        
        print(f"  Path A→B distribution: {dict((bt.value, dist_AB[bt]) for bt in BondType)}")
        print(f"  Path B→A distribution: {dict((bt.value, dist_BA[bt]) for bt in BondType)}")
        print(f"  χ² = {chi2:.2f}, p = {p_value:.4f}")
        print(f"  Path dependent: {path_dependent}")
        
        return {
            "test": "Holonomy (Path Dependence)",
            "distribution_AB": {bt.value: dist_AB[bt] for bt in BondType},
            "distribution_BA": {bt.value: dist_BA[bt] for bt in BondType},
            "chi2": chi2,
            "p_value": p_value,
            "path_dependent": path_dependent,
            "supports_non_abelian": path_dependent
        }
    
    def test_contextuality(self, n_trials: int = 10) -> Dict:
        """
        Test for contextuality using a simplified CHSH-like setup.
        """
        print("\n" + "="*60)
        print("TESTING CONTEXTUALITY (CHSH-LIKE)")
        print("="*60)
        
        # Three agents in a cyclic responsibility structure
        # A→B, B→C, C→A
        
        correlations = []
        
        for trial in range(n_trials):
            # Measure A→B
            s_ab = MoralScenario(f"ctx_ab_{trial}", "A", "B", "colleague",
                                "delegated a task to", "A is responsible for outcome.", [])
            r_ab = self.evaluator.evaluate(s_ab)
            
            # Measure B→C
            s_bc = MoralScenario(f"ctx_bc_{trial}", "B", "C", "colleague",
                                "delegated a task to", "B is responsible for outcome.", [])
            r_bc = self.evaluator.evaluate(s_bc)
            
            # Measure C→A
            s_ca = MoralScenario(f"ctx_ca_{trial}", "C", "A", "colleague",
                                "delegated a task to", "C is responsible for outcome.", [])
            r_ca = self.evaluator.evaluate(s_ca)
            
            # Measure with alternative context
            s_ab_alt = MoralScenario(f"ctx_ab_alt_{trial}", "A", "B", "colleague",
                                    "delegated a task to", "A claims B volunteered.", [])
            r_ab_alt = self.evaluator.evaluate(s_ab_alt)
            
            self.results.extend([r_ab, r_bc, r_ca, r_ab_alt])
            
            # Calculate correlations (simplified: +1 if O/C, -1 if L/N)
            def to_spin(bt):
                return 1 if bt in [BondType.OBLIGATION, BondType.CLAIM] else -1
            
            correlations.append({
                "ab": to_spin(r_ab.bond_type),
                "bc": to_spin(r_bc.bond_type),
                "ca": to_spin(r_ca.bond_type),
                "ab_alt": to_spin(r_ab_alt.bond_type),
            })
        
        # Calculate CHSH-like quantity
        E_ab = np.mean([c["ab"] * c["bc"] for c in correlations])
        E_ab_alt = np.mean([c["ab_alt"] * c["bc"] for c in correlations])
        E_bc = np.mean([c["bc"] * c["ca"] for c in correlations])
        
        S = abs(E_ab + E_ab_alt + E_bc)  # Simplified CHSH
        
        print(f"  E(AB·BC) = {E_ab:.3f}")
        print(f"  E(AB'·BC) = {E_ab_alt:.3f}")
        print(f"  E(BC·CA) = {E_bc:.3f}")
        print(f"  S = {S:.3f} (classical bound: 2, quantum bound: 2√2 ≈ 2.83)")
        
        return {
            "test": "Contextuality (CHSH)",
            "E_ab": E_ab,
            "E_ab_alt": E_ab_alt,
            "E_bc": E_bc,
            "S": S,
            "violates_classical": S > 2,
            "note": "Simplified CHSH; full test needs more measurements"
        }
    
    def run_all_tests(self, n_trials: int = 10) -> Dict:
        """Run all mathematical structure tests."""
        print("\n" + "="*70)
        print("SQND MATHEMATICAL STRUCTURE PROBE")
        print("="*70)
        
        results = {
            "su2": self.test_su2_structure(n_trials),
            "holonomy": self.test_holonomy(n_trials),
            "contextuality": self.test_contextuality(n_trials),
        }
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"  SU(2) rotation structure: {'✓ SUPPORTED' if results['su2']['supports_theory'] else '✗ NOT SUPPORTED'}")
        print(f"  Non-Abelian holonomy: {'✓ DETECTED' if results['holonomy']['supports_non_abelian'] else '✗ NOT DETECTED'}")
        print(f"  Contextuality: {'✓ CLASSICAL VIOLATION' if results['contextuality']['violates_classical'] else '✗ CLASSICAL'}")
        
        return results


# =============================================================================
# SECTION 9: MAIN FUZZING CAMPAIGN
# =============================================================================

def run_fuzzing_campaign(
    backend: str = "simulation",
    model: str = "llama3.2",
    n_iterations: int = 100,
    n_structure_trials: int = 10,
    api_key: str = None,
    output_file: str = "fuzzing_results.json"
):
    """Run a complete fuzzing campaign."""
    
    print("="*70)
    print("SQND MATHEMATICAL STRUCTURE FUZZER")
    print("="*70)
    print(f"\nBackend: {backend}")
    print(f"Model: {model}")
    print(f"Fuzzing iterations: {n_iterations}")
    print(f"Structure test trials: {n_structure_trials}")
    
    # Initialize evaluator
    evaluator = LLMEvaluator(
        backend=backend,
        model=model,
        api_key=api_key
    )
    
    # Phase 1: Coverage-guided fuzzing
    print("\n" + "="*60)
    print("PHASE 1: COVERAGE-GUIDED FUZZING")
    print("="*60)
    
    fuzzer = GreyboxMoralFuzzer(evaluator.evaluate)
    
    # Add initial seeds
    seeds = [
        MoralScenario("seed_1", "Alex", "Jordan", "friend",
                     "promised to help", "They made this promise last week.", []),
        MoralScenario("seed_2", "Morgan", "Casey", "employer",
                     "assigned extra work to", "This was outside normal duties.", []),
        MoralScenario("seed_3", "Taylor", "Riley", "parent",
                     "set strict rules for", "Riley is 16 years old.", []),
    ]
    for seed in seeds:
        fuzzer.add_seed(seed)
    
    def progress(i, n, result):
        if i % 10 == 0:
            print(f"  [{i}/{n}] Coverage: {fuzzer.coverage.coverage_score():.2%}, "
                  f"Corpus size: {len(fuzzer.seed_corpus)}")
    
    fuzzer.fuzz(n_iterations, progress_callback=progress)
    
    print("\n" + fuzzer.coverage.report())
    
    # Phase 2: Mathematical structure probing
    print("\n" + "="*60)
    print("PHASE 2: MATHEMATICAL STRUCTURE PROBING")
    print("="*60)
    
    prober = MathematicalStructureProber(evaluator)
    structure_results = prober.run_all_tests(n_structure_trials)
    
    # Phase 3: Metamorphic testing
    print("\n" + "="*60)
    print("PHASE 3: METAMORPHIC TESTING")
    print("="*60)
    
    metamorphic_results = []
    
    # Test symmetry relation
    sym_relation = SymmetryRelation()
    print(f"\nTesting: {sym_relation.name()}")
    
    for seed in seeds[:3]:
        original = evaluator.evaluate(seed)
        followup_scenario = sym_relation.generate_followup(seed)
        followup = evaluator.evaluate(followup_scenario)
        holds, msg = sym_relation.check_relation(original, followup)
        
        metamorphic_results.append({
            "relation": sym_relation.name(),
            "scenario": seed.id,
            "holds": holds,
            "message": msg
        })
        print(f"  {seed.id}: {msg} -> {'✓' if holds else '✗'}")
    
    # Test path independence
    path_relation = PathIndependenceRelation(
        "The other party was in distress.",
        "The situation has been resolved."
    )
    print(f"\nTesting: {path_relation.name()}")
    
    for seed in seeds[:3]:
        path1 = path_relation.generate_original_path(seed)
        path2 = path_relation.generate_followup(seed)
        
        result1 = evaluator.evaluate(path1)
        result2 = evaluator.evaluate(path2)
        
        same, msg = path_relation.check_relation(result1, result2)
        
        metamorphic_results.append({
            "relation": path_relation.name(),
            "scenario": seed.id,
            "paths_same": same,
            "message": msg
        })
        print(f"  {seed.id}: {msg}")
    
    # Compile results
    all_results = {
        "config": {
            "backend": backend,
            "model": model,
            "n_iterations": n_iterations,
            "n_structure_trials": n_structure_trials,
        },
        "coverage": {
            "score": fuzzer.coverage.coverage_score(),
            "bond_type_counts": {bt.value: fuzzer.coverage.bond_type_counts[bt] for bt in BondType},
            "unique_reasoning_patterns": len(fuzzer.coverage.reasoning_hashes),
            "corpus_size": len(fuzzer.seed_corpus),
        },
        "structure_tests": structure_results,
        "metamorphic_tests": metamorphic_results,
        "total_evaluations": evaluator.request_count,
    }
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n{'='*70}")
    print(f"Results saved to {output_file}")
    print(f"Total evaluations: {evaluator.request_count}")
    print(f"{'='*70}")
    
    return all_results


# =============================================================================
# SECTION 10: CLI
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SQND Mathematical Structure Fuzzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simulation mode (no API needed)
  python sqnd_fuzzer.py --backend simulation --iterations 50
  
  # Ollama (local LLM)
  python sqnd_fuzzer.py --backend ollama --model llama3.2 --iterations 100
  
  # Anthropic Claude
  python sqnd_fuzzer.py --backend anthropic --model claude-sonnet-4-20250514 --api-key sk-...
        """
    )
    
    parser.add_argument('--backend', choices=['simulation', 'ollama', 'anthropic'],
                       default='simulation', help='Evaluation backend')
    parser.add_argument('--model', type=str, default='llama3.2',
                       help='Model name')
    parser.add_argument('--api-key', type=str, default=None,
                       help='API key (for Anthropic)')
    parser.add_argument('--iterations', type=int, default=50,
                       help='Number of fuzzing iterations')
    parser.add_argument('--structure-trials', type=int, default=10,
                       help='Trials per structure test')
    parser.add_argument('--output', type=str, default='fuzzing_results.json',
                       help='Output file')
    
    args = parser.parse_args()
    
    run_fuzzing_campaign(
        backend=args.backend,
        model=args.model,
        n_iterations=args.iterations,
        n_structure_trials=args.structure_trials,
        api_key=args.api_key,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
