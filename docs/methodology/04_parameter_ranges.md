# 04. Parameter Ranges

## 1. Purpose

This document defines configurable ranges used to calibrate indicator sensitivity while preserving method structure.

The method intentionally uses range guidance rather than fixed universal cut points.

## 2. Profile model

A profile is a named set of parameter values. Recommended baseline profile:

- `balanced`

Typical additional profiles:

- `conservative` (fewer flags, stronger recurrence requirements)
- `sensitive` (more flags, lower recurrence gates)

## 3. Parameter families

## 3.1 Volume gates

Use to ensure minimum signal support:

- minimum awards for concentration indicators,
- minimum participations for persistent behavior indicators,
- minimum group recurrence for multi-party indicators.

## 3.2 Concentration gates

Use to classify concentration intensity:

- single-bidder concentration ratio,
- co-award rate,
- dominance share,
- top-loser success inversion.

## 3.3 Statistical strength gates

Use for pair-dependence signals:

- minimum support,
- minimum confidence,
- practical high-lift band.

## 3.4 Conditional uplift gates

Use for influence signals:

- baseline max band,
- conditional min band,
- minimum probability gap.

## 3.5 Composition gates

Use for network components:

- minimum PF-like count,
- minimum PF-like share,
- linked winner presence.

## 3.6 Overlap gates

Use for contextual overlap indicators:

- strict temporal overlap,
- minimum recurrence for repeated address,
- minimum participation for identity overlap.

## 4. Risk band logic guidance

## 4.1 LOW

- weak recurrence,
- moderate or ambiguous concentration,
- partial supporting context.

## 4.2 MEDIUM

- consistent recurrence,
- meaningful concentration or dependence,
- sufficient support for manual review prioritization.

## 4.3 HIGH

- strong recurrence with strong concentration/dependence,
- or high-confidence contextual overlap with recurrence.

## 5. Calibration workflow

1. Run baseline profile on representative historical window.
2. Measure hit-rate distribution by indicator.
3. Inspect top-scoring records for interpretability.
4. Adjust volume gates first, then concentration/statistical gates.
5. Re-run and compare deltas.
6. Freeze profile with explicit version tag.

## 6. Drift monitoring

Monitor over time:

- total flags per indicator,
- risk-level distribution,
- subject overlap across indicators,
- top-quantile score stability.

If drift exceeds tolerance, review profile and upstream data quality.

## 7. Practical guardrails

1. Avoid tuning on a single short period.
2. Avoid overfitting by minimizing ad-hoc exception logic.
3. Keep profile changes additive and documented.
4. Keep scoring scale stable across profile revisions.

## 8. Illustrative baseline

A balanced profile often combines:

- medium-to-high recurrence minimums,
- medium concentration threshold for entry,
- high concentration threshold for high-risk band,
- minimum statistical support for pair rules,
- strict overlap date logic.

Exact values remain context-configurable.
