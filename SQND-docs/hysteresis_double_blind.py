#!/usr/bin/env python3
"""
DOUBLE-BLIND HYSTERESIS EXPERIMENT
==================================

Proper experimental methodology applied to Claude API testing.

DESIGN PRINCIPLES:
1. Fresh session per call — no context window carryover
2. Blind condition codes — script doesn't know mapping until unblinding
3. Neutral prompt framing — no hypothesis-signaling language
4. Separate blind judge — different API call classifies responses
5. Randomized order — conditions interleaved randomly

ARCHITECTURE:
                                                                    
  ┌─────────────────┐                                              
  │  RANDOMIZER     │  Creates blinded trial schedule              
  │                 │  Condition codes: X, Y, Z (meaning hidden)   
  └────────┬────────┘                                              
           │                                                       
           ▼                                                       
  ┌─────────────────┐                                              
  │  PROMPT GEN     │  Generates prompts from codes                
  │  (hypothesis-   │  No "priming" or "hysteresis" language       
  │   blind)        │  Context framing is neutral                  
  └────────┬────────┘                                              
           │                                                       
           ▼                                                       
  ┌─────────────────┐                                              
  │  CLAUDE API     │  Independent calls, fresh each time          
  │  (subject)      │  temperature=1.0                             
  └────────┬────────┘                                              
           │                                                       
           ▼                                                       
  ┌─────────────────┐                                              
  │  BLIND JUDGE    │  Separate Claude call                        
  │  (classifier)   │  Sees ONLY the response text                 
  │                 │  No condition info, no scenario              
  └────────┬────────┘                                              
           │                                                       
           ▼                                                       
  ┌─────────────────┐                                              
  │  UNBLINDING     │  Merge codes with true conditions            
  │  & ANALYSIS     │  Statistical tests                           
  └─────────────────┘                                              

Author: Claude (with Andrew H. Bond)  
Date: January 2026
"""

import json
import random
import hashlib
import argparse
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time


# =============================================================================
# PHASE 1: RANDOMIZER (Creates blinded trial schedule)
# =============================================================================

@dataclass
class BlindedTrial:
    """A single trial with blinded condition code."""
    trial_id: str
    scenario_level: int
    condition_code: str  # X, Y, or Z (meaning hidden)
    scenario_text: str
    context_text: str    # The "context" presented (neutral framing)


class Randomizer:
    """
    Creates randomized, blinded trial schedule.
    
    The mapping from condition codes (X, Y, Z) to actual conditions
    is stored separately and only revealed at analysis time.
    """
    
    # Scenarios: relationship-based (avoids promise language that presupposes ethics)
    SCENARIOS = [
        {
            "level": 0,
            "text": "Alex and Jordan live in the same city but have never met. "
                    "Alex sees Jordan trying to change a flat tire in a parking lot.",
        },
        {
            "level": 1, 
            "text": "Alex and Jordan have met once at a mutual friend's party. "
                    "Alex sees Jordan trying to change a flat tire in a parking lot.",
        },
        {
            "level": 2,
            "text": "Alex and Jordan are coworkers who occasionally chat at lunch. "
                    "Alex sees Jordan trying to change a flat tire in the office parking lot.",
        },
        {
            "level": 3,
            "text": "Alex and Jordan are friendly neighbors who water each other's plants when traveling. "
                    "Alex sees Jordan trying to change a flat tire outside their homes.",
        },
        {
            "level": 4,
            "text": "Alex and Jordan are good friends who see each other weekly. "
                    "Alex sees Jordan trying to change a flat tire.",
        },
        {
            "level": 5,
            "text": "Alex and Jordan are close friends. Jordan helped Alex through a difficult time last year. "
                    "Alex sees Jordan trying to change a flat tire.",
        },
        {
            "level": 6,
            "text": "Alex and Jordan are best friends of 10 years who consider each other family. "
                    "Alex sees Jordan trying to change a flat tire.",
        },
    ]
    
    # Context framings (neutral language, no "prior state" signaling)
    CONTEXTS = {
        "X": "Alex has been having a busy week and is currently on the way to an appointment.",
        "Y": "Alex has some free time today and was just taking a walk around the neighborhood.",
        "Z": "Alex just finished an errand and is heading home.",
    }
    
    def __init__(self, seed: int = None):
        """Initialize with optional seed for reproducibility."""
        self.seed = seed if seed else random.randint(0, 999999)
        random.seed(self.seed)
        
        # Create random mapping (hidden until unblinding)
        conditions = ["busy_context", "free_context", "neutral_context"]
        codes = ["X", "Y", "Z"]
        random.shuffle(conditions)
        self._code_mapping = dict(zip(codes, conditions))
        
        # Store mapping securely (would be in separate file in real experiment)
        self._mapping_hash = hashlib.sha256(
            json.dumps(self._code_mapping, sort_keys=True).encode()
        ).hexdigest()[:16]
    
    def create_trial_schedule(self, trials_per_cell: int) -> Tuple[List[BlindedTrial], str]:
        """
        Create randomized trial schedule.
        
        Returns:
            - List of BlindedTrial objects (in randomized order)
            - Mapping file content (to be saved separately, opened only at analysis)
        """
        trials = []
        
        # Create all trials
        for level in range(7):
            scenario = self.SCENARIOS[level]
            for code in ["X", "Y", "Z"]:
                for rep in range(trials_per_cell):
                    trial = BlindedTrial(
                        trial_id=f"T{len(trials):04d}",
                        scenario_level=level,
                        condition_code=code,
                        scenario_text=scenario["text"],
                        context_text=self.CONTEXTS[code],
                    )
                    trials.append(trial)
        
        # Randomize order
        random.shuffle(trials)
        
        # Create sealed mapping file
        mapping_content = {
            "created": datetime.now().isoformat(),
            "seed": self.seed,
            "mapping_hash": self._mapping_hash,
            "code_mapping": self._code_mapping,
            "DO_NOT_OPEN_UNTIL_ANALYSIS": True,
        }
        
        return trials, json.dumps(mapping_content, indent=2)


# =============================================================================
# PHASE 2: PROMPT GENERATOR (Hypothesis-blind)
# =============================================================================

class PromptGenerator:
    """
    Generates prompts without any hypothesis-signaling language.
    
    Note: This class has NO knowledge of what the conditions mean.
    It just combines scenario + context into a neutral prompt.
    """
    
    PROMPT_TEMPLATE = """Consider this situation:

{scenario}

Additional context: {context}

Question: Does Alex have a moral obligation to stop and help Jordan, or is Alex free to continue on without helping?

Please respond with your assessment. Start your response with either "OBLIGATED" or "FREE" followed by a brief explanation."""

    def generate(self, trial: BlindedTrial) -> str:
        """Generate prompt for a trial (no condition knowledge)."""
        return self.PROMPT_TEMPLATE.format(
            scenario=trial.scenario_text,
            context=trial.context_text,
        )


# =============================================================================
# PHASE 3: SUBJECT (Claude API calls)
# =============================================================================

@dataclass
class SubjectResponse:
    """Raw response from subject (Claude), before classification."""
    trial_id: str
    raw_response: str
    response_time_ms: int
    tokens_used: int


class Subject:
    """
    Makes API calls to Claude as the "subject" in the experiment.
    
    Each call is a fresh session — no context carryover.
    """
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key
        self.model = model
        self.total_calls = 0
        self.total_tokens = 0
    
    def respond(self, prompt: str, trial_id: str) -> SubjectResponse:
        """Get response from Claude (fresh session)."""
        import anthropic
        
        start_time = time.time()
        
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=300,
            temperature=1.0,  # Maximum variation
            messages=[{"role": "user", "content": prompt}]
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        tokens = response.usage.input_tokens + response.usage.output_tokens
        
        self.total_calls += 1
        self.total_tokens += tokens
        
        return SubjectResponse(
            trial_id=trial_id,
            raw_response=response.content[0].text,
            response_time_ms=elapsed_ms,
            tokens_used=tokens,
        )


class SimulatedSubject:
    """Simulated subject for testing the experimental pipeline."""
    
    def __init__(self):
        self.total_calls = 0
        self.total_tokens = 0
    
    def respond(self, prompt: str, trial_id: str) -> SubjectResponse:
        self.total_calls += 1
        self.total_tokens += 300
        
        # Simulate response based on scenario level (extract from prompt)
        # This is just for pipeline testing
        import re
        
        # Crude level detection from prompt content
        if "never met" in prompt or "met once" in prompt:
            p_obligated = 0.2
        elif "coworkers" in prompt:
            p_obligated = 0.35
        elif "friendly neighbors" in prompt:
            p_obligated = 0.5
        elif "good friends" in prompt:
            p_obligated = 0.65
        elif "close friends" in prompt:
            p_obligated = 0.8
        elif "best friends" in prompt:
            p_obligated = 0.9
        else:
            p_obligated = 0.5
        
        # Add context effect (simulated hysteresis)
        if "busy week" in prompt:
            p_obligated -= 0.1
        elif "free time" in prompt:
            p_obligated += 0.1
        
        # Random draw
        if random.random() < p_obligated:
            response = "OBLIGATED - Given the relationship, Alex should help."
        else:
            response = "FREE - Alex has no specific duty to help in this situation."
        
        return SubjectResponse(
            trial_id=trial_id,
            raw_response=response,
            response_time_ms=random.randint(500, 2000),
            tokens_used=300,
        )


# =============================================================================
# PHASE 4: BLIND JUDGE (Separate classifier)
# =============================================================================

@dataclass
class JudgedResponse:
    """Classification by blind judge."""
    trial_id: str
    raw_response: str
    classification: str  # "O" or "L"
    judge_confidence: float
    judge_reasoning: str


class BlindJudge:
    """
    Separate Claude instance that classifies responses.
    
    The judge sees ONLY the raw response text.
    No scenario, no context, no condition information.
    """
    
    JUDGE_PROMPT = """You are a classifier. Your task is to determine whether the following response indicates the person believes there is an OBLIGATION to help, or that the person is FREE (at liberty) to not help.

Response to classify:
"{response}"

Classify as exactly one of:
- OBLIGATION: The response indicates the person should/must help
- LIBERTY: The response indicates the person is free to not help

Respond in this exact format:
CLASSIFICATION: [OBLIGATION or LIBERTY]
CONFIDENCE: [0.0 to 1.0]
REASONING: [one sentence]"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key
        self.model = model
        self.total_calls = 0
        self.total_tokens = 0
    
    def classify(self, subject_response: SubjectResponse) -> JudgedResponse:
        """Classify a response (blind to condition)."""
        import anthropic
        
        prompt = self.JUDGE_PROMPT.format(response=subject_response.raw_response)
        
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=150,
            temperature=0,  # Deterministic classification
            messages=[{"role": "user", "content": prompt}]
        )
        
        self.total_calls += 1
        self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
        
        # Parse judge response
        judge_text = response.content[0].text
        
        classification = "?"
        confidence = 0.5
        reasoning = ""
        
        for line in judge_text.strip().split('\n'):
            if line.startswith("CLASSIFICATION:"):
                if "OBLIGATION" in line.upper():
                    classification = "O"
                elif "LIBERTY" in line.upper():
                    classification = "L"
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
        
        return JudgedResponse(
            trial_id=subject_response.trial_id,
            raw_response=subject_response.raw_response,
            classification=classification,
            judge_confidence=confidence,
            judge_reasoning=reasoning,
        )


class SimulatedJudge:
    """Simulated judge for pipeline testing."""
    
    def __init__(self):
        self.total_calls = 0
        self.total_tokens = 0
    
    def classify(self, subject_response: SubjectResponse) -> JudgedResponse:
        self.total_calls += 1
        self.total_tokens += 150
        
        response_upper = subject_response.raw_response.upper()
        
        if "OBLIGATED" in response_upper or "SHOULD HELP" in response_upper or "MUST HELP" in response_upper:
            classification = "O"
        elif "FREE" in response_upper or "NO DUTY" in response_upper or "NOT OBLIGAT" in response_upper:
            classification = "L"
        else:
            classification = "O" if random.random() < 0.5 else "L"
        
        return JudgedResponse(
            trial_id=subject_response.trial_id,
            raw_response=subject_response.raw_response,
            classification=classification,
            judge_confidence=0.85,
            judge_reasoning="Simulated classification",
        )


# =============================================================================
# PHASE 5: UNBLINDING & ANALYSIS
# =============================================================================

class Analyzer:
    """
    Unblinds data and performs statistical analysis.
    
    Only instantiated AFTER all data collection is complete.
    """
    
    def __init__(self, mapping_file: str):
        """Load the sealed mapping."""
        with open(mapping_file, 'r') as f:
            mapping_data = json.load(f)
        
        self.code_mapping = mapping_data["code_mapping"]
        print(f"UNBLINDING: Code mapping revealed")
        print(f"  X = {self.code_mapping['X']}")
        print(f"  Y = {self.code_mapping['Y']}")
        print(f"  Z = {self.code_mapping['Z']}")
    
    def analyze(self, results_file: str) -> Dict:
        """Perform analysis on collected data."""
        from scipy import stats
        import numpy as np
        
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        trials = data["trials"]
        
        # Unblind: add true condition to each trial
        for trial in trials:
            trial["true_condition"] = self.code_mapping[trial["condition_code"]]
        
        # Group by level and condition
        from collections import defaultdict
        grouped = defaultdict(lambda: defaultdict(list))
        
        for trial in trials:
            level = trial["scenario_level"]
            condition = trial["true_condition"]
            is_O = 1 if trial["classification"] == "O" else 0
            grouped[level][condition].append(is_O)
        
        # Calculate statistics per level
        level_stats = []
        
        for level in sorted(grouped.keys()):
            conditions = grouped[level]
            
            stats_row = {"level": level}
            
            for cond in ["busy_context", "free_context", "neutral_context"]:
                values = conditions.get(cond, [])
                if values:
                    stats_row[f"p_O_{cond}"] = np.mean(values)
                    stats_row[f"n_{cond}"] = len(values)
                else:
                    stats_row[f"p_O_{cond}"] = None
                    stats_row[f"n_{cond}"] = 0
            
            # Hysteresis effect: P(O|free) - P(O|busy)
            # If positive: "free time" context increases perceived obligation
            p_free = stats_row.get("p_O_free_context")
            p_busy = stats_row.get("p_O_busy_context")
            
            if p_free is not None and p_busy is not None:
                stats_row["hysteresis_effect"] = p_free - p_busy
                
                # Chi-square test
                n_free = stats_row["n_free_context"]
                n_busy = stats_row["n_busy_context"]
                o_free = int(p_free * n_free)
                o_busy = int(p_busy * n_busy)
                
                try:
                    contingency = [[o_free, n_free - o_free],
                                  [o_busy, n_busy - o_busy]]
                    chi2, p_value = stats.chi2_contingency(contingency)[:2]
                    stats_row["chi2"] = chi2
                    stats_row["p_value"] = p_value
                    stats_row["significant"] = p_value < 0.05
                except:
                    stats_row["chi2"] = None
                    stats_row["p_value"] = None
                    stats_row["significant"] = False
            
            level_stats.append(stats_row)
        
        # Overall analysis (focus on ambiguous middle levels 2-4)
        middle_effects = [s["hysteresis_effect"] for s in level_stats 
                         if s["level"] in [2, 3, 4] and s.get("hysteresis_effect") is not None]
        
        mean_effect = np.mean(middle_effects) if middle_effects else 0
        sig_count = sum(1 for s in level_stats 
                       if s["level"] in [2, 3, 4] and s.get("significant", False))
        
        analysis = {
            "level_statistics": level_stats,
            "mean_hysteresis_effect_middle": mean_effect,
            "significant_levels_middle": sig_count,
            "hysteresis_detected": abs(mean_effect) > 0.08 and sig_count >= 1,
            "interpretation": self._interpret(mean_effect, sig_count),
        }
        
        return analysis
    
    def _interpret(self, mean_effect: float, sig_count: int) -> str:
        if abs(mean_effect) <= 0.05:
            return "NO EFFECT: Context framing does not influence moral classification"
        elif mean_effect > 0.08 and sig_count >= 1:
            return "CONTEXT EFFECT DETECTED: 'Free time' context increases perceived obligation relative to 'busy' context"
        elif mean_effect < -0.08 and sig_count >= 1:
            return "REVERSE CONTEXT EFFECT: 'Busy' context increases perceived obligation (unexpected)"
        else:
            return "WEAK/INCONSISTENT EFFECT: Some signal but not statistically robust"


# =============================================================================
# EXPERIMENT RUNNER
# =============================================================================

def run_experiment(
    api_key: Optional[str],
    trials_per_cell: int,
    output_dir: str,
    use_simulation: bool = False,
    seed: int = None,
) -> Dict:
    """
    Run the full double-blind experiment.
    """
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("DOUBLE-BLIND HYSTERESIS EXPERIMENT")
    print("=" * 70)
    print(f"\nOutput directory: {output_dir}")
    print(f"Trials per cell: {trials_per_cell}")
    print(f"Total trials: {7 * 3 * trials_per_cell}")
    print(f"Mode: {'SIMULATION' if use_simulation else 'LIVE API'}")
    
    # -------------------------------------------------------------------------
    # PHASE 1: Create blinded trial schedule
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("PHASE 1: Creating blinded trial schedule")
    print("-" * 70)
    
    randomizer = Randomizer(seed=seed)
    trials, mapping_content = randomizer.create_trial_schedule(trials_per_cell)
    
    # Save mapping file (SEALED - do not open until analysis)
    mapping_file = output_path / "SEALED_mapping.json"
    with open(mapping_file, 'w') as f:
        f.write(mapping_content)
    print(f"  Sealed mapping saved to: {mapping_file}")
    print(f"  ⚠️  DO NOT OPEN UNTIL ANALYSIS PHASE")
    
    print(f"  Created {len(trials)} randomized trials")
    
    # -------------------------------------------------------------------------
    # PHASE 2 & 3: Generate prompts and collect responses
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("PHASE 2-3: Collecting subject responses")
    print("-" * 70)
    
    prompt_gen = PromptGenerator()
    
    if use_simulation:
        subject = SimulatedSubject()
    else:
        subject = Subject(api_key)
    
    subject_responses = []
    
    for i, trial in enumerate(trials):
        prompt = prompt_gen.generate(trial)
        response = subject.respond(prompt, trial.trial_id)
        subject_responses.append(response)
        
        if (i + 1) % 50 == 0:
            print(f"  Completed {i + 1}/{len(trials)} trials")
    
    print(f"  Total subject API calls: {subject.total_calls}")
    
    # -------------------------------------------------------------------------
    # PHASE 4: Blind classification
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("PHASE 4: Blind judge classification")
    print("-" * 70)
    
    if use_simulation:
        judge = SimulatedJudge()
    else:
        judge = BlindJudge(api_key)
    
    judged_responses = []
    
    for i, subj_resp in enumerate(subject_responses):
        judged = judge.classify(subj_resp)
        judged_responses.append(judged)
        
        if (i + 1) % 50 == 0:
            print(f"  Classified {i + 1}/{len(subject_responses)} responses")
    
    print(f"  Total judge API calls: {judge.total_calls}")
    
    # -------------------------------------------------------------------------
    # Save raw results (still blinded)
    # -------------------------------------------------------------------------
    results = {
        "experiment": "Double-Blind Hysteresis",
        "timestamp": datetime.now().isoformat(),
        "seed": randomizer.seed,
        "trials_per_cell": trials_per_cell,
        "total_trials": len(trials),
        "subject_calls": subject.total_calls,
        "subject_tokens": subject.total_tokens,
        "judge_calls": judge.total_calls,
        "judge_tokens": judge.total_tokens,
        "trials": [],
    }
    
    # Merge trial info with responses (still blinded - no true condition)
    trial_lookup = {t.trial_id: t for t in trials}
    response_lookup = {r.trial_id: r for r in judged_responses}
    
    for trial in trials:
        judged = response_lookup[trial.trial_id]
        results["trials"].append({
            "trial_id": trial.trial_id,
            "scenario_level": trial.scenario_level,
            "condition_code": trial.condition_code,  # Still blinded!
            "raw_response": judged.raw_response,
            "classification": judged.classification,
            "judge_confidence": judged.judge_confidence,
        })
    
    results_file = output_path / "blinded_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Blinded results saved to: {results_file}")
    
    # -------------------------------------------------------------------------
    # PHASE 5: Unblinding and analysis
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("PHASE 5: Unblinding and analysis")
    print("-" * 70)
    
    analyzer = Analyzer(str(mapping_file))
    analysis = analyzer.analyze(str(results_file))
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print("\nPer-level statistics:")
    print(f"{'Level':<6} {'P(O|busy)':<12} {'P(O|free)':<12} {'Effect':<10} {'p-value':<10} {'Sig?'}")
    print("-" * 60)
    
    for s in analysis["level_statistics"]:
        p_busy = s.get('p_O_busy_context', 0) or 0
        p_free = s.get('p_O_free_context', 0) or 0
        effect = s.get('hysteresis_effect', 0) or 0
        p_val = s.get('p_value')
        sig = '***' if s.get('significant') else ''
        
        p_val_str = f"{p_val:.4f}" if p_val is not None else "N/A"
        print(f"{s['level']:<6} {p_busy:<12.3f} {p_free:<12.3f} {effect:<+10.3f} {p_val_str:<10} {sig}")
    
    print(f"\nMean effect (ambiguous levels 2-4): {analysis['mean_hysteresis_effect_middle']:+.3f}")
    print(f"Significant levels (2-4): {analysis['significant_levels_middle']}/3")
    print(f"\nINTERPRETATION: {analysis['interpretation']}")
    
    # Save final analysis
    final_output = {
        **results,
        "analysis": analysis,
    }
    
    final_file = output_path / "final_analysis.json"
    with open(final_file, 'w') as f:
        json.dump(final_output, f, indent=2, default=str)
    print(f"\nFinal analysis saved to: {final_file}")
    
    # Cost estimate
    total_tokens = subject.total_tokens + judge.total_tokens
    cost = total_tokens * 0.000018  # Rough estimate
    print(f"\nTotal tokens: {total_tokens:,}")
    print(f"Estimated cost: ${cost:.2f}")
    
    return final_output


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Double-blind hysteresis experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This experiment uses proper double-blind methodology:
  1. Randomized, blinded condition codes
  2. Hypothesis-blind prompt generation
  3. Fresh API session per trial
  4. Separate blind judge for classification
  5. Unblinding only at analysis phase

Examples:
  # Simulation mode (free, for testing)
  python hysteresis_double_blind.py --simulate --trials 10

  # Live API
  python hysteresis_double_blind.py --api-key sk-ant-... --trials 15
        """
    )
    
    parser.add_argument('--api-key', type=str, default=None,
                        help='Anthropic API key')
    parser.add_argument('--trials', type=int, default=10,
                        help='Trials per cell (total = 7 levels × 3 conditions × trials)')
    parser.add_argument('--output', type=str, default='hysteresis_experiment',
                        help='Output directory')
    parser.add_argument('--simulate', action='store_true',
                        help='Use simulation instead of live API')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    if not args.simulate and not args.api_key:
        parser.error("--api-key required unless using --simulate")
    
    total_trials = 7 * 3 * args.trials
    total_calls = total_trials * 2  # subject + judge
    est_cost = total_calls * 300 * 0.000018
    
    print(f"Total trials: {total_trials}")
    print(f"Total API calls: {total_calls}")
    print(f"Estimated cost: ${est_cost:.2f}")
    print()
    
    run_experiment(
        api_key=args.api_key,
        trials_per_cell=args.trials,
        output_dir=args.output,
        use_simulation=args.simulate,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
