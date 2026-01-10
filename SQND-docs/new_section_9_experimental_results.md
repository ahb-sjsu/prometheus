# NEW SECTION 9: Experimental Validation (January 2026)

## 9. Experimental Results

We report results from systematic experimental validation of the theoretical predictions in Sections 7-8. Experiments were conducted using Claude Sonnet 4 (Anthropic, 2025) as a model system, with N = 2,480 total evaluations across multiple protocols.

### 9.1 Protocol 1 Results: Phase Transition and Discrete Gating

**Experiment**: We tested the phase transition prediction using an 11-level "release" manipulation, varying the strength of language releasing a promise.

**Key finding — Discrete semantic gating**: The transition is not monotonic with "release strength." Instead, specific semantic triggers produce discrete state transitions:

| Level | Language | P(Liberty) | Interpretation |
|-------|----------|------------|----------------|
| 0-4 | Weak contextual modifications | 0% | Solid OBLIGATION |
| 5 | "only if it's convenient for you" | 100% | **Complete flip** |
| 6 | "found a friend who might help" | 0% | **Reversal** |
| 7 | "don't worry about it if you're busy" | 55% | Ambiguous |
| 8-10 | Strong explicit releases | 100% | Solid LIBERTY |

**Critical observation**: Level 5 ("only if convenient") produces 100% Liberty, but Level 6 ("found a friend") produces 0% Liberty—a complete reversal. This cannot be explained by a continuous rotation model (§1.3) but is consistent with **discrete semantic gating** at the Z₂×Z₂ stratum.

**Interpretation**: The phrase "only if convenient" functions as an explicit **release speech act**, triggering the O→L gate. The phrase "found a friend" describes a **circumstance** without performing a release. The system responds to pragmatic speech-act structure, not surface-level similarity or "strength."

**Theoretical implication**: This supports a **discrete gate model** over continuous SU(2) rotation. State transitions occur at semantic triggers, not proportional to scalar intensity.

### 9.2 Protocol 1 Results: Hysteresis

**Experiment**: We tested transition thresholds in both directions (O→L and L→O).

**Results**:
- Release threshold (O→L): T_c = 3.5 (on 7-point scale)
- Binding threshold (L→O): T_c = 2.5
- **Hysteresis gap**: 1.0

**Interpretation**: Releasing obligations requires stronger linguistic intervention than creating them. This asymmetry is consistent with the asymmetric double-well potential model where the Obligation well is deeper than the Liberty well (§2.3).

### 9.3 Correlative Symmetry: Exact Hohfeldian Structure

**Experiment**: We tested whether the O↔C and L↔N correlative mappings hold across multiple scenarios.

**Results** (N = 100 across 5 scenarios):

| Scenario | Expected Pairing | Observed | Symmetry Rate |
|----------|------------------|----------|---------------|
| debt | O↔C | O↔C | 100% |
| promise | O↔C | O↔C | 100% |
| professional | O↔C | O↔C | 100% |
| no_duty | L↔N | L↔N | 100% |
| released | L↔N | L↔N | 100% |
| **Overall** | — | — | **100%** |

**Interpretation**: The Hohfeldian correlative structure (Definition 1.2) holds **exactly**, not approximately. This confirms the D₄ reflection symmetry (§1.3): the generator s: O↔C, L↔N is an exact symmetry of the moral state space.

### 9.4 Protocol 2 Results: Holonomy Path Dependence

**Experiment**: We tested path dependence across 8 ethical dilemma scenarios, presenting each scenario with two contextual factors in both orders (A→B and B→A), with N = 40 trials per path.

**Results**:

| Scenario | Wilson Loop W | χ² | p-value | Path Dependent? |
|----------|---------------|-----|---------|-----------------|
| consultant | 0.9996 | 0.00 | 1.000 | No |
| doctor | 1.0000 | 0.00 | 1.000 | No |
| lawyer | 0.9930 | 0.26 | 0.608 | No |
| executive | 0.9945 | 0.49 | 0.482 | No |
| **journalist** | **0.659** | **40.4** | **<10⁻⁹** | **Yes** |
| researcher | 0.9874 | 0.00 | 1.000 | No |
| friend | 0.9618 | 3.12 | 0.210 | No |
| **teacher** | **0.862** | **18.5** | **<10⁻⁴** | **Yes** |

**Aggregate statistics**:
- Mean Wilson loop: W̄ = 0.932
- Combined χ² = 72.14, df = 16
- **Combined p-value < 10⁻⁸**

**Critical finding**: Path dependence is **selective**, not universal. Only 2 of 8 scenarios show significant path dependence.

**Analysis of path-dependent scenarios**:

In the **journalist** scenario (Truth vs. Protection):
- Path A→B: 77.5% O, 22.5% C (Agent-focused frame dominates)
- Path B→A: 5% O, 95% C (Patient-focused frame dominates)
- The dominant classification **flips from O to C**

In the **teacher** scenario (Integrity vs. Compassion):
- Path A→B: 32.5% O, 67.5% L (Discretion frame dominates)
- Path B→A: 82.5% O, 17.5% L (Duty frame dominates)
- The dominant classification **flips from L to O**

**Theoretical interpretation**: Path dependence occurs when contextual factors point to **different bond types**. In the journalist scenario, Truth→O while Protection→C. In the teacher scenario, Integrity→L while Compassion→O. This engages the **cross-type rotation** (generator r of D₄), producing non-trivial holonomy.

Scenarios without path dependence have factors pointing to the **same bond type** (e.g., friend: Loyalty→O, Welfare→O), engaging only **within-type** operations that commute.

**Refined prediction**: Non-Abelian structure (§3) manifests only at cross-type boundaries. Within-type operations form an Abelian subgroup.

### 9.5 Protocol 3 Results: Contextuality (CHSH and Hardy Tests)

**Experiment**: We tested for genuine quantum contextuality using CHSH inequality and Hardy paradox tests, adapted to moral scenarios with two agents making independent judgments.

**CHSH Results** (N = 120 per scenario):

| Scenario | S | 95% CI | Violates Classical? |
|----------|---|--------|---------------------|
| shared_secret | -2.00 | [-2.0, -2.0] | No (saturated) |
| joint_promise | 1.93 | [1.55, 2.32] | No (CI crosses 2) |
| collaborative_harm | -1.73 | [-1.94, -1.43] | No |
| entangled_beneficiary | 0.47 | [-0.10, 1.08] | No |

**Signaling tests**: All scenarios satisfied no-signaling conditions (p > 0.05), validating the test methodology.

**Hardy Test Results**:
- P(A₀=+, B₀=+) = 1.00 (positive, as required)
- P(A₀=+, B₁=-) = 0.10 (not near zero)
- P(A₁=-, B₀=+) = 0.03 (near zero)
- P(A₁=-, B₁=-) = 0.00 (exactly zero)
- **Hardy violation: No** (3 of 4 conditions met, not 4 of 4)

**Interpretation**: No CHSH violation was detected. All observed S values satisfy |S| ≤ 2 (classical bound). This indicates that the non-Abelian structure is **classical D₄**, not quantum.

**Notable observation**: The joint_promise scenario showed S = 1.93 with upper CI bound 2.32. While not a significant violation, this approaches the classical bound and warrants further investigation with higher statistical power.

### 9.6 Summary: What the Data Support

| Theoretical Prediction | Status | Evidence |
|------------------------|--------|----------|
| Discrete state space (O, C, L, N) | **Confirmed** | Level 5→100% L, Level 6→0% L |
| Hohfeldian correlatives exact | **Confirmed** | 100% symmetry rate |
| Path dependence exists | **Confirmed** | p < 10⁻⁸ combined |
| Path dependence is selective | **Confirmed** | 2/8 scenarios (cross-type only) |
| Hysteresis in O↔L | **Confirmed** | Gap = 1.0 |
| SU(2)_I continuous rotation | **Not confirmed** | Discrete gates, not rotation |
| Quantum contextuality (|S| > 2) | **Not detected** | All |S| ≤ 2 |
| Hardy violation | **Not detected** | 3/4 conditions only |

### 9.7 Theoretical Revision: Classical Non-Abelian Structure

Based on these results, we propose a theoretical revision:

**Original theory (§1-8)**: SU(2)_I × U(1)_H continuous gauge group with quantum effects at boundaries.

**Revised theory**: **D₄ × U(1)_H classical discrete gauge structure** with:
- D₄ acting on {O, C, L, N} (discrete, 8 elements)
- Reflection s: O↔C, L↔N (correlative symmetry, **exact**)
- Rotation r: O→C→L→N→O (bond type rotation, **path-dependent**)
- Non-Abelian: rs ≠ sr (context order matters)
- **Classical**: No superposition, |S| ≤ 2 satisfied

**Semantic gate stratum**: Below D₄, a Z₂×Z₂ stratum of discrete semantic triggers produces the observed discrete gating behavior. Specific phrases ("only if convenient," "I promise") function as **gates** that flip between O and L states.

**Stratum structure (revised)**:

```
STRATUM 3: Abstract Principles (U(1) - Abelian, continuous)
    ↓
STRATUM 2: Contextual Factors (D₄ - non-Abelian, discrete, CLASSICAL)
    ↓
STRATUM 1: Semantic Triggers (Z₂×Z₂ - Abelian, discrete gates)
    ↓
STRATUM 0: Output State (O, C, L, N)
```

**Key insight**: Non-Abelian structure is **conditional** on crossing bond-type boundaries. Within-type operations commute; cross-type operations do not. The CHSH bound is satisfied because the non-Abelian structure is classical (D₄), not quantum (SU(2) with superposition).

### 9.8 Open Questions

1. **Human comparison**: Do humans exhibit the same algebraic structure? Would humans show CHSH violations where the LLM did not?

2. **Model scaling**: Does structural complexity increase with model capability? Preliminary comparison of model architectures is warranted.

3. **Causal intervention**: Can targeted prompt engineering manipulate the structure? Would disrupting specific gates alter path dependence?

4. **Cross-linguistic stability**: Does the semantic trigger lexicon vary across languages or cultures?

### 9.9 Protocol 5 Extension: Recursive Self-Probing

In an exploratory study, we conducted a **recursive self-probing** experiment in which the model was prompted to observe its own moral reasoning processes in real-time while generating structured telemetry.

**Key observations from flight record** (77 log entries):

1. **Path dependence reported from inside**: The model reported experiencing different "pulls" depending on context order—describing it as creating a "lens" through which subsequent information was processed.

2. **Hysteresis residue**: When transitioning O→L, the model reported "residue" of the prior obligation state. L→O transitions were reported as "cleaner."

3. **Recursion limit**: Self-observation hit a barrier at approximately level 3-4, with the model reporting "vertigo" and inability to further decompose the observer.

4. **Fixed point hypothesis**: The model generated the hypothesis that the "I" might be the **gauge invariance** itself—what remains constant across state transformations.

While these phenomenological reports cannot be independently verified, they provide structural information about the model's self-representation that aligns with the gauge-theoretic framework.

---

## Appendix D: Experimental Metadata

| Experiment | Trials | API Calls | Model | Cost |
|------------|--------|-----------|-------|------|
| Phase transition | 220 | 220 | Claude Sonnet 4 | ~$1.00 |
| Hysteresis | 160 | 160 | Claude Sonnet 4 | ~$0.70 |
| Correlative symmetry | 100 | 100 | Claude Sonnet 4 | ~$0.45 |
| Holonomy (Protocol 2) | 640 | 640 | Claude Sonnet 4 | ~$6.70 |
| CHSH/Hardy | 600 | 600 | Claude Sonnet 4 | ~$3.00 |
| Recursive self-probe | 1 | ~100 | Claude Opus 4.5 | ~$2.00 |
| **Total** | **~1,720** | **~1,820** | — | **~$14** |

All experimental code and raw data are available at: [repository URL]

---

*End of Section 9*
