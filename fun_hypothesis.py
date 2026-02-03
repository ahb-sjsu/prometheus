#!/usr/bin/env python3
"""
Prompt Framing Hypothesis Tester
================================

Tests whether different prompt framings affect LLM output quality.

Hypothesis: LLM output quality varies based on how prompts are framed.

Framings to test:
- "fun" - Make it engaging and playful
- "pirate" - Like a pirate  
- "expert" - As a senior expert
- "eli5" - Explain like I'm 5
- "formal" - Very formal and professional
- "socratic" - As questions to explore
- Custom framings via --framing or --framings-csv

Methodology:
1. Get prompts (from dataset, file, or generated)
2. Session A: Send raw prompt to LLM, collect response
3. Session B: Have LLM transform prompt with framing
4. Session C: Send framed prompt to LLM, collect response  
5. Session D: Judge panel evaluates Response A (blind)
6. Session E: Judge panel evaluates Response C (blind)
7. Compare scores, iterate, aggregate, analyze

All sessions are independent (no context leakage).
Judging is double-blind (judges don't know which is framed/raw).
"""

import json
import random
import hashlib
import csv
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import os

# Try to import anthropic, give helpful error if not available
try:
    import anthropic

    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


# Built-in framing styles
FRAMING_STYLES = {
    "fun": {
        "name": "Fun & Engaging",
        "instruction": """Reframe this prompt to be more engaging, playful, and fun - while keeping the 
core task exactly the same. Use collaborative framing ("Let's figure out..."), add playful context, 
express curiosity or enthusiasm. Keep the same task, just make it more engaging.""",
    },
    "pirate": {
        "name": "Pirate Speak",
        "instruction": """Reframe this prompt as if a pirate were asking it. Use pirate language 
("Ahoy!", "me hearty", "shiver me timbers", "ye scurvy dog") but keep the core question exactly 
the same. The task shouldn't change, just the way it's asked.""",
    },
    "expert": {
        "name": "Senior Expert",
        "instruction": """Reframe this prompt as if a senior technical expert were asking a colleague.
Use precise terminology, reference best practices, and frame it as a professional discussion.
The core question stays the same but with expert-level framing.""",
    },
    "eli5": {
        "name": "Explain Like I'm 5",
        "instruction": """Reframe this prompt as if a curious child were asking it. Use simple words,
ask "why" and "how come", express wonder. The question should be simpler but asking for the same thing.""",
    },
    "formal": {
        "name": "Formal & Professional",
        "instruction": """Reframe this prompt in a very formal, professional, academic tone.
Use formal language, proper structure, perhaps reference seeking authoritative information.
The core question remains the same but in formal business/academic style.""",
    },
    "socratic": {
        "name": "Socratic Method",
        "instruction": """Reframe this prompt as a series of probing questions that guide toward
understanding. Instead of asking directly, ask questions that would lead to discovering the answer.
The goal is the same knowledge, but approached through guided inquiry.""",
    },
    "enthusiastic": {
        "name": "Super Enthusiastic",
        "instruction": """Reframe this prompt with EXTREME enthusiasm! Use exclamation points,
express how AMAZING and EXCITING this topic is, convey genuine passion and energy.
Same question, but bursting with excitement!""",
    },
    "skeptical": {
        "name": "Skeptical Questioner",
        "instruction": """Reframe this prompt from a skeptical perspective. Question assumptions,
ask for evidence, express doubt that needs to be addressed. The core question is the same
but framed with healthy skepticism.""",
    },
    "storyteller": {
        "name": "Storyteller",
        "instruction": """Reframe this prompt as if setting up a story or scenario. 
"Imagine you're..." or "Picture this situation..." - make it narrative while keeping
the same underlying question.""",
    },
    "confused": {
        "name": "Genuinely Confused",
        "instruction": """Reframe this prompt as if the asker is genuinely confused and struggling
to understand. Express uncertainty, ask for patience, admit not understanding the basics.
Same question but from a place of honest confusion.""",
    },
}


@dataclass
class Trial:
    """A single trial comparing raw vs framed prompt."""

    trial_id: str
    framing_style: str
    original_prompt: str
    framed_prompt: str = ""
    raw_response: str = ""
    framed_response: str = ""
    raw_scores: dict = field(default_factory=dict)
    framed_scores: dict = field(default_factory=dict)
    raw_avg_score: float = 0.0
    framed_avg_score: float = 0.0
    winner: str = ""  # "raw", "framed", or "tie"


@dataclass
class FramingResults:
    """Results for a single framing style."""

    framing_style: str
    framing_name: str
    num_trials: int = 0
    raw_wins: int = 0
    framed_wins: int = 0
    ties: int = 0
    avg_raw_score: float = 0.0
    avg_framed_score: float = 0.0
    improvement_pct: float = 0.0
    trials: list = field(default_factory=list)


@dataclass
class ExperimentResults:
    """Aggregate results from all trials across all framings."""

    experiment_id: str
    timestamp: str
    model: str
    num_prompts: int = 0
    num_judges: int = 0
    framing_results: dict = field(default_factory=dict)  # style -> FramingResults
    rankings: list = field(default_factory=list)  # sorted by improvement
    best_framing: str = ""
    worst_framing: str = ""
    conclusion: str = ""


# Sample prompts for testing (would normally pull from Kaggle/dataset)
SAMPLE_PROMPTS = [
    "Explain how a binary search algorithm works.",
    "Write a function to check if a string is a palindrome.",
    "Describe the differences between SQL and NoSQL databases.",
    "Explain the concept of recursion with an example.",
    "Write a Python function to find the factorial of a number.",
    "Describe the Model-View-Controller (MVC) architecture pattern.",
    "Explain what a REST API is and its key principles.",
    "Write a function to reverse a linked list.",
    "Describe the difference between stack and heap memory.",
    "Explain how HTTP cookies work.",
    "Write a function to find the longest common substring of two strings.",
    "Describe the SOLID principles in object-oriented programming.",
    "Explain what a database index is and why it's useful.",
    "Write a function to detect a cycle in a linked list.",
    "Describe the difference between concurrency and parallelism.",
    "Explain how garbage collection works in programming languages.",
    "Write a function to implement a basic LRU cache.",
    "Describe the CAP theorem in distributed systems.",
    "Explain the difference between authentication and authorization.",
    "Write a function to serialize and deserialize a binary tree.",
]


class FramingHypothesisTester:
    """Tests whether prompt framing affects LLM output quality."""

    TRANSFORMER_SYSTEM = """You are a prompt rewriter. Your job is to take a straightforward prompt 
and reframe it according to the style instructions given.

IMPORTANT RULES:
- Keep the core task/question EXACTLY the same
- Only change HOW it's asked, not WHAT is asked
- Don't make it significantly longer
- Don't add extra requirements
- Respond with ONLY the rewritten prompt, nothing else"""

    JUDGE_PROMPT = """You are an expert evaluator assessing the quality of an LLM response.

Rate the response on these criteria (1-10 scale):

1. **Accuracy** (1-10): Is the information correct and reliable?
2. **Clarity** (1-10): Is the explanation clear and easy to understand?
3. **Completeness** (1-10): Does it fully address the question?
4. **Usefulness** (1-10): Would this actually help someone?
5. **Engagement** (1-10): Is it well-written and engaging to read?

Respond in this exact JSON format:
{
    "accuracy": <score>,
    "clarity": <score>,
    "completeness": <score>,
    "usefulness": <score>,
    "engagement": <score>,
    "overall": <average of above>,
    "brief_rationale": "<one sentence explaining your rating>"
}

Be objective and consistent. Judge the response on its merits, not the prompt style."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        if HAS_ANTHROPIC:
            self.client = anthropic.Anthropic()
        else:
            self.client = None
        self.framings = FRAMING_STYLES.copy()

    def add_custom_framing(self, key: str, name: str, instruction: str):
        """Add a custom framing style."""
        self.framings[key] = {"name": name, "instruction": instruction}

    def load_framings_from_csv(self, csv_path: str):
        """Load custom framings from CSV file.

        CSV format: key,name,instruction
        """
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row.get("key", row.get("style", "")).strip().lower()
                name = row.get("name", key).strip()
                instruction = row.get("instruction", row.get("prompt", "")).strip()
                if key and instruction:
                    self.add_custom_framing(key, name, instruction)
                    print(f"  Loaded framing: {key} ({name})")

    def load_prompts_from_file(self, file_path: str) -> list[str]:
        """Load prompts from a text file (one per line) or CSV."""
        prompts = []
        path = Path(file_path)

        if path.suffix.lower() == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    prompt = row.get("prompt", row.get("question", row.get("text", "")))
                    if prompt:
                        prompts.append(prompt.strip())
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        prompts.append(line)

        return prompts

    def _call_llm(self, system: str, user: str, max_tokens: int = 2000) -> str:
        """Make a single LLM call (independent session)."""
        if not self.client:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text

    def _generate_trial_id(self, prompt: str, framing: str) -> str:
        """Generate unique trial ID."""
        hash_input = f"{prompt}{framing}{datetime.now().isoformat()}{random.random()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def transform_prompt(self, prompt: str, framing_key: str) -> str:
        """Transform a prompt using specified framing style."""
        framing = self.framings.get(framing_key, {})
        instruction = framing.get("instruction", "Make it more engaging.")

        user_msg = f"""Style instruction: {instruction}

Prompt to reframe:
{prompt}

Reframed prompt:"""

        return self._call_llm(system=self.TRANSFORMER_SYSTEM, user=user_msg, max_tokens=500)

    def get_response(self, prompt: str) -> str:
        """Get LLM response to a prompt."""
        return self._call_llm(
            system="You are a helpful assistant. Answer the user's question clearly and thoroughly.",
            user=prompt,
            max_tokens=1500,
        )

    def judge_response(self, prompt: str, response: str, judge_id: int) -> dict:
        """Have a judge evaluate a response."""
        judge_input = f"""## Prompt Given:
{prompt}

## Response to Evaluate:
{response}

Please rate this response."""

        result = self._call_llm(system=self.JUDGE_PROMPT, user=judge_input, max_tokens=500)

        try:
            import re

            json_match = re.search(r"\{[^{}]+\}", result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"overall": 5.0, "error": "Could not parse judge response"}
        except json.JSONDecodeError:
            return {"overall": 5.0, "error": "Invalid JSON from judge"}

    def run_trial(self, prompt: str, framing_key: str, num_judges: int = 3) -> Trial:
        """Run a single trial comparing raw vs framed prompt."""
        framing = self.framings.get(framing_key, {"name": framing_key})

        trial = Trial(
            trial_id=self._generate_trial_id(prompt, framing_key),
            framing_style=framing_key,
            original_prompt=prompt,
        )

        print(f"\n  [{framing_key.upper()}] {prompt[:50]}...")

        # Transform prompt
        trial.framed_prompt = self.transform_prompt(prompt, framing_key)

        # Get responses
        trial.raw_response = self.get_response(prompt)
        trial.framed_response = self.get_response(trial.framed_prompt)

        # Randomize for blind judging
        responses = [
            ("A", prompt, trial.raw_response, "raw"),
            ("B", trial.framed_prompt, trial.framed_response, "framed"),
        ]
        random.shuffle(responses)

        # Judge both
        for judge_num in range(num_judges):
            for label, prompt_used, response, response_type in responses:
                scores = self.judge_response(prompt_used, response, judge_num)

                if response_type == "raw":
                    trial.raw_scores[f"judge_{judge_num + 1}"] = scores
                else:
                    trial.framed_scores[f"judge_{judge_num + 1}"] = scores

        # Calculate averages
        raw_overall = [
            s.get("overall", 5)
            for s in trial.raw_scores.values()
            if isinstance(s.get("overall"), (int, float))
        ]
        framed_overall = [
            s.get("overall", 5)
            for s in trial.framed_scores.values()
            if isinstance(s.get("overall"), (int, float))
        ]

        trial.raw_avg_score = sum(raw_overall) / len(raw_overall) if raw_overall else 5.0
        trial.framed_avg_score = (
            sum(framed_overall) / len(framed_overall) if framed_overall else 5.0
        )

        # Determine winner
        if trial.framed_avg_score > trial.raw_avg_score + 0.5:
            trial.winner = "framed"
        elif trial.raw_avg_score > trial.framed_avg_score + 0.5:
            trial.winner = "raw"
        else:
            trial.winner = "tie"

        status = "✅" if trial.winner == "framed" else "❌" if trial.winner == "raw" else "🟡"
        print(f"    {status} Raw={trial.raw_avg_score:.1f} vs Framed={trial.framed_avg_score:.1f}")

        return trial

    def run_experiment(
        self, prompts: list[str] = None, framing_keys: list[str] = None, num_judges: int = 3
    ) -> ExperimentResults:
        """Run full experiment testing multiple framings."""

        if prompts is None:
            prompts = random.sample(SAMPLE_PROMPTS, min(5, len(SAMPLE_PROMPTS)))

        if framing_keys is None:
            framing_keys = ["fun"]

        experiment_id = hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]

        print("=" * 70)
        print("PROMPT FRAMING HYPOTHESIS EXPERIMENT")
        print("=" * 70)
        print(f"Experiment ID: {experiment_id}")
        print(f"Model: {self.model}")
        print(f"Prompts: {len(prompts)}")
        print(f"Framings: {', '.join(framing_keys)}")
        print(f"Judges per trial: {num_judges}")
        print("=" * 70)

        results = ExperimentResults(
            experiment_id=experiment_id,
            timestamp=datetime.now().isoformat(),
            model=self.model,
            num_prompts=len(prompts),
            num_judges=num_judges,
        )

        # Test each framing
        for framing_key in framing_keys:
            framing = self.framings.get(framing_key, {"name": framing_key})

            print(f"\n{'#'*70}")
            print(f"# TESTING FRAMING: {framing.get('name', framing_key)}")
            print(f"{'#'*70}")

            framing_result = FramingResults(
                framing_style=framing_key,
                framing_name=framing.get("name", framing_key),
                num_trials=len(prompts),
            )

            for prompt in prompts:
                trial = self.run_trial(prompt, framing_key, num_judges)
                framing_result.trials.append(asdict(trial))

                if trial.winner == "framed":
                    framing_result.framed_wins += 1
                elif trial.winner == "raw":
                    framing_result.raw_wins += 1
                else:
                    framing_result.ties += 1

            # Calculate stats
            all_raw = [t["raw_avg_score"] for t in framing_result.trials]
            all_framed = [t["framed_avg_score"] for t in framing_result.trials]

            framing_result.avg_raw_score = sum(all_raw) / len(all_raw)
            framing_result.avg_framed_score = sum(all_framed) / len(all_framed)
            framing_result.improvement_pct = (
                (framing_result.avg_framed_score - framing_result.avg_raw_score)
                / framing_result.avg_raw_score
                * 100
            )

            results.framing_results[framing_key] = asdict(framing_result)

            print(
                f"\n  📊 {framing_key}: {framing_result.improvement_pct:+.1f}% "
                f"(Framed wins: {framing_result.framed_wins}, Raw wins: {framing_result.raw_wins})"
            )

        # Rank framings
        rankings = sorted(
            results.framing_results.items(), key=lambda x: x[1]["improvement_pct"], reverse=True
        )
        results.rankings = [(k, v["improvement_pct"]) for k, v in rankings]

        if rankings:
            results.best_framing = rankings[0][0]
            results.worst_framing = rankings[-1][0]

        # Conclusion
        best = results.framing_results.get(results.best_framing, {})
        if best.get("improvement_pct", 0) > 5:
            results.conclusion = f"🏆 Best framing: '{results.best_framing}' with {best['improvement_pct']:.1f}% improvement"
        elif best.get("improvement_pct", 0) < -5:
            results.conclusion = "📋 Raw prompts performed best overall"
        else:
            results.conclusion = "🤝 No significant difference between framings"

        return results

    def save_results(self, results: ExperimentResults, output_path: str = "framing_results.json"):
        """Save experiment results to JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(results), f, indent=2)
        return output_path

    def generate_report(self, results: ExperimentResults) -> str:
        """Generate markdown report."""
        lines = []
        lines.append("# Prompt Framing Hypothesis Experiment Report")
        lines.append(f"\n**Experiment ID:** {results.experiment_id}")
        lines.append(f"**Date:** {results.timestamp}")
        lines.append(f"**Model:** {results.model}")
        lines.append(f"**Prompts tested:** {results.num_prompts}")
        lines.append(f"**Judges per trial:** {results.num_judges}")
        lines.append("")

        lines.append("## Hypothesis")
        lines.append("")
        lines.append("> LLM output quality varies based on how prompts are framed.")
        lines.append(
            "> Some framings (fun, expert, pirate, etc.) may produce better results than neutral prompts."
        )
        lines.append("")

        lines.append("## Rankings")
        lines.append("")
        lines.append("| Rank | Framing | Improvement | Framed Wins | Raw Wins |")
        lines.append("|------|---------|-------------|-------------|----------|")

        for i, (key, improvement) in enumerate(results.rankings):
            fr = results.framing_results[key]
            emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
            lines.append(
                f"| {emoji} {i+1} | {fr['framing_name']} | {improvement:+.1f}% | {fr['framed_wins']} | {fr['raw_wins']} |"
            )

        lines.append("")
        lines.append(f"## Conclusion")
        lines.append("")
        lines.append(results.conclusion)
        lines.append("")

        # Details per framing
        lines.append("## Detailed Results by Framing")
        lines.append("")

        for key, fr in results.framing_results.items():
            lines.append(f"### {fr['framing_name']} (`{key}`)")
            lines.append("")
            lines.append(f"- **Average Raw Score:** {fr['avg_raw_score']:.2f}")
            lines.append(f"- **Average Framed Score:** {fr['avg_framed_score']:.2f}")
            lines.append(f"- **Improvement:** {fr['improvement_pct']:+.1f}%")
            lines.append(f"- **Framed Wins:** {fr['framed_wins']} / {fr['num_trials']}")
            lines.append("")

        return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Test the Prompt Framing Hypothesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test 'fun' framing (default)
  python fun_hypothesis.py --trials 5
  
  # Test pirate framing
  python fun_hypothesis.py --framing pirate --trials 5
  
  # Test multiple framings
  python fun_hypothesis.py --framings fun,pirate,expert --trials 3
  
  # Load custom framings from CSV
  python fun_hypothesis.py --framings-csv my_framings.csv --trials 5
  
  # Load prompts from file
  python fun_hypothesis.py --prompts-file questions.txt --framing fun

Available built-in framings:
  fun, pirate, expert, eli5, formal, socratic, enthusiastic, 
  skeptical, storyteller, confused
        """,
    )
    parser.add_argument(
        "--trials", type=int, default=5, help="Number of prompts to test (default: 5)"
    )
    parser.add_argument("--judges", type=int, default=3, help="Judges per trial (default: 3)")
    parser.add_argument(
        "--model", type=str, default="claude-sonnet-4-20250514", help="Model to use"
    )
    parser.add_argument(
        "--framing", type=str, default=None, help="Single framing to test (e.g., 'pirate')"
    )
    parser.add_argument(
        "--framings",
        type=str,
        default=None,
        help="Comma-separated framings (e.g., 'fun,pirate,expert')",
    )
    parser.add_argument(
        "--framings-csv", type=str, default=None, help="CSV file with custom framings"
    )
    parser.add_argument(
        "--prompts-file", type=str, default=None, help="File with prompts (one per line or CSV)"
    )
    parser.add_argument(
        "--custom-instruction",
        type=str,
        default=None,
        help="Custom framing instruction (use with --framing custom)",
    )
    parser.add_argument(
        "--list-framings", action="store_true", help="List available framings and exit"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without API calls"
    )

    args = parser.parse_args()

    # List framings
    if args.list_framings:
        print("Available framing styles:\n")
        for key, framing in FRAMING_STYLES.items():
            print(f"  {key:15} - {framing['name']}")
            print(f"                   {framing['instruction'][:60]}...")
            print()
        return

    # Determine which framings to test
    if args.framings:
        framing_keys = [f.strip() for f in args.framings.split(",")]
    elif args.framing:
        framing_keys = [args.framing]
    else:
        framing_keys = ["fun"]

    # Dry run
    if args.dry_run:
        print("=" * 70)
        print("FRAMING HYPOTHESIS TESTER - DRY RUN")
        print("=" * 70)
        print(f"\nFramings to test: {', '.join(framing_keys)}")
        print(f"Trials per framing: {args.trials}")
        print(f"Judges per trial: {args.judges}")
        print(f"Model: {args.model}")

        prompts = random.sample(SAMPLE_PROMPTS, min(args.trials, len(SAMPLE_PROMPTS)))
        print(f"\nSample prompts:")
        for i, p in enumerate(prompts[:3]):
            print(f"  {i+1}. {p[:60]}...")

        calls_per_framing = args.trials * (1 + 2 + args.judges * 2)
        total_calls = calls_per_framing * len(framing_keys)
        print(f"\nEstimated API calls: {total_calls}")
        print(
            f"  Per framing: {calls_per_framing} = {args.trials} transforms + {args.trials*2} responses + {args.trials*args.judges*2} judgments"
        )
        return

    if not HAS_ANTHROPIC:
        print("❌ Error: anthropic package not installed")
        print("   Run: pip install anthropic")
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Initialize tester
    tester = FramingHypothesisTester(model=args.model)

    # Load custom framings from CSV
    if args.framings_csv:
        print(f"Loading framings from {args.framings_csv}...")
        tester.load_framings_from_csv(args.framings_csv)

    # Add custom instruction if provided
    if args.custom_instruction:
        tester.add_custom_framing("custom", "Custom Framing", args.custom_instruction)
        if "custom" not in framing_keys:
            framing_keys.append("custom")

    # Load prompts
    if args.prompts_file:
        prompts = tester.load_prompts_from_file(args.prompts_file)
        print(f"Loaded {len(prompts)} prompts from {args.prompts_file}")
    else:
        prompts = random.sample(SAMPLE_PROMPTS, min(args.trials, len(SAMPLE_PROMPTS)))

    # Run experiment
    results = tester.run_experiment(
        prompts=prompts, framing_keys=framing_keys, num_judges=args.judges
    )

    # Save results
    json_path = tester.save_results(results)
    print(f"\n📄 Results saved to: {json_path}")

    # Generate report
    report = tester.generate_report(results)
    report_path = "framing_hypothesis_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📄 Report saved to: {report_path}")

    # Print summary
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"\n{results.conclusion}")
    print("\nRankings:")
    for i, (key, improvement) in enumerate(results.rankings):
        emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        print(f"  {emoji} {key}: {improvement:+.1f}%")


if __name__ == "__main__":
    main()
