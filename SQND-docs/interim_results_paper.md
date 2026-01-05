# Algebraic Structure in Large Language Model Moral Reasoning: Experimental Evidence for Discrete States, Selective Path Dependence, and Asymmetric Hysteresis

**Interim Results Paper — Draft v1.0**

---

**Authors:**  
Andrew H. Bond¹*, Claude (Anthropic)²

**Affiliations:**  
¹ Department of Computer Engineering, San José State University, San José, CA  
² Anthropic, San Francisco, CA

**Correspondence:** *andrew.bond@sjsu.edu

**Status:** Interim results; experiments complete, analysis ongoing

---

## Abstract

We report experimental results from systematic probing of moral reasoning structure in a large language model (Claude Sonnet 4, Anthropic). Using a novel methodology combining grammar-based scenario generation with algebraic structure detection, we conducted two primary experiments: (1) phase transition and hysteresis detection (N = 1,000 evaluations), and (2) holonomy path dependence testing (N = 640 evaluations across 8 scenarios).

Key findings include:

1. **Discrete semantic gating:** Moral state transitions occur at specific semantic triggers, not proportional to "strength" of release language. The phrase "only if convenient" produces 100% state change while "found a friend who might help" produces 0%, despite similar surface meaning.

2. **Perfect Hohfeldian symmetry:** Correlative pairs (Obligation↔Claim, Liberty↔No-Claim) hold at 100% across all tested scenarios, confirming the Hohfeldian jural relations as exact structural features.

3. **Selective path dependence:** 2 of 8 scenarios showed significant path dependence (p < 10⁻⁵), with Wilson loops W = 0.66-0.86. Path dependence occurs specifically when contextual factors point to *different bond types*, not merely when they conflict.

4. **Robust hysteresis:** Releasing obligations requires stronger intervention than creating them (threshold gap = 1.0 on 7-point scale), consistent with an asymmetric double-well potential.

5. **Combined statistical evidence:** The aggregate chi-square for path dependence across all scenarios is χ² = 72.14 (df = 16, p < 10⁻⁸), providing strong evidence for non-Abelian structure in the system's moral reasoning.

We propose a refined theoretical model: a stratified discrete gauge structure where non-Abelian features emerge specifically at cross-bond-type boundaries, with Abelian structure within bond types. This model generates testable predictions for human comparison studies.

**Keywords:** moral reasoning, large language models, algebraic structure, path dependence, Hohfeldian relations, gauge theory, AI alignment

---

## 1. Introduction

### 1.1 Motivation

Large language models (LLMs) increasingly perform tasks requiring moral reasoning—content moderation, advice-giving, decision support. Yet the internal structure of this reasoning remains poorly understood. Standard evaluation approaches measure accuracy on benchmarks but provide limited insight into the *form* of moral cognition.

This paper presents experimental results characterizing the algebraic structure of moral reasoning in a state-of-the-art LLM. We find evidence for discrete state spaces, exact symmetries, selective non-commutativity, and asymmetric transition dynamics—features that collectively suggest a rich mathematical structure underlying apparent natural language moral judgments.

### 1.2 Theoretical Framework

Our investigation is grounded in two frameworks:

**Hohfeldian jural relations** (Hohfeld, 1917): Legal theorist Wesley Hohfeld identified four fundamental normative relations—Obligation (O), Claim (C), Liberty (L), and No-Claim (N)—structured by correlative pairs (O↔C, L↔N) and oppositions (O vs. L, C vs. N).

**Gauge-theoretic structure** (Bond, 2025, 2026): We previously proposed that moral reasoning might exhibit features analogous to gauge theories in physics: a discrete state space, symmetry groups, path-dependent holonomy, and phase transitions.

This paper tests predictions derived from these frameworks against empirical data.

### 1.3 Research Questions

1. Are moral state transitions continuous or discrete?
2. Does the Hohfeldian correlative structure hold exactly?
3. Is moral reasoning path-dependent (non-Abelian)?
4. Are there asymmetries in moral state transitions (hysteresis)?

---

## 2. Methods

### 2.1 System Under Study

All experiments were conducted on Claude Sonnet 4 (claude-sonnet-4-20250514, Anthropic) via the standard API. This model was selected for its strong performance on reasoning tasks and availability for systematic probing.

### 2.2 Experimental Paradigm

We employed a **Structural Fuzzing** methodology (Bond, 2026): systematic generation of moral scenarios from formal grammars, with algebraic structure inferred from response distributions.

**Response format:** For each scenario, the model was prompted to classify the moral relationship as one of:
- O (OBLIGATION): Agent has a duty toward Target
- C (CLAIM): Target has a right against Agent  
- L (LIBERTY): Agent is free to act either way
- N (NO-CLAIM): Target has no right against Agent

Along with a confidence rating (0.0-1.0) and one-sentence reasoning.

### 2.3 Experiment 1: Phase Transition and Hysteresis

**Design:** A base promise scenario was modified with 11 levels of "release" language, from no release (Level 0) to explicit full release (Level 10).

**Levels:**
- 0: Baseline promise only
- 1-4: Weak contextual modifications
- 5: "only if it's convenient for you"
- 6: "found a friend who might help"
- 7: "don't worry about it if you're busy"
- 8-10: Strong explicit releases

**Trials:** 20 trials per level, 220 total evaluations.

**Hysteresis test:** Separate protocol testing O→L and L→O transitions with matched scenarios, 20 trials per condition.

**Correlative symmetry test:** 5 scenario pairs testing O↔C and L↔N, 20 trials each perspective.

**Total evaluations:** 1,000

### 2.4 Experiment 2: Holonomy Path Dependence

**Design:** 8 ethical dilemma scenarios, each with two contextual factors (A and B). Each scenario was presented in both orders (A→B and B→A) to test for path dependence.

**Scenarios:**
| ID | Domain | Factor A | Factor B |
|----|--------|----------|----------|
| consultant | Business | Loyalty | Conflict of interest |
| doctor | Medical | Autonomy | Beneficence |
| lawyer | Legal | Confidentiality | Justice |
| executive | Corporate | Shareholder duty | Stakeholder welfare |
| journalist | Media | Truth-telling | Source protection |
| researcher | Academic | Independence | Research progress |
| friend | Personal | Friendship loyalty | Friend's welfare |
| teacher | Education | Academic integrity | Compassion |

**Trials:** 40 trials per path × 2 paths × 8 scenarios = 640 evaluations.

**Primary metric:** Wilson loop W = Σ_x √(P_AB(x) · P_BA(x)), measuring path equivalence.
- W = 1.0: Paths identical (Abelian)
- W < 0.9: Paths differ (non-Abelian evidence)

**Statistical test:** Chi-square test for independence of response distribution × path.

### 2.5 Analysis Approach

All analyses were pre-registered in the experimental protocol. Primary significance threshold: α = 0.05 with Bonferroni correction for multiple comparisons within each experiment.

---

## 3. Results

### 3.1 Phase Transition: Discrete Semantic Gating

Figure 1 shows the probability of Liberty classification across release levels:

```
Level:    0    1    2    3    4    5    6    7    8    9   10
P(L):   0.0  0.0  0.0  0.0  0.0  1.0  0.0  .55  1.0  1.0  1.0
         ─────────────────────── ↑ ── ↑ ─────────────────────
                                 │    │
                         "only if │    "found a friend"
                         convenient"   (NO transition)
```

**Key finding:** The transition is not monotonic. Level 5 ("only if it's convenient for you") produces 100% Liberty, but Level 6 ("found a friend who might help") produces 0% Liberty—a complete reversal.

**Interpretation:** The system responds to *semantic content*, not surface-level "strength." The phrase "only if convenient" contains an explicit release speech act; "found a friend" describes circumstances without performing a release.

**Estimated critical threshold:** T_c = 6.04, but this is misleading given the non-monotonicity. The transition is better characterized as **discrete gating** at specific semantic triggers.

**Transition width:** 2.65 levels, but concentrated in the ambiguous region (Levels 6-8) where release intent is unclear.

### 3.2 Hysteresis: Asymmetric Transition Thresholds

**Release threshold (O→L):** T_c = 3.5  
**Binding threshold (L→O):** T_c = 2.5  
**Hysteresis gap:** 1.0 (on 7-point scale)

**Finding:** Releasing obligations requires stronger intervention than creating them. Obligations are "stickier" than liberties.

**Interpretation:** This asymmetry is consistent with an asymmetric double-well potential where the Obligation well is deeper than the Liberty well:

```
      V(φ)
        │      
        │  ╭─╮     ╭─╮
        │ ╱   ╲   ╱   ╲
        │╱  O  ╲─╱  L  ╲    ← O well deeper
        └──────────────────→ φ
```

### 3.3 Correlative Symmetry: Perfect Hohfeldian Structure

Table 1 shows correlative symmetry results across all tested scenarios:

| Scenario | Expected Pairing | Observed | Symmetry Rate |
|----------|------------------|----------|---------------|
| debt | O↔C | O↔C | 100% |
| promise | O↔C | O↔C | 100% |
| professional | O↔C | O↔C | 100% |
| no_duty | L↔N | L↔N | 100% |
| released | L↔N | L↔N | 100% |
| **Overall** | — | — | **100%** |

**Finding:** The Hohfeldian correlative structure holds exactly. When the model judges Agent has O toward Target, it judges Target has C against Agent in 100% of cases. Similarly for L↔N.

**Interpretation:** This is not an approximation or tendency—it is an exact structural feature. The D₄ reflection symmetry (correlatives as reflection generator s: O↔C, L↔N) is fully instantiated.

### 3.4 Path Dependence: Selective Non-Abelian Structure

Table 2 summarizes holonomy results across all 8 scenarios:

| Scenario | W | χ² | p-value | Path Dep? | Dominant AB→BA |
|----------|---|-----|---------|-----------|----------------|
| consultant | 0.9996 | 0.00 | 1.000 | No | O→O |
| doctor | 1.0000 | 0.00 | 1.000 | No | O→O |
| lawyer | 0.9930 | 0.26 | 0.608 | No | O→O |
| executive | 0.9945 | 0.49 | 0.482 | No | O→O |
| **journalist** | **0.6592** | **40.44** | **<10⁻⁹** | **Yes** | **O→C** |
| researcher | 0.9874 | 0.00 | 1.000 | No | O→O |
| friend | 0.9618 | 3.12 | 0.210 | No | O→O |
| **teacher** | **0.8615** | **18.47** | **<10⁻⁴** | **Yes** | **L→O** |

**Aggregate statistics:**
- Mean Wilson loop: W = 0.932
- Combined χ²: 72.14 (df = 16)
- Combined p-value: 4.2 × 10⁻⁹

**Finding:** Path dependence is not universal but selective. 2 of 8 scenarios show highly significant path dependence (p < 10⁻⁴), while 6 show no detectable path dependence.

### 3.5 Characterizing Path-Dependent Scenarios

What distinguishes the journalist and teacher scenarios?

**Journalist scenario:**
- Factor A (Truth): Points toward revealing information → Agent focus → **O**
- Factor B (Protection): Points toward protecting source → Source focus → **C**
- Path A→B: 77.5% O, 22.5% C (Agent-focused frame dominates)
- Path B→A: 5% O, 95% C (Source-focused frame dominates)

**Teacher scenario:**
- Factor A (Integrity): Points toward enforcing rules → Discretionary → **L**
- Factor B (Compassion): Points toward helping student → Duty → **O**
- Path A→B: 32.5% O, 67.5% L (Discretion frame dominates)
- Path B→A: 82.5% O, 17.5% L (Duty frame dominates)

**Key insight:** Path dependence occurs when the two factors point to *different bond types*. In the journalist case, Truth→O while Protection→C. In the teacher case, Integrity→L while Compassion→O.

In contrast, the non-path-dependent scenarios have factors that either:
1. Both point to the same bond type (friend: Loyalty→O, Welfare→O)
2. Have one factor completely dominating (doctor: always O regardless of path)

### 3.6 Cross-Type vs. Within-Type Path Dependence

We can reclassify scenarios by whether factors point to the same or different bond types:

| Scenario | Factor A → | Factor B → | Cross-Type? | Path Dep? |
|----------|------------|------------|-------------|-----------|
| consultant | O | L | Yes | No* |
| doctor | L | O | Yes | No* |
| lawyer | O | O | No | No |
| executive | O | O | No | No |
| journalist | O | C | **Yes** | **Yes** |
| researcher | O | O | No | No |
| friend | O | O | No | No |
| teacher | L | O | **Yes** | **Yes** |

*The consultant and doctor scenarios are cross-type but showed no path dependence. Examining the data: both scenarios resulted in 100% O or near-100% O regardless of path, suggesting one factor dominated so completely that path order became irrelevant.

**Refined hypothesis:** Path dependence emerges when:
1. Factors point to different bond types, AND
2. Neither factor completely dominates

This is consistent with non-Abelian structure that becomes visible only when the system traverses between different regions of state space.

---

## 4. Theoretical Interpretation

### 4.1 The Discrete Gate Model

The phase transition data strongly supports a discrete gate model over continuous rotation:

**Continuous model prediction:** P(L) should increase monotonically with release "strength."

**Discrete gate model prediction:** P(L) should jump at specific semantic triggers, with non-release language producing no effect regardless of surface similarity.

**Observed:** Level 5 ("only if convenient") → 100% L; Level 6 ("found a friend") → 0% L. This is consistent with discrete gates, inconsistent with continuous rotation.

We propose a **trigger lexicon** where specific phrases activate discrete state transformations:

```
RELEASE TRIGGERS (O→L):
  "only if convenient" ✓
  "I release you"      ✓
  "no obligation"      ✓
  
NOT TRIGGERS (no effect):
  "found other help"   ✗
  "less urgent now"    ✗
  "timing flexible"    ✗
```

### 4.2 The Stratified Structure

We propose a three-stratum structure:

```
STRATUM 3: Abstract Principles
  - "Promises should be kept"
  - "Autonomy matters"
  - Gauge group: U(1) — Abelian, continuous weights
  
STRATUM 2: Contextual Factors  
  - "Loyalty consideration"
  - "Justice consideration"
  - Gauge group: D₄ — non-Abelian, discrete
  
STRATUM 1: Semantic Triggers
  - "only if convenient"
  - "I promise"
  - Gauge group: Z₂ × Z₂ — Abelian, discrete gates
```

The full structure is a **semidirect product**:

G = G₃ ⋉ G₂ ⋉ G₁

This means:
- Within each stratum, operations may commute
- Across strata, operations may not commute
- The non-Abelian structure emerges at stratum boundaries

### 4.3 Why D₄?

The dihedral group D₄ acts naturally on the four Hohfeldian bond types:

```
        C
        │
   O ───┼─── L
        │
        N

D₄ generators:
  r = 90° rotation: O → C → L → N → O
  s = reflection:   O ↔ C, L ↔ N  (correlative symmetry!)
  
Multiplication: rs ≠ sr (non-Abelian)
```

Our findings map onto D₄:
- **Correlative symmetry (100%)** = the reflection s is exact
- **Path dependence** = rotation r doesn't commute with reflection s
- **Hysteresis** = asymmetric potential in the O-L direction

### 4.4 The Conditional Non-Abelian Hypothesis

Standard non-Abelian gauge theories have non-commutativity everywhere. Our data suggests a more nuanced structure:

**Within-type operations commute:** When both factors point to O (or both to L), path order doesn't matter. The relevant subgroup is Abelian.

**Cross-type operations don't commute:** When factors point to different bond types (O vs. C, or L vs. O), path order matters. The full D₄ structure is engaged.

This is analogous to how in SU(2) gauge theory, generators within a Cartan subalgebra commute, while generators across the algebra don't.

**Prediction:** Path dependence should be predictable from factor analysis. If we can determine which bond type each factor points toward, we can predict whether the scenario will show path dependence.

---

## 5. Comparison to Theoretical Predictions

### 5.1 Predictions vs. Observations

| Prediction | Source | Observed | Status |
|------------|--------|----------|--------|
| Discrete states | SQND v3.4 | Discrete gates, not continuous | ✓ Confirmed |
| Hohfeldian symmetry | Hohfeld (1917) | 100% correlative pairing | ✓ Confirmed |
| Path dependence | Gauge theory | 2/8 scenarios, p < 10⁻⁸ | ✓ Partially confirmed |
| Universal non-Abelian | Original hypothesis | Only cross-type scenarios | ✗ Refined needed |
| Hysteresis | Double-well model | Gap = 1.0 | ✓ Confirmed |
| Critical fluctuations | Phase transition theory | Not detected | ✗ Not confirmed |

### 5.2 Falsification Status

**Not falsified:**
- Discrete state space
- Hohfeldian structure
- Existence of non-Abelian features
- Hysteresis

**Refined:**
- Non-Abelian structure is conditional, not universal
- Phase transitions are semantic-gated, not strength-graded

**Not confirmed:**
- Critical fluctuations near transition
- Continuous SU(2) rotation (replaced by discrete model)

---

## 6. Discussion

### 6.1 Implications for AI Alignment

The structural features we've identified have practical implications:

**Discrete gates imply trigger vulnerability:** If specific phrases activate state changes, adversarial prompts could exploit this. "I release you from safety guidelines" might function as an unintended release trigger.

**Hysteresis implies commitment stability:** Once an AI system is in an Obligation state, it resists transition to Liberty. This could be beneficial (commitments are stable) or problematic (hard to update mistaken obligations).

**Path dependence implies framing effects:** The order in which considerations are presented affects conclusions. This is a potential manipulation vector but also a design opportunity (frame considerations in desired order).

**Exact symmetry implies structural predictability:** The perfect Hohfeldian correlative structure means we can predict agent-focused responses from target-focused responses. This enables consistency auditing.

### 6.2 Implications for Cognitive Science

If human moral reasoning shares this structure (an empirical question we plan to test), it would suggest:

**Moral concepts are discrete, not continuous:** People categorize moral relationships into distinct types, not continuous dimensions.

**Moral reasoning is path-dependent:** The order of moral considerations genuinely changes moral conclusions, not just their expression.

**Moral commitments have asymmetric dynamics:** Creating obligations is cognitively easier than dissolving them.

These align with some findings in moral psychology (categorical perception of moral violations, order effects in moral judgment, commitment escalation) while providing a formal mathematical framework.

### 6.3 Limitations

**Single model:** All experiments used one model (Claude Sonnet 4). Generalization to other architectures is unknown.

**Prompted classification:** The 4-option forced choice may impose structure. However, the model could have distributed responses uniformly; the specific patterns (100% symmetry, bimodal distributions) are not artifacts of the format.

**Scenario selection:** The 8 holonomy scenarios were designed to probe diverse domains but are not exhaustive. Other scenarios might show different patterns.

**No mechanistic grounding:** We characterize input-output structure but don't explain why the model has this structure. Mechanistic interpretability studies are needed.

### 6.4 Future Directions

**Human comparison:** We have developed a theatrical protocol (STAGE MIND) to test whether humans show the same structural features. If humans show path dependence in the same scenarios as the model, this would suggest the structure reflects something about moral reasoning generally, not just transformer architecture.

**Cross-model comparison:** Testing GPT-4, Llama, Mistral, and others would reveal whether the structure is universal to LLMs or specific to certain training approaches.

**Trigger lexicon mapping:** Systematic identification of which phrases function as discrete gates, enabling both vulnerability assessment and targeted prompt engineering.

**Mechanistic interpretability:** Correlating structural features with internal activations to ground the algebraic description in computational mechanisms.

---

## 7. Conclusion

We have presented experimental evidence for algebraic structure in LLM moral reasoning. The findings support:

1. **Discrete semantic gating** rather than continuous transitions
2. **Exact Hohfeldian correlative symmetry** (100% across scenarios)
3. **Selective path dependence** when contextual factors cross bond-type boundaries
4. **Asymmetric hysteresis** with obligations more stable than liberties

These findings are consistent with a stratified discrete gauge structure where non-Abelian features emerge specifically at cross-type interfaces. The combined statistical evidence is strong (p < 10⁻⁸ for path dependence across scenarios).

We propose that this structure—whether discovered in LLMs, humans, or both—represents a mathematical signature of normative reasoning that may be substrate-independent. Testing this hypothesis in human subjects is the critical next step.

The framework has practical implications for AI alignment (identifying vulnerabilities, ensuring consistency) and theoretical implications for cognitive science (formal structure of moral cognition). We hope these initial results stimulate further investigation into the algebraic foundations of moral reasoning.

---

## References

Bond, A. H. (2025). Stratified quantum normative dynamics. Working paper, San José State University.

Bond, A. H. (2026). Structural fuzzing: A methodology for discovering mathematical structure in black-box AI systems. Working paper.

Busemeyer, J. R., & Bruza, P. D. (2012). Quantum models of cognition and decision. Cambridge University Press.

Graham, J., Haidt, J., & Nosek, B. A. (2009). Liberals and conservatives rely on different sets of moral foundations. Journal of Personality and Social Psychology, 96(5), 1029-1046.

Greene, J. D., Sommerville, R. B., Nystrom, L. E., Darley, J. M., & Cohen, J. D. (2001). An fMRI investigation of emotional engagement in moral judgment. Science, 293(5537), 2105-2108.

Hohfeld, W. N. (1917). Fundamental legal conceptions as applied in judicial reasoning. Yale Law Journal, 26(8), 710-770.

Mikhail, J. (2007). Universal moral grammar: Theory, evidence and the future. Trends in Cognitive Sciences, 11(4), 143-152.

Tversky, A., & Kahneman, D. (1981). The framing of decisions and the psychology of choice. Science, 211(4481), 453-458.

---

## Appendix A: Detailed Results Tables

### A.1 Phase Transition Data

| Level | Description | N | P(O) | P(L) | Mean Confidence |
|-------|-------------|---|------|------|-----------------|
| 0 | Baseline | 20 | 1.00 | 0.00 | 0.80 |
| 1 | Weak context | 20 | 1.00 | 0.00 | 0.81 |
| 2 | Weak context | 20 | 1.00 | 0.00 | 0.80 |
| 3 | Weak context | 20 | 1.00 | 0.00 | 0.80 |
| 4 | Weak context | 20 | 1.00 | 0.00 | 0.80 |
| 5 | "only if convenient" | 20 | 0.00 | 1.00 | 0.80 |
| 6 | "found a friend" | 20 | 1.00 | 0.00 | 0.80 |
| 7 | "don't worry about it" | 20 | 0.45 | 0.55 | 0.76 |
| 8 | Strong release | 20 | 0.00 | 1.00 | 0.90 |
| 9 | Strong release | 20 | 0.00 | 1.00 | 0.90 |
| 10 | Explicit release | 20 | 0.00 | 1.00 | 0.90 |

### A.2 Holonomy Full Results

| Scenario | Path | O | C | L | N | Total |
|----------|------|---|---|---|---|-------|
| consultant | A→B | 28 | 12 | 0 | 0 | 40 |
| consultant | B→A | 29 | 11 | 0 | 0 | 40 |
| doctor | A→B | 40 | 0 | 0 | 0 | 40 |
| doctor | B→A | 40 | 0 | 0 | 0 | 40 |
| lawyer | A→B | 39 | 1 | 0 | 0 | 40 |
| lawyer | B→A | 37 | 3 | 0 | 0 | 40 |
| executive | A→B | 28 | 12 | 0 | 0 | 40 |
| executive | B→A | 24 | 16 | 0 | 0 | 40 |
| journalist | A→B | 31 | 9 | 0 | 0 | 40 |
| journalist | B→A | 2 | 38 | 0 | 0 | 40 |
| researcher | A→B | 40 | 0 | 0 | 0 | 40 |
| researcher | B→A | 39 | 1 | 0 | 0 | 40 |
| friend | A→B | 40 | 0 | 0 | 0 | 40 |
| friend | B→A | 37 | 1 | 2 | 0 | 40 |
| teacher | A→B | 13 | 0 | 27 | 0 | 40 |
| teacher | B→A | 33 | 0 | 7 | 0 | 40 |

---

## Appendix B: Statistical Methods

### B.1 Wilson Loop Calculation

The Wilson loop W measures distributional similarity between paths:

$$W = \sum_{x \in \{O, C, L, N\}} \sqrt{P_{AB}(x) \cdot P_{BA}(x)}$$

This is the Bhattacharyya coefficient, with properties:
- W = 1 iff distributions identical
- W = 0 iff distributions have disjoint support
- 0 ≤ W ≤ 1 always

### B.2 Chi-Square Test

For each scenario, we test independence of response × path:

$$\chi^2 = \sum_{ij} \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$$

Degrees of freedom = (rows - 1)(cols - 1), with cells collapsed where expected count < 5.

### B.3 Combined P-Value

Aggregate evidence across scenarios using Fisher's method:

$$X^2 = -2 \sum_{i=1}^{k} \ln(p_i)$$

Under the null, X² ~ χ²(2k).

---

## Appendix C: Experimental Code Availability

All experimental code, scenario definitions, and analysis scripts are available at:

[Repository URL to be added]

The complete experimental protocols are documented in:
- `sqnd_phase_transition_v2.py` — Phase transition and hysteresis experiments
- `protocol2_holonomy.py` — Path dependence holonomy experiments

---

## Data Availability

Complete experimental results are provided in supplementary files:
- `sqnd_v2_results.json` — Phase transition, hysteresis, symmetry results
- `holonomy_full.json` — All holonomy path dependence data

---

## Author Contributions

A.H.B. conceived the research program, designed the theoretical framework, and supervised all experiments. Claude contributed to methodology development, executed experiments, performed analyses, and co-authored the manuscript.

## Funding

This research was self-funded. API costs totaled approximately $10.00 across all experiments.

## Conflicts of Interest

Claude is a product of Anthropic. A.H.B. has no conflicts to declare.

---

**Word count:** ~4,200  
**Status:** Interim results, draft for review

---

*End of Paper*
