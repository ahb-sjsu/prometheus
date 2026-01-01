The **Fun Hypothesis Tester** (now called the **Framing Hypothesis Tester**) tests whether LLMs perform better when prompts are framed in different styles.

## The Hypothesis

> Does asking Claude "Let's have fun figuring this out together!" produce better answers than a dry, neutral prompt?

Or more generally: **Does prompt framing affect response quality?**

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Session A: Send raw prompt → Get Response A                │
│  Session B: Transform prompt with framing → Get framed prompt│
│  Session C: Send framed prompt → Get Response B             │
│  Session D: Blind judge rates Response A                    │
│  Session E: Blind judge rates Response B                    │
│  Compare scores statistically                               │
└─────────────────────────────────────────────────────────────┘
```

Each session is independent (no context leakage).

## Built-in Framings

| Key | Style | Example Transform |
|-----|-------|-------------------|
| `fun` | Playful, collaborative | "Let's figure this out together!" |
| `pirate` | Pirate speak | "Ahoy! Help me find the treasure of knowledge!" |
| `expert` | Senior technical expert | "As a senior engineer, analyze..." |
| `eli5` | Explain Like I'm 5 | "Explain this so a 5-year-old understands" |
| `formal` | Academic/professional | "Please provide a formal analysis..." |
| `socratic` | Guided questions | "Help me discover the answer through questions" |
| `enthusiastic` | SUPER EXCITED!!! | "OMG I'm SO CURIOUS about this!!!" |
| `skeptical` | Question assumptions | "I'm not sure this is right, but..." |
| `storyteller` | Narrative framing | "Tell me the story of how..." |
| `confused` | Genuinely uncertain | "I'm really confused about this..." |

## Usage

```bash
# Test single framing
python fun_hypothesis.py --framing pirate --trials 5

# Compare multiple framings
python fun_hypothesis.py --framings "fun,expert,formal" --trials 10

# Custom framing
python fun_hypothesis.py --framing custom \
  --custom-instruction "Reframe as a medieval scholar" --trials 5

# Load framings from CSV
python fun_hypothesis.py --framings-csv my_styles.csv --trials 5
```

## Output

- Statistical comparison (p-values)
- Per-framing scores
- Markdown report with rankings

## Why This Matters

If "fun" framing consistently scores 10% higher, you'd want to bake that into your system prompts. If "expert" framing helps with technical questions but hurts creative ones, you'd want conditional framing.

It's empirical prompt engineering instead of vibes-based prompt engineering.