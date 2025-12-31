# Prometheus Prediction Benchmark Report

Generated: 2025-12-30 19:06:51

Tested 10 repositories

## Results Summary

| Repo | Language | Predicted | Actual | Resilience | Freshness | Conf | Score |
|------|----------|-----------|--------|------------|-----------|------|-------|
| `antirez/sds` | C | BUNKER | ✅ BUNKER | ✅ BRONZE (54) | ✅ MOLDY | 70% | 66% |
| `tidwall/gjson` | Go | BUNKER | 🟡 GLASS HOUSE | ✅ BRONZE (47) | ✅ MOLDY | 67% | 78% |
| `kelseyhightower/envconfig` | Go | BUNKER | ✅ BUNKER | ✅ BRONZE (53) | 🟡 MOLDY | 68% | 77% |
| `sindresorhus/is` | TypeScript | BUNKER | ✅ BUNKER | ✅ BRONZE (59) | 🟡 MOLDY | 62% | 79% |
| `chalk/chalk` | JavaScript | BUNKER | 🟡 GLASS HOUSE | 🟡 PAPER (19) | ✅ FRESH | 67% | 65% |
| `psf/black` | Python | BUNKER | ✅ BUNKER | ✅ STEEL (65) | ✅ MOLDY | 73% | 67% |
| `pallets/click` | Python | BUNKER | 🟡 GLASS HOUSE | ✅ BRONZE (41) | ✅ MOLDY | 73% | 76% |
| `BurntSushi/ripgrep` | Rust | BUNKER | ✅ BUNKER | ✅ STEEL (61) | ✅ MOLDY | 60% | 62% |
| `sharkdp/bat` | Rust | BUNKER | ✅ BUNKER | ✅ BRONZE (52) | ✅ MOLDY | 58% | 62% |
| `junegunn/fzf` | Go | BUNKER | ✅ BUNKER | ✅ STEEL (62) | ✅ MOLDY | 70% | 66% |

**Overall Prediction Accuracy: 69.8%** (Raw: 71.1%)

## Confidence Calibration

How well did confidence levels predict accuracy?

- **High confidence (≥70%):** 4 predictions, 75% accuracy

## Detailed Results

### antirez/sds

**Language:** C | **Type:** Library | **Size:** ~2K LOC
**Reason for prediction:** Small C library, deep nesting common in C
**Confidence notes:** C libs usually BUNKER with --library flag

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 80% | BUNKER | ✅ |
| Resilience | BRONZE (≥50) | 60% | BRONZE (54) | ✅ |
| Freshness | MOLDY | 70% | MOLDY | ✅ |
| Complexity | - | - | LOW (80) | - |
| Smell Score | - | - | 54/100 | - |

**Scores:** Raw: 78% | Confidence: 70% | Weighted: 66%

### tidwall/gjson

**Language:** Go | **Type:** Library | **Size:** ~3K LOC
**Reason for prediction:** JSON parser - deep nesting for parsing logic
**Confidence notes:** JSON parsers inherently nested; Go error handling may not be detected

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 70% | GLASS HOUSE | 🟡 |
| Resilience | BRONZE (≥45) | 50% | BRONZE (47) | ✅ |
| Freshness | MOLDY | 80% | MOLDY | ✅ |
| Complexity | - | - | LOW (80) | - |
| Smell Score | - | - | 55/100 | - |

**Scores:** Raw: 67% | Confidence: 67% | Weighted: 78%

### kelseyhightower/envconfig

**Language:** Go | **Type:** Library | **Size:** ~1K LOC
**Reason for prediction:** Tiny, focused library
**Confidence notes:** Tiny lib, high confidence on quadrant

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 90% | BUNKER | ✅ |
| Resilience | BRONZE (≥50) | 55% | BRONZE (53) | ✅ |
| Freshness | STALE | 60% | MOLDY | 🟡 |
| Complexity | - | - | LOW (80) | - |
| Smell Score | - | - | 37/100 | - |

**Scores:** Raw: 67% | Confidence: 68% | Weighted: 77%

### sindresorhus/is

**Language:** TypeScript | **Type:** Library | **Size:** ~2K LOC
**Reason for prediction:** Pure computation, type checking
**Confidence notes:** Pure type checking lib, should be simple

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 85% | BUNKER | ✅ |
| Resilience | BRONZE (≥55) | 50% | BRONZE (59) | ✅ |
| Freshness | STALE | 50% | MOLDY | 🟡 |
| Complexity | - | - | LOW (80) | - |
| Smell Score | - | - | 38/100 | - |

**Scores:** Raw: 67% | Confidence: 62% | Weighted: 79%

### chalk/chalk

**Language:** JavaScript | **Type:** Library | **Size:** ~1K LOC
**Reason for prediction:** Tiny terminal colors lib
**Confidence notes:** So small it might not have patterns to detect

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 90% | GLASS HOUSE | 🟡 |
| Resilience | WOOD (≥15) | 40% | PAPER (19) | 🟡 |
| Freshness | FRESH | 70% | FRESH | ✅ |
| Complexity | - | - | LOW (80) | - |
| Smell Score | - | - | 4/100 | - |

**Scores:** Raw: 56% | Confidence: 67% | Weighted: 65%

### psf/black

**Language:** Python | **Type:** Tool | **Size:** ~15K LOC
**Reason for prediction:** Complex formatter but deep nesting for AST handling
**Confidence notes:** Would be FORTRESS with working cyclomatic calc

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 60% | BUNKER | ✅ |
| Resilience | STEEL (≥60) | 75% | STEEL (65) | ✅ |
| Freshness | MOLDY | 85% | MOLDY | ✅ |
| Complexity | - | - | MEDIUM (60) | - |
| Smell Score | - | - | 42/100 | - |

**Scores:** Raw: 78% | Confidence: 73% | Weighted: 67%

### pallets/click

**Language:** Python | **Type:** Library | **Size:** ~10K LOC
**Reason for prediction:** CLI framework, lots of nesting for arg parsing
**Confidence notes:** CLI frameworks have inherent nesting

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 75% | GLASS HOUSE | 🟡 |
| Resilience | BRONZE (≥40) | 65% | BRONZE (41) | ✅ |
| Freshness | MOLDY | 80% | MOLDY | ✅ |
| Complexity | - | - | LOW (80) | - |
| Smell Score | - | - | 44/100 | - |

**Scores:** Raw: 67% | Confidence: 73% | Weighted: 76%

### BurntSushi/ripgrep

**Language:** Rust | **Type:** Tool | **Size:** ~20K LOC
**Reason for prediction:** Rust - good error handling but deep nesting for regex/search
**Confidence notes:** Rust Result<T,E> not fully detected; would be FORTRESS with proper cyclomatic

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 50% | BUNKER | ✅ |
| Resilience | STEEL (≥60) | 55% | STEEL (61) | ✅ |
| Freshness | MOLDY | 75% | MOLDY | ✅ |
| Complexity | - | - | LOW (80) | - |
| Smell Score | - | - | 41/100 | - |

**Scores:** Raw: 78% | Confidence: 60% | Weighted: 62%

### sharkdp/bat

**Language:** Rust | **Type:** Tool | **Size:** ~10K LOC
**Reason for prediction:** Rust cat clone - includes test fixtures that add noise
**Confidence notes:** Test fixtures (jquery.js etc) add noise to analysis

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 55% | BUNKER | ✅ |
| Resilience | BRONZE (≥50) | 50% | BRONZE (52) | ✅ |
| Freshness | MOLDY | 70% | MOLDY | ✅ |
| Complexity | - | - | LOW (80) | - |
| Smell Score | - | - | 55/100 | - |

**Scores:** Raw: 78% | Confidence: 58% | Weighted: 62%

### junegunn/fzf

**Language:** Go | **Type:** Tool | **Size:** ~15K LOC
**Reason for prediction:** Terminal UI - lots of deep nesting for input handling
**Confidence notes:** TUI code inherently complex; Go cyclomatic not calculated

| Metric | Predicted | Confidence | Actual | Match |
|--------|-----------|------------|--------|-------|
| Quadrant | BUNKER | 60% | BUNKER | ✅ |
| Resilience | STEEL (≥60) | 65% | STEEL (62) | ✅ |
| Freshness | MOLDY | 85% | MOLDY | ✅ |
| Complexity | - | - | LOW (80) | - |
| Smell Score | - | - | 41/100 | - |

**Scores:** Raw: 78% | Confidence: 70% | Weighted: 66%

## Analysis

### ✅ Correct Predictions

- **antirez/sds**: Predicted BUNKER (80% conf), got BUNKER
- **kelseyhightower/envconfig**: Predicted BUNKER (90% conf), got BUNKER
- **sindresorhus/is**: Predicted BUNKER (85% conf), got BUNKER
- **psf/black**: Predicted BUNKER (60% conf), got BUNKER
- **BurntSushi/ripgrep**: Predicted BUNKER (50% conf), got BUNKER
- **sharkdp/bat**: Predicted BUNKER (55% conf), got BUNKER
- **junegunn/fzf**: Predicted BUNKER (60% conf), got BUNKER

### 📚 Lessons Learned

Based on confidence calibration:

- **Overconfident on chalk/chalk**: 90% confidence but wrong quadrant
