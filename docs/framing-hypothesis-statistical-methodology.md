# Statistical Methodology: Framing Hypothesis Tester

## Experimental Design

### Design Type
**Within-subjects repeated measures design** with independent sampling per condition.

Each prompt serves as its own control, eliminating between-prompt variance. The same prompt is evaluated under baseline (no framing) and one or more treatment conditions (framed versions).

### Isolation Protocol
Critical to validity: each API call is a **separate session** with no shared context.

```
Trial i, Framing j:
  Session 1: P → R_baseline(i)      # Baseline response
  Session 2: P → P'_j               # Transform prompt with framing j  
  Session 3: P'_j → R_j(i)          # Framed response
  Session 4: R_baseline(i) → S_baseline(i)   # Blind score baseline
  Session 5: R_j(i) → S_j(i)        # Blind score framed
```

This prevents:
- Context contamination between conditions
- Order effects in judging
- The model "knowing" it's being compared

---

## Variables

### Independent Variable
**Framing condition** (categorical)
- Baseline (no transformation)
- Treatment conditions: {fun, expert, formal, pirate, ...}

### Dependent Variable
**Response quality score** (ordinal/interval, 1-10 scale)

Judging prompt:
```
Rate the following response on a scale of 1-10, where:
1-3: Poor (incorrect, unhelpful, or incoherent)
4-5: Below average (partially correct, somewhat helpful)
6-7: Good (correct and helpful)
8-9: Very good (correct, helpful, well-structured)
10: Excellent (exceptional clarity, insight, completeness)

Respond with only a number.

Response to evaluate:
{response}
```

### Control Variables
- Model (held constant, e.g., claude-sonnet-4-20250514)
- Temperature (held constant, default)
- Max tokens (held constant)
- Prompt set (same prompts across all conditions)

---

## Sample Size Determination

### Power Analysis

For paired t-test comparing framing vs baseline:

```
n = ((z_α + z_β)² × 2σ²) / δ²

Where:
  α = 0.05 (Type I error rate)
  β = 0.20 (Type II error rate, power = 0.80)
  z_α = 1.96
  z_β = 0.84
  σ = estimated standard deviation of score differences
  δ = minimum detectable effect size
```

**Pilot estimates** (based on preliminary runs):
- σ ≈ 1.5 points
- δ = 1.0 point (minimum meaningful difference)

```
n = ((1.96 + 0.84)² × 2 × 1.5²) / 1.0²
n = (7.84 × 4.5) / 1.0
n ≈ 35 trials per framing
```

### Recommendations

| Purpose | Trials per Framing | Detectable Effect |
|---------|-------------------|-------------------|
| Exploratory | 10-15 | ~1.5 points |
| Confirmatory | 30-50 | ~0.8 points |
| Publication | 50-100 | ~0.5 points |

---

## Statistical Tests

### Primary Analysis: Paired t-test

For comparing a single framing against baseline:

```
H₀: μ_framed - μ_baseline = 0
H₁: μ_framed - μ_baseline ≠ 0

t = (x̄_d - 0) / (s_d / √n)

Where:
  x̄_d = mean of paired differences
  s_d = standard deviation of paired differences
  n = number of trials
  df = n - 1
```

**Implementation:**
```python
from scipy import stats

differences = [framed_scores[i] - baseline_scores[i] for i in range(n)]
t_stat, p_value = stats.ttest_rel(framed_scores, baseline_scores)
```

### Multiple Comparisons: Bonferroni Correction

When testing k framings simultaneously:

```
α_adjusted = α / k

For k = 5 framings and α = 0.05:
  α_adjusted = 0.05 / 5 = 0.01
```

A framing is significant only if p < α_adjusted.

**Alternative: Holm-Bonferroni** (less conservative)
```python
from statsmodels.stats.multitest import multipletests

rejected, p_adjusted, _, _ = multipletests(p_values, method='holm')
```

### Non-parametric Alternative: Wilcoxon Signed-Rank Test

If normality assumption is violated:

```python
from scipy import stats

stat, p_value = stats.wilcoxon(framed_scores, baseline_scores)
```

Use when:
- n < 20
- Score distributions are heavily skewed
- Shapiro-Wilk test rejects normality (p < 0.05)

---

## Effect Size Measures

### Cohen's d (Paired)

```
d = x̄_d / s_d

Where:
  x̄_d = mean difference
  s_d = standard deviation of differences
```

**Interpretation:**
| d | Interpretation |
|---|----------------|
| 0.2 | Small effect |
| 0.5 | Medium effect |
| 0.8 | Large effect |

### Percentage Improvement

```
% improvement = ((μ_framed - μ_baseline) / μ_baseline) × 100
```

### 95% Confidence Interval for Mean Difference

```
CI = x̄_d ± t_(α/2, df) × (s_d / √n)
```

---

## Assumptions and Diagnostics

### 1. Independence
**Assumption:** Trials are independent.
**Ensured by:** Separate API sessions, no context carryover.

### 2. Normality of Differences
**Assumption:** Paired differences are approximately normally distributed.

**Diagnostic:**
```python
from scipy import stats

differences = framed_scores - baseline_scores
stat, p_value = stats.shapiro(differences)

if p_value < 0.05:
    print("Normality violated - use Wilcoxon test")
```

### 3. No Extreme Outliers
**Diagnostic:** Check for differences > 3 standard deviations.

```python
z_scores = (differences - differences.mean()) / differences.std()
outliers = np.abs(z_scores) > 3
```

---

## Multi-Framing Analysis

### One-way Repeated Measures ANOVA

When comparing 3+ framings simultaneously:

```
H₀: μ_baseline = μ_fun = μ_expert = μ_formal
H₁: At least one mean differs
```

**Implementation:**
```python
from scipy import stats

# Friedman test (non-parametric alternative)
stat, p_value = stats.friedmanchisquare(
    baseline_scores, 
    fun_scores, 
    expert_scores, 
    formal_scores
)
```

### Post-hoc Pairwise Comparisons

If ANOVA is significant, perform pairwise comparisons with correction:

```python
from scikit_posthocs import posthoc_nemenyi_friedman

# Returns matrix of p-values for all pairs
p_matrix = posthoc_nemenyi_friedman(data)
```

---

## Reporting Template

### Results Section

```
We conducted N = {n} trials comparing {k} framing conditions against 
an unframed baseline. Responses were scored on a 1-10 scale by a 
blind LLM judge (separate session, no access to condition labels).

Baseline responses received a mean score of {μ_baseline:.2f} 
(SD = {σ_baseline:.2f}).

[TABLE: Results by Framing Condition]
| Framing | Mean (SD) | Δ vs Baseline | 95% CI | t | p | d |
|---------|-----------|---------------|--------|---|---|---|
| fun | 7.4 (1.2) | +1.2 | [0.6, 1.8] | 3.2 | .003* | 0.72 |
| expert | 6.8 (1.4) | +0.6 | [-0.1, 1.3] | 1.8 | .081 | 0.35 |
| formal | 6.5 (1.3) | +0.3 | [-0.4, 1.0] | 0.9 | .372 | 0.18 |

* p < .01 (Bonferroni-corrected α = .017 for k=3 comparisons)

The "fun" framing condition produced significantly higher quality 
scores compared to baseline, with a medium-to-large effect size 
(d = 0.72). No other framing conditions reached statistical 
significance after correction for multiple comparisons.
```

### Visualization

```
      Framing Effect Sizes (Cohen's d)
      
      fun     ████████████████████░░░░  0.72*
      expert  ██████████░░░░░░░░░░░░░░  0.35
      formal  █████░░░░░░░░░░░░░░░░░░░  0.18
      pirate  ██░░░░░░░░░░░░░░░░░░░░░░  0.08
              |    |    |    |    |
              0   0.2  0.5  0.8  1.0
                   S    M    L
              
      * p < .05 (corrected)
```

---

## Limitations and Threats to Validity

### Internal Validity

| Threat | Mitigation | Residual Risk |
|--------|------------|---------------|
| Context contamination | Separate API sessions | Low |
| Order effects | Randomized presentation to judge | Low |
| Judge bias | Blind evaluation, no condition labels | Medium |
| LLM self-preference | Judge may favor own style | Medium |

### External Validity

| Threat | Mitigation | Residual Risk |
|--------|------------|---------------|
| Model specificity | Test on multiple models | High (single model) |
| Prompt specificity | Diverse prompt set | Medium |
| Temporal instability | Note model version, date | Medium |

### Construct Validity

| Threat | Mitigation | Residual Risk |
|--------|------------|---------------|
| Score validity | Calibrated 1-10 rubric | Medium |
| LLM-as-judge reliability | Check inter-session consistency | Medium |

---

## Reproducibility Checklist

```
□ Model and version recorded (e.g., claude-sonnet-4-20250514)
□ Temperature and parameters documented
□ Random seed set (if applicable)
□ Full prompt texts archived
□ Raw response data saved (not just scores)
□ Analysis code versioned
□ Framing transformation prompts documented
□ Judging prompt documented
□ Date of experiments recorded
```

---

## Code: Full Statistical Analysis

```python
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
import json

def analyze_framing_experiment(results_json_path):
    """
    Complete statistical analysis of framing hypothesis experiment.
    
    Parameters
    ----------
    results_json_path : str
        Path to JSON file with trial data
        
    Returns
    -------
    dict
        Statistical results including effect sizes, p-values, CIs
    """
    with open(results_json_path) as f:
        data = json.load(f)
    
    trials = data['trials']
    framings = data['config']['framings']
    
    # Extract scores
    baseline_scores = np.array([t['baseline']['score'] for t in trials])
    
    results = {
        'n_trials': len(trials),
        'baseline': {
            'mean': baseline_scores.mean(),
            'std': baseline_scores.std(),
        },
        'framings': {}
    }
    
    p_values = []
    
    for framing in framings:
        framed_scores = np.array([
            t['framings'][framing]['score'] for t in trials
        ])
        
        # Paired differences
        differences = framed_scores - baseline_scores
        mean_diff = differences.mean()
        std_diff = differences.std(ddof=1)
        n = len(differences)
        
        # Paired t-test
        t_stat, p_value = stats.ttest_rel(framed_scores, baseline_scores)
        p_values.append(p_value)
        
        # Effect size (Cohen's d for paired samples)
        cohens_d = mean_diff / std_diff if std_diff > 0 else 0
        
        # 95% CI for mean difference
        se = std_diff / np.sqrt(n)
        t_crit = stats.t.ppf(0.975, df=n-1)
        ci_lower = mean_diff - t_crit * se
        ci_upper = mean_diff + t_crit * se
        
        # Normality test on differences
        if n >= 20:
            _, normality_p = stats.shapiro(differences)
        else:
            normality_p = None
        
        # Wilcoxon signed-rank (non-parametric alternative)
        wilcoxon_stat, wilcoxon_p = stats.wilcoxon(
            framed_scores, baseline_scores, 
            alternative='two-sided'
        )
        
        results['framings'][framing] = {
            'mean': framed_scores.mean(),
            'std': framed_scores.std(),
            'mean_difference': mean_diff,
            'std_difference': std_diff,
            'percent_improvement': (mean_diff / baseline_scores.mean()) * 100,
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'ci_95': (ci_lower, ci_upper),
            'normality_p': normality_p,
            'wilcoxon_p': wilcoxon_p,
        }
    
    # Multiple comparison correction (Holm-Bonferroni)
    rejected, p_adjusted, _, _ = multipletests(
        p_values, method='holm', alpha=0.05
    )
    
    for i, framing in enumerate(framings):
        results['framings'][framing]['p_adjusted'] = p_adjusted[i]
        results['framings'][framing]['significant'] = rejected[i]
    
    # Overall ANOVA (Friedman test for repeated measures)
    all_scores = [baseline_scores] + [
        np.array([t['framings'][f]['score'] for t in trials])
        for f in framings
    ]
    
    if len(all_scores) >= 3:
        friedman_stat, friedman_p = stats.friedmanchisquare(*all_scores)
        results['omnibus_test'] = {
            'test': 'Friedman',
            'statistic': friedman_stat,
            'p_value': friedman_p,
        }
    
    return results


def print_results_table(results):
    """Print formatted results table."""
    print(f"\nN = {results['n_trials']} trials")
    print(f"Baseline: M = {results['baseline']['mean']:.2f}, "
          f"SD = {results['baseline']['std']:.2f}\n")
    
    print("| Framing | Mean (SD) | Δ | 95% CI | t | p | p_adj | d | Sig |")
    print("|---------|-----------|---|--------|---|---|-------|---|-----|")
    
    for framing, r in results['framings'].items():
        ci = f"[{r['ci_95'][0]:.1f}, {r['ci_95'][1]:.1f}]"
        sig = "✓" if r['significant'] else ""
        print(f"| {framing} | {r['mean']:.1f} ({r['std']:.1f}) | "
              f"{r['mean_difference']:+.1f} | {ci} | "
              f"{r['t_statistic']:.2f} | {r['p_value']:.3f} | "
              f"{r['p_adjusted']:.3f} | {r['cohens_d']:.2f} | {sig} |")


if __name__ == "__main__":
    import sys
    results = analyze_framing_experiment(sys.argv[1])
    print_results_table(results)
```

---

## References

1. Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.

2. Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65-70.

3. Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80-83.

4. Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality. *Biometrika*, 52(3/4), 591-611.

5. Friedman, M. (1937). The use of ranks to avoid the assumption of normality. *Journal of the American Statistical Association*, 32(200), 675-701.
