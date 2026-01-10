# Framing Hypothesis Tester: How It Works

## The Problem

Everyone has opinions about prompt engineering:

- "Be polite to the AI"
- "Ask it to think step by step"
- "Tell it to act as an expert"
- "Make it fun and collaborative"

But does any of this actually work? And by how much? And for which types of questions?

**This tool replaces vibes with data.**

---

## The Method

### Isolation is Everything

The key insight: you can't test framing effects in the same conversation. The model remembers context. You need **complete isolation**.

```
┌─────────────────────────────────────────────────────────────┐
│                    SINGLE TRIAL                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SESSION A (isolated)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Input: Raw prompt                                    │   │
│  │ Output: Response A                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  SESSION B (isolated)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Input: "Transform this prompt to be more fun: ..."   │   │
│  │ Output: Framed prompt                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  SESSION C (isolated)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Input: Framed prompt                                 │   │
│  │ Output: Response B                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  SESSION D (isolated)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Input: "Rate this response 1-10: {Response A}"       │   │
│  │ Output: Score A (e.g., 7)                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  SESSION E (isolated)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Input: "Rate this response 1-10: {Response B}"       │   │
│  │ Output: Score B (e.g., 8)                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  RESULT: Framed version scored +1 on this trial            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Why 5 Sessions Per Trial?

| Session | Purpose | Why Isolated? |
|---------|---------|---------------|
| A | Get baseline response | Can't know about framing |
| B | Transform the prompt | Can't see responses |
| C | Get framed response | Can't know it's being compared |
| D | Judge response A | Can't see response B |
| E | Judge response B | Can't see response A |

**Blind judging is critical.** If the judge sees both responses, it might prefer the second one (recency bias) or try to be "fair" and rate them similarly.

---

## The Pipeline

```
                    ┌──────────────┐
                    │  Raw Prompt  │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Session A  │ │  Session B  │ │  Session B' │
    │  Raw → Resp │ │  Transform  │ │  Transform  │
    │      A      │ │  to "fun"   │ │  to "expert"│
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           │               ▼               ▼
           │        ┌─────────────┐ ┌─────────────┐
           │        │  Session C  │ │  Session C' │
           │        │  Fun prompt │ │ Expert prmt │
           │        │  → Resp B   │ │  → Resp B'  │
           │        └──────┬──────┘ └──────┬──────┘
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Session D  │ │  Session E  │ │  Session E' │
    │  Judge A    │ │  Judge B    │ │  Judge B'   │
    │  Score: 6   │ │  Score: 8   │ │  Score: 7   │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Statistical       │
                 │ Comparison        │
                 │                   │
                 │ Baseline: 6.0     │
                 │ Fun: 8.0 (+2.0)   │
                 │ Expert: 7.0 (+1.0)│
                 │                   │
                 │ p-value: 0.03     │
                 └───────────────────┘
```

---

## Framing Transformations

The tool includes 10 built-in framing styles:

### 🎉 Fun
```
Original: "Explain how TCP/IP works"

Transformed: "Let's have fun exploring how TCP/IP works together! 
I'm genuinely curious and excited to learn about this with you."
```

### 🏴‍☠️ Pirate
```
Original: "Explain how TCP/IP works"

Transformed: "Ahoy, matey! I be needin' to understand how this 
TCP/IP treasure map works! Help this old sea dog navigate 
these digital waters!"
```

### 🎓 Expert
```
Original: "Explain how TCP/IP works"

Transformed: "As a senior network engineer, provide a rigorous 
technical explanation of the TCP/IP protocol stack, including 
implementation considerations."
```

### 👶 ELI5
```
Original: "Explain how TCP/IP works"

Transformed: "Can you explain how TCP/IP works like I'm 5 years 
old? Use simple words and maybe a fun analogy!"
```

### 📜 Formal
```
Original: "Explain how TCP/IP works"

Transformed: "Please provide a formal, academic explanation of 
the TCP/IP protocol suite, suitable for technical documentation."
```

### 🤔 Socratic
```
Original: "Explain how TCP/IP works"

Transformed: "I'd like to understand TCP/IP. Rather than just 
telling me, could you guide me to discover how it works through 
a series of questions?"
```

---

## Statistical Analysis

After N trials, the tool computes:

### Per-Framing Statistics
```
Framing: fun
  Trials: 20
  Mean Score: 7.4
  Std Dev: 1.2
  Min: 5, Max: 9
  vs Baseline: +1.2
```

### Significance Testing
```
Comparison: fun vs baseline
  t-statistic: 2.45
  p-value: 0.023
  Significant: YES (p < 0.05)
  
Comparison: expert vs baseline
  t-statistic: 1.12
  p-value: 0.271
  Significant: NO
```

### Effect Size
```
fun: +16% improvement over baseline (Cohen's d = 0.8)
expert: +5% improvement over baseline (Cohen's d = 0.2)
pirate: -3% vs baseline (Cohen's d = -0.1)
```

---

## Output Files

### 1. Raw Data (JSON)
```json
{
  "config": {
    "framings": ["fun", "expert", "pirate"],
    "trials": 20,
    "model": "claude-sonnet-4-20250514"
  },
  "trials": [
    {
      "trial_id": 1,
      "prompt": "Explain quantum entanglement",
      "baseline": {
        "response": "Quantum entanglement is...",
        "score": 7
      },
      "framings": {
        "fun": {
          "framed_prompt": "Let's explore quantum entanglement together!...",
          "response": "Great question! Quantum entanglement is like...",
          "score": 8
        }
      }
    }
  ],
  "statistics": { ... }
}
```

### 2. Report (Markdown)
```markdown
# Framing Hypothesis Test Results

## Summary
| Framing | Mean Score | vs Baseline | p-value | Significant? |
|---------|------------|-------------|---------|--------------|
| fun | 7.8 | +1.2 | 0.02 | ✅ YES |
| expert | 7.1 | +0.5 | 0.18 | ❌ NO |
| pirate | 6.4 | -0.2 | 0.71 | ❌ NO |

## Recommendation
Use "fun" framing for general questions (+16% improvement).
```

---

## Usage Examples

### Test a Single Framing
```bash
python fun_hypothesis.py \
  --framing fun \
  --trials 10 \
  --prompts-csv my_test_questions.csv
```

### Compare Multiple Framings
```bash
python fun_hypothesis.py \
  --framings "fun,expert,eli5,formal" \
  --trials 20
```

### Custom Framing
```bash
python fun_hypothesis.py \
  --framing custom \
  --custom-instruction "Reframe as a wise grandmother giving advice" \
  --trials 10
```

### Load Framings from CSV
```csv
key,name,instruction
grandma,Wise Grandma,Reframe as a wise grandmother giving gentle advice
coach,Sports Coach,Reframe as an enthusiastic sports coach motivating the team
noir,Film Noir,Reframe as a hardboiled detective narrating in film noir style
```

```bash
python fun_hypothesis.py \
  --framings-csv custom_framings.csv \
  --trials 15
```

---

## Best Practices

### Sample Size
- **Minimum:** 10 trials per framing
- **Recommended:** 20+ trials for statistical significance
- **For publication:** 50+ trials

### Prompt Selection
- Use diverse prompts (factual, creative, analytical)
- Include prompts of varying difficulty
- Test domain-specific prompts if that's your use case

### Interpreting Results
- **p < 0.05** = statistically significant
- **Effect size matters** = +0.5 points might not be worth the complexity
- **Check consistency** = high variance means unreliable effect

---

## Limitations

1. **LLM-as-judge bias**: The model rating itself may have blind spots
2. **Single model**: Results may not generalize to other models
3. **Prompt-dependent**: A framing that helps with math might hurt with poetry
4. **API costs**: 5 API calls per trial × N trials × M framings adds up

---

## The Bottom Line

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│   Before: "I think adding 'please' makes it work better"      │
│                                                                │
│   After: "Fun framing improves scores by 16% (p=0.02)         │
│           on general knowledge questions, but has no          │
│           significant effect on code generation tasks."       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Stop guessing. Start measuring.**
