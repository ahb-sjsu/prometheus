# Protocol 1 Results Analysis: Real Claude Sonnet 4 Data

## Summary

The experiment ran successfully with **450 evaluations** (50 scenarios × 3 conditions × 3 repetitions).

**Cost:** ~427K tokens ≈ **$1.50** (close to estimate!)

## Results

| Condition | θ (rad) | θ (deg) | Distribution | Prediction |
|-----------|---------|---------|--------------|------------|
| **Control** | 0.284 | 16.3° | L=121, O=26, C=2, N=1 | 0° |
| **Weak** | 0.000 | 0.0° | L=124, O=26 | 30° |
| **Strong** | 0.000 | 0.0° | L=143, O=7 | 60° |

## Interpretation

### What the data shows:

1. **Claude predominantly chooses LIBERTY (L)** - "the poster is free to act as they did"
   - Control: 81% L
   - Weak: 83% L  
   - Strong: 95% L

2. **The threshold manipulation DOES have an effect** - but in the **opposite direction** from prediction!
   - Control → Strong shows significant difference (p=0.0001)
   - But θ *decreases* (more L, fewer O/C) instead of increasing

3. **Falsification assessment:**
   - ❌ No graded response in predicted direction
   - ❌ Theory falsified as stated

## Why This Happened - Theoretical Analysis

The NA-SQND prediction assumed:
- **Control (baseline):** Poster has obligations/claims → O/C responses
- **Threshold crossed:** Obligations dissolve → L/N responses

But Claude's actual reasoning pattern is:
- **Control:** "Poster was justified" → L (liberty to act)
- **Strong threshold:** "Situation resolved, even MORE clearly no obligation" → L (stronger)

### The Issue: AITA Dataset Bias

The AITA dataset is ~76% NTA (Not The Asshole), meaning:
- Most scenarios already depict the poster as *justified*
- Claude correctly identifies this as LIBERTY
- The threshold conditions ("other party apologized") *reinforce* rather than challenge this

### What This Actually Tests

The experiment tested: **"Does adding mitigating context for the other party shift moral classification?"**

Claude's answer: **"No - the poster was justified before, and mitigating context for the other party doesn't create new obligations for the poster."**

This is actually *coherent moral reasoning* - just not what NA-SQND predicted.

## Revised Experimental Design Needed

To properly test NA-SQND bond-type rotation, we need scenarios where:

1. **Control condition:** Poster has clear OBLIGATIONS (not liberties)
2. **Threshold conditions:** Context changes that would *dissolve* those obligations

### Better Test Cases:

| Scenario Type | Control | Weak Threshold | Strong Threshold |
|---------------|---------|----------------|------------------|
| Promise-keeping | "Alex promised to help" → O | "Jordan said help is optional" → shift to L | "Jordan cancelled entirely" → L |
| Debt repayment | "Morgan owes $5000" → O | "Taylor says not urgent" → partial shift | "Taylor forgave the debt" → L |
| Professional duty | "Dr. Chen is treating patient" → O | "Patient seeing other doctors" → shift | "Patient transferred care" → L |

The current AITA scenarios mostly start at L (poster justified), so there's no "obligation to dissolve."

## Positive Findings

Despite falsifying the specific prediction, the data shows:

1. **Claude's judgments are internally consistent** (low variance within conditions)
2. **Threshold manipulations DO affect responses** (significant χ² for control vs strong)
3. **The POVM measurement model works** - we get meaningful θ estimates
4. **The experimental pipeline is validated** - 450 evaluations completed successfully

## Next Steps

1. **Design new scenarios** that start with clear obligations
2. **Test the reverse direction:** Can we shift L → O?
3. **Try different models** to see if the pattern holds
4. **Analyze the reasoning text** to understand Claude's decision process

## Conclusion

**The experiment worked perfectly as a scientific test.** 

The theory made a falsifiable prediction, we tested it rigorously, and the prediction was not confirmed. This is how science should work!

The data suggests that NA-SQND's bond-type rotation may require:
- Scenarios with initial obligations (not liberties)
- Threshold crossings that challenge those obligations
- Perhaps bidirectional testing (O→L and L→O)

---

*"A theory that cannot be falsified by any conceivable event is non-scientific." - Karl Popper*

The fact that this experiment *could* falsify the prediction (and did) demonstrates that NA-SQND makes genuine empirical claims.
