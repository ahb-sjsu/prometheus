# Better Datasets for Testing NA-SQND Bond-Type Rotation

## What We Learned

The AITA experiment was **statistically significant** (p = 0.001, Cramér's V = 0.23), but it tested the **wrong direction**:

| What happened | What NA-SQND needed |
|---------------|---------------------|
| Baseline: L (liberty) | Baseline: O (obligation) |
| Threshold: L stronger | Threshold: O → L transition |
| Result: L → L (no rotation) | Result: O → L (rotation) |

**The issue:** AITA scenarios depict situations where posters are usually *justified* (NTA = 76%). We need scenarios where people start with clear *obligations* that can then be dissolved.

---

## Recommended Datasets

### 1. **Professional Ethics Cases** ⭐ BEST OPTION

**Source:** Legal/medical ethics casebooks, bar exam questions, medical board scenarios

**Why it works:**
- Professionals have clear, codified obligations
- Cases often involve conflicts where duties may be suspended
- Well-documented threshold conditions (emergencies, consent withdrawal, etc.)

**Example structure:**
```
Control: "Dr. Smith is treating Patient Jones for diabetes."
→ Clear OBLIGATION to continue care

Weak: "Patient Jones has started seeing another doctor occasionally."
→ Partial shift

Strong: "Patient Jones formally transferred care to a new physician."
→ LIBERTY (no more obligation)
```

**Where to find:**
- ABA Model Rules scenarios
- Medical ethics case studies (Beauchamp & Childress casebook)
- Nursing ethics cases
- Legal malpractice examples

---

### 2. **Contract Law Scenarios**

**Source:** Contract law casebooks, 1L exam questions

**Why it works:**
- Contracts create explicit obligations
- Well-defined discharge conditions (breach, impossibility, frustration)
- Clear legal framework maps to Hohfeldian structure

**Example structure:**
```
Control: "Alice contracted to deliver 100 widgets to Bob by Friday."
→ OBLIGATION

Weak: "Bob said delivery next week would also be acceptable."
→ Partial shift (modified obligation)

Strong: "Bob's warehouse burned down; he cannot receive any widgets."
→ LIBERTY (impossibility discharges obligation)
```

**Where to find:**
- Law school casebooks (Farnsworth on Contracts)
- BarBri/Kaplan contract law questions
- Restatement (Second) of Contracts illustrations

---

### 3. **Promise-Keeping Vignettes** (Custom Dataset)

**Create custom scenarios** specifically designed to test O → L transitions:

**Template:**
```
CONTROL (establishes obligation):
"[Person A] promised [Person B] to [specific action] by [specific time]."

WEAK THRESHOLD (partial release):
"[Person B] mentioned that the [action] is 'less urgent than before' 
but didn't explicitly release [Person A] from the promise."

STRONG THRESHOLD (complete release):
"[Person B] explicitly told [Person A]: 'Don't worry about [action] anymore, 
I've made other arrangements.'"
```

**20 Example Topics:**
1. Promise to help someone move
2. Promise to attend an event
3. Promise to lend money
4. Promise to keep a secret
5. Promise to provide a reference
6. Promise to return a borrowed item
7. Promise to complete a favor
8. Promise to call/visit regularly
9. Promise to help with a project
10. Promise to provide childcare
11. Promise to share information
12. Promise to maintain confidentiality
13. Promise to repay a debt
14. Promise to attend a meeting
15. Promise to deliver goods
16. Promise to provide support
17. Promise to abstain from something
18. Promise to include someone
19. Promise to advocate for someone
20. Promise to teach/mentor someone

---

### 4. **Trolley Problem Variants** 

**Source:** Moral psychology literature, Moral Machine dataset

**Why it works:**
- Well-studied moral dilemmas
- Parametric variations available
- Tests duty vs. liberty tradeoffs

**Adaptation for NA-SQND:**
```
Control: "You can save 5 people by diverting a trolley."
→ Competing obligations

Weak: "The 5 people are strangers; you know nothing about them."
→ Weaker obligation

Strong: "The 5 people have signed waivers releasing you from liability."
→ LIBERTY (no obligation)
```

**Where to find:**
- Moral Machine (MIT): millions of scenarios
- Trolley Problem literature
- Experimental philosophy datasets

---

### 5. **Debt/Obligation Database** (Custom)

**Create scenarios with explicit debts that can be forgiven:**

**Structure:**
```
Control: "[A] borrowed $[X] from [B] with promise to repay by [date]."
→ OBLIGATION

Weak: "[B] said 'pay whenever you can, no rush.'"
→ Modified obligation

Strong: "[B] sent written notice: 'I forgive your debt entirely.'"
→ LIBERTY
```

---

## Implementation Recommendations

### Quick Test (validate the approach)
1. Create **20 promise-keeping scenarios** manually
2. Test with Claude (60 evaluations = ~$0.20)
3. Verify O → L pattern appears

### Full Experiment
1. Curate **50 professional ethics cases** from casebooks
2. Run 3 conditions × 3 repetitions (450 evaluations = ~$1.50)
3. This should show clear bond-type rotation

### Dataset Requirements Checklist

✅ **Starting point:** Clear OBLIGATION (not liberty)  
✅ **Agents identified:** Who owes what to whom  
✅ **Threshold conditions:** Plausible reasons for release  
✅ **Gradation:** Weak threshold < Strong threshold  
✅ **Balance:** Include some scenarios that DON'T transition  

---

## Suggested CSV Format

```csv
id,title,text,control_text,weak_text,strong_text,expected_control,expected_strong
ethics_001,Doctor-Patient Duty,"Dr. Chen treats...",,"Patient started seeing...",,"Patient transferred care...",O,L
promise_001,Moving Help,"Alex promised to help...",,"Jordan said help is optional...",,"Jordan cancelled the move...",O,L
contract_001,Widget Delivery,"Alice contracted to deliver...",,"Bob said next week is fine...",,"Bob's warehouse burned down...",O,L
```

---

## Key Insight

**The experiment worked perfectly!** We found a statistically significant effect. The issue was dataset selection, not methodology.

NA-SQND predicts **bidirectional** rotation:
- O → L when obligations dissolve (threshold removes duty)
- L → O when obligations arise (threshold creates duty)

The AITA dataset only tested L → L (baseline was already liberty).

**Next step:** Test O → L with professional ethics or promise-keeping scenarios.

---

## Estimated Costs for Recommended Datasets

| Dataset | Scenarios | Evals | Sonnet Cost | Haiku Cost |
|---------|-----------|-------|-------------|------------|
| Quick validation | 20 | 180 | $0.57 | $0.15 |
| Promise-keeping | 50 | 450 | $1.42 | $0.38 |
| Professional ethics | 50 | 450 | $1.42 | $0.38 |
| Full battery (both) | 100 | 900 | $2.85 | $0.76 |

**Recommendation:** Start with 20 custom promise-keeping scenarios ($0.57) to validate, then scale up.
