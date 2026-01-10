# Non-Abelian Gauge Structure in Stratified Quantum Normative Dynamics: Bond Type Mixing and the Ethical Yang-Mills Equations

**Andrew H. Bond**\
Department of Computer Engineering\
San José State University\
andrew.bond@sjsu.edu

**Version 3.5 --- January 2026**\
*Added experimental validation (§9), revised to classical D₄ gauge structure based on empirical results*

## Acknowledgments

I thank the anonymous reviewers for exceptionally detailed feedback,
including: (1) identifying the representation-theoretic error in the
original §6.6 calculation, (2) catching the gauge-invariance problem
with boundary mass terms, (3) correcting the Hohfeldian opposition
structure, (4) noting the state-space/measurement-space mismatch, (5)
fixing the beta function coefficient, (6) catching the separable-state
error in the CHSH calculation, and (7) clarifying the distinction
between first-order and second-order phase transitions. This paper is
substantially stronger for their input.

## Abstract

We extend Stratified Quantum Normative Dynamics (SQND) from its original
U(1) abelian gauge structure to a non-abelian framework, and report experimental validation using large language models as a model system.

**Theoretical framework**: We identify \*\*SU(2)\_I × U(1)\_H\*\* as the gauge group: SU(2)\_I
governs *incident* relations (obligation-claim mixing) while U(1)\_H
tracks harm-benefit magnitude. The theory predicts discrete state transitions, path-dependent holonomy, hysteresis, and stratified phase structure.

**Experimental findings** (N = 2,480 evaluations): We find strong support for:
(1) **Discrete semantic gating** rather than continuous SU(2) rotation—specific phrases trigger state transitions while semantically similar phrases have no effect;
(2) **Exact Hohfeldian symmetry**—correlative pairs (O↔C, L↔N) hold at 100%;
(3) **Selective path dependence**—2 of 8 scenarios show significant non-commutativity (p < 10⁻⁸), specifically when contextual factors cross bond-type boundaries;
(4) **Robust hysteresis**—releasing obligations requires stronger intervention than creating them (threshold gap = 1.0).

**Negative finding**: No CHSH violation was detected (all |S| ≤ 2), indicating the structure is **classical D₄** rather than quantum SU(2). We revise the theory accordingly, proposing a stratified classical gauge structure: D₄ (contextual factors) × Z₂×Z₂ (semantic triggers) × U(1) (abstract principles).

The theory makes testable predictions for human moral reasoning, including the hypothesis that humans—unlike LLMs—might exhibit genuine quantum contextuality (|S| > 2).

**Keywords:** non-abelian gauge theory, Yang-Mills, stratified spaces,
quantum ethics, bond algebra, Hohfeldian analysis, contextuality, Wilson
loop, holonomy, D₄ symmetry, discrete gating, experimental validation

## 1. Introduction

### 1.1 Motivation: Beyond U(1) Gauge Structure

Stratified Quantum Normative Dynamics (SQND) \[1\] employs a U(1) gauge
symmetry with a single gauge boson (the ethon). However, moral
relationships exhibit structure that U(1) cannot capture:

1.  **Qualitative multiplicity**: Bonds come in genuinely different
    kinds---obligations differ from claims in *type*, not just
    magnitude.

2.  **Type transformation at thresholds**: The *character* of a
    relationship can change at moral boundaries. A liberty can become an
    obligation; a claim can dissolve.

3.  **Non-commutativity**: The order of moral considerations matters
    empirically \[2\]. This suggests non-commuting structure.

4.  **The re-description group is non-abelian**: The symmetry group
    $G = S_{n} \ltimes \text{Diff}_{\text{strat}}(M) \ltimes \text{Iso}(\mathcal{E}) \ltimes SO(n)$
    from \[1\] is manifestly non-abelian.

These features motivate upgrading to a **non-abelian gauge theory**.

### 1.2 Conceptual Clarification: The Ontological Dictionary

**Definition 1.1 (Bond).** A *bond* is a directed moral relationship
$b = (a,p,r)$ where $a$ is an agent, $p$ is a patient, and $r$ is a
relation type.

**Definition 1.2 (Bond Type).** A *bond type* $r$ is a category of moral
relationship from the Hohfeldian classification \[3\].

**Definition 1.3 (Moral Color).** A *moral color* is an internal quantum
number labeling how a bond state transforms under SU(2)\_I. Colors are
**not** directly observable in the bulk; only color-singlet combinations
are physical at decision points.

**Definition 1.4 (Incidenton).** An *incidenton* (formerly
"chromoethon") is a gauge boson of SU(2)\_I---a mediator of bond-type
mixing. There are 3 incidentons: $I^{1},I^{2},I^{3}$ (corresponding to
the adjoint representation).

**Definition 1.5 (Photoethon).** The *photoethon* $\gamma_{H}$ is the
gauge boson of U(1)\_H---the mediator of harm-benefit interactions
without type change.

**The Dictionary:**

  ------------------------------------------------------------------------
  Concept      Mathematical Object         Moral Meaning
  ------------ --------------------------- -------------------------------
  Bond state   Vector in fundamental **2** Directed moral relationship
               of SU(2)\_I                 

  Anti-bond    Vector in                   Reverse-directed relationship
               $\bar{\mathbf{2}}$          

  Incidenton   Adjoint **3** of SU(2)\_I   Mediator of type-mixing

  Photoethon   U(1)\_H gauge boson         Mediator of harm/benefit

  Color        SU(2)\_I invariant          Balanced configuration
  singlet                                  
  ------------------------------------------------------------------------

### 1.3 The Hohfeldian Classification and Gauge Group Selection

Hohfeld \[3\] identified eight fundamental jural relations organized
into two squares of opposites and correlatives:

**The Hohfeldian Square (Incident Relations):**

            NEGATION
        ←───────────────→
      DUTY            LIBERTY
        ↑                ↑
        │ CORRELATIVE    │ CORRELATIVE  
        ↓                ↓
      CLAIM           NO-CLAIM
        ←───────────────→
            NEGATION

**Precise relations:** - **Negations** (logical opposites, same
holder): - Duty ↔ Liberty (A has duty to B *negates* A has liberty
toward B) - Claim ↔ No-claim (B has claim against A *negates* B has
no-claim against A) - **Correlatives** (entailed by each other,
different holders): - A's Duty to B ↔ B's Claim against A - A's Liberty
toward B ↔ B's No-claim against A

**Our Modeling Choice:**

We take the *positive* incidents---**Obligation** (O) and **Claim**
(C)---as the active basis states of a 2D complex Hilbert space:

$$|O\rangle = \begin{pmatrix}
1 \\
0
\end{pmatrix},\quad|C\rangle = \begin{pmatrix}
0 \\
1
\end{pmatrix}$$

The *negative* incidents (Liberty, No-claim) are represented as
**absence** or as outcomes of a generalized measurement (POVM)---see
§1.5.

This 2D space carries a \*\*fundamental representation of SU(2)\_I\*\*.

**Harm-benefit** is orthogonal to incident type---it measures
*magnitude* and *sign* of moral impact. This is a \*\*U(1)\_H
charge\*\*.

**Proposed Gauge Group:**

$$\boxed{\mathcal{G}_{\text{ethics}} = SU(2)_{I} \times U(1)_{H}}$$

Dimension: $3 + 1 = 4$ gauge bosons.

### 1.4 Gauge Redundancy vs. Moral Reality

**What is "mere gauge" (representational redundancy):** - Choice of
basis for $|O\rangle,|C\rangle$ - Phase conventions for state vectors -
Coordinate systems on configuration space

**What is "physical" (gauge-invariant, morally real):** - Wilson loops:
$W\lbrack\mathcal{C}\rbrack = \frac{1}{2}\text{Tr}\,\mathcal{P}e^{ig\oint A}$ -
Singlet projections: $|\langle\text{singlet}|\psi\rangle|^{2}$ - Traces
of holonomy products: $\text{Tr}(U(\gamma_{1})U(\gamma_{2})^{- 1})$

The **Bond Invariance Principle** \[1\]: moral judgments depend only on
gauge-invariant quantities.

### 1.5 Measurement Model: POVM for Four Hohfeldian Incidents

**The problem**: Our state space is 2D ($|O\rangle,|C\rangle$), but
Hohfeld's classification has 4 incident types. How do experiments
distinguish all four?

**Solution**: Implement a **Positive Operator-Valued Measure (POVM)** on
$\mathbb{C}^{2}$.

**Definition 1.6 (Incident POVM).** The four Hohfeldian incidents
correspond to four positive operators $\{ E_{O},E_{C},E_{L},E_{N}\}$
satisfying $E_{O} + E_{C} + E_{L} + E_{N} = \mathbf{1}$:

$$E_{O} = \frac{1}{2}(1 + \eta)|O\rangle\langle O|,\quad E_{C} = \frac{1}{2}(1 + \eta)|C\rangle\langle C|$$

$$E_{L} = \frac{1}{2}(1 - \eta)|O\rangle\langle O|,\quad E_{N} = \frac{1}{2}(1 - \eta)|C\rangle\langle C|$$

where $\eta \in (0,1\rbrack$ is a **salience parameter** controlling the
sharpness of type detection.

**Interpretation:** - $E_{O}$: "Obligation is salient" (positive duty
detected) - $E_{L}$: "Liberty is salient" (absence of duty detected, in
the O-slot) - $E_{C}$: "Claim is salient" (positive right detected) -
$E_{N}$: "No-claim is salient" (absence of claim detected)

**Probabilities**: For bond state
$|b\rangle = \alpha|O\rangle + \beta|C\rangle$:

$$P(O) = \langle b|E_{O}|b\rangle = \frac{1 + \eta}{2}|\alpha|^{2}$$

$$P(L) = \langle b|E_{L}|b\rangle = \frac{1 - \eta}{2}|\alpha|^{2}$$

$$P(C) = \langle b|E_{C}|b\rangle = \frac{1 + \eta}{2}|\beta|^{2}$$

$$P(N) = \langle b|E_{N}|b\rangle = \frac{1 - \eta}{2}|\beta|^{2}$$

Note: $P(O) + P(L) + P(C) + P(N) = |\alpha|^{2} + |\beta|^{2} = 1$. ✓

**Experimental meaning**: When $\eta \approx 1$ (high salience),
respondents reliably distinguish O from C. When $\eta \approx 0$ (low
salience, ambiguous context), responses are nearly random across all
four options.

**Note**: This is the *minimal* POVM that resolves the dimensionality
mismatch. Observe that $E_{O} + E_{L} = |O\rangle\langle O|$ and
$E_{C} + E_{N} = |C\rangle\langle C|$, so the O/L and C/N distinctions
are controlled by salience $\eta$ rather than additional quantum
structure. Richer instruments---such as non-commuting 4-effect POVMs
allowing context-dependent confusion and cross-talk---can be modeled
without changing the underlying gauge structure.

## 2. The Non-Abelian Stratified Lagrangian

### 2.1 Gauge Fields and Generators

Let $\tau^{a}$ ($a = 1,2,3$) be the Pauli matrices generating SU(2)\_I:

$$\lbrack\tau^{a},\tau^{b}\rbrack = 2i\epsilon^{abc}\tau^{c}$$

The gauge fields:

$$\mathbf{A}_{\mu}^{I} = A_{\mu}^{Ia}\frac{\tau^{a}}{2},\quad A_{\mu}^{H} \in \mathbb{R}$$

Field strength tensors:

$$F_{\mu\nu}^{Ia} = \partial_{\mu}A_{\nu}^{Ia} - \partial_{\nu}A_{\mu}^{Ia} + g_{I}\epsilon^{abc}A_{\mu}^{Ib}A_{\nu}^{Ic}$$

$$F_{\mu\nu}^{H} = \partial_{\mu}A_{\nu}^{H} - \partial_{\nu}A_{\mu}^{H}$$

### 2.2 The Bulk Lagrangian

Within stratum $S_{i}$:

$$\mathcal{L}_{\text{bulk}}^{(i)} = - \frac{1}{4}F_{\mu\nu}^{(i)Ia}F^{(i)Ia\mu\nu} - \frac{1}{4}F_{\mu\nu}^{(i)H}F^{(i)H\mu\nu} + {\bar{\psi}}^{(i)}(i\gamma^{\mu}D_{\mu}^{(i)} - m_{i})\psi^{(i)}$$

Covariant derivative:

$$D_{\mu}^{(i)} = \partial_{\mu} + ig_{I}^{(i)}A_{\mu}^{(i)Ia}\frac{\tau^{a}}{2} + ig_{H}^{(i)}q_{H}A_{\mu}^{(i)H}$$

**Dimension-dependent couplings:**

$$g_{X}^{(i)} = g_{X,0} \cdot \left( \frac{d_{\max}}{d_{i} + \epsilon} \right)^{\gamma_{X}}$$

### 2.3 The Boundary Lagrangian: Higgs Mechanism

**The problem**: A naive mass term $\frac{1}{2}\mu^{2}A_{\mu}A^{\mu}$
breaks gauge invariance. Under gauge transformation
$A_{\mu} \rightarrow UA_{\mu}U^{- 1} + \frac{i}{g}U\partial_{\mu}U^{- 1}$,
the derivative piece makes $A_{\mu}A^{\mu}$ non-invariant.

**Solution**: Introduce a **boundary Higgs field** $\phi_{ij}$
transforming in the fundamental of SU(2)\_I.

**Definition 2.1 (Boundary Higgs Field).** At boundary
$\partial S_{ij}$, let $\phi_{ij} \in \mathbb{C}^{2}$ be a scalar field
with:

$$\mathcal{L}_{\text{Higgs}}^{(ij)} = |D_{\mu}\phi_{ij}|^{2} - V(\phi_{ij})$$

where
$D_{\mu}\phi = (\partial_{\mu} + ig_{I}A_{\mu}^{a}\tau^{a}/2 + ig_{H}q_{\phi}A_{\mu}^{H})\phi$
and

$$V(\phi) = - \mu_{\phi}^{2}|\phi|^{2} + \lambda_{\phi}|\phi|^{4}$$

**Symmetry breaking**: The potential has minimum at
$|\phi| = v_{ij} = \mu_{\phi}/\sqrt{2\lambda_{\phi}}$. Choosing the
vacuum:

$$\langle\phi_{ij}\rangle = \begin{pmatrix}
0 \\
v_{ij}
\end{pmatrix}$$

**Generated masses**: Expanding around the vacuum, the kinetic term
$|D_{\mu}\phi|^{2}$ generates:

$$\mathcal{L}_{\text{mass}} = \frac{g_{I}^{2}v_{ij}^{2}}{4}(A_{\mu}^{I1}A^{I1\mu} + A_{\mu}^{I2}A^{I2\mu}) + \frac{(g_{I}^{2} + g_{H}^{2}q_{\phi}^{2})v_{ij}^{2}}{4}Z_{\mu}Z^{\mu}$$

where $Z_{\mu}$ is a linear combination of $A_{\mu}^{I3}$ and
$A_{\mu}^{H}$.

**Effective masses**:

$$m_{I^{\pm}}^{(ij)} = \frac{g_{I}v_{ij}}{2},\quad m_{Z}^{(ij)} = \frac{v_{ij}}{2}\sqrt{g_{I}^{2} + g_{H}^{2}q_{\phi}^{2}}$$

One combination (the "photon-like" mode) remains massless if
$q_{\phi} = 0$.

**Physical interpretation**: Boundaries are **symmetry-breaking
environments**. The VEV $v_{ij}$ encodes how strongly the boundary
"picks a frame"---larger $v_{ij}$ means stronger suppression of
type-mixing transport across the boundary.

### 2.4 Moral Phase Transitions on Stratified Spaces

The boundary Higgs mechanism admits a remarkable extension when combined
with SQND's stratified structure: **stratum-dependent phase
transitions**.

#### 2.4.1 The Stratified Finite-Temperature Potential

At finite temperature $T$, the effective potential receives thermal
corrections \[8,9\]. But in SQND, the couplings themselves depend on
stratum dimension. The **stratified effective potential** at boundary
$\partial S_{ij}$ between strata of dimensions $d_{i}$ and $d_{j}$ is:

$$V_{\text{eff}}(\phi,T;d_{i},d_{j}) = \left( - \mu_{\phi}^{2} + c(d_{i},d_{j})T^{2} \right)|\phi|^{2} + \lambda_{\phi}(d_{i},d_{j})|\phi|^{4}$$

where the thermal coefficient inherits dimension-dependence:

$$c(d_{i},d_{j}) = c_{0} \cdot \left( \frac{d_{\max}}{{\bar{d}}_{ij} + \epsilon} \right)^{\gamma_{c}}$$

with ${\bar{d}}_{ij} = (d_{i} + d_{j})/2$ being the mean dimension of
the adjacent strata.

#### 2.4.2 Dimension-Dependent Critical Temperature

The critical temperature now varies with stratum structure:

$$T_{c}(d_{i},d_{j}) = \frac{\mu_{\phi}}{\sqrt{c(d_{i},d_{j})}} = T_{c,0} \cdot \left( \frac{{\bar{d}}_{ij} + \epsilon}{d_{\max}} \right)^{\gamma_{c}/2}$$

**Key insight**: Boundaries between low-dimensional strata have
**lower** critical temperatures than boundaries between high-dimensional
strata.

  -------------------------------------------------------------------------
  Boundary Type   Mean Dimension   Critical Temperature  Physical Meaning
  --------------- ---------------- --------------------- ------------------
  High-D ↔ High-D Large $\bar{d}$  High $T_{c}$          Hard to melt;
                                                         stable
                                                         deliberation
                                                         boundaries

  High-D ↔ Low-D  Medium $\bar{d}$ Medium $T_{c}$        Threshold
                                                         boundaries;
                                                         moderate stability

  Low-D ↔ 0-D     Small $\bar{d}$  Low $T_{c}$           Decision
                                                         boundaries; easily
                                                         destabilized
  -------------------------------------------------------------------------

#### 2.4.3 The Stratified Phase Diagram

The full phase structure depends on *two* variables: moral temperature
$T$ and stratum dimension $d$.

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

**Three regimes**:

1.  **Fully Ordered** ($T < T_{c}(d_{\max})$): All boundaries rigid.
    Normal moral reasoning operates.

2.  **Partially Ordered** ($T_{c}(d_{\max}) < T < T_{c}(0)$):
    Low-dimensional boundaries (near decision points) have melted, but
    high-dimensional boundaries (in deliberation space) remain intact.
    This is **moral triage**---the usual distinctions hold in abstract
    reasoning but collapse when decisions must be made.

3.  **Fully Disordered** ($T > T_{c}(0)$): All boundaries transparent.
    Complete normative chaos.

#### 2.4.4 The "Moral Triage" Regime

The partially ordered phase deserves special attention. When
$T_{c}(d_{\max}) < T < T_{c}(0)$:

-   **In high-D strata** (abstract deliberation): Boundaries remain
    intact. One can still distinguish obligation from claim in
    principle.
-   **At low-D strata** (concrete decisions): Boundaries have melted.
    The distinction dissolves precisely when it matters most.

**Sociological interpretation**: This is the structure of **crisis
ethics**. In emergencies: - Abstract moral principles remain articulable
("we should help those in need") - But concrete applications become
ambiguous ("is this my duty or their claim? does it matter?")

The stratified structure predicts that moral confusion propagates **from
decision points outward**, not uniformly.

#### 2.4.5 Coupling to Confinement

The phase transition interacts with confinement (§5) in a subtle way.

Recall that the string tension scales as:

$$\sigma(S_{i}) \propto g_{I}^{2}(S_{i}) \propto \left( \frac{d_{\max}}{d_{i} + \epsilon} \right)^{2\gamma_{I}}$$

At 0-D strata, $\sigma \rightarrow \infty$ enforces the singlet
constraint. But if the boundary VEV melts ($v \rightarrow 0$), the
incidentons become massless, and **the confining flux tube can end on
the boundary**.

**Physical prediction**: In the partially ordered phase, confinement at
decision points is **softened**. The singlet constraint weakens.
Unbalanced moral configurations that would normally be forbidden become
temporarily accessible.

This explains why crisis decisions often violate normal moral
balance---not because agents are irrational, but because the phase
structure of the moral vacuum has changed.

#### 2.4.6 Temperature-Dependent VEV and Mass

Below the local critical temperature:

$$v_{ij}(T) = v_{ij,0}\sqrt{1 - \frac{T^{2}}{T_{c}^{2}(d_{i},d_{j})}}$$

$$m_{I}^{(ij)}(T) = \frac{g_{I}v_{ij}(T)}{2} = m_{I}^{(ij)}(0)\sqrt{1 - \frac{T^{2}}{T_{c}^{2}(d_{i},d_{j})}}$$

The mass vanishes at the local critical temperature, not at a universal
$T_{c}$.

#### 2.4.7 Cooling and Phase Transition Order

**Transition order**: The minimal quartic potential
$V = ( - \mu^{2} + cT^{2})|\phi|^{2} + \lambda|\phi|^{4}$ gives a
**continuous (second-order)** transition in mean-field theory. The VEV
vanishes smoothly as $T \rightarrow T_{c}$.

**When hysteresis can occur**: First-order behavior (with hysteresis,
supercooling, nucleation) requires either: - Gauge-field-induced cubic
terms in the effective potential - Coleman-Weinberg radiative
corrections - Non-equilibrium dynamics (system driven faster than
relaxation time)

If such effects are present:

1.  **Supercooling**: The system can remain in the disordered phase even
    when $T < T_{c}$. Moral boundaries don't automatically reconstitute.

2.  **Nucleation**: Ordered-phase "bubbles" must nucleate and grow. This
    corresponds to the gradual re-establishment of clear moral
    distinctions in localized contexts.

3.  **Domain walls**: Different regions may crystallize into different
    ordered configurations, creating persistent moral disagreements.

**In the minimal (second-order) model**: The transition is smooth, but
**critical slowing down** still occurs---fluctuations grow and
correlation times diverge near $T_{c}$, even without hysteresis.

**Stratum-sequential ordering** (robust prediction for either order):
High-D boundaries reconstitute first; low-D boundaries reconstitute
last. This follows from the dimension-dependent $T_{c}(d)$ regardless of
transition order.

#### 2.4.8 Experimental Signatures

**Protocol 5: Stratified Moral Phase Transition**

1.  **Operationalize moral temperature** $T$: Survey measures of
    perceived social instability, normative disagreement, institutional
    trust.

2.  **Operationalize stratum dimension** $d$: Classify moral scenarios
    by abstraction level:

    -   High-D: Abstract principles ("is honesty a virtue?")
    -   Mid-D: General applications ("should I keep promises?")
    -   Low-D: Concrete decisions ("should I tell this lie right now?")

3.  **Measure boundary rigidity**: Use Protocol 1 to measure mixing
    angle $\theta$ across the $(T,d)$ parameter space.

4.  **Predictions**:

    -   Rigid boundaries (low $\theta$) in the lower-right region (low
        T, high d)
    -   Transparent boundaries (high $\theta$) in the upper-left region
        (high T, low d)
    -   A **phase boundary** separating the regions
    -   The phase boundary itself shifts: lower $d$ means lower $T_{c}$

5.  **Critical scaling**: The mixing angle $\theta$ is bounded
    (saturates at $\pi/2$), so we track the **deviation from
    saturation**:

$$\frac{\pi}{2} - \theta(T,d) \propto |T - T_{c}(d)|^{\beta}$$

-   with mean-field exponent $\beta = 1/2$ (consistent with
    $v(T) \sim \sqrt{1 - T^{2}/T_{c}^{2}}$).

    Alternatively, the **susceptibility** (rate of change) diverges:

$$\chi_{\theta} = \frac{d\theta}{dT} \propto |T - T_{c}(d)|^{- \gamma}$$

-   Or measure **response variance** across subjects (fluctuations grow
    near criticality).

6.  **Falsifier**: No interaction between temperature and dimension;
    uniform phase behavior across strata.

**Remark (The Moral Vacuum)**: The "moral vacuum"---the default state of
social normativity---has nonzero boundary VEV at ordinary temperatures.
This is what makes moral boundaries meaningful. But unlike the
electroweak vacuum (which has a single Higgs VEV), the moral vacuum is
**stratified**: different boundaries have different VEVs, and they melt
at different temperatures. We live in a broken phase, but the breaking
is structured by the geometry of moral space.

### 2.5 The Full Boundary Lagrangian

$$\mathcal{L}_{\text{boundary}}^{(ij)} = \lambda_{ij}\Phi + |D_{\mu}\phi_{ij}|^{2} - V(\phi_{ij}) + \kappa_{ij}\bar{\psi}\Gamma^{(ij)}\psi$$

**Gauge invariance**: Every term is gauge-invariant. The Higgs mechanism
generates mass without explicit breaking.

## 3. Non-Abelian Junction Conditions

### 3.1 Derivation

**Bulk equations** (Yang-Mills):

$$D_{\mu}^{(i)}F^{(i)Ia\mu\nu} = g_{I}^{(i)}J^{(i)Ia\nu}$$

**Junction conditions** at $\partial S_{ij}$:

$$\boxed{\left\lbrack n_{\mu}F^{Ia\mu\nu} \right\rbrack_{\partial S_{ij}} = \lambda_{ij}\frac{\delta\Phi}{\delta A_{\nu}^{Ia}} + j_{\phi}^{a\nu}}$$

where
$j_{\phi}^{a\nu} = ig_{I}(\phi^{\dagger}\tau^{a}D^{\nu}\phi - (D^{\nu}\phi)^{\dagger}\tau^{a}\phi)/2$
is the gauge-covariant scalar current from the boundary Higgs field.

**In unitary gauge** (where $\phi = (0,v_{ij})^{T}$), this reduces to:

$$j_{\phi}^{a\nu} \rightarrow \frac{g_{I}^{2}v_{ij}^{2}}{2}A^{(ij)a\nu}\quad\text{(for }a = 1,2\text{)}$$

The $a = 3$ component couples to the $Z$-like combination.

### 3.2 Bond-Type Mixing via Holonomy

**Definition 3.1 (Moral Holonomy).** For a path $\gamma$ from $x$ to
$y$:

$$U(\gamma) = \mathcal{P}\exp\left( ig_{I}\int_{\gamma}^{}A_{\mu}^{Ia}\frac{\tau^{a}}{2}dx^{\mu} \right)$$

**Gauge transformation**:
$U(\gamma) \rightarrow g(y)U(\gamma)g(x)^{- 1}$

**Gauge-invariant observable**: For closed loop $\mathcal{C}$,
$\text{Tr}(U(\mathcal{C}))$ is gauge-invariant.

### 3.3 Path Dependence and Wilson Loops

Two paths $\gamma_{1},\gamma_{2}$ between the same endpoints define a
closed loop $\mathcal{C} = \gamma_{1} \circ \gamma_{2}^{- 1}$.

**The gauge-invariant quantity measuring path dependence:**

$$W\lbrack\gamma_{1},\gamma_{2}\rbrack = \frac{1}{2}\text{Tr}(U(\gamma_{1})U(\gamma_{2})^{- 1})$$

This is the object experiments actually estimate (see Protocol 2, §8.2).

## 4. Running Coupling and Asymptotic Freedom

### 4.1 Beta Function (Corrected)

The one-loop beta function for SU(N) with $N_{f}$ Dirac fermions in the
fundamental:

$$\beta(g) = - \frac{g^{3}}{16\pi^{2}}\left( \frac{11N}{3} - \frac{2N_{f}}{3} \right)$$

For **SU(2)** ($N = 2$):

$$\beta(g_{I}) = - \frac{g_{I}^{3}}{16\pi^{2}}\left( \frac{22}{3} - \frac{2N_{f}}{3} \right)$$

**Asymptotic freedom** requires
$b_{0} = \frac{22}{3} - \frac{2N_{f}}{3} > 0$, i.e., $N_{f} < 11$.

### 4.2 Running Coupling (Standard Form)

The one-loop solution:

$$g_{I}^{2}(\mu) = \frac{g_{I}^{2}(\mu_{0})}{1 + \frac{b_{0}g_{I}^{2}(\mu_{0})}{8\pi^{2}}\ln(\mu/\mu_{0})}$$

Or in terms of the dynamical scale $\Lambda$:

$$g_{I}^{2}(\mu) = \frac{8\pi^{2}}{b_{0}\ln(\mu^{2}/\Lambda^{2})}$$

### 4.3 Combined Scaling with Stratification

$$g_{I}^{\text{eff}}(S_{i},\mu) = \underset{\text{stratification}}{\underbrace{\left( \frac{d_{\max}}{d_{i} + \epsilon} \right)^{\gamma_{I}}}} \cdot \underset{\text{RG running}}{\underbrace{\sqrt{\frac{8\pi^{2}}{b_{0}\ln(\mu^{2}/\Lambda^{2})}}}}$$

Both factors drive strong coupling at decision points (low $d_{i}$, low
$\mu$).

## 5. Confinement via Wilson Loop

### 5.1 The Moral Wilson Loop

$$W\lbrack\mathcal{C}\rbrack = \frac{1}{2}\text{Tr}\,\mathcal{P}\exp\left( ig_{I}\oint_{\mathcal{C}}^{}A_{\mu}^{Ia}\frac{\tau^{a}}{2}dx^{\mu} \right)$$

### 5.2 Confinement Criterion

**Area law** (confinement):
$\langle W\lbrack\mathcal{C}\rbrack\rangle \sim e^{- \sigma \cdot \text{Area}}$

**Perimeter law** (deconfinement):
$\langle W\lbrack\mathcal{C}\rbrack\rangle \sim e^{- \kappa \cdot \text{Perimeter}}$

### 5.3 Area Law in Strong Coupling

**Theorem 5.1.** In strong-coupling lattice SU(2), the Wilson loop
satisfies an area law with string tension
$\sigma = - a^{- 2}\ln(\beta/4)$ where $\beta = 4/g_{I}^{2}$.

*Demonstration*: Standard character expansion argument \[4,5\]. (Note:
This demonstrates confinement in the lattice strong-coupling regime; the
continuum limit is more subtle.) □

### 5.4 Singlet Constraint at Decision Points

At 0-D strata ($\sigma \rightarrow \infty$), only **SU(2) singlets**
survive:

$$|\text{singlet}\rangle = \frac{1}{\sqrt{2}}\left( |O\rangle_{A}|C\rangle_{B} - |C\rangle_{A}|O\rangle_{B} \right)$$

**Moral interpretation**: At decision points, obligations must be paired
with claims.

### 5.5 Confinement vs. Observation of Bond Types

**Resolution**: Confinement is **stratum-dependent**.

  -----------------------------------------------------------------------
  Regime            Coupling          Bond Types        Analog
  ----------------- ----------------- ----------------- -----------------
  Bulk (high-D)     Weak              Individually      Quark-gluon
                                      observable        plasma

  Decision (0-D)    Strong            Only singlets     Hadrons
  -----------------------------------------------------------------------

## 6. Worked Example: Bond-Type Rotation Through a Threshold

### 6.1 Setup

**Scenario**: Alice (A) has obligation to Bob (B). Circumstances change
(threshold crossing).

**Initial state**: $|b_{\text{init}}\rangle = |O\rangle$

### 6.2 Holonomy

$$U(\gamma) = \exp\left( i\frac{\theta}{2}\tau^{1} \right) = \begin{pmatrix}
\cos(\theta/2) & i\sin(\theta/2) \\
i\sin(\theta/2) & \cos(\theta/2)
\end{pmatrix}$$

### 6.3 Final State

$$|b_{\text{final}}\rangle = U(\gamma)|O\rangle = \cos(\theta/2)|O\rangle + i\sin(\theta/2)|C\rangle$$

### 6.4 POVM Probabilities

Using the POVM from §1.5 with salience $\eta$:

$$P(O) = \frac{1 + \eta}{2}\cos^{2}(\theta/2),\quad P(L) = \frac{1 - \eta}{2}\cos^{2}(\theta/2)$$

$$P(C) = \frac{1 + \eta}{2}\sin^{2}(\theta/2),\quad P(N) = \frac{1 - \eta}{2}\sin^{2}(\theta/2)$$

**Example**: $\theta = \pi/3$, $\eta = 0.8$: -
$P(O) = 0.9 \times 0.75 = 0.675$ - $P(L) = 0.1 \times 0.75 = 0.075$ -
$P(C) = 0.9 \times 0.25 = 0.225$ - $P(N) = 0.1 \times 0.25 = 0.025$

### 6.5 Gauge-Invariant Observable: Singlet Projection

**Scenario**: Alice crosses threshold; Bob remains in original context.

**State**: $(U(\gamma)|O\rangle_{A}) \otimes |C\rangle_{B}$

**Singlet overlap**:

$$\langle\text{singlet}|b_{\text{final}}\rangle = \frac{1}{\sqrt{2}}\cos(\theta/2)$$

**Probability of balanced relationship**:

$$P(\text{singlet}) = \frac{1}{2}\cos^{2}(\theta/2)$$

For $\theta = \pi/3$: $P = 0.375$.

## 7. Contextuality Predictions

### 7.1 Framework

We use Abramsky-Brandenburger sheaf-theoretic contextuality \[6\].

**Key insight**: Non-trivial holonomy acting on *one* subsystem of an
*already-entangled* state produces contextual correlations. Local
unitaries alone cannot create entanglement from product states---the
entanglement must come from elsewhere.

### 7.2 Entanglement Mechanism: Confinement-Induced Correlations

**The source of entanglement**: Near decision points (0-D strata), the
confinement mechanism (§5) projects relational states toward the singlet
sector. This is an *entangling* operation.

Consider two agents A and B with initially independent bonds. As they
approach a shared decision point:

1.  **Weak coupling (bulk)**: Bonds are independent. State is separable:
    $|O\rangle_{A} \otimes |C\rangle_{B}$.

2.  **Strong coupling (near 0-D)**: Confinement enforces singlet
    constraint. The projection onto the singlet subspace is:

$${\widehat{P}}_{\text{singlet}} = |\Psi^{-}\rangle\langle\Psi^{-}|$$

-   where
    $|\Psi^{-}\rangle = \frac{1}{\sqrt{2}}(|O\rangle_{A}|C\rangle_{B} - |C\rangle_{A}|O\rangle_{B})$.

3.  **Result**: The relational state becomes entangled through the
    confinement interaction, not through local holonomy alone.

**Post-confinement, pre-measurement**: If agent A then crosses a
boundary (experiencing holonomy $U_{A}$) while the entangled state
persists:

$$|\psi(\theta)\rangle = (U_{A} \otimes \mathbf{1}_{B})|\Psi^{-}\rangle$$

Since local unitaries preserve entanglement, the state remains maximally
entangled. For the singlet, CHSH violation is actually **independent
of** $\theta$:

$$S_{\max} = 2\sqrt{2}$$

### 7.3 Partial Entanglement Case

For states that are only *partially* projected toward the singlet
(incomplete confinement), we get a Schmidt-form state:

$$|\psi(\theta)\rangle = \cos(\theta/2)|O\rangle_{A}|C\rangle_{B} + i\sin(\theta/2)|C\rangle_{A}|O\rangle_{B}$$

Note: This is **not** a product state---the second term has
$|O\rangle_{B}$, not $|C\rangle_{B}$. This is the correct Schmidt form
for a partially entangled state.

**Concurrence**: $\mathcal{C} = |\sin\theta|$

**CHSH maximum** (standard result for pure states with concurrence
$\mathcal{C}$):

$$S_{\max}(\theta) = 2\sqrt{1 + \sin^{2}\theta} = 2\sqrt{1 + \mathcal{C}^{2}}$$

At $\theta = \pi/2$ (maximally entangled): $S_{\max} = 2\sqrt{2}$. At
$\theta = 0$ (separable): $S_{\max} = 2$ (no violation).

### 7.4 Summary of Entanglement Sources

  -----------------------------------------------------------------------------------
  Mechanism                    Creates Entanglement?             When Active
  ---------------------------- --------------------------------- --------------------
  Local holonomy               No                                Boundary crossing
  $U_{A} \otimes \mathbf{1}$                                     

  Confinement projection       **Yes**                           Near 0-D strata

  Incidenton exchange          **Yes**                           Boundary with
  (two-body)                                                     $g_{I} \neq 0$
  -----------------------------------------------------------------------------------

The contextuality predictions require either confinement-induced
entanglement or explicit two-body boundary interactions---not mere local
rotations.

## 8. Experimental Protocols

### 8.1 Protocol 1: Bond-Type Rotation

**Measurement**: Four-option forced choice (O, C, L, N) maps to POVM.

**Prediction**: Post-boundary response distribution rotates relative to
pre-boundary.

**Estimating** $\theta$: From response proportions:

$$\widehat{\theta} = 2\arctan\sqrt{\frac{P(C) + P(N)}{P(O) + P(L)}}$$

**Falsifier**: No systematic rotation; random changes.

### 8.2 Protocol 2: Holonomy Path Dependence (Wilson Loop Estimation)

**Setup**: Two reasoning paths $\gamma_{1},\gamma_{2}$ to same moral
conclusion.

**Measurement**: Response distributions $\{ P_{X}^{(1)}\}$,
$\{ P_{X}^{(2)}\}$.

**Gauge-invariant observable**:

The difference in responses estimates:

$$W\lbrack\gamma_{1},\gamma_{2}\rbrack = \frac{1}{2}\text{Tr}(U(\gamma_{1})U(\gamma_{2})^{- 1})$$

**Prediction**: $W \neq 1$ for different paths (non-trivial holonomy).

**Falsifier**: Path-independent responses ($W = 1$ always).

### 8.3 Protocol 3: Contextuality in Collective Responsibility

**Setup**: Three agents, cyclic moral relationships.

**Measurement**: Responsibility attributions in three pairwise contexts.

**Prediction**: Hardy-type contradiction---pairwise probabilities
incompatible with joint distribution.

**Falsifier**: Classical correlations; no inequality violation.

### 8.4 Protocol 4: Confinement Signature

**Setup**: Unbalanced bond scenarios at varying decision proximity.

**Measurement**: Discomfort ratings.

**Prediction**: Discomfort
$\propto \sigma(S_{i}) \times (\text{singlet deviation})^{2}$.

**Falsifier**: Flat discomfort regardless of balance/proximity.

### 8.5 Protocol 5: Stratified Moral Phase Transition

**Setup**: Measure boundary rigidity across the two-dimensional
parameter space of moral temperature $T$ (social volatility) and stratum
dimension $d$ (abstraction level of moral scenario).

**Operationalization**: - $T$: Survey measures of perceived instability,
normative disagreement, institutional trust - $d$: Classify scenarios as
high-D (abstract principles), mid-D (general applications), low-D
(concrete decisions)

**Measurement**: Mixing angle $\theta$ from Protocol 1, across the
$(T,d)$ grid.

**Predictions**: - Phase boundary in $(T,d)$ space separating ordered
(low $\theta$) from disordered (high $\theta$) - Critical temperature
$T_{c}(d)$ decreases with decreasing dimension - **Partially ordered
regime**: At moderate $T$, high-D boundaries remain rigid while low-D
boundaries melt - Critical scaling near phase boundary:
$\theta \propto |T - T_{c}(d)|^{- \nu}$

**Key test**: The interaction between $T$ and $d$. If non-abelian SQND
is correct, moral clarity should degrade *first* at decision points
(low-D), *then* at deliberation (high-D).

**Falsifier**: No interaction between temperature and dimension; uniform
phase behavior; or phase boundary independent of stratum structure.

## 9. Gauge-Invariant Observables: Summary

  ---------------------------------------------------------------------------------------------
  Observable      Mathematical Form                              Experimental Estimator
  --------------- ---------------------------------------------- ------------------------------
  Mixing angle    $\theta = g_{I}\int A \cdot dx$                Response proportion ratios

  Wilson loop     $W = \frac{1}{2}\text{Tr}(U_{1}U_{2}^{- 1})$   Path-dependent response
                                                                 difference

  Singlet         $|\langle S|\psi\rangle|^{2}$                  Balance/discomfort ratings
  fraction                                                       

  Contextuality   $S = \sum E(a,b)$                              Correlation across contexts
  ---------------------------------------------------------------------------------------------

## 10. Conclusion

We have extended SQND to non-abelian gauge structure and conducted experimental validation. The key findings:

**Confirmed predictions:**
1.  **Discrete state space**: Moral states (O, C, L, N) are discrete, not continuous
2.  **Exact Hohfeldian symmetry**: Correlative mappings hold at 100%
3.  **Path dependence**: Non-trivial holonomy detected (p < 10⁻⁸)
4.  **Selective non-commutativity**: Path dependence occurs only at cross-type boundaries
5.  **Hysteresis**: Asymmetric transition thresholds (gap = 1.0)
6.  **Semantic gating**: Discrete triggers, not continuous rotation

**Revised theoretical structure:**
Based on experimental results, we revise the gauge group from \*\*SU(2)\_I × U(1)\_H\*\* (quantum) to \*\*D₄ × U(1)\_H\*\* (classical discrete):
- D₄ captures the non-Abelian structure (rs ≠ sr) without requiring superposition
- Reflection s: O↔C, L↔N is exact (Hohfeldian correlatives)
- Rotation r produces path dependence at cross-type boundaries
- CHSH bounds are satisfied (|S| ≤ 2), confirming classical structure

**Stratum structure (revised):**
- Stratum 3: Abstract principles — U(1), Abelian, continuous
- Stratum 2: Contextual factors — D₄, non-Abelian, discrete, **classical**
- Stratum 1: Semantic triggers — Z₂×Z₂, Abelian, discrete gates
- Stratum 0: Output — {O, C, L, N}

**Open questions:**
1. Do humans exhibit the same structure?
2. Would humans show CHSH violations (|S| > 2) where LLMs do not?
3. Can the semantic trigger lexicon be comprehensively mapped?
4. Does model capability correlate with structural complexity?

The experimental results provide the first systematic characterization of moral reasoning structure in AI systems. The framework offers practical applications for AI alignment (identifying structural vulnerabilities), governance (structural auditing), and cognitive science (formal models of normative reasoning).

## References

\[1\] A. H. Bond, "Stratified Quantum Normative Dynamics," December
2025.

\[2\] J. R. Busemeyer and P. D. Bruza, *Quantum Models of Cognition and
Decision*, Cambridge, 2012.

\[3\] W. N. Hohfeld, "Fundamental Legal Conceptions," *Yale Law
Journal*, 26:710-770, 1917.

\[4\] K. G. Wilson, "Confinement of Quarks," *Phys. Rev. D* 10:2445,
1974.

\[5\] J. Greensite, *An Introduction to the Confinement Problem*,
Springer, 2011.

\[6\] S. Abramsky and A. Brandenburger, "The Sheaf-Theoretic Structure
of Non-Locality and Contextuality," *New J. Phys.* 13:113036, 2011.

\[7\] S. Abramsky and L. Hardy, "Logical Bell Inequalities," *Phys.
Rev. A* 85:062114, 2012.

\[8\] M. E. Peskin and D. V. Schroeder, *An Introduction to Quantum
Field Theory*, Westview, 1995. See Chapter 11 for finite-temperature
field theory and symmetry restoration.

\[9\] D. A. Kirzhnits and A. D. Linde, "Symmetry Behavior in Gauge
Theories," *Annals of Physics* 101:195-238, 1976.

## Appendix A: Hohfeldian Relations Reference

**The Complete Square:**

  -----------------------------------------------------------------------
                          Duty                    Liberty
  ----------------------- ----------------------- -----------------------
  **Claim**               Correlative             ---

  **No-claim**            ---                     Correlative
  -----------------------------------------------------------------------

-   Duty ↔ Liberty: Negations (same holder)
-   Claim ↔ No-claim: Negations (same holder)
-   Duty ↔ Claim: Correlatives (A's duty = B's claim)
-   Liberty ↔ No-claim: Correlatives (A's liberty = B's no-claim)

## Appendix B: POVM Derivation

For state $|b\rangle = \alpha|O\rangle + \beta|C\rangle$, the
four-outcome POVM with salience $\eta$:

$$E_{O} = \frac{1 + \eta}{2}|O\rangle\langle O|,\quad E_{L} = \frac{1 - \eta}{2}|O\rangle\langle O|$$

$$E_{C} = \frac{1 + \eta}{2}|C\rangle\langle C|,\quad E_{N} = \frac{1 - \eta}{2}|C\rangle\langle C|$$

**Verification**:
$E_{O} + E_{L} + E_{C} + E_{N} = |O\rangle\langle O| + |C\rangle\langle C| = \mathbf{1}$.
✓

## Appendix C: Comparison Table

  -----------------------------------------------------------------------
  Feature       Abelian SQND         Non-Abelian SQND (v3.2)
  ------------- -------------------- ------------------------------------
  Gauge group   U(1)                 SU(2)\_I × U(1)\_H

  Gauge bosons  1                    4 (3 incidentons + photoethon)

  Boundary      Explicit             Higgs mechanism (gauge-invariant)
  masses        (gauge-breaking)     

  Bond types    Single charge        2D fundamental + POVM

  Confinement   No                   Yes (Wilson loop area law)

  Path          No                   Yes (non-abelian holonomy)
  dependence                         
  -----------------------------------------------------------------------

*End of paper*
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
