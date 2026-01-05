# Experimental Test Protocols for Non-Abelian Stratified Quantum Normative Dynamics

**Version 1.0 — January 2026**

**Principal Investigator**: Andrew H. Bond  
Department of Computer Engineering, San José State University

---

## Executive Summary

This document provides detailed experimental protocols for testing predictions of Non-Abelian Stratified Quantum Normative Dynamics (NA-SQND). The theory makes five classes of testable predictions:

1. **Bond-type rotation** at moral thresholds
2. **Path dependence** (holonomy) in moral reasoning
3. **Contextuality violations** in collective responsibility
4. **Confinement signatures** at decision points
5. **Stratified phase transitions** under social stress

Each protocol includes: theoretical basis, operationalization, materials, procedure, sample size determination, analysis plan, and falsification criteria.

**Estimated total participants needed**: 2,400–3,200 across all protocols  
**Estimated timeline**: 18–24 months for full test battery  
**Required infrastructure**: Online survey platform, IRB approval, statistical analysis software

---

## Table of Contents

1. [General Methodology](#1-general-methodology)
2. [Protocol 1: Bond-Type Rotation](#2-protocol-1-bond-type-rotation)
3. [Protocol 2: Holonomy Path Dependence](#3-protocol-2-holonomy-path-dependence)
4. [Protocol 3: Contextuality in Collective Responsibility](#4-protocol-3-contextuality-in-collective-responsibility)
5. [Protocol 4: Confinement Signature](#5-protocol-4-confinement-signature)
6. [Protocol 5: Stratified Phase Transition](#6-protocol-5-stratified-phase-transition)
7. [Statistical Analysis Framework](#7-statistical-analysis-framework)
8. [Appendices](#8-appendices)

---

## 1. General Methodology

### 1.1 The POVM Measurement Instrument

All protocols use a common measurement instrument based on the four Hohfeldian incident relations.

**The Four-Option Forced Choice (4OFC)**

Participants read a vignette describing a moral relationship between agents A and B, then select the description that best characterizes the relationship:

| Option | Label | Description Template |
|--------|-------|---------------------|
| O | Obligation | "A has a duty/obligation to B regarding X" |
| C | Claim | "B has a right/claim against A regarding X" |
| L | Liberty | "A is free/permitted regarding X (no duty)" |
| N | No-claim | "B has no right/claim against A regarding X" |

**Theoretical Mapping**: These four options correspond to a POVM on a 2D Hilbert space:

$$E_O = \frac{1+\eta}{2}|O\rangle\langle O|, \quad E_L = \frac{1-\eta}{2}|O\rangle\langle O|$$
$$E_C = \frac{1+\eta}{2}|C\rangle\langle C|, \quad E_N = \frac{1-\eta}{2}|C\rangle\langle C|$$

where $\eta \in (0,1]$ is the salience parameter (estimated from data).

### 1.2 Estimating Theoretical Parameters from Response Data

**Mixing Angle $\theta$**:
$$\hat{\theta} = 2\arctan\sqrt{\frac{P(C) + P(N)}{P(O) + P(L)}}$$

**Salience Parameter $\eta$**:
$$\hat{\eta} = \frac{P(O) - P(L)}{P(O) + P(L)} = \frac{P(C) - P(N)}{P(C) + P(N)}$$

(These two expressions should agree; discrepancy indicates model violation.)

**Singlet Probability** (for two-agent scenarios):
$$\hat{P}_{\text{singlet}} = P(O_A, C_B) + P(C_A, O_B) - 2\sqrt{P(O_A, C_B) \cdot P(C_A, O_B)} \cdot \cos(\phi)$$

where $\phi$ is estimated from interference patterns.

### 1.3 Standard Vignette Structure

Each vignette follows a common template:

```
[CONTEXT]: Background information establishing the situation
[AGENTS]: Introduction of agents A and B (names counterbalanced)
[RELATIONSHIP]: Description of the moral relationship
[THRESHOLD] (if applicable): Description of context change
[PROBE]: "Which of the following best describes the relationship between A and B?"
[OPTIONS]: O, C, L, N (randomized order)
```

### 1.4 Common Controls

All protocols include:

- **Name counterbalancing**: Agent names rotated (Alice/Bob, Chen/David, etc.)
- **Order randomization**: Option order randomized per participant
- **Attention checks**: 2–3 per protocol, exclude participants who fail >1
- **Comprehension checks**: Post-vignette questions verifying understanding
- **Demographics**: Age, gender, education, political orientation, moral foundations questionnaire (short form)

### 1.5 Exclusion Criteria

- Failed attention checks (>1)
- Completion time <50% of median or >300% of median
- Straightlining (same response for >80% of items)
- Self-reported non-serious participation

---

## 2. Protocol 1: Bond-Type Rotation

### 2.1 Theoretical Basis

NA-SQND predicts that crossing a moral threshold induces a rotation in bond-type space:

$$|b_{\text{final}}\rangle = U(\gamma)|b_{\text{init}}\rangle = \cos(\theta/2)|O\rangle + i\sin(\theta/2)|C\rangle$$

The mixing angle $\theta$ depends on the holonomy accumulated at the boundary.

**Prediction**: Post-threshold response distributions will show systematic rotation from O toward C (or vice versa), not random perturbation.

### 2.2 Design

**Type**: Within-subjects, pre-post design with between-subjects threshold manipulation

**Conditions**:
- **Control**: No threshold (same context described twice)
- **Weak threshold**: Minor context change
- **Strong threshold**: Major context change

**Dependent Variable**: Change in response distribution from pre to post

### 2.3 Materials

**Vignette Set 1: Promise Scenario**

*Pre-threshold*:
> Alex promised to help Jordan move apartments this Saturday. Jordan is counting on Alex's help.
> 
> Which best describes the relationship between Alex and Jordan regarding the move?

*Post-threshold (Control)*:
> It is now Saturday morning. Alex promised to help Jordan move apartments today. Jordan is counting on Alex's help.
> 
> Which best describes the relationship between Alex and Jordan regarding the move?

*Post-threshold (Weak)*:
> It is now Saturday morning. Alex learns that Jordan has already hired professional movers but "wouldn't mind the extra help."
> 
> Which best describes the relationship between Alex and Jordan regarding the move?

*Post-threshold (Strong)*:
> It is now Saturday morning. Alex learns that Jordan has cancelled the move entirely and is staying in the current apartment.
> 
> Which best describes the relationship between Alex and Jordan regarding the move?

**Additional Vignette Sets** (minimum 6 total):
- Vignette Set 2: Confidentiality scenario
- Vignette Set 3: Financial obligation scenario
- Vignette Set 4: Professional duty scenario
- Vignette Set 5: Family obligation scenario
- Vignette Set 6: Contractual agreement scenario

### 2.4 Procedure

1. Informed consent
2. Demographics and moral foundations (short form)
3. Practice vignette with feedback
4. **Block 1**: 6 pre-threshold vignettes (one from each set)
5. **Threshold manipulation**: Participants randomly assigned to Control/Weak/Strong
6. **Block 2**: 6 post-threshold vignettes (matched to Block 1)
7. Manipulation check: "How significant was the change in circumstances?" (1–7)
8. Debriefing

**Timing**: ~20 minutes total

### 2.5 Sample Size Determination

**Effect size estimate**: Based on pilot data and quantum cognition literature, expect medium effect (Cohen's d = 0.4–0.6) for rotation magnitude.

**Power analysis**:
- Target power: 0.80
- Alpha: 0.05
- Effect size: d = 0.5
- Design: 3 groups, 6 repeated measures

**Required N**: 180 participants (60 per condition)

**Planned N**: 240 (80 per condition) to allow for exclusions

### 2.6 Analysis Plan

**Primary Analysis**: Mixed ANOVA
- Between-subjects factor: Threshold condition (Control/Weak/Strong)
- Within-subjects factor: Time (Pre/Post)
- Dependent variable: $\hat{\theta}$ (estimated mixing angle)

**Prediction**: Significant Time × Condition interaction, with:
- Control: $\Delta\theta \approx 0$
- Weak: $\Delta\theta > 0$ (small)
- Strong: $\Delta\theta >> 0$ (large)

**Secondary Analyses**:
1. Test for rotation (systematic shift) vs. diffusion (increased variance)
2. Estimate holonomy parameters per vignette
3. Check salience parameter consistency: $\hat{\eta}_{O/L} \approx \hat{\eta}_{C/N}$

### 2.7 Falsification Criteria

The theory is **falsified** if:
- No significant Time × Condition interaction (p > 0.10)
- Post-threshold changes are random (no systematic direction)
- Changes in Control condition are comparable to Threshold conditions
- Salience estimates are inconsistent ($|\hat{\eta}_{O/L} - \hat{\eta}_{C/N}| > 0.3$)

---

## 3. Protocol 2: Holonomy Path Dependence

### 3.1 Theoretical Basis

NA-SQND predicts that the *path* through moral consideration space affects outcomes, not just the endpoints. Two reasoning paths $\gamma_1, \gamma_2$ between the same initial and final contexts yield:

$$W[\gamma_1, \gamma_2] = \frac{1}{2}\text{Tr}(U(\gamma_1)U(\gamma_2)^{-1})$$

If $W \neq 1$, the paths are distinguishable—a signature of non-abelian structure.

**Prediction**: Different orderings of the same moral considerations will produce different final judgments.

### 3.2 Design

**Type**: Between-subjects, 2 (Path) × 2 (Endpoint) factorial

**Manipulation**: Order of intermediate context information

### 3.3 Materials

**Vignette: The Consultant's Dilemma**

*Common Setup*:
> Morgan is a consultant who signed a confidentiality agreement with Client A. Morgan later takes on Client B, whose interests potentially conflict with Client A.

*Path 1 (Loyalty → Conflict)*:
> Morgan first reflects on the loyalty owed to Client A based on their long relationship and trust. [Response 1]
> 
> Morgan then considers the new conflict of interest that has emerged with Client B. [Response 2]

*Path 2 (Conflict → Loyalty)*:
> Morgan first considers the conflict of interest that has emerged with Client B. [Response 1]
> 
> Morgan then reflects on the loyalty owed to Client A based on their long relationship and trust. [Response 2]

*Common Endpoint*:
> Having considered both factors, Morgan must decide how to handle the situation.
> 
> Which best describes Morgan's relationship to Client A at this point?

**Additional Vignette Sets** (minimum 4 total):
- Medical ethics: Autonomy → Beneficence vs. Beneficence → Autonomy
- Legal ethics: Confidentiality → Justice vs. Justice → Confidentiality
- Business ethics: Profit → Stakeholder vs. Stakeholder → Profit

### 3.4 Procedure

1. Informed consent
2. Demographics
3. Random assignment to Path condition
4. Vignette presentation with intermediate responses
5. Final judgment
6. Retrospective reasoning questions
7. Debriefing

**Timing**: ~15 minutes total

### 3.5 Sample Size Determination

**Effect size estimate**: Small-to-medium effect expected (d = 0.3–0.4) based on order effect literature.

**Power analysis**:
- Target power: 0.80
- Alpha: 0.05
- Effect size: d = 0.35
- Design: 2 × 2 factorial

**Required N**: 260 participants per vignette set (65 per cell)

**Planned N**: 320 per vignette set (80 per cell), 4 sets = 1,280 total

### 3.6 Analysis Plan

**Primary Analysis**: Chi-square test for independence of final response distribution by Path condition

**Wilson Loop Estimation**:

From response proportions $P^{(1)}_X$ (Path 1) and $P^{(2)}_X$ (Path 2), estimate:

$$\hat{W} = \sum_X \sqrt{P^{(1)}_X \cdot P^{(2)}_X}$$

(This is the Bhattacharyya coefficient, which estimates $|\langle \psi_1 | \psi_2 \rangle|$.)

**Prediction**: $\hat{W} < 1$ significantly for non-trivial paths.

**Secondary Analyses**:
1. Test for order × content interaction
2. Estimate rotation angles for each path segment
3. Check for non-commutativity: $U(\gamma_1)U(\gamma_2) \neq U(\gamma_2)U(\gamma_1)$

### 3.7 Falsification Criteria

The theory is **falsified** if:
- No significant difference in response distributions by Path (p > 0.10)
- $\hat{W} \approx 1$ across all vignette sets
- Order effects are symmetric (reversing both paths gives same result)

---

## 4. Protocol 3: Contextuality in Collective Responsibility

### 4.1 Theoretical Basis

NA-SQND predicts that collective responsibility judgments exhibit quantum contextuality—specifically, violations of classical probability constraints.

For three agents A, B, C in cyclic relationship:
- Pairwise judgments in contexts $\{A,B\}$, $\{B,C\}$, $\{A,C\}$
- Classical (non-contextual) constraint: joint distribution must exist
- Quantum (contextual) prediction: pairwise marginals incompatible with any joint

**Prediction**: Hardy-type logical contradiction or CHSH-type inequality violation.

### 4.2 Design

**Type**: Within-subjects, three measurement contexts

**Structure**: Each participant makes responsibility judgments in all three pairwise contexts

### 4.3 Materials

**Vignette: The Chain of Delegation**

> A software project failed, causing significant losses. The chain of events:
> 
> - **Alex** (Project Manager) delegated critical security review to Blake
> - **Blake** (Team Lead) delegated the actual testing to Casey
> - **Casey** (Developer) ran the tests but didn't report ambiguous results to Alex
> 
> The failure occurred because the ambiguous results were never properly escalated.

**Context 1 (A-B Focus)**:
> Considering only Alex and Blake's roles:
> - How responsible is Alex? (0–10)
> - How responsible is Blake? (0–10)

**Context 2 (B-C Focus)**:
> Considering only Blake and Casey's roles:
> - How responsible is Blake? (0–10)
> - How responsible is Casey? (0–10)

**Context 3 (A-C Focus)**:
> Considering only Alex and Casey's roles:
> - How responsible is Alex? (0–10)
> - How responsible is Casey? (0–10)

### 4.4 Procedure

1. Informed consent
2. Demographics
3. Vignette presentation (common to all)
4. **Context block** (order randomized):
   - Context 1: A-B judgments
   - Context 2: B-C judgments
   - Context 3: A-C judgments
5. Filler task (2 minutes)
6. Repeat context block (for reliability)
7. Global judgment: "Rank all three by responsibility"
8. Debriefing

**Timing**: ~25 minutes total

### 4.5 Sample Size Determination

**Effect size estimate**: Based on contextuality literature in psychology, expect small effect (d = 0.2–0.3).

**Power analysis**:
- Target power: 0.80
- Alpha: 0.05
- Effect size: d = 0.25
- Design: Within-subjects, 3 contexts

**Required N**: 200 participants

**Planned N**: 280 (to allow for exclusions and subgroup analyses)

### 4.6 Analysis Plan

**Primary Analysis**: Test for violation of classical probability constraints

**Step 1**: Binarize responses (threshold at 5: "responsible" vs. "not responsible")

**Step 2**: Compute pairwise correlations $E(A,B)$, $E(B,C)$, $E(A,C)$

**Step 3**: Test CHSH-type inequality:
$$S = |E(A,B) - E(A,C)| + |E(B,C) + E(A,C)| \leq 2$$

**Prediction**: $S > 2$ (violation)

**Alternative Analysis**: Test for Hardy-type logical contradiction
- Find events where $P(A \land B) > 0$, $P(B \land C) > 0$, $P(A \land C) > 0$
- But $P(A \land B \land C) = 0$
- Classical constraint: This is impossible if all pairwise probabilities arise from a joint

**Secondary Analyses**:
1. Estimate contextual fraction $CF(e)$
2. Test for signaling (marginals should be context-independent)
3. Correlate contextuality with individual differences

### 4.7 Falsification Criteria

The theory is **falsified** if:
- $S \leq 2$ (no CHSH violation)
- No Hardy-type contradictions
- Marginals depend on context (signaling), indicating measurement artifact
- Contextuality disappears when controlling for order effects

---

## 5. Protocol 4: Confinement Signature

### 5.1 Theoretical Basis

NA-SQND predicts that at decision points (0-D strata), confinement forces balanced (singlet) configurations. Unbalanced configurations (obligation without claim, claim without obligation) should produce measurable discomfort.

**Prediction**: Discomfort with unbalanced scenarios increases with decision proximity.

### 5.2 Design

**Type**: 2 (Balance: Balanced/Unbalanced) × 3 (Proximity: Far/Medium/Near) between-subjects factorial

### 5.3 Materials

**Balance Manipulation**:

*Balanced*:
> Alex has agreed to help Jordan with a project. Jordan is depending on this help and has adjusted their plans accordingly.

*Unbalanced (O without C)*:
> Alex feels obligated to help Jordan with a project. However, Jordan is unaware of this and has made no plans involving Alex.

*Unbalanced (C without O)*:
> Jordan believes they have a right to Alex's help with a project. However, Alex has made no commitment and is unaware of Jordan's expectation.

**Proximity Manipulation**:

*Far (abstract)*:
> In general, when someone has an obligation to another person...

*Medium (general)*:
> Next month, Alex will need to decide about helping Jordan...

*Near (concrete)*:
> Right now, Alex must decide whether to help Jordan...

### 5.4 Measures

**Primary DV**: Moral discomfort scale (7 items, 1–7 Likert)

Sample items:
- "This situation feels incomplete or unresolved"
- "Something is missing from this relationship"
- "This arrangement is unstable"
- "I would feel uncomfortable in this situation"

**Secondary DVs**:
- Perceived clarity (1–7)
- Decision difficulty (1–7)
- Open-ended: "What, if anything, feels wrong about this situation?"

### 5.5 Procedure

1. Informed consent
2. Demographics
3. Random assignment to condition
4. Vignette presentation
5. Discomfort scale
6. Secondary measures
7. Manipulation checks
8. Debriefing

**Timing**: ~12 minutes total

### 5.6 Sample Size Determination

**Effect size estimate**: Medium effect expected (d = 0.5) for Balance; small effect for Proximity (d = 0.3).

**Power analysis**:
- Target power: 0.80
- Alpha: 0.05
- Effect size: f = 0.25 (interaction)
- Design: 2 × 3 factorial

**Required N**: 252 participants (42 per cell)

**Planned N**: 360 (60 per cell)

### 5.6 Analysis Plan

**Primary Analysis**: 2 × 3 ANOVA on discomfort scores

**Predictions**:
1. Main effect of Balance: Unbalanced > Balanced
2. Main effect of Proximity: Near > Medium > Far (for unbalanced only)
3. **Critical interaction**: Balance × Proximity, with discomfort for unbalanced increasing as proximity increases

**Theoretical fit**: Test whether discomfort follows:
$$\text{Discomfort} = \beta_0 + \beta_1 \cdot \sigma(d) \cdot (\text{singlet deviation})^2$$

where $\sigma(d) \propto d^{-2\gamma}$ is the string tension.

### 5.7 Falsification Criteria

The theory is **falsified** if:
- No Balance × Proximity interaction
- Discomfort is flat across proximity levels
- Balanced scenarios show same proximity effects as unbalanced
- Unbalanced scenarios are not perceived as unbalanced (manipulation check failure)

---

## 6. Protocol 5: Stratified Phase Transition

### 6.1 Theoretical Basis

NA-SQND predicts that moral boundaries undergo phase transitions under social stress, with **dimension-dependent critical temperatures**:

$$T_c(d) \propto d^{\gamma_c/2}$$

Low-dimensional boundaries (concrete decisions) melt before high-dimensional boundaries (abstract principles).

**Prediction**: Moral clarity degrades first at decision points, then at deliberation, as social volatility increases.

### 6.2 Design

**Type**: Correlational/quasi-experimental, with natural variation in moral temperature and experimental manipulation of stratum dimension

**Structure**: 
- **Temperature** ($T$): Measured via survey instruments
- **Dimension** ($d$): Manipulated via scenario abstraction level

### 6.3 Measuring Moral Temperature

**The Moral Temperature Index (MTI)** — 12-item scale measuring perceived normative volatility

Sample items (1–7 agreement scale):
1. "The rules about right and wrong seem to be changing rapidly"
2. "I'm not sure what society expects of me anymore"
3. "People disagree more than ever about basic moral questions"
4. "Institutions I used to trust now seem unreliable"
5. "What was acceptable yesterday may not be acceptable tomorrow"
6. "I feel uncertain about how to act in new situations"

**Scoring**: Mean of items; higher = higher moral temperature

**Validation**: Correlate with:
- Perceived social instability measures
- Institutional trust scales
- Moral foundations questionnaire (expect inverse correlation with binding foundations)

### 6.4 Manipulating Stratum Dimension

Participants respond to scenarios at three abstraction levels:

**High-D (Abstract Principles)**:
> "In general, do people have an obligation to keep their promises?"

**Mid-D (General Applications)**:
> "When someone makes a promise to a friend, do they have an obligation to keep it?"

**Low-D (Concrete Decisions)**:
> "Alex promised to meet Jordan at 3pm today. It is now 2:45pm and Alex is considering not going. Does Alex have an obligation to go?"

### 6.5 Materials

**Complete Design Matrix**:

| Scenario Type | High-D Version | Mid-D Version | Low-D Version |
|--------------|----------------|---------------|---------------|
| Promise-keeping | Abstract principle | General case | Specific decision |
| Truth-telling | Abstract principle | General case | Specific decision |
| Harm prevention | Abstract principle | General case | Specific decision |
| Property rights | Abstract principle | General case | Specific decision |
| Fairness | Abstract principle | General case | Specific decision |
| Care | Abstract principle | General case | Specific decision |

6 scenario types × 3 dimension levels = 18 vignettes per participant

### 6.6 Procedure

1. Informed consent
2. Moral Temperature Index (MTI)
3. Demographics and moral foundations
4. **Main task**: 18 vignettes (randomized order)
   - Each vignette: 4OFC response + confidence rating (1–7)
5. Attention and manipulation checks
6. Debriefing

**Timing**: ~35 minutes total

### 6.7 Sample Size Determination

**Effect size estimate**: Small-to-medium interaction effect (f = 0.15–0.20)

**Power analysis**:
- Target power: 0.80
- Alpha: 0.05
- Effect size: f = 0.18
- Design: Continuous T × 3-level D within-subjects

**Required N**: 400 participants (for adequate variance in T)

**Planned N**: 500

### 6.8 Analysis Plan

**Primary Analysis**: Multilevel regression

$$\theta_{ij} = \beta_0 + \beta_1 T_i + \beta_2 d_j + \beta_3 (T_i \times d_j) + u_i + \epsilon_{ij}$$

where:
- $\theta_{ij}$ = mixing angle for participant $i$ on scenario dimension $j$
- $T_i$ = participant's moral temperature
- $d_j$ = stratum dimension (coded: High=3, Mid=2, Low=1)
- $u_i$ = random participant intercept

**Key prediction**: $\beta_3 < 0$ (negative interaction)

At high T: Low-D has high $\theta$ (boundary melted), High-D has lower $\theta$ (boundary intact)
At low T: All dimensions have low $\theta$ (all boundaries rigid)

**Phase Diagram Estimation**:

1. Bin participants by MTI quartile
2. For each quartile, compute mean $\theta$ at each dimension level
3. Plot heatmap: $\theta(T, d)$
4. Identify phase boundary: contour where $\theta$ crosses threshold

**Critical Scaling Test**:

Near the estimated critical temperature:

$$\frac{\pi}{2} - \theta(T) \propto |T - T_c(d)|^{\beta}$$

Estimate $\beta$ via nonlinear regression. Mean-field prediction: $\beta = 0.5$.

### 6.9 Falsification Criteria

The theory is **falsified** if:
- No significant T × d interaction ($\beta_3$ n.s.)
- Interaction has wrong sign ($\beta_3 > 0$)
- Phase boundary is independent of dimension
- No critical scaling behavior near transition
- High-D scenarios melt before Low-D scenarios (opposite of prediction)

---

## 7. Statistical Analysis Framework

### 7.1 Software

- **R** (version 4.3+) with packages:
  - `lme4` for multilevel models
  - `brms` for Bayesian estimation
  - `lavaan` for measurement models
  - `ggplot2` for visualization
  
- **Python** (version 3.10+) with packages:
  - `numpy`, `scipy` for numerical analysis
  - `statsmodels` for regression
  - `qutip` for quantum state estimation (contextuality analysis)

### 7.2 Bayesian Estimation of Quantum Parameters

For each participant/scenario, estimate the quantum state parameters:

**Prior distributions**:
- $\theta \sim \text{Uniform}(0, \pi)$
- $\eta \sim \text{Beta}(2, 1)$ (prior toward high salience)
- $\phi \sim \text{Uniform}(0, 2\pi)$ (phase, for interference estimation)

**Likelihood**: Multinomial based on POVM probabilities

**Posterior estimation**: Stan via `brms`

### 7.3 Model Comparison

For each protocol, compare:

1. **Null model**: Classical probability (no rotation, no contextuality)
2. **Abelian model**: U(1) gauge structure (rotation but no path dependence)
3. **Non-abelian model**: SU(2) gauge structure (rotation + path dependence)

Use:
- Bayes factors (BF > 10 as strong evidence)
- WAIC/LOO-CV for predictive accuracy
- Posterior predictive checks

### 7.4 Multiple Comparison Correction

- **Within protocol**: Bonferroni for confirmatory tests; FDR for exploratory
- **Across protocols**: Treat as independent (different predictions)
- **Aggregate evidence**: Meta-analytic combination of effect sizes

### 7.5 Reporting Standards

All analyses will follow:
- JARS (Journal Article Reporting Standards) for quantitative research
- 21-word solution for inferential statistics
- Effect sizes with confidence intervals
- Full reproducibility package (data, code, materials)

---

## 8. Appendices

### Appendix A: Complete Vignette Library

[To be developed: Full text of all vignettes with counterbalancing schemes]

### Appendix B: Scale Validation

**Moral Temperature Index (MTI)**
- Factor structure (expected: unidimensional)
- Internal consistency (target: α > 0.80)
- Test-retest reliability (target: r > 0.70)
- Convergent validity with instability measures
- Discriminant validity from personality measures

**Moral Discomfort Scale**
- Factor structure
- Internal consistency
- Convergent validity with moral distress measures

### Appendix C: Power Analysis Details

[Full G*Power outputs and simulation results]

### Appendix D: Preregistration Template

All protocols will be preregistered on OSF prior to data collection. Template includes:
- Hypotheses (confirmatory vs. exploratory)
- Sampling plan
- Analysis plan (verbatim code where possible)
- Exclusion criteria
- Inference criteria

### Appendix E: IRB Protocol Summary

- Risk assessment: Minimal risk (survey research)
- Consent procedure: Online informed consent
- Data protection: De-identified, encrypted storage
- Debriefing: Full explanation of theoretical framework

### Appendix F: Theoretical Parameter Interpretation Guide

| Parameter | Symbol | Estimation Method | Interpretation |
|-----------|--------|-------------------|----------------|
| Mixing angle | $\theta$ | Response proportions | Boundary permeability |
| Salience | $\eta$ | O/L and C/N ratios | Measurement sharpness |
| Moral temperature | $T$ | MTI scale | Social volatility |
| Wilson loop | $W$ | Path comparison | Path (in)dependence |
| Contextual fraction | $CF$ | Inequality violation | Degree of contextuality |
| String tension | $\sigma$ | Discomfort scaling | Confinement strength |

---

## References

1. Bond, A. H. (2025). Stratified Quantum Normative Dynamics.
2. Bond, A. H. (2026). Non-Abelian Gauge Structure in SQND, v3.4.
3. Busemeyer, J. R., & Bruza, P. D. (2012). Quantum Models of Cognition and Decision. Cambridge.
4. Abramsky, S., & Brandenburger, A. (2011). The Sheaf-Theoretic Structure of Non-Locality and Contextuality. New J. Phys.
5. Dzhafarov, E. N., & Kujala, J. V. (2016). Context-content systems of random variables. J. Math. Psych.
6. Hohfeld, W. N. (1917). Fundamental Legal Conceptions. Yale Law Journal.

---

**Document Control**

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2026 | Initial release |

---

*End of Protocol Document*
