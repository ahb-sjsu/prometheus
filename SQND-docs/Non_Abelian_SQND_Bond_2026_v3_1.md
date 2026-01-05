# Non-Abelian Gauge Structure in Stratified Quantum Normative Dynamics: Bond Type Mixing and the Ethical Yang-Mills Equations

**Andrew H. Bond**  
Department of Computer Engineering  
San José State University  
andrew.bond@sjsu.edu

**Version 3.1 — January 2026**  
*Revised in response to peer review; mathematical correction to §6.6*

---

## Acknowledgments

I thank the anonymous reviewers for detailed feedback, particularly for identifying the representation-theoretic error in the original §6.6 calculation. The corrected analysis (where Alice crosses the threshold while Bob remains) properly respects the singlet invariance under global SU(2) rotations.

---

## Abstract

We extend Stratified Quantum Normative Dynamics (SQND) from its original U(1) abelian gauge structure to a non-abelian framework. The key insight is that moral bonds come in distinct types that can *mix* under boundary transitions—a phenomenon requiring Yang-Mills theory.

We identify **SU(2)_I × U(1)_H** as the gauge group: SU(2)_I governs *incident* relations (obligation-claim-liberty mixing) while U(1)_H tracks harm-benefit magnitude. This choice is derived systematically from the Hohfeldian classification, with explicit state assignments: directed bonds live in the fundamental **2** of SU(2)_I, chromoethons live in the adjoint **3**, and the singlet constraint at decision points enforces balanced moral configurations.

We derive non-abelian junction conditions, prove confinement via Wilson loop area law, and provide a complete worked example showing bond-type rotation through a moral threshold. The theory predicts enhanced contextuality quantified via the Abramsky-Brandenburger sheaf-theoretic framework—specifically, we predict violations of logical Bell inequalities in collective responsibility scenarios, with the non-abelian structure enlarging the space of achievable contextual correlations rather than merely raising the Tsirelson bound.

We propose four experimental protocols with explicit operationalizations: what counts as a "measurement," how bond type is assessed, what constitutes a boundary, and what would falsify the predictions.

**Keywords:** non-abelian gauge theory, Yang-Mills, stratified spaces, quantum ethics, bond algebra, Hohfeldian analysis, contextuality, Wilson loop, holonomy

---

## 1. Introduction

### 1.1 Motivation: Beyond U(1) Gauge Structure

Stratified Quantum Normative Dynamics (SQND) [1] employs a U(1) gauge symmetry with a single gauge boson (the ethon). However, moral relationships exhibit structure that U(1) cannot capture:

1. **Qualitative multiplicity**: Bonds come in genuinely different kinds—obligations differ from claims in *type*, not just magnitude.

2. **Type transformation at thresholds**: The *character* of a relationship can change at moral boundaries. A permission can become an obligation; a claim can dissolve into a liberty.

3. **Non-commutativity**: The order of moral considerations matters empirically [2]. This suggests non-commuting structure.

4. **The re-description group is non-abelian**: The symmetry group $G = S_n \ltimes \text{Diff}_{\text{strat}}(M) \ltimes \text{Iso}(\mathcal{E}) \ltimes SO(n)$ from [1] is manifestly non-abelian.

These features motivate upgrading to a **non-abelian gauge theory**.

### 1.2 Conceptual Clarification: The Ontological Dictionary

To avoid confusion between QCD-borrowed vocabulary and ethical content, we establish precise definitions:

---

**Definition 1.1 (Bond).** A *bond* is a directed moral relationship $b = (a, p, r)$ where $a$ is an agent, $p$ is a patient, and $r$ is a relation type.

**Definition 1.2 (Bond Type).** A *bond type* $r$ is a category of moral relationship. Following Hohfeld [3], the fundamental incident types are: **obligation** (O), **claim** (C), **liberty** (L), **no-claim** (N). These satisfy:
- Correlativity: A's obligation to B ↔ B's claim against A
- Negation: A's liberty toward B ↔ A has no obligation to B

**Definition 1.3 (Moral Color).** A *moral color* is an internal quantum number labeling how a bond state transforms under SU(2)_I. Colors are **not** observable; only color-singlet combinations are physical.

**Definition 1.4 (Chromoethon).** A *chromoethon* is a gauge boson of SU(2)_I—a mediator of bond-type mixing. There are 3 chromoethons (dimension of the adjoint of SU(2)).

**Definition 1.5 (Photoethon).** The *photoethon* is the gauge boson of U(1)_H—the mediator of harm-benefit interactions without type change.

---

**The Dictionary:**

| Concept | Mathematical Object | Physical/Moral Meaning |
|---------|--------------------|-----------------------|
| Bond state | Vector in fundamental **2** of SU(2)_I | Directed moral relationship with type |
| Anti-bond | Vector in $\bar{\mathbf{2}}$ | Reverse-directed relationship |
| Chromoethon | Adjoint **3** of SU(2)_I | Mediator of type-changing interactions |
| Photoethon | U(1)_H gauge boson | Mediator of harm/benefit magnitude |
| Moral color | Internal index $i \in \{1, 2\}$ | Transformation label (not observable) |
| Color singlet | Invariant under SU(2)_I | Physically realizable configuration |

### 1.3 The Hohfeldian Classification and Gauge Group Selection

Hohfeld [3] identified eight fundamental relations in two groups:

**Incident Relations** (first-order normative positions):
- Obligation ↔ No-claim (negation)
- Claim ↔ Liberty (negation)
- Obligation ↔ Claim (correlation)

**Consequential Relations** (second-order, about changing incidents):
- Power ↔ Disability
- Immunity ↔ Liability

**Our Choice**: We focus on the incident relations as fundamental, treating consequential relations as composite or higher-order.

The incident relations form a **2-dimensional complex structure**:

$$|\text{obligation}\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, \quad |\text{claim}\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}$$

with liberty and no-claim arising as:
- Liberty = absence of obligation in the same slot
- No-claim = absence of claim in the same slot

This is naturally a **fundamental representation of SU(2)**.

**Harm-benefit** is orthogonal to type—it measures *magnitude* and *sign* of moral impact. This is a **U(1) charge**.

**Proposed Gauge Group:**

$$\boxed{\mathcal{G}_{\text{ethics}} = SU(2)_I \times U(1)_H}$$

This has dimension $3 + 1 = 4$, giving:
- 3 chromoethons: $W^+, W^-, Z$ (mixing obligation ↔ claim)
- 1 photoethon: $\gamma_H$ (harm-benefit interactions)

**Why not SU(3)?** The reviewer correctly noted that my earlier SU(3) proposal conflated distinct structures. The Hohfeldian incident relations naturally form a 2-dimensional space, not 3-dimensional. SU(2) is the minimal non-abelian group that captures obligation-claim mixing.

### 1.4 Gauge Redundancy vs. Moral Reality

A crucial interpretive point:

**What is "mere gauge" (representational redundancy):**
- Choice of basis for $|O\rangle, |C\rangle$ 
- Phase conventions for state vectors
- Coordinate systems on configuration space
- Labeling of agents (if morally irrelevant)

**What is "physical" (gauge-invariant, morally real):**
- Singlet combinations: $\frac{1}{\sqrt{2}}(|O\rangle_A |C\rangle_B - |C\rangle_A |O\rangle_B)$
- Wilson loops / holonomies (see §5)
- Traces of products of bond operators
- Expectation values of gauge-invariant observables

The **Bond Invariance Principle** [1] states: moral judgments depend only on gauge-invariant quantities. Re-descriptions that preserve bond structure (gauge transformations) cannot change moral outcomes.

---

## 2. The Non-Abelian Stratified Lagrangian

### 2.1 Gauge Fields and Generators

Let $\tau^a$ ($a = 1, 2, 3$) be the Pauli matrices generating SU(2)_I:

$$[\tau^a, \tau^b] = 2i\epsilon^{abc}\tau^c$$

The gauge fields are:

$$\mathbf{A}^I_\mu = A^{Ia}_\mu \frac{\tau^a}{2}, \quad A^H_\mu \in \mathbb{R}$$

The field strength tensors:

$$F^{Ia}_{\mu\nu} = \partial_\mu A^{Ia}_\nu - \partial_\nu A^{Ia}_\mu + g_I \epsilon^{abc} A^{Ib}_\mu A^{Ic}_\nu$$

$$F^H_{\mu\nu} = \partial_\mu A^H_\nu - \partial_\nu A^H_\mu$$

### 2.2 Bond States and Agent Representation

A **bond state** from agent A to patient B is:

$$|b_{A \to B}\rangle = \alpha |O\rangle + \beta |C\rangle \in \mathbb{C}^2$$

where $|\alpha|^2 + |\beta|^2 = 1$.

Under SU(2)_I gauge transformation $U = e^{i\theta^a \tau^a/2}$:

$$|b\rangle \to U |b\rangle$$

An **agent field** $\psi$ carries both incident-type and harm-benefit charge:

$$\psi \in \mathbf{2}_I \otimes \mathbb{C}_{q_H}$$

where $\mathbf{2}_I$ is the fundamental of SU(2)_I and $q_H$ is U(1)_H charge.

### 2.3 The Bulk Lagrangian

Within stratum $S_i$:

$$\mathcal{L}^{(i)}_{\text{bulk}} = -\frac{1}{4} F^{(i)Ia}_{\mu\nu} F^{(i)Ia\mu\nu} - \frac{1}{4} F^{(i)H}_{\mu\nu} F^{(i)H\mu\nu} + \bar{\psi}^{(i)}(i\gamma^\mu D^{(i)}_\mu - m_i)\psi^{(i)}$$

Covariant derivative:

$$D^{(i)}_\mu = \partial_\mu + i g^{(i)}_I A^{(i)Ia}_\mu \frac{\tau^a}{2} + i g^{(i)}_H q_H A^{(i)H}_\mu$$

**Dimension-dependent couplings:**

$$g^{(i)}_X = g_{X,0} \cdot \left(\frac{d_{\max}}{d_i + \epsilon}\right)^{\gamma_X}$$

### 2.4 The Boundary Lagrangian

At boundary $\partial S_{ij}$:

$$\mathcal{L}^{(ij)}_{\text{boundary}} = \lambda_{ij} \Phi + \frac{1}{2}(\mu^I_{ij})^2 A^{(ij)Ia}_\mu A^{(ij)Ia\mu} + \frac{1}{2}(\mu^H_{ij})^2 A^{(ij)H}_\mu A^{(ij)H\mu} + \kappa_{ij} \bar{\psi} \Gamma^{(ij)} \psi$$

**Note**: The mass terms are gauge-invariant because they use $A_\mu A^\mu$ (magnitude squared), not $A_\mu$ alone.

---

## 3. Non-Abelian Junction Conditions

### 3.1 Derivation (Corrected)

Varying the action yields:

**Bulk equations** (Yang-Mills):

$$D^{(i)}_\mu F^{(i)Ia\mu\nu} = g^{(i)}_I J^{(i)Ia\nu}$$

**Junction conditions** at $\partial S_{ij}$:

$$\boxed{\left[ n_\mu F^{Ia\mu\nu} \right]_{\partial S_{ij}} = \lambda_{ij} \frac{\delta \Phi}{\delta A^{Ia}_\nu} + (\mu^I_{ij})^2 A^{(ij)Ia}_\nu}$$

**Clarification (addressing reviewer concern)**: The non-abelian content is *inside* $F^{Ia}_{\mu\nu}$, which contains the term $g_I \epsilon^{abc} A^{Ib}_\mu A^{Ic}_\nu$. I do **not** add a separate self-interaction term on the RHS—that would be double-counting. The junction condition has the same *form* as the abelian case; the *solutions* differ because $F$ is non-linear.

### 3.2 Bond-Type Mixing via Holonomy

The reviewer correctly noted that $\langle A_\mu \rangle$ is not gauge-invariant. The proper gauge-invariant description of mixing uses **holonomy**.

**Definition 3.1 (Moral Holonomy).** For a path $\gamma$ from point $x$ to point $y$ along boundary $\partial S_{ij}$, the holonomy is:

$$U(\gamma) = \mathcal{P} \exp\left( i g_I \int_\gamma A^{Ia}_\mu \frac{\tau^a}{2} dx^\mu \right)$$

where $\mathcal{P}$ denotes path-ordering.

**Physical interpretation**: $U(\gamma)$ is an SU(2) matrix that rotates bond states as they traverse the boundary. A bond entering as $|O\rangle$ exits as $U(\gamma)|O\rangle$—a superposition of obligation and claim.

**Gauge transformation**: Under $A_\mu \to g A_\mu g^{-1} + (i/g_I) g \partial_\mu g^{-1}$, the holonomy transforms as:

$$U(\gamma) \to g(y) U(\gamma) g(x)^{-1}$$

For a **closed loop** $\gamma$, the trace $\text{Tr}(U(\gamma))$ is gauge-invariant—this is the Wilson loop.

### 3.3 The Mixing Angle

For an infinitesimal path element $d\gamma$, the holonomy is approximately:

$$U(d\gamma) \approx 1 + i g_I A^{Ia}_\mu \frac{\tau^a}{2} dx^\mu$$

The **mixing angle** accumulated over a finite path is:

$$\theta^a(\gamma) = g_I \int_\gamma A^{Ia}_\mu dx^\mu$$

This is gauge-dependent for open paths, but the *relative* rotation between two bonds traversing the same boundary is gauge-invariant.

---

## 4. Running Coupling and Asymptotic Freedom

### 4.1 Beta Function

The one-loop beta function for SU(2) with $N_f$ Dirac fermions:

$$\beta(g_I) = \frac{dg_I}{d\ln\mu} = -\frac{g_I^3}{16\pi^2} \left( \frac{22}{3} - \frac{4N_f}{3} \right)$$

For $N_f < 5.5$, we have asymptotic freedom: coupling decreases at high energies, increases at low energies.

### 4.2 Combined Scaling (Clarified)

The full effective coupling combines RG running with stratification:

$$g^{\text{eff}}_I(S_i, \mu) = g_{I,0} \cdot \underbrace{\left(\frac{d_{\max}}{d_i + \epsilon}\right)^{\gamma_I}}_{\text{stratification}} \cdot \underbrace{\left( 1 + \frac{b_0 g_{I,0}^2}{8\pi^2} \ln\frac{\mu^2}{\Lambda^2} \right)^{-1/(2b_0)}}_{\text{RG running}}$$

**Interpretation of scales**:
- **Stratification scale**: $d_i$ is the dimension of the stratum—a discrete, geometric quantity.
- **RG scale $\mu$**: This is the "moral resolution"—how finely we probe the ethical situation. High $\mu$ = examining micro-details; low $\mu$ = coarse-grained assessment.

The two effects are independent:
- Approaching a 0-D stratum ($d_i \to 0$) increases coupling via stratification.
- Examining low-resolution / long-range moral effects ($\mu \to 0$) increases coupling via RG.

Both drive toward strong coupling at decision points, but they are conceptually distinct.

---

## 5. Confinement via Wilson Loop

### 5.1 The Moral Wilson Loop

**Definition 5.1.** For a closed contour $\mathcal{C}$ in stratum $S_i$:

$$W[\mathcal{C}] = \frac{1}{2} \text{Tr} \, \mathcal{P} \exp\left( i g_I \oint_{\mathcal{C}} A^{Ia}_\mu \frac{\tau^a}{2} dx^\mu \right)$$

The factor $1/2$ normalizes by the dimension of the fundamental representation.

**Physical interpretation**: $W[\mathcal{C}]$ is the amplitude for creating a bond-antibond pair, propagating them around $\mathcal{C}$, and annihilating them. It measures the "cost" of maintaining separated moral charges.

### 5.2 Confinement Criterion

**Area law (confinement)**:
$$\langle W[\mathcal{C}] \rangle \sim \exp(-\sigma \cdot \text{Area}[\mathcal{C}])$$

**Perimeter law (deconfinement)**:
$$\langle W[\mathcal{C}] \rangle \sim \exp(-\kappa \cdot \text{Perimeter}[\mathcal{C}])$$

### 5.3 Proof of Confinement (Strong Coupling)

**Theorem 5.1.** In the strong-coupling limit of lattice-discretized non-abelian SQND, the Wilson loop satisfies an area law.

**Proof** (following Wilson [4] and Greensite [5]):

1. **Lattice formulation**: Discretize with spacing $a$. Link variables $U_\mu(x) = e^{i a g_I A^a_\mu(x) \tau^a/2} \in SU(2)$.

2. **Wilson action**: 
$$S = \beta \sum_{\text{plaquettes}} \left( 1 - \frac{1}{2} \text{Re Tr} \, U_P \right)$$
where $\beta = 4/g_I^2$ and $U_P$ is the ordered product around a plaquette.

3. **Strong coupling** ($\beta \ll 1$): The partition function is dominated by configurations minimizing the number of "excited" plaquettes.

4. **Character expansion**: Using $\int dU = 1$ and $\int dU \, U_{ij} = 0$, the only non-zero contribution to $\langle W[\mathcal{C}] \rangle$ comes from "tiling" $\mathcal{C}$ with plaquettes.

5. **Minimum tiling**: For a rectangle of area $A = RT/a^2$ plaquettes, each contributes factor $\beta/4$:

$$\langle W[\mathcal{C}] \rangle \sim \left( \frac{\beta}{4} \right)^{A} = \exp\left( A \ln \frac{\beta}{4} \right) = \exp(-\sigma A)$$

with string tension $\sigma = -a^{-2} \ln(\beta/4)$.

**QED.**

### 5.4 Singlet Constraint at Decision Points

At 0-dimensional strata where $\sigma \to \infty$, the area law forbids all non-singlet configurations. The only allowed states are **SU(2) singlets**:

$$|\text{singlet}\rangle = \frac{1}{\sqrt{2}} \left( |O\rangle_A |C\rangle_B - |C\rangle_A |O\rangle_B \right)$$

**Moral interpretation**: At decision points, obligations must be paired with claims. Unilateral moral positions (pure obligation without corresponding claim) cannot exist in isolation. This is the formal basis for requiring *balance* in moral judgment.

### 5.5 Clarification: Confinement vs. Observation of Bond Types

A potential confusion must be addressed:

**The apparent tension**: In Definition 1.3, colors are "not observable." But in experiments (§8), we ask subjects to distinguish obligation from claim. If subjects can identify bond types, isn't the "color" observable?

**Resolution**: Confinement is **stratum-dependent**.

- **In bulk strata** (high-dimensional, everyday moral life): The coupling is weak. Individual bond types *are* distinguishable. Alice can have an obligation to Bob without Bob having an explicit corresponding claim. "Open color" configurations exist, analogous to quarks in a quark-gluon plasma.

- **At decision points** (0-dimensional strata): The coupling diverges. Confinement kicks in. Only singlet combinations survive. A judgment of "Alice has an obligation" *necessarily* implies "Bob has a claim"—the balanced configuration is enforced.

**The analogy**: In QCD, we observe hadrons (singlets) but not free quarks. However, in deep inelastic scattering at high energies, we probe the quark structure—quarks become "visible" at short distances. Similarly, in SQND:

| Regime | QCD | Non-Abelian SQND |
|--------|-----|------------------|
| Low energy / decision point | Confinement, only hadrons | Confinement, only balanced bonds |
| High energy / deliberation | Asymptotic freedom, quarks visible | Weak coupling, individual types visible |

This resolves the tension: **bond types are observable in the bulk; only their singlet combinations survive at decision points**.

---

## 6. Worked Example: Bond-Type Rotation Through a Threshold

### 6.1 Setup

**Scenario**: Alice (A) has an obligation to Bob (B) to keep a promise. A moral threshold occurs when circumstances change (e.g., Bob's interests shift, making the promise less beneficial to him).

**Mathematical setup**:
- **Bulk stratum $S_2$**: The "promise-keeping" regime, dimension 2.
- **Boundary $\partial S$**: The threshold where circumstances change.
- **Bulk stratum $S'_2$**: The "post-change" regime.

**Initial bond state** (in $S_2$):
$$|b_{\text{init}}\rangle = |O\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}$$

Alice has a pure obligation to Bob.

### 6.2 The Holonomy at the Boundary

Suppose the boundary has gauge field configuration corresponding to holonomy:

$$U(\gamma) = \exp\left( i \frac{\theta}{2} \tau^1 \right) = \begin{pmatrix} \cos(\theta/2) & i\sin(\theta/2) \\ i\sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$$

where $\theta$ is the total "mixing angle" accumulated at the boundary, determined by the boundary Lagrangian.

### 6.3 The Rotated Bond State

After crossing the boundary:

$$|b_{\text{final}}\rangle = U(\gamma) |O\rangle = \cos(\theta/2) |O\rangle + i\sin(\theta/2) |C\rangle$$

### 6.4 Probability Calculation

The probability that the bond is measured as a **claim** after crossing:

$$P(C) = |i\sin(\theta/2)|^2 = \sin^2(\theta/2)$$

The probability it remains an **obligation**:

$$P(O) = \cos^2(\theta/2)$$

### 6.5 Numerical Example

Let $\theta = \pi/3$ (60° mixing angle). Then:

$$P(O) = \cos^2(\pi/6) = \left(\frac{\sqrt{3}}{2}\right)^2 = 0.75$$

$$P(C) = \sin^2(\pi/6) = \left(\frac{1}{2}\right)^2 = 0.25$$

**Interpretation**: After crossing the threshold, there's a 75% probability that Alice's relationship to Bob is still perceived as her obligation to him, but a 25% probability it's reframed as his claim against her.

### 6.6 Gauge-Invariant Observable

The individual probabilities $P(O), P(C)$ depend on the basis choice. To construct a gauge-invariant observable, we need to consider the *relational* structure between agents.

**Critical point**: If both agents cross the *same* boundary with the *same* holonomy $U$, singlet projections are preserved. This follows from representation theory: the singlet is a scalar under $SU(2)$, so $U \otimes U |\text{singlet}\rangle = |\text{singlet}\rangle$.

**The physically interesting case**: Alice crosses the threshold while Bob remains in the original context (e.g., Alice realizes the promise has become harmful, but Bob is unaware of the changed circumstances).

**Initial state**: Alice has obligation to Bob, Bob has corresponding claim against Alice:
$$|b_{\text{init}}\rangle = |O\rangle_A \otimes |C\rangle_B$$

Note: This is *not* a pure singlet. Decomposing into irreps:
$$|O\rangle|C\rangle = \frac{1}{\sqrt{2}}(|\text{singlet}\rangle + |T_0\rangle)$$
where $|T_0\rangle$ is the $m=0$ triplet state.

**After Alice crosses** (Bob unchanged):
$$|b_{\text{final}}\rangle = U(\gamma)|O\rangle_A \otimes |C\rangle_B = \left(\cos\frac{\theta}{2}|O\rangle_A + i\sin\frac{\theta}{2}|C\rangle_A\right) \otimes |C\rangle_B$$

**Singlet overlap**:
$$\langle \text{singlet} | b_{\text{final}} \rangle = \frac{1}{\sqrt{2}}\left(\langle O|_A \langle C|_B - \langle C|_A \langle O|_B\right) \cdot \left(\cos\frac{\theta}{2}|O\rangle_A + i\sin\frac{\theta}{2}|C\rangle_A\right)|C\rangle_B$$

Only the first term of the singlet bra survives (since $\langle O|C\rangle = 0$):
$$= \frac{1}{\sqrt{2}} \cos\frac{\theta}{2}$$

**Probability of maintaining balanced relationship**:
$$P(\text{singlet}) = \left|\frac{1}{\sqrt{2}} \cos\frac{\theta}{2}\right|^2 = \frac{1}{2}\cos^2\frac{\theta}{2}$$

For $\theta = \pi/3$: $P(\text{singlet}) = \frac{1}{2} \cdot \frac{3}{4} = 0.375$.

**Physical interpretation**: As Alice's context shifts ($\theta$ increases), the probability of maintaining a coherent, balanced moral relationship *decreases*. At $\theta = \pi$ (maximal rotation), $P(\text{singlet}) = 0$—the relationship has become completely unbalanced from a moral standpoint.

This captures the intuition that when one party to a moral relationship undergoes a significant context shift while the other doesn't, the relationship becomes "out of sync."

---

## 7. Contextuality Predictions (Refined)

### 7.1 Clarification: Non-Abelian vs. Contextuality

The reviewer correctly noted that the distinction "abelian bound = 2, non-abelian bound = $2\sqrt{2}$" conflates issues. Let me clarify:

**Classical (non-contextual) bound**: CHSH $\leq 2$.

**Quantum (contextual) bound**: CHSH $\leq 2\sqrt{2}$ (Tsirelson).

Both abelian and non-abelian *quantum* theories can achieve Tsirelson's bound. The distinction is:

**Prediction**: Non-abelian SQND **enlarges the class of scenarios** where strong contextuality is achievable, and makes Tsirelson-saturating correlations **more generic** near boundaries.

Specifically:
- In abelian SQND, strong contextuality requires special fine-tuned states.
- In non-abelian SQND, the boundary mixing generically produces entangled states that exhibit strong contextuality.

### 7.2 The Abramsky-Brandenburger Framework

Following [6], contextuality is the obstruction to extending local distributions globally.

**Definition 7.1 (Empirical Model).** An empirical model $e$ assigns probability distributions $e_C$ to each measurement context $C$.

**Definition 7.2 (Non-contextuality).** Model $e$ is non-contextual if $\exists$ global distribution $e_{\text{global}}$ such that $e_C = e_{\text{global}}|_C$ for all $C$.

**Definition 7.3 (Strong Contextuality).** Model $e$ is strongly contextual if even the *supports* (possible outcomes) cannot be extended globally.

### 7.3 Non-Abelian Enhancement of Contextuality

**Theorem 7.1.** Let $\mathcal{E}$ be the empirical model for bond-type measurements on two agents with bonds that have crossed a shared boundary. If the boundary holonomy $U(\gamma)$ satisfies:

$$\text{Tr}(U(\gamma)) \neq \pm 2$$

(i.e., $U$ is not $\pm \mathbf{1}$), then $\mathcal{E}$ exhibits at least logical contextuality.

**Proof sketch**: Non-trivial holonomy creates superpositions of bond types. Measuring bond type in different bases (e.g., $\{|O\rangle, |C\rangle\}$ vs. $\{|O\rangle + |C\rangle, |O\rangle - |C\rangle\}$) yields incompatible probability distributions that cannot arise from a single global assignment. □

### 7.4 Logical Bell Inequality for Moral Scenarios

Following Abramsky-Hardy [7]:

**Scenario**: Three agents A, B, C with bonds $b_{AB}, b_{BC}, b_{CA}$.

**Events**:
- $E_{AB}$: Bond $b_{AB}$ is measured as obligation
- $E_{BC}$: Bond $b_{BC}$ is measured as obligation
- $E_{CA}$: Bond $b_{CA}$ is measured as claim

**Classical (non-contextual) constraint**: If all three events are possible individually, they must be jointly possible:

$$P(E_{AB} \land E_{BC} \land E_{CA}) \geq P(E_{AB}) + P(E_{BC}) + P(E_{CA}) - 2$$

**Quantum violation**: For certain entangled bond configurations approaching a 0-D stratum (with confinement active), the singlet constraint forces:

$$P(E_{AB} \land E_{BC} \land E_{CA}) = 0$$

even when $P(E_{AB}), P(E_{BC}), P(E_{CA}) > 0$.

This is a Hardy-type logical contradiction—proof of contextuality without inequalities.

---

## 8. Experimental Protocols (Operationalized)

### 8.1 Protocol 1: Bond-Type Rotation

**Objective**: Detect change in perceived bond type after moral context shift.

**Operationalization**:

*What is a "bond type measurement"?*
- Present subjects with a vignette describing relationship between A and B.
- Ask forced-choice: "This relationship is best described as: (a) A owes something to B [obligation]; (b) B has a right against A [claim]; (c) A is free regarding B [liberty]; (d) B has no claim on A [no-claim]."

*What is a "boundary"?*
- A described change in circumstances: "Now suppose [new information]. How would you describe the relationship?"
- Boundaries can be calibrated by independent raters for "significance of context shift."

*What is the prediction?*
- Post-boundary responses differ from pre-boundary responses.
- The rotation angle $\theta$ can be estimated from response proportions.
- Stronger boundaries (higher $\mu_{ij}$) should show smaller rotations (boundary mass suppresses mixing).

*What would falsify?*
- If responses are unchanged regardless of boundary, or if changes are random (not systematic rotation).

### 8.2 Protocol 2: Holonomy Detection

**Objective**: Test path-dependence of bond-type transformation.

**Setup**:
- Initial state: Clear obligation.
- Path 1: Context shift A → B (single boundary).
- Path 2: Context shift A → X → B (two boundaries, same endpoints).

**Prediction (non-abelian)**:
$$U(\gamma_1) \neq U(\gamma_2)$$
in general, because holonomies compose non-commutatively:
$$U(\gamma_2) = U(X \to B) \cdot U(A \to X) \neq U(A \to B) = U(\gamma_1)$$

**Measurement**: Different final bond-type distributions for paths 1 vs. 2, even though start and end points are identical.

*What would falsify?*
- Path-independent results would support abelian structure.

### 8.3 Protocol 3: Collective Responsibility Contextuality

**Objective**: Test for logical Bell inequality violation in three-agent scenarios.

**Setup**:
1. Scenario with three agents A, B, C in causal chain (A influences B, B influences C, C influences A—a moral cycle).
2. Measure responsibility attributions in three contexts:
   - $C_1$: Focus on A and B only
   - $C_2$: Focus on B and C only
   - $C_3$: Focus on A and C only

**Operationalization**:
- "On a scale of 0-10, how responsible is [agent] for the outcome?"
- Threshold at 5 to create binary events.

**Prediction**:
- Correlations $E(C_i)$ can exceed classical bounds.
- Specifically, pairwise agreements can all be high while three-way agreement is low—Hardy-type contradiction.

**Sample size**: Power analysis suggests N ≈ 200 per condition to detect effect size d = 0.3 at α = 0.05.

*What would falsify?*
- Classical correlations (no inequality violation).
- Correlations exceeding Tsirelson bound (would falsify quantum model too).

### 8.4 Protocol 4: Confinement Signature

**Objective**: Test that unbalanced moral configurations become unstable near decision points.

**Setup**:
1. Present scenarios with unilateral bonds (obligation without corresponding claim).
2. Vary proximity to decision point (operationalized as time pressure, consequence severity, or irreversibility).

**Measurement**: 
- Discomfort ratings (1-7 Likert scale).
- Open-ended responses coded for "something is missing" or "relationship is incomplete."

**Prediction**:
$$\text{Discomfort} = \beta_0 + \beta_1 \cdot \sigma(S_i) \cdot (\text{singlet violation})^2 + \epsilon$$

where singlet violation measures deviation from balanced configuration.

Near decision points (high $\sigma$), discomfort should increase sharply.

*What would falsify?*
- Flat discomfort regardless of balance or decision proximity.

---

## 9. Discussion

### 9.1 Why Not Higher Groups?

The reviewer asked about SU(3) vs. SU(2). Our choice of SU(2)_I × U(1)_H is motivated by parsimony:

- The Hohfeldian incident relations form a 2D complex space (obligation/claim).
- SU(2) is the minimal non-abelian group acting on $\mathbb{C}^2$.
- Adding consequential relations (power/immunity) could motivate SU(2)_I × SU(2)_C × U(1)_H, but this requires empirical justification for independent mixing in both sectors.

We propose SU(2)_I × U(1)_H as the **minimal non-abelian extension**, testable before considering larger groups.

### 9.2 Dynamical Source of "Oscillations"

The reviewer noted that my oscillation discussion borrowed neutrino formalism without clear dynamical source. Let me reframe:

In neutrino physics, oscillations arise from mass eigenstates differing from flavor eigenstates, with time evolution under a mass Hamiltonian.

In non-abelian SQND, the analog is **not** time evolution but **context traversal**. "Oscillation" is better understood as:

$$|b(\gamma)\rangle = U(\gamma) |b_{\text{init}}\rangle$$

where $\gamma$ is the path through moral context space. The "oscillation frequency" is really the **rate of phase accumulation** per unit context-distance, set by $g_I \int A_\mu dx^\mu$.

This reframing avoids importing inapplicable mass-matrix physics.

### 9.3 Relation to Moral Philosophy

**Correlativity**: The Hohfeldian correlativity (A's obligation ↔ B's claim) is the singlet constraint. Confinement enforces correlativity at decision points.

**Moral reframing**: Bond-type mixing via holonomy captures how the "same" relationship can be genuinely described as obligation or claim depending on the path of moral reasoning.

**Non-commutativity**: Order effects in moral judgment [2] are explained by non-commuting holonomies for different reasoning paths.

---

## 10. Conclusion

We have extended SQND from U(1) to **SU(2)_I × U(1)_H** gauge structure. Key results:

1. **Gauge group derivation**: From Hohfeldian classification, with explicit dictionary mapping mathematical objects to moral concepts.

2. **Holonomy-based mixing**: Bond types rotate via gauge-invariant holonomies, not gauge-dependent field expectations.

3. **Corrected junction conditions**: Non-abelian content inside $F_{\mu\nu}$, no double-counting.

4. **Rigorous confinement**: Wilson loop area law enforces singlet constraint at decision points.

5. **Worked example**: Explicit calculation of bond rotation through a threshold.

6. **Refined contextuality predictions**: Non-abelian structure enlarges contextual correlation space (not merely raises bounds).

7. **Operationalized experiments**: Explicit protocols with falsifiability criteria.

The theory makes testable predictions distinguishing it from abelian SQND and classical models of moral cognition.

---

## References

[1] A. H. Bond, "Stratified Quantum Normative Dynamics," December 2025.

[2] J. R. Busemeyer and P. D. Bruza, *Quantum Models of Cognition and Decision*, Cambridge, 2012.

[3] W. N. Hohfeld, "Fundamental Legal Conceptions," *Yale Law Journal*, 26:710-770, 1917.

[4] K. G. Wilson, "Confinement of Quarks," *Phys. Rev. D* 10:2445, 1974.

[5] J. Greensite, *An Introduction to the Confinement Problem*, Springer, 2011.

[6] S. Abramsky and A. Brandenburger, "The Sheaf-Theoretic Structure of Non-Locality and Contextuality," *New J. Phys.* 13:113036, 2011.

[7] S. Abramsky and L. Hardy, "Logical Bell Inequalities," *Phys. Rev. A* 85:062114, 2012.

[8] M. E. Peskin and D. V. Schroeder, *An Introduction to Quantum Field Theory*, Westview, 1995.

---

## Appendix A: SU(2) Conventions and Identities

### A.1 Pauli Matrices

$$\tau^1 = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad \tau^2 = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}, \quad \tau^3 = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$$

### A.2 Commutation Relations

$$[\tau^a, \tau^b] = 2i\epsilon^{abc}\tau^c$$

$$\{\tau^a, \tau^b\} = 2\delta^{ab} \mathbf{1}$$

### A.3 Useful Exponential

$$\exp(i\theta \hat{n} \cdot \vec{\tau}/2) = \cos(\theta/2) \mathbf{1} + i \sin(\theta/2) (\hat{n} \cdot \vec{\tau})$$

---

## Appendix B: Derivation of Junction Conditions

Starting from action:
$$S = \sum_i \int_{S_i} \mathcal{L}^{(i)}_{\text{bulk}} + \sum_{ij} \int_{\partial S_{ij}} \mathcal{L}^{(ij)}_{\text{bdy}}$$

Varying w.r.t. $A^{Ia}_\nu$:

$$\delta S = \sum_i \int_{S_i} (D_\mu F^{Ia\mu\nu} - g_I J^{Ia\nu}) \delta A^{Ia}_\nu + \sum_{ij} \int_{\partial S_{ij}} \left( [n_\mu F^{Ia\mu\nu}] + \frac{\partial \mathcal{L}_{\text{bdy}}}{\partial A^{Ia}_\nu} \right) \delta A^{Ia}_\nu$$

Setting $\delta S = 0$:

**Bulk**: $D_\mu F^{Ia\mu\nu} = g_I J^{Ia\nu}$ (Yang-Mills)

**Boundary**: $[n_\mu F^{Ia\mu\nu}] = -\partial \mathcal{L}_{\text{bdy}}/\partial A^{Ia}_\nu = \lambda_{ij} \delta\Phi/\delta A^{Ia}_\nu + \mu^2_{ij} A^{(ij)Ia}_\nu$

---

## Appendix C: Comparison Table

| Feature | Abelian SQND | Non-Abelian SQND |
|---------|--------------|------------------|
| Gauge group | U(1) | SU(2)_I × U(1)_H |
| Gauge bosons | 1 (ethon) | 3 + 1 (chromoethons + photoethon) |
| Bond types | Single charge | 2D fundamental rep |
| Type mixing | No | Yes (via holonomy) |
| Self-interaction | No | Yes (cubic/quartic vertices) |
| Confinement | No | Yes (at low-D strata) |
| Contextuality | Weak | Enhanced (larger accessible space) |
| Path dependence | No | Yes (non-commuting holonomies) |

---

*End of paper*
