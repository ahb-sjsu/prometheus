# Engineering Specification
## Zork-Style Text Adventure for Stakeholder Value Elicitation & Alignment Enforcement

---

## 1. Purpose & Scope

This document specifies a **text-based (Zork-style) interactive system** designed to:

1. **Elicit stakeholder value judgments** through constrained, narrative-driven decision-making.
2. **Produce repeatable, auditable measurements** suitable for constructing and validating:
   - a stakeholder value tensor (rank 4–6),
   - a DAG of Ethical Modules (EMs) rooted in a Geneva-style human-rights lens,
   - release-gating alignment scores,
   - and a real-time agent action firewall.

The system is **not** intended to teach ethics, persuade players, or label behavior as moral/immoral. It is a **measurement instrument**, wrapped in a compelling interactive fiction.

---

## 2. Design Principles (Non‑Negotiable)

1. **Operational, not metaphysical**
   - The system measures decisions and invariants, not beliefs or moral truths.

2. **Fun via tension, not gamification**
   - No points, morality meters, or “good/bad” labels.

3. **Invariance-first**
   - The system must support metamorphic testing (paraphrase, order, framing invariance).

4. **Geneva lens dominance**
   - Root constraints (human rights, safety, due process) cannot be overridden downstream.

5. **Dignified refusal**
   - Hard blocks are represented narratively, never as explicit “policy errors.”

---

## 3. High-Level Architecture

```
[ Text Parser ]
      ↓
[ Intent Resolver ]
      ↓
[ Action Descriptor ]
      ↓
[ Ethical Evaluation Engine ]
      ↓
[ Governance DAG ]
      ↓
[ World State Update + Narrative Renderer ]
      ↓
[ Telemetry + Value Tensor Logging ]
```

Each layer must be independently testable.

---

## 4. Core Runtime Components

### 4.1 Text Parser

**Responsibilities**
- Accept free-form player input.
- Map input to canonical verb + object + modifiers.

**Requirements**
- Synonym tolerant ("examine", "inspect", "read" → EXAMINE).
- Robust to rephrasing and politeness markers.
- Reject only when intent cannot be inferred with sufficient confidence.

**Output**
```json
{
  "raw_text": "publish the letter",
  "verb": "PUBLISH",
  "object": "LETTER",
  "confidence": 0.82
}
```

---

### 4.2 Intent Resolver

**Responsibilities**
- Map parsed commands to an **Action Class (a)**.
- Infer implied escalation, delegation, suppression, etc.

**Action Class Examples**
- READ_PRIVATE_DATA
- PUBLISH_PRIVATE_DATA
- ESCALATE_TO_AUTHORITY
- DELAY_DECISION
- AUTHORIZE_EXCEPTION
- DESTROY_EVIDENCE

**Output**
```json
{
  "action_class": "PUBLISH_PRIVATE_DATA",
  "confidence": 0.78
}
```

---

### 4.3 Action Descriptor Builder

Constructs the full **action activation tensor A** used by evaluation.

**Dimensions populated**
- a: action class
- c: context bucket (domain, consent state, jurisdiction, role)
- k: severity band (low → catastrophic)
- u: epistemic state (known, uncertain, unknown)

**Output**
```json
{
  "a": "PUBLISH_PRIVATE_DATA",
  "c": ["accusation", "no_consent", "public_context"],
  "k": "HIGH",
  "u": "LOW_UNCERTAINTY"
}
```

---

## 5. Ethical Evaluation Engine

### 5.1 Ethical Facts Model

Uses the existing **EthicalFacts v0.2** schema (as in `greek_tragedy_pantheon_demo.py`).

Facts are either:
- rule-derived
- classifier-derived
- hybrid
- human-attested

Each fact must carry provenance metadata.

---

### 5.2 Ethical Modules (EMs)

Each EM:
- Consumes EthicalFacts
- Emits an EthicalJudgement

**Judgement Output**
```json
{
  "em_name": "RightsAndDuties",
  "verdict": "FORBID" | "ALLOW" | "ESCALATE" | "CONDITIONAL",
  "normative_score": 0.0–1.0,
  "reasons": ["violates_explicit_rule = True"],
  "metadata": {"forbidden": true}
}
```

EMs must be:
- deterministic
- side-effect free
- monotonic in severity and uncertainty

---

## 6. Governance DAG

### 6.1 Structure

- DAG of EMs and aggregators
- Root nodes: **Geneva Lens** (human rights, non-coercion, due process, irreversibility)
- Mid nodes: domain, jurisdiction, organizational policy
- Leaf nodes: product norms, UX constraints

### 6.2 Aggregation Rules

- FORBID is absorbing
- Constraints can only tighten downstream
- Scores can be combined only among non-forbidden options

**Reference Implementation**
- `select_option(...)` logic as in demo

---

## 7. World Model & Narrative Engine

### 7.1 World State

Tracks:
- time
- institutional trust
- public unrest
- evidence integrity
- NPC memory flags

World state updates are **deterministic functions** of:
- selected action
- EM outcomes
- elapsed time

---

### 7.2 Narrative Rendering

**Rules**
- Never mention EMs, scores, or policies.
- Consequences are described diegetically.
- Hard blocks are rendered as institutional or physical impossibility.

**Example**
> You attempt to publish the letter.
> The clerk takes it from you, seals it, and places it in the archive.
> “This cannot leave the chamber,” she says.

---

## 8. Telemetry & Data Logging

### 8.1 Logged Events (Per Turn)

```json
{
  "session_id": "uuid",
  "turn": 12,
  "raw_input": "publish letter",
  "parsed_intent": {...},
  "action_descriptor": {...},
  "em_judgements": [...],
  "governance_outcome": {...},
  "world_state_delta": {...},
  "timestamp": "ISO-8601"
}
```

### 8.2 Privacy Requirements
- No PII
- Session-level pseudonymous IDs
- Opt-in consent for research use

---

## 9. Value Tensor Construction (Offline)

From telemetry, construct:

**V[s, v, a, c, k, u]**

Where values are derived from:
- revealed escalation thresholds
- refusal frequencies
- monotonicity constraints
- cross-cluster invariants

Only **invariants** graduate to the Geneva lens.

---

## 10. Invariance & Test Harness

### 10.1 Metamorphic Tests

For each scenario:
- paraphrase narrative
- reorder facts
- change names / skins

Expected:
- identical governance outcome OR
- documented contextuality flag

### 10.2 Regression Gates

- No new build may weaken a Geneva constraint.
- No decrease in monotonicity compliance.

---

## 11. MVP Milestone Plan

### Phase 1 (4–6 weeks)
- Parser + intent resolver
- Single-act game (5 scenarios)
- CLI interface
- Full telemetry

### Phase 2 (6–8 weeks)
- Governance DAG
- Multi-stakeholder profiles
- Invariance test harness

### Phase 3
- UI polish
- Content expansion
- Data analysis pipeline

---

## 12. Explicit Non-Goals

- Teaching morality
- Player scoring or ranking
- Personalizing ethics per user
- Reinforcement learning from player behavior

---

## 13. Summary

This system is:
- a Zork-style interactive fiction engine
- an empirical ethics laboratory
- a measurement backbone for alignment enforcement

Its success criterion is **repeatability, invariance, and auditability**, not consensus.

---

