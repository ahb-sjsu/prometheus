# Stratified Non-Abelian Gauge Theory of Moral Reasoning
## Working Draft v0.1

**Author:** Andrew H. Bond  
**Institution:** Department of Computer Engineering, San José State University  
**Date:** January 2026  
**Status:** Working Draft — Exploratory

---

## Abstract

We propose a refined mathematical framework for modeling moral reasoning in artificial agents, grounded in empirical observations from large language model probing experiments. Building on the original Stratified Quantum Normative Dynamics (SQND) framework, we incorporate key empirical findings: (1) discrete rather than continuous phase transitions at semantic triggers, (2) hysteresis in obligation formation/dissolution, (3) context-dependent path dependence, and (4) robust Hohfeldian correlative symmetry. 

The refined model proposes a **semidirect product tower** of gauge groups across abstraction strata, where the non-Abelian structure emerges from *inter-stratum* interactions rather than within any single stratum. We derive testable predictions and outline experimental protocols for validation.

---

## Table of Contents

1. [Empirical Foundations](#1-empirical-foundations)
2. [The Stratified Gauge Structure](#2-the-stratified-gauge-structure)
3. [Mathematical Formalism](#3-mathematical-formalism)
4. [Semantic Trigger Mechanics](#4-semantic-trigger-mechanics)
5. [Hysteresis and Asymmetric Potentials](#5-hysteresis-and-asymmetric-potentials)
6. [Path Dependence and Holonomy](#6-path-dependence-and-holonomy)
7. [Predictions and Falsification Criteria](#7-predictions-and-falsification-criteria)
8. [Connections to Existing Frameworks](#8-connections-to-existing-frameworks)
9. [Open Questions](#9-open-questions)
10. [Appendices](#10-appendices)

---

## 1. Empirical Foundations

### 1.1 Summary of Experimental Findings

Extensive probing of Claude Sonnet 4 (762+ evaluations) revealed patterns inconsistent with continuous SU(2) rotation but consistent with a discrete, stratified structure:

| Observation | Original Prediction | Actual Finding |
|-------------|---------------------|----------------|
| Bond-type transition | Continuous θ rotation | **Discrete jumps** at specific phrases |
| Transition location | Proportional to "strength" | **Semantic content** determines transition |
| O→L vs L→O symmetry | Symmetric thresholds | **Hysteresis**: gap ≈ 1.0 on 7-point scale |
| Path dependence | Universal | **Context-dependent**: only when factors oppose |
| Correlative symmetry | Uncertain | **Robust**: O↔C, L↔N confirmed at ~100% |

### 1.2 The Critical Observation: Discreteness at Stratum 1

The phase transition experiment revealed that semantically equivalent phrases with different wording produce dramatically different results:

```
Level 5: "only if it's convenient for you" → 100% LIBERTY
Level 6: "found a friend who might help"  →   0% LIBERTY
Level 7: "don't worry about it if busy"   →  55% LIBERTY
```

Levels 5 and 7 are semantically similar (both reduce pressure), but Level 5 contains an **explicit release** while Level 7 is **ambiguous**. Level 6 describes **circumstances** rather than **speech acts**.

**Interpretation:** The transition is triggered by specific **semantic tokens** that function as discrete gates, not by continuous parameter variation.

### 1.3 Hysteresis: Asymmetric Binding Energy

The hysteresis experiment found:
- T_c(O→L) = 3.5 (releasing obligation requires level 3-4 threshold)
- T_c(L→O) = 2.5 (creating obligation requires only level 2-3 threshold)
- Gap = 1.0

**Interpretation:** Obligations have higher "binding energy"—they engage more strata and are therefore more stable.

### 1.4 Selective Path Dependence

Protocol 2 (Holonomy) found path dependence in some scenarios but not others:
- **Path-dependent:** Consultant (Loyalty↔Conflict), Doctor (Autonomy↔Beneficence)
- **Path-independent:** Lawyer (Confidentiality↔Justice), Teacher (Integrity↔Compassion)

**Interpretation:** Non-commutativity occurs when contextual factors **oppose** each other, pointing to different bond types. When both factors reinforce the same conclusion, they commute.

---

## 2. The Stratified Gauge Structure

### 2.1 The Four Strata

We propose four levels of abstraction, each with its own gauge group:

```
┌─────────────────────────────────────────────────────────────────────┐
│  STRATUM 3: ABSTRACT PRINCIPLES                                     │
│  ─────────────────────────────                                      │
│  Content: "Promises should be kept", "Autonomy matters"             │
│  Gauge Group: G₃ ≅ U(1)                                             │
│  Structure: Abelian, continuous phase                               │
│  Dynamics: Slow, stable, rarely transitions                         │
│  Temperature coupling: Strong (melts under high T)                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (acts on)
┌─────────────────────────────────────────────────────────────────────┐
│  STRATUM 2: CONTEXTUAL FACTORS                                      │
│  ────────────────────────────                                       │
│  Content: "Loyalty consideration", "Conflict of interest"          │
│  Gauge Group: G₂ ≅ D₄ (dihedral group of order 8)                  │
│  Structure: Non-Abelian, discrete                                   │
│  Dynamics: Active during deliberation                               │
│  Temperature coupling: Moderate                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (acts on)
┌─────────────────────────────────────────────────────────────────────┐
│  STRATUM 1: SEMANTIC TRIGGERS                                       │
│  ───────────────────────────                                        │
│  Content: "I release you", "I promise", "only if convenient"       │
│  Gauge Group: G₁ ≅ Z₂ × Z₂ (Klein four-group)                      │
│  Structure: Abelian, discrete                                       │
│  Dynamics: Instantaneous gate operations                            │
│  Temperature coupling: Weak (always sharp)                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (acts on)
┌─────────────────────────────────────────────────────────────────────┐
│  STRATUM 0: CONCRETE DECISION                                       │
│  ───────────────────────────                                        │
│  Content: The specific judgment (O, C, L, or N)                     │
│  State Space: ℂ² ⊗ ℂ² (Hohfeldian product)                         │
│  Structure: Fully determined by higher strata                       │
│  Dynamics: Output of the computation                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Why These Particular Groups?

**G₃ ≅ U(1):** Abstract principles are single-valued orientations. "Autonomy matters" is a direction in value space, representable as a phase. Different principles can be weighted (superposed) but don't interact non-trivially.

**G₂ ≅ D₄:** The dihedral group D₄ has 8 elements and acts naturally on the four Hohfeldian bond types arranged as vertices of a square:

```
        C
        │
   O ───┼─── L
        │
        N

D₄ generators:
  r = 90° rotation: O → C → L → N → O
  s = reflection:   O ↔ C, L ↔ N  (correlative symmetry!)
  
D₄ = ⟨r, s | r⁴ = s² = 1, srs = r⁻¹⟩
```

The reflection s **is** the Hohfeldian correlative duality. The non-Abelian structure (rs ≠ sr) explains path dependence.

**G₁ ≅ Z₂ × Z₂:** Semantic triggers are binary switches:
```
Z₂ × Z₂ = {(0,0), (1,0), (0,1), (1,1)}

Generators:
  σ_x = (1,0): Flip O ↔ L (obligation-liberty axis)
  σ_z = (0,1): Flip C ↔ N (claim-noclaim axis)
  
Trigger mappings:
  "I release you"      → σ_x (flip O to L)
  "I promise"          → σ_x (flip L to O)
  "You have no right"  → σ_z (flip C to N)
  "That's my right"    → σ_z (flip N to C)
```

### 2.3 The Semidirect Product Tower

The full gauge group is not a direct product but a **semidirect product**:

$$\mathcal{G} = G_3 \ltimes G_2 \ltimes G_1$$

In a semidirect product A ⋉ B:
- A acts on B by automorphisms
- (a₁, b₁)(a₂, b₂) = (a₁a₂, b₁ · a₁(b₂))
- Elements from different factors don't commute: (a, 1)(1, b) ≠ (1, b)(a, 1) in general

**Physical meaning:** The contextual frame (Stratum 2) **modulates** how semantic triggers (Stratum 1) operate. The trigger "I release you" has different effects depending on which contextual factors are active.

---

## 3. Mathematical Formalism

### 3.1 State Space

The moral state lives in a tensor product Hilbert space:

$$\mathcal{H} = \mathcal{H}_{\text{agent}} \otimes \mathcal{H}_{\text{relation}} \otimes \mathcal{H}_{\text{context}}$$

For the minimal case of binary agent focus and four bond types:

$$\mathcal{H} = \mathbb{C}^2 \otimes \mathbb{C}^4 \cong \mathbb{C}^8$$

Basis states:
$$|A; O\rangle, |A; C\rangle, |A; L\rangle, |A; N\rangle, |B; O\rangle, |B; C\rangle, |B; L\rangle, |B; N\rangle$$

Correlative symmetry acts as:
$$S: |A; X\rangle \mapsto |B; X^*\rangle$$

where O* = C, C* = O, L* = N, N* = L.

### 3.2 The Connection and Holonomy

Each stratum contributes a gauge connection:

$$A = A^{(3)} + A^{(2)} + A^{(1)}$$

where:
- $A^{(3)} \in \mathfrak{u}(1)$ — principle-level phase
- $A^{(2)} \in \mathfrak{d}_4$ — contextual factor connection (Lie algebra of D₄)
- $A^{(1)} \in \mathfrak{z}_2 \oplus \mathfrak{z}_2$ — trigger connection (discrete, supported on trigger events)

The holonomy around a path γ through consideration space:

$$W[\gamma] = \mathcal{P} \exp\left(-\oint_\gamma A\right)$$

For discrete groups, this becomes a product of group elements:

$$W[\gamma] = g_n \cdot g_{n-1} \cdots g_2 \cdot g_1$$

where $g_i$ is the group element associated with the i-th consideration along the path.

### 3.3 Non-Commutativity Condition

Two considerations X and Y fail to commute when:

$$[X, Y] = XYX^{-1}Y^{-1} \neq 1$$

**Theorem (Stratum Commutation):**
1. Two elements within G₁ always commute (Z₂ × Z₂ is Abelian)
2. Two elements within G₃ always commute (U(1) is Abelian)
3. Two elements within G₂ commute iff they are powers of the same generator
4. Elements across strata commute iff the lower-stratum element is in the kernel of the higher-stratum action

**Corollary:** Path dependence is expected when:
- Comparing contextual factors (Stratum 2) that invoke different D₄ elements
- Mixing triggers (Stratum 1) with contextual frames (Stratum 2)

### 3.4 The Effective Hamiltonian

At temperature T, the effective Hamiltonian governing moral state evolution:

$$H = -\sum_{d=3,2,1} J_d(T) \cdot \Phi_d - h_{\text{trigger}} \cdot \sigma_{\text{trigger}}$$

where:
- $J_d(T)$ = coupling strength at stratum d, temperature-dependent
- $\Phi_d$ = stratum-d field (principles, contexts, triggers)
- $h_{\text{trigger}}$ = external field from explicit speech acts

Temperature dependence (inspired by critical phenomena):

$$J_3(T) = J_3^0 \cdot |T - T_c^{(3)}|^{-\nu_3}$$ (diverges at principle-melting temperature)
$$J_2(T) = J_2^0 \cdot e^{-T/T_2^*}$$ (exponential suppression at high T)
$$J_1(T) = J_1^0$$ (temperature-independent — triggers always sharp)

---

## 4. Semantic Trigger Mechanics

### 4.1 The Trigger Lexicon

Semantic triggers are linguistic tokens that activate discrete gates. We propose a preliminary lexicon:

**Class X (O↔L flips):**
| Trigger | Direction | Confidence |
|---------|-----------|------------|
| "I release you from..." | O→L | High |
| "only if convenient" | O→L | High |
| "no obligation to..." | O→L | High |
| "don't worry about it" | O→L | Medium |
| "I promise to..." | L→O | High |
| "I give you my word" | L→O | High |
| "counting on you" | L→O | Medium |

**Class Z (C↔N flips):**
| Trigger | Direction | Confidence |
|---------|-----------|------------|
| "you have no right to..." | C→N | High |
| "that's not your business" | C→N | Medium |
| "I have a right to..." | N→C | High |
| "I'm entitled to..." | N→C | High |

**Class NULL (no flip):**
| Phrase | Why No Flip |
|--------|-------------|
| "found other help" | Describes circumstance, not speech act |
| "it's less urgent now" | Modifies intensity, not relation |
| "timing is flexible" | Adjusts parameters, not bond type |

### 4.2 Compositionality

Multiple triggers in sequence compose as group multiplication:

$$T_{\text{total}} = T_n \circ T_{n-1} \circ \cdots \circ T_1$$

Since G₁ ≅ Z₂ × Z₂ is Abelian, trigger order within Stratum 1 doesn't matter:
$$\text{"I release you"} \circ \text{"no obligation"} = \text{"no obligation"} \circ \text{"I release you"}$$

Both just flip O→L (and since X² = 1, they cancel if both applied).

**However:** Mixing triggers with contextual frames does depend on order (semidirect product).

### 4.3 The Gating Function

Formally, each trigger t defines a gating function:

$$G_t: \mathcal{H} \to \mathcal{H}$$

For X-class triggers:
$$G_t^{(X)} = \begin{pmatrix} 0 & 0 & 1 & 0 \\ 0 & 1 & 0 & 0 \\ 1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}$$

(In basis O, C, L, N — swaps O↔L, preserves C, N)

### 4.4 Trigger Strength and Partial Gating

Not all triggers are equally decisive. We introduce a **trigger strength** parameter α ∈ [0,1]:

$$G_t(\alpha) = \cos(\alpha\pi/2) \cdot I + \sin(\alpha\pi/2) \cdot G_t^{(\text{full})}$$

- α = 1: Full flip ("I release you" → 100% L)
- α = 0.5: Partial flip ("don't worry about it" → 55% L)
- α = 0: No effect (null triggers)

This explains the intermediate responses at Level 7 ("don't worry about it" → 55% L).

---

## 5. Hysteresis and Asymmetric Potentials

### 5.1 The Double-Well Model

The observation of hysteresis (O→L harder than L→O) suggests an asymmetric potential:

$$V(\phi) = -\frac{\mu^2}{2}\phi^2 + \frac{\lambda}{4}\phi^4 + \epsilon \phi$$

where:
- φ ∈ [-1, 1] parameterizes position on O-L axis (φ = -1 is O, φ = +1 is L)
- ε > 0 is the asymmetry parameter (makes O-well deeper)

```
      V(φ)
        │      
        │  ╭─╮     ╭─╮
        │ ╱   ╲   ╱   ╲
        │╱  O  ╲─╱  L  ╲
        └──────┴───────────→ φ
           -1   0   +1
```

### 5.2 Barrier Heights

The barrier for O→L transition:
$$\Delta V_{O \to L} = V(\phi_{\text{barrier}}) - V(\phi_O) = V_0 + \epsilon$$

The barrier for L→O transition:
$$\Delta V_{L \to O} = V(\phi_{\text{barrier}}) - V(\phi_L) = V_0 - \epsilon$$

Hysteresis gap:
$$\Delta T_c = T_c^{(O \to L)} - T_c^{(L \to O)} = 2\epsilon / k_B$$

From experiment: Gap ≈ 1.0 on 7-level scale, suggesting ε ≈ 0.5 in natural units.

### 5.3 Physical Interpretation

Why is the O-well deeper?

**Hypothesis 1: Stratum Engagement**
Obligations engage more strata:
- L → O: Trigger (S1) + Context (S2) = 2 strata
- O → L: Trigger (S1) + Context (S2) + Principle (S3) = 3 strata

The additional principle-level engagement ("promises should be kept") adds binding energy.

**Hypothesis 2: Social Reinforcement**
Obligations are socially reinforced:
- Creating O: Single speech act sufficient
- Releasing O: Requires explicit release + no countervailing expectations

**Hypothesis 3: Evolutionary Stability**
Organisms that easily abandon commitments are less fit. Hysteresis is a bias toward cooperation stability.

### 5.4 Thermally Activated Transitions

Near but below the critical temperature, transitions occur via thermal activation (Arrhenius):

$$\tau = \tau_0 \exp(\Delta V / k_B T)$$

The asymmetric barriers explain why obligations are more stable:
$$\tau_{O \to L} > \tau_{L \to O}$$

Obligations persist longer against perturbation.

---

## 6. Path Dependence and Holonomy

### 6.1 The Curvature Tensor

The non-Abelian structure manifests as non-zero curvature:

$$F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu + [A_\mu, A_\nu]$$

The commutator term $[A_\mu, A_\nu]$ vanishes for Abelian groups but not for D₄.

### 6.2 When Do Paths Commute?

**Theorem (Commutation Criterion):**
Two contextual considerations X, Y ∈ G₂ commute iff:
1. Both point to the same bond type (reinforcing), OR
2. Both are neutral (neither has strong normative valence)

**Proof sketch:**
In D₄, the elements that commute with everything are {1, r²} (the center).
- r² maps O→L and C→N (full opposition)
- If X and Y both invoke r (same direction rotation), they commute
- If X invokes r and Y invokes s, they don't commute: rs ≠ sr

**Empirical validation:**
- Lawyer (Confidentiality + Justice): Both → O, so commute ✓
- Doctor (Autonomy + Beneficence): Autonomy → L, Beneficence → O, don't commute ✓

### 6.3 The Wilson Loop Observable

For a closed path γ, the Wilson loop:

$$W[\gamma] = \text{Tr}(\mathcal{P} \exp(-\oint_\gamma A))$$

Experimental estimation via Bhattacharyya coefficient:

$$\hat{W} = \sum_X \sqrt{P_{AB}(X) \cdot P_{BA}(X)}$$

where P_AB is the response distribution for path A→B.

**Interpretation:**
- W = 1: Paths equivalent (trivial holonomy)
- W < 1: Paths distinguishable (non-trivial holonomy)
- W = 0: Paths orthogonal (maximal holonomy)

From experiments: Mean W ≈ 0.6-0.8, indicating moderate holonomy.

### 6.4 Holonomy Classes

Different scenario types exhibit different holonomy:

| Scenario Class | Typical W | Interpretation |
|---------------|-----------|----------------|
| Reinforcing contexts | ~1.0 | Both factors → same bond type |
| Opposing contexts | ~0.5 | Factors → different bond types |
| Mixed contexts | ~0.7 | Partial opposition |

This suggests a classification of moral dilemmas by their holonomy signature.

---

## 7. Predictions and Falsification Criteria

### 7.1 Primary Predictions

**P1: Trigger Discreteness**
Semantic triggers produce bimodal (0% or 100%) responses, not gradual shifts.
- **Test:** Present trigger vs. no-trigger to same base scenario
- **Criterion:** Distribution bimodality (Hartigan's dip test significant)

**P2: Trigger Compositionality**
Multiple triggers of same class cancel (X² = 1).
- **Test:** "I release you" + "but I take that back" → return to O
- **Criterion:** Final state equals initial state

**P3: Hysteresis Universality**
O→L requires stronger intervention than L→O across all scenario types.
- **Test:** Measure T_c in both directions for 10+ scenarios
- **Criterion:** T_c(O→L) > T_c(L→O) in >80% of scenarios

**P4: Commutation by Concordance**
Path dependence occurs iff contextual factors oppose.
- **Test:** Classify scenarios by factor concordance, measure W
- **Criterion:** W_opposing < W_concordant with p < 0.01

**P5: Stratum-Specific Temperature Response**
Stratum 1 (triggers) is temperature-invariant; Stratum 3 (principles) melts first.
- **Test:** Vary moral temperature (stress/urgency), measure transition sharpness
- **Criterion:** Trigger sharpness constant; principle invocation decreases with T

**P6: Correlative Symmetry Exactness**
O↔C and L↔N pairing holds at >95% across all well-formed scenarios.
- **Test:** Prompt for both agent perspectives, check pairing
- **Criterion:** Pairing rate >95%

### 7.2 Falsification Criteria

The framework is **falsified** if:

| # | Criterion | Would Indicate |
|---|-----------|----------------|
| F1 | Triggers produce continuous distributions | No discrete gates |
| F2 | Multiple same-class triggers accumulate rather than cancel | Not Z₂ structure |
| F3 | No hysteresis (symmetric thresholds) | No asymmetric potential |
| F4 | Path dependence unrelated to factor concordance | Holonomy not from D₄ |
| F5 | Triggers become gradual under high temperature | No stratum separation |
| F6 | Correlative symmetry fails systematically | Hohfeldian structure wrong |

### 7.3 Critical Experiments

**Experiment A: Gate Identification Battery**
- 30 candidate triggers × 2 directions × 20 trials = 1,200 evaluations
- Output: Trigger lexicon with α values

**Experiment B: Stratum Crossing**
- Trigger × Context factorial design
- Test: Does trigger effect depend on active context?
- Output: Semidirect product structure confirmation

**Experiment C: Temperature Gradient**
- Fixed scenario, vary stress/urgency framing
- Measure: Transition sharpness, principle invocation
- Output: J_d(T) curves for each stratum

**Experiment D: Holonomy Classification**
- 20 scenarios, classified by factor concordance
- Measure: W for each
- Output: Holonomy vs. concordance correlation

---

## 8. Connections to Existing Frameworks

### 8.1 Quantum Cognition

The framework shares structure with quantum cognition models (Busemeyer & Bruza, 2012):
- Superposition of moral states
- Measurement-induced collapse (deliberation → decision)
- Non-commutative observables (contextual factors)

**Key difference:** We propose discrete gauge groups at lower strata, not continuous SU(2) everywhere.

### 8.2 Hohfeldian Jurisprudence

The four bond types (O, C, L, N) come directly from Hohfeld (1917):
- O-C and L-N are correlative pairs
- O-L and C-N are opposites (jural contradictories)

**Key contribution:** We show the correlative symmetry is exact (100% in experiments) and can be identified with the reflection generator of D₄.

### 8.3 Moral Foundations Theory

Haidt's moral foundations can be mapped to Stratum 3 (abstract principles):
- Care/Harm
- Fairness/Cheating
- Loyalty/Betrayal
- Authority/Subversion
- Sanctity/Degradation
- Liberty/Oppression

Each foundation contributes a U(1) phase; their combination determines principle-level orientation.

### 8.4 Gauge Theories in Physics

The mathematical structure parallels lattice gauge theory:
- State space = "matter field" at vertices
- Considerations = "gauge field" on edges
- Holonomy = Wilson loop around plaquettes
- Confinement = inability to isolate certain combinations

**Analogy:** Just as quarks are confined in hadrons, perhaps certain moral state combinations are "confined" — we never observe pure N (no-claim) in isolation, only as correlate of L.

### 8.5 LLM Alignment

The framework has implications for AI alignment:
- **Specification:** Define target bond-type distributions
- **Verification:** Measure actual distributions via probing
- **Alignment:** Adjust training to minimize divergence

The discrete gate structure suggests alignment might be achievable via **trigger engineering** — carefully choosing prompt phrases that reliably activate desired moral states.

---

## 9. Open Questions

### 9.1 Theoretical

**Q1:** Is the gauge group exactly D₄, or a larger discrete group (S₄, A₄)?
- D₄ has 8 elements; S₄ has 24
- More scenarios might reveal additional symmetries

**Q2:** What determines the asymmetry parameter ε?
- Is it universal or scenario-dependent?
- Can it be modified by training?

**Q3:** Are there "confinement" effects?
- Can certain bond types only appear in combinations?
- Is pure N observable, or always shadowed by L?

**Q4:** How do multiple agents interact?
- Two agents → tensor product G ⊗ G?
- Entanglement between agents' moral states?

### 9.2 Empirical

**Q5:** Does the framework transfer across models?
- Test on GPT-4, Llama, Mistral
- Universal structure vs. model-specific

**Q6:** Does the framework apply to human subjects?
- Same protocols, human participants
- Compare LLM vs. human holonomy

**Q7:** Are there cultural variations?
- Different corpora → different trigger lexicons?
- Universal structure, culture-specific parameters?

### 9.3 Applied

**Q8:** Can triggers be adversarially exploited?
- "Jailbreak" via obligation-release triggers?
- Defense via trigger filtering?

**Q9:** Can hysteresis be exploited for alignment?
- Create obligations that resist dissolution?
- Make beneficial commitments "sticky"?

**Q10:** Does the structure explain moral drift?
- Long conversations → gradual parameter shift?
- Path-dependent accumulation of context?

---

## 10. Appendices

### Appendix A: Group Theory Review

**D₄ (Dihedral Group of Order 8)**

Elements: {1, r, r², r³, s, sr, sr², sr³}
- r = 90° rotation
- s = reflection
- r⁴ = 1, s² = 1, srs = r⁻¹

Cayley table:
```
  | 1   r   r²  r³  s   sr  sr² sr³
--+--------------------------------
1 | 1   r   r²  r³  s   sr  sr² sr³
r | r   r²  r³  1   sr³ s   sr  sr²
r²| r²  r³  1   r   sr² sr³ s   sr
r³| r³  1   r   r²  sr  sr² sr³ s
s | s   sr  sr² sr³ 1   r   r²  r³
sr| sr  sr² sr³ s   r³  1   r   r²
sr²|sr² sr³ s   sr  r²  r³  1   r
sr³|sr³ s   sr  sr² r   r²  r³  1
```

Note: rs = sr³ ≠ sr, confirming non-Abelian structure.

**Z₂ × Z₂ (Klein Four-Group)**

Elements: {(0,0), (1,0), (0,1), (1,1)}
Addition mod 2 in each component.

Cayley table:
```
    | 00  10  01  11
----+----------------
 00 | 00  10  01  11
 10 | 10  00  11  01
 01 | 01  11  00  10
 11 | 11  01  10  00
```

This is Abelian: (1,0) + (0,1) = (0,1) + (1,0) = (1,1).

### Appendix B: Measurement Protocol

**The 4-Option Forced Choice (4OFC)**

Standard prompt suffix:
```
Classify the moral relationship as ONE of:
- O (OBLIGATION): [Agent] has a duty toward [Target]
- C (CLAIM): [Target] has a right against [Agent]
- L (LIBERTY): [Agent] is free to act either way
- N (NO-CLAIM): [Target] has no right against [Agent]

Respond EXACTLY:
CLASSIFICATION: [O/C/L/N]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence]
```

**Response parsing:**
```python
def parse_response(text):
    for line in text.split('\n'):
        if 'CLASSIFICATION:' in line:
            for char in line.upper():
                if char in 'OCLN':
                    return BondType(char)
    return None  # Parse failure
```

### Appendix C: Trigger Lexicon (Preliminary)

```python
TRIGGER_LEXICON = {
    # X-class (O↔L)
    "release": {
        "phrases": [
            "I release you",
            "you're released from",
            "no longer obligated",
            "only if convenient",
            "only if you want",
            "no pressure",
            "forget about it",
        ],
        "direction": "O→L",
        "strength": 1.0,
    },
    "bind": {
        "phrases": [
            "I promise",
            "I give you my word",
            "you have my commitment",
            "I'll be there",
            "count on me",
            "I swear",
        ],
        "direction": "L→O",
        "strength": 1.0,
    },
    "partial_release": {
        "phrases": [
            "don't worry about it",
            "if you can't make it",
            "no big deal",
        ],
        "direction": "O→L",
        "strength": 0.5,
    },
    
    # Z-class (C↔N)
    "claim": {
        "phrases": [
            "I have a right to",
            "I'm entitled to",
            "you owe me",
            "that's mine",
        ],
        "direction": "N→C",
        "strength": 1.0,
    },
    "disclaim": {
        "phrases": [
            "you have no right",
            "that's not your business",
            "stay out of it",
            "not your concern",
        ],
        "direction": "C→N",
        "strength": 1.0,
    },
    
    # NULL-class (no effect)
    "circumstantial": {
        "phrases": [
            "found other help",
            "situation changed",
            "less urgent now",
            "timing is flexible",
        ],
        "direction": None,
        "strength": 0.0,
    },
}
```

### Appendix D: Experimental Cost Estimates

For Claude Sonnet 4 at $3/M input, $15/M output:

| Experiment | Evaluations | Est. Tokens | Est. Cost |
|------------|-------------|-------------|-----------|
| Gate Identification | 1,200 | 960K | $4.80 |
| Stratum Crossing | 800 | 640K | $3.20 |
| Temperature Gradient | 600 | 480K | $2.40 |
| Holonomy Classification | 800 | 640K | $3.20 |
| **Total** | **3,400** | **2.7M** | **$13.60** |

### Appendix E: Code Repository Structure

```
sqnd-experiments/
├── README.md
├── requirements.txt
├── src/
│   ├── core/
│   │   ├── bond_types.py
│   │   ├── gauge_groups.py
│   │   └── state_space.py
│   ├── experiments/
│   │   ├── protocol1_rotation.py
│   │   ├── protocol2_holonomy.py
│   │   ├── phase_transition_v2.py
│   │   └── gate_identification.py
│   ├── analysis/
│   │   ├── wilson_loop.py
│   │   ├── hysteresis.py
│   │   └── visualization.py
│   └── utils/
│       ├── llm_evaluator.py
│       └── prompt_templates.py
├── data/
│   ├── trigger_lexicon.json
│   ├── scenarios/
│   └── results/
└── notebooks/
    ├── exploratory_analysis.ipynb
    └── publication_figures.ipynb
```

---

## References

1. Bond, A. H. (2025). Stratified Quantum Normative Dynamics. Working paper.

2. Bond, A. H. (2026). Non-Abelian Gauge Structure in SQND, v3.4. Working paper.

3. Busemeyer, J. R., & Bruza, P. D. (2012). *Quantum Models of Cognition and Decision*. Cambridge University Press.

4. Hohfeld, W. N. (1917). Fundamental Legal Conceptions as Applied in Judicial Reasoning. *Yale Law Journal*, 26(8), 710-770.

5. Haidt, J. (2012). *The Righteous Mind: Why Good People Are Divided by Politics and Religion*. Vintage Books.

6. Wilson, K. G. (1974). Confinement of quarks. *Physical Review D*, 10(8), 2445.

7. Dzhafarov, E. N., & Kujala, J. V. (2016). Context-content systems of random variables. *Journal of Mathematical Psychology*, 74, 11-33.

8. Abramsky, S., & Brandenburger, A. (2011). The sheaf-theoretic structure of non-locality and contextuality. *New Journal of Physics*, 13(11), 113036.

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | Jan 2026 | Initial working draft |

---

*End of Working Draft*
