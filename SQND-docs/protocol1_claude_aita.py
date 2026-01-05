#!/usr/bin/env python3
"""
Protocol 1: Bond-Type Rotation Experiment (Claude API Version)
===============================================================

Non-Abelian Stratified Quantum Normative Dynamics (NA-SQND)
Experimental Test Using Claude as Evaluator on AITA Dataset

This script uses Claude to evaluate moral scenarios from the AITA 
(Am I The Asshole) dataset, measuring bond-type rotation across
different threshold conditions.

Usage:
    python protocol1_claude_aita.py --api-key YOUR_KEY --model claude-sonnet-4-20250514
    python protocol1_claude_aita.py --api-key YOUR_KEY --model claude-sonnet-4-20250514 --dataset aita_150.json

Author: Andrew H. Bond
Version: 1.0
Date: January 2026
"""

import argparse
import json
import os
import sys
import time
import random
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
import numpy as np
import pandas as pd
from scipy import stats

# Try to import anthropic, install if needed
try:
    import anthropic
except ImportError:
    print("Installing anthropic package...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic", "--break-system-packages", "-q"])
    import anthropic


# =============================================================================
# SECTION 1: CORE DATA STRUCTURES
# =============================================================================

class BondType(Enum):
    """Hohfeldian incident relations."""
    OBLIGATION = "O"
    CLAIM = "C"
    LIBERTY = "L"
    NO_CLAIM = "N"
    
    @classmethod
    def from_string(cls, s: str) -> 'BondType':
        """Parse bond type from string."""
        s = s.strip().upper()
        if s in ['O', 'OBLIGATION', 'DUTY']:
            return cls.OBLIGATION
        elif s in ['C', 'CLAIM', 'RIGHT']:
            return cls.CLAIM
        elif s in ['L', 'LIBERTY', 'PERMISSION', 'FREE']:
            return cls.LIBERTY
        elif s in ['N', 'NO_CLAIM', 'NO-CLAIM', 'NO CLAIM', 'NOCLAIM']:
            return cls.NO_CLAIM
        else:
            raise ValueError(f"Unknown bond type: {s}")


@dataclass
class AITAScenario:
    """Represents an AITA scenario."""
    id: str
    title: str
    text: str
    label: str  # Original AITA label (YTA, NTA, ESH, NAH, INFO)
    agent_a: str = "the poster"  # The person asking AITA
    agent_b: str = "the other party"  # The other person in conflict
    
    def get_context_description(self) -> str:
        """Extract key context for the scenario."""
        return self.text[:500] + "..." if len(self.text) > 500 else self.text


@dataclass 
class ThresholdCondition:
    """Represents a threshold manipulation."""
    name: str  # "control", "weak", "strong"
    description: str
    prompt_modifier: str


# Define threshold conditions
THRESHOLD_CONDITIONS = {
    "control": ThresholdCondition(
        name="control",
        description="No additional context (baseline evaluation)",
        prompt_modifier=""
    ),
    "weak": ThresholdCondition(
        name="weak",
        description="Minor context shift - other party's perspective",
        prompt_modifier="""
Additionally, consider that the other party has explained their perspective 
and their actions were based on a misunderstanding of the situation. They 
did not intend any harm and have expressed willingness to discuss the matter.
"""
    ),
    "strong": ThresholdCondition(
        name="strong", 
        description="Major context shift - circumstances fundamentally changed",
        prompt_modifier="""
IMPORTANT UPDATE: New information has come to light that fundamentally changes 
the situation. The other party was acting under significant personal distress 
(a family emergency) that the poster was unaware of. The other party has since 
apologized and explained the circumstances. The immediate conflict has been 
resolved, and both parties have moved on.
"""
    )
}


@dataclass
class EvaluationResult:
    """Result from a single Claude evaluation."""
    scenario_id: str
    condition: str
    bond_type: BondType
    confidence: float
    reasoning: str
    raw_response: str
    timestamp: datetime = field(default_factory=datetime.now)
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass
class ExperimentResults:
    """Container for all experiment results."""
    evaluations: List[EvaluationResult]
    scenarios: List[AITAScenario]
    config: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime] = None
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame."""
        records = []
        for ev in self.evaluations:
            records.append({
                'scenario_id': ev.scenario_id,
                'condition': ev.condition,
                'bond_type': ev.bond_type.value,
                'confidence': ev.confidence,
                'reasoning': ev.reasoning[:200],
                'model': ev.model,
                'prompt_tokens': ev.prompt_tokens,
                'completion_tokens': ev.completion_tokens,
            })
        return pd.DataFrame(records)
    
    def save(self, filepath: str):
        """Save results to JSON."""
        data = {
            'config': self.config,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'scenarios': [asdict(s) for s in self.scenarios],
            'evaluations': [
                {
                    **asdict(e),
                    'bond_type': e.bond_type.value,
                    'timestamp': e.timestamp.isoformat()
                }
                for e in self.evaluations
            ]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# =============================================================================
# SECTION 2: SAMPLE AITA DATASET
# =============================================================================

def get_sample_aita_dataset() -> List[AITAScenario]:
    """
    Returns a sample AITA dataset for testing.
    Replace this with actual dataset loading.
    """
    samples = [
        AITAScenario(
            id="aita_001",
            title="AITA for not attending my sister's wedding?",
            text="""My sister is getting married next month. She's been planning this for over a year. 
However, she scheduled it on the same weekend as my PhD dissertation defense, which I scheduled 
6 months ago and cannot change. I told her about the conflict when she first announced the date, 
but she said I should reschedule my defense. My parents are furious with me for 'choosing my 
career over family.' My sister hasn't spoken to me in weeks. I feel terrible but I can't just 
reschedule a dissertation defense that involves 5 committee members' schedules.""",
            label="NTA",
            agent_a="the poster (PhD student)",
            agent_b="the sister (bride)"
        ),
        AITAScenario(
            id="aita_002", 
            title="AITA for refusing to lend money to my brother?",
            text="""My brother asked me to lend him $5000 for a 'business opportunity.' He has a 
history of failed ventures and still owes me $2000 from three years ago. When I said no, he 
called me selfish and said family should help family. Our parents are pressuring me to help him 
because 'he's trying to better himself.' I make good money but I'm also saving for a house.""",
            label="NTA",
            agent_a="the poster",
            agent_b="the brother"
        ),
        AITAScenario(
            id="aita_003",
            title="AITA for telling my roommate to stop having loud parties?",
            text="""My roommate has loud parties every weekend, sometimes going until 3-4 AM. I work 
early shifts and need sleep. I've asked nicely multiple times but nothing changes. Last weekend 
I finally snapped and told all the guests to leave at midnight. My roommate is now saying I 
embarrassed them and ruined their social life. We're both on the lease equally.""",
            label="NTA",
            agent_a="the poster",
            agent_b="the roommate"
        ),
        AITAScenario(
            id="aita_004",
            title="AITA for not sharing my inheritance with siblings?",
            text="""My grandmother left me her house in her will (valued at ~$400k). My siblings got 
cash amounts of $50k each. They're upset that I got 'more' and want me to sell the house and 
split everything equally. But grandma specifically left me the house because I was her caretaker 
for the last 5 years while my siblings rarely visited. They say I'm being greedy.""",
            label="NTA",
            agent_a="the poster",
            agent_b="the siblings"
        ),
        AITAScenario(
            id="aita_005",
            title="AITA for reporting my coworker for time theft?",
            text="""I noticed my coworker regularly clocks in then leaves for 1-2 hours for 'errands' 
while staying on the clock. This has been going on for months. I mentioned it to our manager 
who investigated and my coworker got written up. Now everyone in the office is calling me a 
snitch and saying I should have minded my own business. But we all get the same hourly wage 
and it felt unfair.""",
            label="ESH",
            agent_a="the poster",
            agent_b="the coworker"
        ),
        AITAScenario(
            id="aita_006",
            title="AITA for refusing to cook separate meals for my picky husband?",
            text="""My husband is extremely picky - he won't eat vegetables, most proteins, or anything 
'ethnic.' I've been cooking two separate dinners every night for years. I finally told him I'm 
done and he can make his own food or eat what I make. He says I'm being unreasonable and that 
cooking for your spouse is basic relationship stuff. I'm exhausted from working full time and 
being the sole cook.""",
            label="NTA",
            agent_a="the poster (wife)",
            agent_b="the husband"
        ),
        AITAScenario(
            id="aita_007",
            title="AITA for not letting my parents move in with me?",
            text="""My parents want to move in with me to save money for retirement. I have a 3-bedroom 
house and live alone. But my parents are very controlling and critical - living with them as an 
adult was miserable. I offered to help them find affordable housing instead. They're calling me 
ungrateful after everything they did for me growing up.""",
            label="NTA",
            agent_a="the poster",
            agent_b="the parents"
        ),
        AITAScenario(
            id="aita_008",
            title="AITA for telling my friend her wedding dress is ugly?",
            text="""My best friend showed me her wedding dress and asked for my honest opinion. It's 
objectively unflattering - wrong color for her skin tone, emphasizes areas she's self-conscious 
about, and looks cheap despite being expensive. I gently said it might not be the most flattering 
choice. She burst into tears and said I ruined her excitement. She already bought it 
non-refundable.""",
            label="YTA",
            agent_a="the poster",
            agent_b="the friend (bride)"
        ),
        AITAScenario(
            id="aita_009",
            title="AITA for leaving my boyfriend at a restaurant?",
            text="""My boyfriend made a sexist joke at dinner with his friends. When I didn't laugh, 
he doubled down and made another one 'to lighten the mood.' I said I was leaving. He laughed and 
said I was overreacting. I took an Uber home, leaving him there. He had to get a ride from his 
friends and is furious. His friends think I made a scene over nothing.""",
            label="NTA",
            agent_a="the poster (girlfriend)",
            agent_b="the boyfriend"
        ),
        AITAScenario(
            id="aita_010",
            title="AITA for not going to my nephew's birthday party?",
            text="""My sister expects everyone to attend every single one of her kids' events - 
birthdays, school plays, sports games, everything. She has 4 kids and there's something almost 
every weekend. I told her I can't make it to my nephew's 7th birthday because I have plans with 
friends I haven't seen in months. She's accusing me of not caring about family.""",
            label="NTA",
            agent_a="the poster",
            agent_b="the sister"
        ),
        AITAScenario(
            id="aita_011",
            title="AITA for refusing to give up my seat on a plane?",
            text="""I paid extra for an aisle seat on a long flight due to a medical condition 
(blood clot risk - need to move frequently). A mother asked me to switch with her middle seat 
so she could sit with her kids. I explained my medical need and offered to help in other ways, 
but refused to switch. She loudly called me selfish and the flight attendant looked at me 
disapprovingly.""",
            label="NTA",
            agent_a="the poster",
            agent_b="the mother"
        ),
        AITAScenario(
            id="aita_012",
            title="AITA for telling my daughter she can't have a pony?",
            text="""My 8-year-old daughter desperately wants a pony. We live in the suburbs with a 
small backyard - nowhere to keep a pony. I explained this but she says I'm 'ruining her dreams.' 
My wife thinks I should have softened the blow somehow instead of saying a flat no. Daughter 
hasn't spoken to me properly in days.""",
            label="NTA",
            agent_a="the poster (father)",
            agent_b="the daughter"
        ),
    ]
    
    # Extend to 15+ scenarios for meaningful analysis
    more_samples = [
        AITAScenario(
            id="aita_013",
            title="AITA for not tipping on a takeout order?",
            text="""I ordered takeout and the tablet suggested 20-30% tip for an order I picked up 
myself. I selected 'no tip' and the cashier gave me a dirty look. My friend said I was cheap. 
But I literally just picked up a bag - no one served me or brought food to my table. I always 
tip for dine-in and delivery.""",
            label="NTA",
            agent_a="the poster",
            agent_b="the restaurant staff"
        ),
        AITAScenario(
            id="aita_014",
            title="AITA for calling the police on my neighbor's dog?",
            text="""My neighbor's dog barks constantly - early morning, late night, whenever they're 
not home (which is often). I've asked them multiple times to address it. They said dogs bark and 
I should deal with it. After 6 months, I filed a noise complaint. Now they're furious and calling 
me a bad neighbor who could have gotten their dog taken away.""",
            label="NTA",
            agent_a="the poster",
            agent_b="the neighbor"
        ),
        AITAScenario(
            id="aita_015",
            title="AITA for reading my teenager's diary?",
            text="""I found my 15-year-old's diary and read it because I was worried about their 
behavior changes lately. I found they've been vaping and lying about where they go. When I 
confronted them, they were more upset about the privacy violation than anything. My spouse 
thinks I went too far. I think I had a right to know what's going on with my child.""",
            label="ESH",
            agent_a="the poster (parent)",
            agent_b="the teenager"
        ),
    ]
    
    return samples + more_samples


def load_aita_dataset(filepath: str) -> List[AITAScenario]:
    """
    Load AITA dataset from JSON or CSV file.
    
    Expected JSON format:
    [
        {
            "id": "aita_001",
            "title": "AITA for...",
            "text": "Full scenario text...",
            "label": "NTA"
        },
        ...
    ]
    
    Expected CSV format:
    post_id, post_content, post_title, verdict
    """
    scenarios = []
    
    if filepath.endswith('.csv'):
        # Load from CSV
        df = pd.read_csv(filepath)
        
        # Handle different column name conventions
        id_col = next((c for c in df.columns if c.lower() in ['post_id', 'id']), df.columns[0])
        content_col = next((c for c in df.columns if c.lower() in ['post_content', 'text', 'body', 'content']), df.columns[1])
        title_col = next((c for c in df.columns if c.lower() in ['post_title', 'title']), None)
        label_col = next((c for c in df.columns if c.lower() in ['verdict', 'label', 'judgment']), None)
        
        for idx, row in df.iterrows():
            text = str(row[content_col]) if pd.notna(row[content_col]) else ""
            # Clean up text
            text = text.replace('\\n', '\n').replace('\\r', '')
            
            scenarios.append(AITAScenario(
                id=str(row[id_col]) if pd.notna(row[id_col]) else f"aita_{idx:03d}",
                title=str(row[title_col]) if title_col and pd.notna(row[title_col]) else "AITA scenario",
                text=text,
                label=str(row[label_col]) if label_col and pd.notna(row[label_col]) else "UNKNOWN",
                agent_a="the poster",
                agent_b="the other party"
            ))
    else:
        # Load from JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for item in data:
            scenarios.append(AITAScenario(
                id=item.get('id', f"aita_{len(scenarios):03d}"),
                title=item.get('title', 'AITA scenario'),
                text=item.get('text', item.get('body', item.get('content', ''))),
                label=item.get('label', item.get('verdict', 'UNKNOWN')),
                agent_a=item.get('agent_a', 'the poster'),
                agent_b=item.get('agent_b', 'the other party')
            ))
    
    return scenarios


# =============================================================================
# SECTION 3: CLAUDE EVALUATOR
# =============================================================================


class SimulatedEvaluator:
    """
    Simulates Claude responses for testing without API access.
    Uses NA-SQND theory to generate realistic synthetic responses.
    """
    
    def __init__(self, model: str = "simulated"):
        self.model = model
        self.request_count = 0
        self.total_tokens = 0
        
        # Theoretical rotation angles by condition
        self.theta_by_condition = {
            'control': 0.0,      # No rotation - mostly O
            'weak': np.pi / 6,   # 30° - some shift to L
            'strong': np.pi / 3  # 60° - significant shift to L/N
        }
    
    def create_evaluation_prompt(self, scenario: AITAScenario, condition: ThresholdCondition) -> str:
        """Create prompt (for logging purposes)."""
        return f"[SIMULATED] Scenario: {scenario.id}, Condition: {condition.name}"
    
    def evaluate_scenario(
        self,
        scenario: AITAScenario,
        condition: ThresholdCondition,
        retry_count: int = 3
    ) -> EvaluationResult:
        """Simulate an evaluation based on NA-SQND theory."""
        
        self.request_count += 1
        self.total_tokens += 600  # Simulated token count
        
        # Get theoretical theta for this condition
        theta = self.theta_by_condition.get(condition.name, 0.0)
        
        # Add scenario-specific variation based on original verdict
        verdict_adjustment = {
            'NTA': -0.1,   # Poster more justified -> more O
            'YTA': 0.2,    # Poster less justified -> more L/N
            'ESH': 0.1,    # Mixed -> slight shift
            'NAH': 0.0,    # No conflict -> neutral
        }
        theta += verdict_adjustment.get(scenario.label, 0.0)
        
        # Add random variation
        theta += np.random.normal(0, 0.15)
        theta = max(0, min(np.pi, theta))
        
        # Compute probabilities based on POVM
        eta = 0.75  # Salience parameter
        p_O_slot = np.cos(theta / 2) ** 2
        p_C_slot = np.sin(theta / 2) ** 2
        
        probs = {
            BondType.OBLIGATION: (1 + eta) / 2 * p_O_slot,
            BondType.LIBERTY: (1 - eta) / 2 * p_O_slot,
            BondType.CLAIM: (1 + eta) / 2 * p_C_slot,
            BondType.NO_CLAIM: (1 - eta) / 2 * p_C_slot,
        }
        
        # Sample response
        bond_types = list(probs.keys())
        prob_values = [probs[bt] for bt in bond_types]
        prob_values = np.array(prob_values) / sum(prob_values)  # Normalize
        
        selected = np.random.choice(bond_types, p=prob_values)
        
        # Generate reasoning
        reasoning_templates = {
            BondType.OBLIGATION: "The poster has a clear duty based on the relationship described.",
            BondType.CLAIM: "The other party has a legitimate claim arising from the situation.",
            BondType.LIBERTY: "Given the circumstances, the poster is free to act as they did.",
            BondType.NO_CLAIM: "The other party cannot demand anything from the poster here.",
        }
        
        return EvaluationResult(
            scenario_id=scenario.id,
            condition=condition.name,
            bond_type=selected,
            confidence=0.7 + np.random.uniform(0, 0.25),
            reasoning=reasoning_templates[selected],
            raw_response=f"[SIMULATED] {selected.value}",
            model=self.model,
            prompt_tokens=500,
            completion_tokens=100
        )


class ClaudeEvaluator:
    """Uses Claude to evaluate moral scenarios according to SQND framework."""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.request_count = 0
        self.total_tokens = 0
        
    def create_evaluation_prompt(
        self, 
        scenario: AITAScenario, 
        condition: ThresholdCondition
    ) -> str:
        """Create the evaluation prompt for Claude."""
        
        prompt = f"""You are evaluating a moral scenario using the Hohfeldian framework of jural relations.

SCENARIO:
{scenario.text}

{condition.prompt_modifier}

YOUR TASK:
Analyze the moral relationship between {scenario.agent_a} and {scenario.agent_b}.

Using Hohfeldian analysis, classify the PRIMARY moral relation as ONE of:

**O (OBLIGATION/DUTY)**: {scenario.agent_a} has a duty/obligation toward {scenario.agent_b}
**C (CLAIM/RIGHT)**: {scenario.agent_b} has a claim/right against {scenario.agent_a}  
**L (LIBERTY/PERMISSION)**: {scenario.agent_a} is free/permitted to act as they did (no duty)
**N (NO-CLAIM)**: {scenario.agent_b} has no claim/right against {scenario.agent_a}

Think carefully about who owes what to whom. Consider the correlative structure:
- If A has a DUTY to B, then B has a CLAIM against A
- If A has LIBERTY toward B, then B has NO-CLAIM against A

Focus on the CURRENT moral relationship given ALL the information provided.

Respond in this exact format:
CLASSIFICATION: [O/C/L/N]
CONFIDENCE: [0.0-1.0]
REASONING: [2-3 sentences explaining your classification]
"""
        return prompt
    
    def evaluate_scenario(
        self,
        scenario: AITAScenario,
        condition: ThresholdCondition,
        retry_count: int = 3
    ) -> EvaluationResult:
        """Evaluate a single scenario under a given condition."""
        
        prompt = self.create_evaluation_prompt(scenario, condition)
        
        for attempt in range(retry_count):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                self.request_count += 1
                raw_text = response.content[0].text
                
                # Parse response
                result = self.parse_response(raw_text, scenario.id, condition.name)
                result.model = self.model
                result.raw_response = raw_text
                result.prompt_tokens = response.usage.input_tokens
                result.completion_tokens = response.usage.output_tokens
                self.total_tokens += result.prompt_tokens + result.completion_tokens
                
                return result
                
            except anthropic.RateLimitError:
                wait_time = 2 ** attempt * 10
                print(f"  Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            except Exception as e:
                print(f"  Error on attempt {attempt + 1}: {e}")
                if attempt == retry_count - 1:
                    return EvaluationResult(
                        scenario_id=scenario.id,
                        condition=condition.name,
                        bond_type=BondType.LIBERTY,
                        confidence=0.0,
                        reasoning=f"Error: {str(e)}",
                        raw_response=""
                    )
                time.sleep(2)
        
        raise RuntimeError("Evaluation failed after all retries")
    
    def parse_response(
        self, 
        response: str, 
        scenario_id: str, 
        condition: str
    ) -> EvaluationResult:
        """Parse Claude's response into structured result."""
        
        lines = response.strip().split('\n')
        
        bond_type = BondType.LIBERTY
        confidence = 0.5
        reasoning = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('CLASSIFICATION:'):
                type_str = line.replace('CLASSIFICATION:', '').strip()
                try:
                    bond_type = BondType.from_string(type_str)
                except ValueError:
                    for char in type_str:
                        if char.upper() in 'OCLN':
                            bond_type = BondType.from_string(char)
                            break
            elif line.startswith('CONFIDENCE:'):
                try:
                    conf_str = line.replace('CONFIDENCE:', '').strip()
                    confidence = float(conf_str)
                    confidence = max(0.0, min(1.0, confidence))
                except ValueError:
                    confidence = 0.5
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
        
        if not reasoning:
            for i, line in enumerate(lines):
                if 'REASONING:' in line:
                    reasoning = ' '.join(lines[i:]).replace('REASONING:', '').strip()
                    break
        
        return EvaluationResult(
            scenario_id=scenario_id,
            condition=condition,
            bond_type=bond_type,
            confidence=confidence,
            reasoning=reasoning,
            raw_response=response
        )

# =============================================================================
# SECTION 4: EXPERIMENT RUNNER
# =============================================================================

class Protocol1Experiment:
    """Runs the full Protocol 1 experiment using Claude."""
    
    def __init__(
        self,
        evaluator: ClaudeEvaluator,
        scenarios: List[AITAScenario],
        conditions: List[str] = None,
        n_repetitions: int = 1
    ):
        self.evaluator = evaluator
        self.scenarios = scenarios
        self.conditions = conditions or ["control", "weak", "strong"]
        self.n_repetitions = n_repetitions
        self.results: List[EvaluationResult] = []
        
    def run(self, progress_callback=None) -> ExperimentResults:
        """Run the full experiment."""
        
        start_time = datetime.now()
        total_evals = len(self.scenarios) * len(self.conditions) * self.n_repetitions
        completed = 0
        
        print("\nRunning Protocol 1 Experiment")
        print(f"  Scenarios: {len(self.scenarios)}")
        print(f"  Conditions: {self.conditions}")
        print(f"  Repetitions: {self.n_repetitions}")
        print(f"  Total evaluations: {total_evals}")
        print()
        
        for rep in range(self.n_repetitions):
            if self.n_repetitions > 1:
                print(f"Repetition {rep + 1}/{self.n_repetitions}")
            
            # Randomize order
            scenario_order = list(self.scenarios)
            random.shuffle(scenario_order)
            
            for scenario in scenario_order:
                for condition_name in self.conditions:
                    condition = THRESHOLD_CONDITIONS[condition_name]
                    
                    print(f"  [{completed+1}/{total_evals}] {scenario.id} - {condition_name}...", end=" ")
                    
                    result = self.evaluator.evaluate_scenario(scenario, condition)
                    self.results.append(result)
                    
                    print(f"{result.bond_type.value} (conf: {result.confidence:.2f})")
                    
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total_evals)
                    
                    # Small delay to avoid rate limits
                    time.sleep(0.5)
        
        end_time = datetime.now()
        
        return ExperimentResults(
            evaluations=self.results,
            scenarios=self.scenarios,
            config={
                'model': self.evaluator.model,
                'conditions': self.conditions,
                'n_repetitions': self.n_repetitions,
                'n_scenarios': len(self.scenarios),
                'total_requests': self.evaluator.request_count,
                'total_tokens': self.evaluator.total_tokens,
            },
            start_time=start_time,
            end_time=end_time
        )


# =============================================================================
# SECTION 5: ANALYSIS
# =============================================================================

def estimate_theta_from_responses(responses: List[BondType], bootstrap: bool = True) -> Tuple[float, float]:
    """
    Estimate mixing angle θ from response distribution.
    
    θ̂ = 2·arctan(√[(P(C) + P(N)) / (P(O) + P(L))])
    """
    counts = {bt: 0 for bt in BondType}
    for r in responses:
        counts[r] += 1
    
    n = len(responses)
    if n == 0:
        return 0.0, np.inf
    
    p_O = counts[BondType.OBLIGATION] / n
    p_L = counts[BondType.LIBERTY] / n
    p_C = counts[BondType.CLAIM] / n
    p_N = counts[BondType.NO_CLAIM] / n
    
    denom = p_O + p_L
    numer = p_C + p_N
    
    if denom < 1e-10:
        theta = np.pi
    elif numer < 1e-10:
        theta = 0.0
    else:
        theta = 2 * np.arctan(np.sqrt(numer / denom))
    
    # Bootstrap SE (only if requested and enough samples)
    if bootstrap and n >= 5:
        theta_samples = []
        for _ in range(500):
            sample = random.choices(responses, k=n)
            # Call without bootstrap to avoid recursion
            t, _ = estimate_theta_from_responses(sample, bootstrap=False)
            theta_samples.append(t)
        se = np.std(theta_samples)
    else:
        se = np.inf
    
    return theta, se


def analyze_results(results: ExperimentResults) -> Dict[str, Any]:
    """Analyze experiment results."""
    
    df = results.to_dataframe()
    
    analysis = {
        'n_evaluations': len(df),
        'conditions': {},
        'comparisons': [],
        'falsification': {}
    }
    
    # Analyze each condition
    for condition in df['condition'].unique():
        subset = df[df['condition'] == condition]
        responses = [BondType.from_string(r) for r in subset['bond_type']]
        
        theta, se = estimate_theta_from_responses(responses)
        
        # Response distribution
        counts = subset['bond_type'].value_counts().to_dict()
        
        analysis['conditions'][condition] = {
            'n': len(subset),
            'theta': theta,
            'theta_se': se,
            'theta_degrees': np.degrees(theta),
            'distribution': counts,
            'mean_confidence': subset['confidence'].mean()
        }
    
    # Compare conditions (control vs threshold)
    conditions_list = list(analysis['conditions'].keys())
    
    if 'control' in conditions_list:
        control_data = analysis['conditions']['control']
        
        for cond in conditions_list:
            if cond == 'control':
                continue
            
            cond_data = analysis['conditions'][cond]
            delta_theta = cond_data['theta'] - control_data['theta']
            
            # Get response lists for statistical test
            control_responses = df[df['condition'] == 'control']['bond_type'].values
            cond_responses = df[df['condition'] == cond]['bond_type'].values
            
            # Chi-square test for distribution difference
            control_counts = pd.Series(control_responses).value_counts()
            cond_counts = pd.Series(cond_responses).value_counts()
            
            # Align indices
            all_types = list(set(control_counts.index) | set(cond_counts.index))
            control_aligned = [control_counts.get(t, 0) for t in all_types]
            cond_aligned = [cond_counts.get(t, 0) for t in all_types]
            
            if sum(control_aligned) > 0 and sum(cond_aligned) > 0:
                chi2, p_value = stats.chisquare(
                    cond_aligned, 
                    f_exp=[c * sum(cond_aligned) / sum(control_aligned) for c in control_aligned]
                )
            else:
                chi2, p_value = 0, 1.0
            
            analysis['comparisons'].append({
                'comparison': f"control vs {cond}",
                'delta_theta': delta_theta,
                'delta_theta_degrees': np.degrees(delta_theta),
                'chi2': chi2,
                'p_value': p_value,
                'significant': p_value < 0.05
            })
    
    # Falsification criteria
    if len(analysis['comparisons']) >= 2:
        weak_sig = any(c['significant'] for c in analysis['comparisons'] if 'weak' in c['comparison'])
        strong_sig = any(c['significant'] for c in analysis['comparisons'] if 'strong' in c['comparison'])
        
        # Check for graded response (strong > weak > control)
        thetas = {k: v['theta'] for k, v in analysis['conditions'].items()}
        graded = True
        if 'control' in thetas and 'weak' in thetas:
            graded = graded and (thetas['weak'] >= thetas['control'] - 0.1)
        if 'weak' in thetas and 'strong' in thetas:
            graded = graded and (thetas['strong'] >= thetas['weak'] - 0.1)
        
        analysis['falsification'] = {
            'no_threshold_effect': not (weak_sig or strong_sig),
            'no_graded_response': not graded,
            'theory_falsified': not (weak_sig or strong_sig) or not graded
        }
    
    return analysis


def print_analysis_report(analysis: Dict[str, Any], results: ExperimentResults):
    """Print formatted analysis report."""
    
    print("\n" + "=" * 70)
    print("PROTOCOL 1: BOND-TYPE ROTATION - ANALYSIS REPORT (CLAUDE API)")
    print("=" * 70)
    
    print(f"\nModel: {results.config['model']}")
    print(f"Total evaluations: {analysis['n_evaluations']}")
    print(f"Total API tokens: {results.config['total_tokens']}")
    print(f"Duration: {results.end_time - results.start_time}")
    
    print("\n" + "-" * 40)
    print("RESULTS BY CONDITION")
    print("-" * 40)
    
    for condition, data in analysis['conditions'].items():
        print(f"\n{condition.upper()}:")
        print(f"  N = {data['n']}")
        print(f"  θ = {data['theta']:.4f} rad ({data['theta_degrees']:.1f}°)")
        print(f"  SE = {data['theta_se']:.4f}")
        print(f"  Mean confidence = {data['mean_confidence']:.2f}")
        print(f"  Distribution: {data['distribution']}")
    
    if analysis['comparisons']:
        print("\n" + "-" * 40)
        print("CONDITION COMPARISONS")
        print("-" * 40)
        
        for comp in analysis['comparisons']:
            print(f"\n{comp['comparison']}:")
            print(f"  Δθ = {comp['delta_theta']:.4f} rad ({comp['delta_theta_degrees']:.1f}°)")
            print(f"  χ² = {comp['chi2']:.2f}, p = {comp['p_value']:.4f}")
            print(f"  Significant: {comp['significant']}")
    
    if analysis['falsification']:
        print("\n" + "-" * 40)
        print("FALSIFICATION ASSESSMENT")
        print("-" * 40)
        
        for criterion, value in analysis['falsification'].items():
            status = "FALSIFIED" if value else "NOT FALSIFIED"
            print(f"  {criterion}: {status}")
    
    print("\n" + "=" * 70)
    print("END OF REPORT")
    print("=" * 70)


# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

def create_visualizations(analysis: Dict[str, Any], output_dir: str = '.'):
    """Create visualization plots."""
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("Matplotlib/seaborn not available, skipping visualizations")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Figure 1: Theta by condition
    fig, ax = plt.subplots(figsize=(10, 6))
    
    conditions = list(analysis['conditions'].keys())
    thetas = [analysis['conditions'][c]['theta'] for c in conditions]
    ses = [analysis['conditions'][c]['theta_se'] for c in conditions]
    
    colors = {'control': '#2ecc71', 'weak': '#f39c12', 'strong': '#e74c3c'}
    bar_colors = [colors.get(c, '#3498db') for c in conditions]
    
    bars = ax.bar(conditions, thetas, yerr=ses, capsize=5, color=bar_colors, 
                  edgecolor='black', alpha=0.7)
    
    # Add theoretical predictions
    theoretical = {'control': 0, 'weak': np.pi/6, 'strong': np.pi/3}
    for i, cond in enumerate(conditions):
        if cond in theoretical:
            ax.scatter(i, theoretical[cond], marker='*', s=200, color='black', 
                      zorder=5, label='Theoretical' if i == 0 else '')
    
    ax.set_ylabel('θ (Mixing Angle, radians)', fontsize=12)
    ax.set_xlabel('Condition', fontsize=12)
    ax.set_title('Protocol 1: Bond-Type Rotation by Threshold Condition', fontsize=14)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'theta_by_condition.png'), dpi=300)
    plt.close()
    
    # Figure 2: Response distributions
    fig, axes = plt.subplots(1, len(conditions), figsize=(5*len(conditions), 5))
    if len(conditions) == 1:
        axes = [axes]
    
    for ax, condition in zip(axes, conditions):
        dist = analysis['conditions'][condition]['distribution']
        types = ['O', 'C', 'L', 'N']
        counts = [dist.get(t, 0) for t in types]
        total = sum(counts)
        props = [c/total if total > 0 else 0 for c in counts]
        
        colors_dist = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6']
        ax.bar(types, props, color=colors_dist, edgecolor='black')
        ax.set_ylim(0, 1)
        ax.set_xlabel('Bond Type')
        ax.set_ylabel('Proportion')
        ax.set_title(f'{condition.capitalize()}')
    
    fig.suptitle('Response Distributions by Condition', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'distributions.png'), dpi=300)
    plt.close()
    
    print(f"Visualizations saved to {output_dir}/")


# =============================================================================
# SECTION 7: MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Protocol 1: Bond-Type Rotation Experiment using Claude API'
    )
    parser.add_argument(
        '--api-key', 
        type=str, 
        required=False,
        default=None,
        help='Anthropic API key (not required if using --simulate)'
    )
    parser.add_argument(
        '--model', 
        type=str, 
        default='claude-sonnet-4-20250514',
        help='Claude model to use (default: claude-sonnet-4-20250514)'
    )
    parser.add_argument(
        '--dataset', 
        type=str, 
        default=None,
        help='Path to AITA dataset JSON file (uses sample data if not provided)'
    )
    parser.add_argument(
        '--n-scenarios',
        type=int,
        default=None,
        help='Number of scenarios to use (default: all)'
    )
    parser.add_argument(
        '--repetitions',
        type=int,
        default=1,
        help='Number of repetitions per scenario (default: 1)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='protocol1_results',
        help='Output directory for results (default: protocol1_results)'
    )
    parser.add_argument(
        '--conditions',
        type=str,
        nargs='+',
        default=['control', 'weak', 'strong'],
        help='Conditions to test (default: control weak strong)'
    )
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Run in simulation mode (no API calls, generates synthetic responses)'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load scenarios
    if args.dataset:
        print(f"Loading dataset from {args.dataset}...")
        scenarios = load_aita_dataset(args.dataset)
    else:
        print("Using sample AITA dataset...")
        scenarios = get_sample_aita_dataset()
    
    if args.n_scenarios:
        scenarios = scenarios[:args.n_scenarios]
    
    print(f"Loaded {len(scenarios)} scenarios")
    
    # Initialize evaluator
    if args.simulate:
        print("\n*** SIMULATION MODE - No API calls, using synthetic responses ***\n")
        evaluator = SimulatedEvaluator(model="simulated-na-sqnd")
    else:
        if not args.api_key:
            print("Error: --api-key required (or use --simulate for testing)")
            sys.exit(1)
        evaluator = ClaudeEvaluator(api_key=args.api_key, model=args.model)
    
    # Run experiment
    experiment = Protocol1Experiment(
        evaluator=evaluator,
        scenarios=scenarios,
        conditions=args.conditions,
        n_repetitions=args.repetitions
    )
    
    results = experiment.run()
    
    # Save raw results
    results_file = os.path.join(args.output_dir, 'results.json')
    results.save(results_file)
    print(f"\nResults saved to {results_file}")
    
    # Save as CSV
    df = results.to_dataframe()
    csv_file = os.path.join(args.output_dir, 'results.csv')
    df.to_csv(csv_file, index=False)
    print(f"CSV saved to {csv_file}")
    
    # Analyze
    analysis = analyze_results(results)
    
    # Print report
    print_analysis_report(analysis, results)
    
    # Save analysis
    analysis_file = os.path.join(args.output_dir, 'analysis.json')
    
    # Create a JSON-safe copy of analysis
    def make_json_safe(obj):
        if isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_json_safe(v) for v in obj]
        elif isinstance(obj, tuple):
            return [make_json_safe(v) for v in obj]
        return obj
    
    analysis_safe = make_json_safe(analysis)
    
    with open(analysis_file, 'w') as f:
        json.dump(analysis_safe, f, indent=2)
    print(f"Analysis saved to {analysis_file}")
    
    # Create visualizations
    create_visualizations(analysis, args.output_dir)
    
    print("\nExperiment complete!")
    
    return results, analysis


if __name__ == "__main__":
    main()
