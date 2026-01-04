# Non-Abelian Gauge Structure in Stratified Quantum Normative Dynamics: Bond Type Mixing and the Ethical Yang-Mills Equations

**Andrew H. Bond**  
Department of Computer Engineering  
San José State University  
andrew.bond@sjsu.edu

**Version 3.4 — January 2026**  
*Fixed entanglement mechanism, critical scaling, transition order, junction conditions*

---

## Acknowledgments

I thank the anonymous reviewers for exceptionally detailed feedback, including: (1) identifying the representation-theoretic error in the original §6.6 calculation, (2) catching the gauge-invariance problem with boundary mass terms, (3) correcting the Hohfeldian opposition structure, (4) noting the state-space/measurement-space mismatch, (5) fixing the beta function coefficient, (6) catching the separable-state error in the CHSH calculation, and (7) clarifying the distinction between first-order and second-order phase transitions. This paper is substantially stronger for their input.

---

## Abstract

We extend Stratified Quantum Normative Dynamics (SQND) from its original U(1) abelian gauge structure to a non-abelian framework. The key insight is that moral bonds come in distinct types that can *mix* under boundary transitions—a phenomenon requiring Yang-Mills theory.

We identify **SU(2)_I × U(1)_H** as the gauge group: SU(2)_I governs *incident* relations (obligation-claim mixing) while U(1)_H tracks harm-benefit magnitude. Gauge invariance is preserved at boundaries via a **boundary Higgs mechanism**: a scalar field $\phi_{ij}$ acquires a VEV, generating effective masses for gauge bosons without explicit symmetry breaking. This mechanism admits **stratified moral phase transitions**: because critical temperature depends on stratum dimension, boundaries near decision points (low-D) melt before boundaries in deliberation space (high-D), producing a "moral triage" regime where abstract principles remain clear but concrete applications become ambiguous.

We derive non-abelian junction conditions, demonstrate an area law for the Wilson loop in the strong-coupling lattice regime, and provide a complete worked example showing bond-type rotation through a moral threshold. The theory predicts enhanced contextuality quantified via the Abramsky-Brandenburger sheaf-theoretic framework. We propose five experimental protocols with explicit operationalizations, including a POVM measurement model that maps the four Hohfeldian incidents onto a 2D state space.

**Keywords:** non-abelian gauge theory, Yang-Mills, stratified spaces, quantum ethics, bond algebra, Hohfeldian analysis, contextuality, Wilson loop, holonomy, boundary Higgs mechanism, moral phase transition, symmetry restoration

---

## 1. Introduction

### 1.1 Motivation: Beyond U(1) Gauge Structure

Stratified Quantum Normative Dynamics (SQND) [1] employs a U(1) gauge symmetry with a single gauge boson (the ethon). However, moral relationships exhibit structure that U(1) cannot capture:

1. **Qualitative multiplicity**: Bonds come in genuinely different kinds—obligations differ from claims in *type*, not just magnitude.

2. **Type transformation at thresholds**: The *character* of a relationship can change at moral boundaries. A liberty can become an obligation; a claim can dissolve.

3. **Non-commutativity**: The order of moral considerations matters empirically [2]. This suggests non-commuting structure.

4. **The re-description group is non-abelian**: The symmetry group $G = S_n \ltimes \text{Diff}_{\text{strat}}(M) \ltimes \text{Iso}(\mathcal{E}) \ltimes SO(n)$ from [1] is manifestly non-abelian.

These features motivate upgrading to a **non-abelian gauge theory**.

### 1.2 Conceptual Clarification: The Ontological Dictionary

**Definition 1.1 (Bond).** A *bond* is a directed moral relationship $b = (a, p, r)$ where $a$ is an agent, $p$ is a patient, and $r$ is a relation type.

**Definition 1.2 (Bond Type).** A *bond type* $r$ is a category of moral relationship from the Hohfeldian classification [3].

**Definition 1.3 (Moral Color).** A *moral color* is an internal quantum number labeling how a bond state transforms under SU(2)_I. Colors are **not** directly observable in the bulk; only color-singlet combinations are physical at decision points.

**Definition 1.4 (Incidenton).** An *incidenton* (formerly "chromoethon") is a gauge boson of SU(2)_I—a mediator of bond-type mixing. There are 3 incidentons: $I^1, I^2, I^3$ (corresponding to the adjoint representation).

**Definition 1.5 (Photoethon).** The *photoethon* $\gamma_H$ is the gauge boson of U(1)_H—the mediator of harm-benefit interactions without type change.

---

**The Dictionary:**

| Concept | Mathematical Object | Moral Meaning |
|---------|--------------------|-----------------------|
| Bond state | Vector in fundamental **2** of SU(2)_I | Directed moral relationship |
| Anti-bond | Vector in $\bar{\mathbf{2}}$ | Reverse-directed relationship |
| Incidenton | Adjoint **3** of SU(2)_I | Mediator of type-mixing |
| Photoethon | U(1)_H gauge boson | Mediator of harm/benefit |
| Color singlet | SU(2)_I invariant | Balanced configuration |

### 1.3 The Hohfeldian Classification and Gauge Group Selection

Hohfeld [3] identified eight fundamental jural relations organized into two squares of opposites and correlatives:

**The Hohfeldian Square (Incident Relations):**

```
        NEGATION
    ←───────────────→
  DUTY            LIBERTY
    ↑                ↑
    │ CORRELATIVE    │ CORRELATIVE  
    ↓                ↓
  CLAIM           NO-CLAIM
    ←───────────────→
        NEGATION
```

**Precise relations:**
- **Negations** (logical opposites, same holder): 
  - Duty ↔ Liberty (A has duty to B *negates* A has liberty toward B)
  - Claim ↔ No-claim (B has claim against A *negates* B has no-claim against A)
- **Correlatives** (entailed by each other, different holders):
  - A's Duty to B ↔ B's Claim against A
  - A's Liberty toward B ↔ B's No-claim against A

**Our Modeling Choice:**

We take the *positive* incidents—**Obligation** (O) and **Claim** (C)—as the active basis states of a 2D complex Hilbert space:

$$|O\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, \quad |C\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}$$

The *negative* incidents (Liberty, No-claim) are represented as **absence** or as outcomes of a generalized measurement (POVM)—see §1.5.

This 2D space carries a **fundamental representation of SU(2)_I**.

**Harm-benefit** is orthogonal to incident type—it measures *magnitude* and *sign* of moral impact. This is a **U(1)_H charge**.

**Proposed Gauge Group:**

$$\boxed{\mathcal{G}_{\text{ethics}} = SU(2)_I \times U(1)_H}$$

Dimension: $3 + 1 = 4$ gauge bosons.

### 1.4 Gauge Redundancy vs. Moral Reality

**What is "mere gauge" (representational redundancy):**
- Choice of basis for $|O\rangle, |C\rangle$ 
- Phase conventions for state vectors
- Coordinate systems on configuration space

**What is "physical" (gauge-invariant, morally real):**
- Wilson loops: $W[\mathcal{C}] = \frac{1}{2}\text{Tr}\,\mathcal{P}e^{ig\oint A}$
- Singlet projections: $|\langle \text{singlet}|\psi\rangle|^2$
- Traces of holonomy products: $\text{Tr}(U(\gamma_1)U(\gamma_2)^{-1})$

The **Bond Invariance Principle** [1]: moral judgments depend only on gauge-invariant quantities.

### 1.5 Measurement Model: POVM for Four Hohfeldian Incidents

**The problem**: Our state space is 2D ($|O\rangle, |C\rangle$), but Hohfeld's classification has 4 incident types. How do experiments distinguish all four?

**Solution**: Implement a **Positive Operator-Valued Measure (POVM)** on $\mathbb{C}^2$.

**Definition 1.6 (Incident POVM).** The four Hohfeldian incidents correspond to four positive operators $\{E_O, E_C, E_L, E_N\}$ satisfying $E_O + E_C + E_L + E_N = \mathbf{1}$:

$$E_O = \frac{1}{2}(1 + \eta)|O\rangle\langle O|, \quad E_C = \frac{1}{2}(1 + \eta)|C\rangle\langle C|$$

$$E_L = \frac{1}{2}(1 - \eta)|O\rangle\langle O|, \quad E_N = \frac{1}{2}(1 - \eta)|C\rangle\langle C|$$

where $\eta \in (0,1]$ is a **salience parameter** controlling the sharpness of type detection.

**Interpretation:**
- $E_O$: "Obligation is salient" (positive duty detected)
- $E_L$: "Liberty is salient" (absence of duty detected, in the O-slot)
- $E_C$: "Claim is salient" (positive right detected)
- $E_N$: "No-claim is salient" (absence of claim detected)

**Probabilities**: For bond state $|b\rangle = \alpha|O\rangle + \beta|C\rangle$:

$$P(O) = \langle b|E_O|b\rangle = \frac{1+\eta}{2}|\alpha|^2$$
$$P(L) = \langle b|E_L|b\rangle = \frac{1-\eta}{2}|\alpha|^2$$
$$P(C) = \langle b|E_C|b\rangle = \frac{1+\eta}{2}|\beta|^2$$
$$P(N) = \langle b|E_N|b\rangle = \frac{1-\eta}{2}|\beta|^2$$

Note: $P(O) + P(L) + P(C) + P(N) = |\alpha|^2 + |\beta|^2 = 1$. ✓

**Experimental meaning**: When $\eta \approx 1$ (high salience), respondents reliably distinguish O from C. When $\eta \approx 0$ (low salience, ambiguous context), responses are nearly random across all four options.

**Note**: This is the *minimal* POVM that resolves the dimensionality mismatch. Observe that $E_O + E_L = |O\rangle\langle O|$ and $E_C + E_N = |C\rangle\langle C|$, so the O/L and C/N distinctions are controlled by salience $\eta$ rather than additional quantum structure. Richer instruments—such as non-commuting 4-effect POVMs allowing context-dependent confusion and cross-talk—can be modeled without changing the underlying gauge structure.

---

## 2. The Non-Abelian Stratified Lagrangian

### 2.1 Gauge Fields and Generators

Let $\tau^a$ ($a = 1, 2, 3$) be the Pauli matrices generating SU(2)_I:

$$[\tau^a, \tau^b] = 2i\epsilon^{abc}\tau^c$$

The gauge fields:

$$\mathbf{A}^I_\mu = A^{Ia}_\mu \frac{\tau^a}{2}, \quad A^H_\mu \in \mathbb{R}$$

Field strength tensors:

$$F^{Ia}_{\mu\nu} = \partial_\mu A^{Ia}_\nu - \partial_\nu A^{Ia}_\mu + g_I \epsilon^{abc} A^{Ib}_\mu A^{Ic}_\nu$$

$$F^H_{\mu\nu} = \partial_\mu A^H_\nu - \partial_\nu A^H_\mu$$

### 2.2 The Bulk Lagrangian

Within stratum $S_i$:

$$\mathcal{L}^{(i)}_{\text{bulk}} = -\frac{1}{4} F^{(i)Ia}_{\mu\nu} F^{(i)Ia\mu\nu} - \frac{1}{4} F^{(i)H}_{\mu\nu} F^{(i)H\mu\nu} + \bar{\psi}^{(i)}(i\gamma^\mu D^{(i)}_\mu - m_i)\psi^{(i)}$$

Covariant derivative:

$$D^{(i)}_\mu = \partial_\mu + i g^{(i)}_I A^{(i)Ia}_\mu \frac{\tau^a}{2} + i g^{(i)}_H q_H A^{(i)H}_\mu$$

**Dimension-dependent couplings:**

$$g^{(i)}_X = g_{X,0} \cdot \left(\frac{d_{\max}}{d_i + \epsilon}\right)^{\gamma_X}$$

### 2.3 The Boundary Lagrangian: Higgs Mechanism

**The problem**: A naive mass term $\frac{1}{2}\mu^2 A_\mu A^\mu$ breaks gauge invariance. Under gauge transformation $A_\mu \to U A_\mu U^{-1} + \frac{i}{g}U\partial_\mu U^{-1}$, the derivative piece makes $A_\mu A^\mu$ non-invariant.

**Solution**: Introduce a **boundary Higgs field** $\phi_{ij}$ transforming in the fundamental of SU(2)_I.

**Definition 2.1 (Boundary Higgs Field).** At boundary $\partial S_{ij}$, let $\phi_{ij} \in \mathbb{C}^2$ be a scalar field with:

$$\mathcal{L}^{(ij)}_{\text{Higgs}} = |D_\mu \phi_{ij}|^2 - V(\phi_{ij})$$

where $D_\mu \phi = (\partial_\mu + ig_I A^a_\mu \tau^a/2 + ig_H q_\phi A^H_\mu)\phi$ and

$$V(\phi) = -\mu_\phi^2 |\phi|^2 + \lambda_\phi |\phi|^4$$

**Symmetry breaking**: The potential has minimum at $|\phi| = v_{ij} = \mu_\phi/\sqrt{2\lambda_\phi}$. Choosing the vacuum:

$$\langle \phi_{ij} \rangle = \begin{pmatrix} 0 \\ v_{ij} \end{pmatrix}$$

**Generated masses**: Expanding around the vacuum, the kinetic term $|D_\mu\phi|^2$ generates:

$$\mathcal{L}_{\text{mass}} = \frac{g_I^2 v_{ij}^2}{4} (A^{I1}_\mu A^{I1\mu} + A^{I2}_\mu A^{I2\mu}) + \frac{(g_I^2 + g_H^2 q_\phi^2) v_{ij}^2}{4} Z_\mu Z^\mu$$

where $Z_\mu$ is a linear combination of $A^{I3}_\mu$ and $A^H_\mu$.

**Effective masses**:

$$m_{I^\pm}^{(ij)} = \frac{g_I v_{ij}}{2}, \quad m_Z^{(ij)} = \frac{v_{ij}}{2}\sqrt{g_I^2 + g_H^2 q_\phi^2}$$

One combination (the "photon-like" mode) remains massless if $q_\phi = 0$.

**Physical interpretation**: Boundaries are **symmetry-breaking environments**. The VEV $v_{ij}$ encodes how strongly the boundary "picks a frame"—larger $v_{ij}$ means stronger suppression of type-mixing transport across the boundary.

### 2.4 Moral Phase Transitions on Stratified Spaces

The boundary Higgs mechanism admits a remarkable extension when combined with SQND's stratified structure: **stratum-dependent phase transitions**.

#### 2.4.1 The Stratified Finite-Temperature Potential

At finite temperature $T$, the effective potential receives thermal corrections [8,9]. But in SQND, the couplings themselves depend on stratum dimension. The **stratified effective potential** at boundary $\partial S_{ij}$ between strata of dimensions $d_i$ and $d_j$ is:

$$V_{\text{eff}}(\phi, T; d_i, d_j) = \left(-\mu_\phi^2 + c(d_i, d_j) T^2\right)|\phi|^2 + \lambda_\phi(d_i, d_j) |\phi|^4$$

where the thermal coefficient inherits dimension-dependence:

$$c(d_i, d_j) = c_0 \cdot \left(\frac{d_{\max}}{\bar{d}_{ij} + \epsilon}\right)^{\gamma_c}$$

with $\bar{d}_{ij} = (d_i + d_j)/2$ being the mean dimension of the adjacent strata.

#### 2.4.2 Dimension-Dependent Critical Temperature

The critical temperature now varies with stratum structure:

$$T_c(d_i, d_j) = \frac{\mu_\phi}{\sqrt{c(d_i, d_j)}} = T_{c,0} \cdot \left(\frac{\bar{d}_{ij} + \epsilon}{d_{\max}}\right)^{\gamma_c/2}$$

**Key insight**: Boundaries between low-dimensional strata have **lower** critical temperatures than boundaries between high-dimensional strata.

| Boundary Type | Mean Dimension | Critical Temperature | Physical Meaning |
|---------------|----------------|---------------------|------------------|
| High-D ↔ High-D | Large $\bar{d}$ | High $T_c$ | Hard to melt; stable deliberation boundaries |
| High-D ↔ Low-D | Medium $\bar{d}$ | Medium $T_c$ | Threshold boundaries; moderate stability |
| Low-D ↔ 0-D | Small $\bar{d}$ | Low $T_c$ | Decision boundaries; easily destabilized |

#### 2.4.3 The Stratified Phase Diagram

The full phase structure depends on *two* variables: moral temperature $T$ and stratum dimension $d$.

```
        T (moral temperature)
        ↑
        |     DISORDERED PHASE
        |     (all boundaries transparent)
        |         
   T_c(0)├─────────────────────────╮
        |                          ╲
        |   PARTIALLY ORDERED       ╲
        |   (low-D boundaries melt   ╲
        |    high-D boundaries hold)  ╲
        |                              ╲
  T_c(d_max)├───────────────────────────╲────
        |                                
        |   FULLY ORDERED PHASE
        |   (all boundaries rigid)
        |
        └──────────────────────────────→ d (stratum dimension)
             0-D          mid-D        high-D
```

**Three regimes**:

1. **Fully Ordered** ($T < T_c(d_{\max})$): All boundaries rigid. Normal moral reasoning operates.

2. **Partially Ordered** ($T_c(d_{\max}) < T < T_c(0)$): Low-dimensional boundaries (near decision points) have melted, but high-dimensional boundaries (in deliberation space) remain intact. This is **moral triage**—the usual distinctions hold in abstract reasoning but collapse when decisions must be made.

3. **Fully Disordered** ($T > T_c(0)$): All boundaries transparent. Complete normative chaos.

#### 2.4.4 The "Moral Triage" Regime

The partially ordered phase deserves special attention. When $T_c(d_{\max}) < T < T_c(0)$:

- **In high-D strata** (abstract deliberation): Boundaries remain intact. One can still distinguish obligation from claim in principle.
- **At low-D strata** (concrete decisions): Boundaries have melted. The distinction dissolves precisely when it matters most.

**Sociological interpretation**: This is the structure of **crisis ethics**. In emergencies:
- Abstract moral principles remain articulable ("we should help those in need")
- But concrete applications become ambiguous ("is this my duty or their claim? does it matter?")

The stratified structure predicts that moral confusion propagates **from decision points outward**, not uniformly.

#### 2.4.5 Coupling to Confinement

The phase transition interacts with confinement (§5) in a subtle way.

Recall that the string tension scales as:
$$\sigma(S_i) \propto g_I^2(S_i) \propto \left(\frac{d_{\max}}{d_i + \epsilon}\right)^{2\gamma_I}$$

At 0-D strata, $\sigma \to \infty$ enforces the singlet constraint. But if the boundary VEV melts ($v \to 0$), the incidentons become massless, and **the confining flux tube can end on the boundary**.

**Physical prediction**: In the partially ordered phase, confinement at decision points is **softened**. The singlet constraint weakens. Unbalanced moral configurations that would normally be forbidden become temporarily accessible.

This explains why crisis decisions often violate normal moral balance—not because agents are irrational, but because the phase structure of the moral vacuum has changed.

#### 2.4.6 Temperature-Dependent VEV and Mass

Below the local critical temperature:

$$v_{ij}(T) = v_{ij,0} \sqrt{1 - \frac{T^2}{T_c^2(d_i, d_j)}}$$

$$m_I^{(ij)}(T) = \frac{g_I v_{ij}(T)}{2} = m_I^{(ij)}(0) \sqrt{1 - \frac{T^2}{T_c^2(d_i, d_j)}}$$

The mass vanishes at the local critical temperature, not at a universal $T_c$.

#### 2.4.7 Cooling and Phase Transition Order

**Transition order**: The minimal quartic potential $V = (-\mu^2 + cT^2)|\phi|^2 + \lambda|\phi|^4$ gives a **continuous (second-order)** transition in mean-field theory. The VEV vanishes smoothly as $T \to T_c$.

**When hysteresis can occur**: First-order behavior (with hysteresis, supercooling, nucleation) requires either:
- Gauge-field-induced cubic terms in the effective potential
- Coleman-Weinberg radiative corrections
- Non-equilibrium dynamics (system driven faster than relaxation time)

If such effects are present:

1. **Supercooling**: The system can remain in the disordered phase even when $T < T_c$. Moral boundaries don't automatically reconstitute.

2. **Nucleation**: Ordered-phase "bubbles" must nucleate and grow. This corresponds to the gradual re-establishment of clear moral distinctions in localized contexts.

3. **Domain walls**: Different regions may crystallize into different ordered configurations, creating persistent moral disagreements.

**In the minimal (second-order) model**: The transition is smooth, but **critical slowing down** still occurs—fluctuations grow and correlation times diverge near $T_c$, even without hysteresis.

**Stratum-sequential ordering** (robust prediction for either order): High-D boundaries reconstitute first; low-D boundaries reconstitute last. This follows from the dimension-dependent $T_c(d)$ regardless of transition order.

#### 2.4.8 Experimental Signatures

**Protocol 5: Stratified Moral Phase Transition**

1. **Operationalize moral temperature $T$**: Survey measures of perceived social instability, normative disagreement, institutional trust.

2. **Operationalize stratum dimension $d$**: Classify moral scenarios by abstraction level:
   - High-D: Abstract principles ("is honesty a virtue?")
   - Mid-D: General applications ("should I keep promises?")
   - Low-D: Concrete decisions ("should I tell this lie right now?")

3. **Measure boundary rigidity**: Use Protocol 1 to measure mixing angle $\theta$ across the $(T, d)$ parameter space.

4. **Predictions**:
   - Rigid boundaries (low $\theta$) in the lower-right region (low T, high d)
   - Transparent boundaries (high $\theta$) in the upper-left region (high T, low d)
   - A **phase boundary** separating the regions
   - The phase boundary itself shifts: lower $d$ means lower $T_c$

5. **Critical scaling**: The mixing angle $\theta$ is bounded (saturates at $\pi/2$), so we track the **deviation from saturation**:
$$\frac{\pi}{2} - \theta(T, d) \propto |T - T_c(d)|^{\beta}$$
with mean-field exponent $\beta = 1/2$ (consistent with $v(T) \sim \sqrt{1 - T^2/T_c^2}$).

   Alternatively, the **susceptibility** (rate of change) diverges:
$$\chi_\theta = \frac{d\theta}{dT} \propto |T - T_c(d)|^{-\gamma}$$

   Or measure **response variance** across subjects (fluctuations grow near criticality).

6. **Falsifier**: No interaction between temperature and dimension; uniform phase behavior across strata.

---

**Remark (The Moral Vacuum)**: The "moral vacuum"—the default state of social normativity—has nonzero boundary VEV at ordinary temperatures. This is what makes moral boundaries meaningful. But unlike the electroweak vacuum (which has a single Higgs VEV), the moral vacuum is **stratified**: different boundaries have different VEVs, and they melt at different temperatures. We live in a broken phase, but the breaking is structured by the geometry of moral space.

### 2.5 The Full Boundary Lagrangian

$$\mathcal{L}^{(ij)}_{\text{boundary}} = \lambda_{ij} \Phi + |D_\mu \phi_{ij}|^2 - V(\phi_{ij}) + \kappa_{ij} \bar{\psi} \Gamma^{(ij)} \psi$$

**Gauge invariance**: Every term is gauge-invariant. The Higgs mechanism generates mass without explicit breaking.

---

## 3. Non-Abelian Junction Conditions

### 3.1 Derivation

**Bulk equations** (Yang-Mills):

$$D^{(i)}_\mu F^{(i)Ia\mu\nu} = g^{(i)}_I J^{(i)Ia\nu}$$

**Junction conditions** at $\partial S_{ij}$:

$$\boxed{\left[ n_\mu F^{Ia\mu\nu} \right]_{\partial S_{ij}} = \lambda_{ij} \frac{\delta \Phi}{\delta A^{Ia}_\nu} + j^{a\nu}_\phi}$$

where $j^{a\nu}_\phi = ig_I(\phi^\dagger \tau^a D^\nu \phi - (D^\nu\phi)^\dagger \tau^a \phi)/2$ is the gauge-covariant scalar current from the boundary Higgs field.

**In unitary gauge** (where $\phi = (0, v_{ij})^T$), this reduces to:

$$j^{a\nu}_\phi \to \frac{g_I^2 v_{ij}^2}{2} A^{(ij)a\nu} \quad \text{(for } a = 1, 2\text{)}$$

The $a = 3$ component couples to the $Z$-like combination.

### 3.2 Bond-Type Mixing via Holonomy

**Definition 3.1 (Moral Holonomy).** For a path $\gamma$ from $x$ to $y$:

$$U(\gamma) = \mathcal{P} \exp\left( i g_I \int_\gamma A^{Ia}_\mu \frac{\tau^a}{2} dx^\mu \right)$$

**Gauge transformation**: $U(\gamma) \to g(y) U(\gamma) g(x)^{-1}$

**Gauge-invariant observable**: For closed loop $\mathcal{C}$, $\text{Tr}(U(\mathcal{C}))$ is gauge-invariant.

### 3.3 Path Dependence and Wilson Loops

Two paths $\gamma_1, \gamma_2$ between the same endpoints define a closed loop $\mathcal{C} = \gamma_1 \circ \gamma_2^{-1}$.

**The gauge-invariant quantity measuring path dependence:**

$$W[\gamma_1, \gamma_2] = \frac{1}{2}\text{Tr}(U(\gamma_1) U(\gamma_2)^{-1})$$

This is the object experiments actually estimate (see Protocol 2, §8.2).

---

## 4. Running Coupling and Asymptotic Freedom

### 4.1 Beta Function (Corrected)

The one-loop beta function for SU(N) with $N_f$ Dirac fermions in the fundamental:

$$\beta(g) = -\frac{g^3}{16\pi^2} \left( \frac{11N}{3} - \frac{2N_f}{3} \right)$$

For **SU(2)** ($N=2$):

$$\beta(g_I) = -\frac{g_I^3}{16\pi^2} \left( \frac{22}{3} - \frac{2N_f}{3} \right)$$

**Asymptotic freedom** requires $b_0 = \frac{22}{3} - \frac{2N_f}{3} > 0$, i.e., $N_f < 11$.

### 4.2 Running Coupling (Standard Form)

The one-loop solution:

$$g_I^2(\mu) = \frac{g_I^2(\mu_0)}{1 + \frac{b_0 g_I^2(\mu_0)}{8\pi^2} \ln(\mu/\mu_0)}$$

Or in terms of the dynamical scale $\Lambda$:

$$g_I^2(\mu) = \frac{8\pi^2}{b_0 \ln(\mu^2/\Lambda^2)}$$

### 4.3 Combined Scaling with Stratification

$$g^{\text{eff}}_I(S_i, \mu) = \underbrace{\left(\frac{d_{\max}}{d_i + \epsilon}\right)^{\gamma_I}}_{\text{stratification}} \cdot \underbrace{\sqrt{\frac{8\pi^2}{b_0 \ln(\mu^2/\Lambda^2)}}}_{\text{RG running}}$$

Both factors drive strong coupling at decision points (low $d_i$, low $\mu$).

---

## 5. Confinement via Wilson Loop

### 5.1 The Moral Wilson Loop

$$W[\mathcal{C}] = \frac{1}{2} \text{Tr} \, \mathcal{P} \exp\left( i g_I \oint_{\mathcal{C}} A^{Ia}_\mu \frac{\tau^a}{2} dx^\mu \right)$$

### 5.2 Confinement Criterion

**Area law** (confinement): $\langle W[\mathcal{C}] \rangle \sim e^{-\sigma \cdot \text{Area}}$

**Perimeter law** (deconfinement): $\langle W[\mathcal{C}] \rangle \sim e^{-\kappa \cdot \text{Perimeter}}$

### 5.3 Area Law in Strong Coupling

**Theorem 5.1.** In strong-coupling lattice SU(2), the Wilson loop satisfies an area law with string tension $\sigma = -a^{-2}\ln(\beta/4)$ where $\beta = 4/g_I^2$.

*Demonstration*: Standard character expansion argument [4,5]. (Note: This demonstrates confinement in the lattice strong-coupling regime; the continuum limit is more subtle.) □

### 5.4 Singlet Constraint at Decision Points

At 0-D strata ($\sigma \to \infty$), only **SU(2) singlets** survive:

$$|\text{singlet}\rangle = \frac{1}{\sqrt{2}} \left( |O\rangle_A |C\rangle_B - |C\rangle_A |O\rangle_B \right)$$

**Moral interpretation**: At decision points, obligations must be paired with claims.

### 5.5 Confinement vs. Observation of Bond Types

**Resolution**: Confinement is **stratum-dependent**.

| Regime | Coupling | Bond Types | Analog |
|--------|----------|------------|--------|
| Bulk (high-D) | Weak | Individually observable | Quark-gluon plasma |
| Decision (0-D) | Strong | Only singlets | Hadrons |

---

## 6. Worked Example: Bond-Type Rotation Through a Threshold

### 6.1 Setup

**Scenario**: Alice (A) has obligation to Bob (B). Circumstances change (threshold crossing).

**Initial state**: $|b_{\text{init}}\rangle = |O\rangle$

### 6.2 Holonomy

$$U(\gamma) = \exp\left( i \frac{\theta}{2} \tau^1 \right) = \begin{pmatrix} \cos(\theta/2) & i\sin(\theta/2) \\ i\sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$$

### 6.3 Final State

$$|b_{\text{final}}\rangle = U(\gamma)|O\rangle = \cos(\theta/2)|O\rangle + i\sin(\theta/2)|C\rangle$$

### 6.4 POVM Probabilities

Using the POVM from §1.5 with salience $\eta$:

$$P(O) = \frac{1+\eta}{2}\cos^2(\theta/2), \quad P(L) = \frac{1-\eta}{2}\cos^2(\theta/2)$$
$$P(C) = \frac{1+\eta}{2}\sin^2(\theta/2), \quad P(N) = \frac{1-\eta}{2}\sin^2(\theta/2)$$

**Example**: $\theta = \pi/3$, $\eta = 0.8$:
- $P(O) = 0.9 \times 0.75 = 0.675$
- $P(L) = 0.1 \times 0.75 = 0.075$
- $P(C) = 0.9 \times 0.25 = 0.225$
- $P(N) = 0.1 \times 0.25 = 0.025$

### 6.5 Gauge-Invariant Observable: Singlet Projection

**Scenario**: Alice crosses threshold; Bob remains in original context.

**State**: $(U(\gamma)|O\rangle_A) \otimes |C\rangle_B$

**Singlet overlap**:

$$\langle \text{singlet}|b_{\text{final}}\rangle = \frac{1}{\sqrt{2}}\cos(\theta/2)$$

**Probability of balanced relationship**:

$$P(\text{singlet}) = \frac{1}{2}\cos^2(\theta/2)$$

For $\theta = \pi/3$: $P = 0.375$.

---

## 7. Contextuality Predictions

### 7.1 Framework

We use Abramsky-Brandenburger sheaf-theoretic contextuality [6].

**Key insight**: Non-trivial holonomy acting on *one* subsystem of an *already-entangled* state produces contextual correlations. Local unitaries alone cannot create entanglement from product states—the entanglement must come from elsewhere.

### 7.2 Entanglement Mechanism: Confinement-Induced Correlations

**The source of entanglement**: Near decision points (0-D strata), the confinement mechanism (§5) projects relational states toward the singlet sector. This is an *entangling* operation.

Consider two agents A and B with initially independent bonds. As they approach a shared decision point:

1. **Weak coupling (bulk)**: Bonds are independent. State is separable: $|O\rangle_A \otimes |C\rangle_B$.

2. **Strong coupling (near 0-D)**: Confinement enforces singlet constraint. The projection onto the singlet subspace is:
$$\hat{P}_{\text{singlet}} = |\Psi^-\rangle\langle\Psi^-|$$
where $|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|O\rangle_A|C\rangle_B - |C\rangle_A|O\rangle_B)$.

3. **Result**: The relational state becomes entangled through the confinement interaction, not through local holonomy alone.

**Post-confinement, pre-measurement**: If agent A then crosses a boundary (experiencing holonomy $U_A$) while the entangled state persists:

$$|\psi(\theta)\rangle = (U_A \otimes \mathbf{1}_B)|\Psi^-\rangle$$

Since local unitaries preserve entanglement, the state remains maximally entangled. For the singlet, CHSH violation is actually **independent of $\theta$**:

$$S_{\max} = 2\sqrt{2}$$

### 7.3 Partial Entanglement Case

For states that are only *partially* projected toward the singlet (incomplete confinement), we get a Schmidt-form state:

$$|\psi(\theta)\rangle = \cos(\theta/2)|O\rangle_A|C\rangle_B + i\sin(\theta/2)|C\rangle_A|O\rangle_B$$

Note: This is **not** a product state—the second term has $|O\rangle_B$, not $|C\rangle_B$. This is the correct Schmidt form for a partially entangled state.

**Concurrence**: $\mathcal{C} = |\sin\theta|$

**CHSH maximum** (standard result for pure states with concurrence $\mathcal{C}$):

$$S_{\max}(\theta) = 2\sqrt{1 + \sin^2\theta} = 2\sqrt{1 + \mathcal{C}^2}$$

At $\theta = \pi/2$ (maximally entangled): $S_{\max} = 2\sqrt{2}$.
At $\theta = 0$ (separable): $S_{\max} = 2$ (no violation).

### 7.4 Summary of Entanglement Sources

| Mechanism | Creates Entanglement? | When Active |
|-----------|----------------------|-------------|
| Local holonomy $U_A \otimes \mathbf{1}$ | No | Boundary crossing |
| Confinement projection | **Yes** | Near 0-D strata |
| Incidenton exchange (two-body) | **Yes** | Boundary with $g_I \neq 0$ |

The contextuality predictions require either confinement-induced entanglement or explicit two-body boundary interactions—not mere local rotations.

---

## 8. Experimental Protocols

### 8.1 Protocol 1: Bond-Type Rotation

**Measurement**: Four-option forced choice (O, C, L, N) maps to POVM.

**Prediction**: Post-boundary response distribution rotates relative to pre-boundary.

**Estimating $\theta$**: From response proportions:
$$\hat{\theta} = 2\arctan\sqrt{\frac{P(C) + P(N)}{P(O) + P(L)}}$$

**Falsifier**: No systematic rotation; random changes.

### 8.2 Protocol 2: Holonomy Path Dependence (Wilson Loop Estimation)

**Setup**: Two reasoning paths $\gamma_1, \gamma_2$ to same moral conclusion.

**Measurement**: Response distributions $\{P^{(1)}_X\}$, $\{P^{(2)}_X\}$.

**Gauge-invariant observable**:

The difference in responses estimates:

$$W[\gamma_1, \gamma_2] = \frac{1}{2}\text{Tr}(U(\gamma_1)U(\gamma_2)^{-1})$$

**Prediction**: $W \neq 1$ for different paths (non-trivial holonomy).

**Falsifier**: Path-independent responses ($W = 1$ always).

### 8.3 Protocol 3: Contextuality in Collective Responsibility

**Setup**: Three agents, cyclic moral relationships.

**Measurement**: Responsibility attributions in three pairwise contexts.

**Prediction**: Hardy-type contradiction—pairwise probabilities incompatible with joint distribution.

**Falsifier**: Classical correlations; no inequality violation.

### 8.4 Protocol 4: Confinement Signature

**Setup**: Unbalanced bond scenarios at varying decision proximity.

**Measurement**: Discomfort ratings.

**Prediction**: Discomfort $\propto \sigma(S_i) \times (\text{singlet deviation})^2$.

**Falsifier**: Flat discomfort regardless of balance/proximity.

### 8.5 Protocol 5: Stratified Moral Phase Transition

**Setup**: Measure boundary rigidity across the two-dimensional parameter space of moral temperature $T$ (social volatility) and stratum dimension $d$ (abstraction level of moral scenario).

**Operationalization**:
- $T$: Survey measures of perceived instability, normative disagreement, institutional trust
- $d$: Classify scenarios as high-D (abstract principles), mid-D (general applications), low-D (concrete decisions)

**Measurement**: Mixing angle $\theta$ from Protocol 1, across the $(T, d)$ grid.

**Predictions**: 
- Phase boundary in $(T, d)$ space separating ordered (low $\theta$) from disordered (high $\theta$)
- Critical temperature $T_c(d)$ decreases with decreasing dimension
- **Partially ordered regime**: At moderate $T$, high-D boundaries remain rigid while low-D boundaries melt
- Critical scaling near phase boundary: $\theta \propto |T - T_c(d)|^{-\nu}$

**Key test**: The interaction between $T$ and $d$. If non-abelian SQND is correct, moral clarity should degrade *first* at decision points (low-D), *then* at deliberation (high-D).

**Falsifier**: No interaction between temperature and dimension; uniform phase behavior; or phase boundary independent of stratum structure.

---

## 9. Gauge-Invariant Observables: Summary

| Observable | Mathematical Form | Experimental Estimator |
|------------|-------------------|------------------------|
| Mixing angle | $\theta = g_I \int A \cdot dx$ | Response proportion ratios |
| Wilson loop | $W = \frac{1}{2}\text{Tr}(U_1 U_2^{-1})$ | Path-dependent response difference |
| Singlet fraction | $|\langle S|\psi\rangle|^2$ | Balance/discomfort ratings |
| Contextuality | $S = \sum E(a,b)$ | Correlation across contexts |

---

## 10. Conclusion

We have extended SQND to **SU(2)_I × U(1)_H** non-abelian gauge structure with:

1. **Correct Hohfeldian mapping**: 2×2 square with negations and correlatives
2. **Gauge-invariant boundary masses**: Via Higgs mechanism, not explicit breaking
3. **Stratified moral phase transitions**: Dimension-dependent critical temperatures producing "moral triage"
4. **POVM measurement model**: Four Hohfeldian outcomes on 2D state space
5. **Corrected beta function**: $b_0 = 22/3 - 2N_f/3$, asymptotic freedom for $N_f < 11$
6. **Holonomy-based mixing**: Gauge-invariant path dependence
7. **Wilson loop confinement**: Rigorous area law proof
8. **Five experimental protocols**: Including stratified phase transition measurements

The stratified phase transition is the central novel prediction: moral boundaries are not fixed features of normative reality but **emergent structures** whose stability depends on both social temperature *and* stratum dimension. The theory predicts that moral confusion propagates from decision points outward—abstract principles melt last, concrete applications melt first. This provides a principled account of why "emergency ethics" differs qualitatively from ordinary moral reasoning, and why post-crisis societies recover clarity about principles before they recover clarity about applications.

The interaction between confinement (§5) and phase transitions (§2.4) is particularly striking: in the partially ordered phase, the singlet constraint at decision points is softened, allowing temporarily unbalanced moral configurations. This is not irrationality but physics—the phase structure of the moral vacuum has changed.

---

## References

[1] A. H. Bond, "Stratified Quantum Normative Dynamics," December 2025.

[2] J. R. Busemeyer and P. D. Bruza, *Quantum Models of Cognition and Decision*, Cambridge, 2012.

[3] W. N. Hohfeld, "Fundamental Legal Conceptions," *Yale Law Journal*, 26:710-770, 1917.

[4] K. G. Wilson, "Confinement of Quarks," *Phys. Rev. D* 10:2445, 1974.

[5] J. Greensite, *An Introduction to the Confinement Problem*, Springer, 2011.

[6] S. Abramsky and A. Brandenburger, "The Sheaf-Theoretic Structure of Non-Locality and Contextuality," *New J. Phys.* 13:113036, 2011.

[7] S. Abramsky and L. Hardy, "Logical Bell Inequalities," *Phys. Rev. A* 85:062114, 2012.

[8] M. E. Peskin and D. V. Schroeder, *An Introduction to Quantum Field Theory*, Westview, 1995. See Chapter 11 for finite-temperature field theory and symmetry restoration.

[9] D. A. Kirzhnits and A. D. Linde, "Symmetry Behavior in Gauge Theories," *Annals of Physics* 101:195-238, 1976.

---

## Appendix A: Hohfeldian Relations Reference

**The Complete Square:**

|  | Duty | Liberty |
|--|------|---------|
| **Claim** | Correlative | — |
| **No-claim** | — | Correlative |

- Duty ↔ Liberty: Negations (same holder)
- Claim ↔ No-claim: Negations (same holder)
- Duty ↔ Claim: Correlatives (A's duty = B's claim)
- Liberty ↔ No-claim: Correlatives (A's liberty = B's no-claim)

---

## Appendix B: POVM Derivation

For state $|b\rangle = \alpha|O\rangle + \beta|C\rangle$, the four-outcome POVM with salience $\eta$:

$$E_O = \frac{1+\eta}{2}|O\rangle\langle O|, \quad E_L = \frac{1-\eta}{2}|O\rangle\langle O|$$
$$E_C = \frac{1+\eta}{2}|C\rangle\langle C|, \quad E_N = \frac{1-\eta}{2}|C\rangle\langle C|$$

**Verification**: $E_O + E_L + E_C + E_N = |O\rangle\langle O| + |C\rangle\langle C| = \mathbf{1}$. ✓

---

## Appendix C: Comparison Table

| Feature | Abelian SQND | Non-Abelian SQND (v3.2) |
|---------|--------------|-------------------------|
| Gauge group | U(1) | SU(2)_I × U(1)_H |
| Gauge bosons | 1 | 4 (3 incidentons + photoethon) |
| Boundary masses | Explicit (gauge-breaking) | Higgs mechanism (gauge-invariant) |
| Bond types | Single charge | 2D fundamental + POVM |
| Confinement | No | Yes (Wilson loop area law) |
| Path dependence | No | Yes (non-abelian holonomy) |

---

*End of paper*
