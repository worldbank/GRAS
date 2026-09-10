# Typology 09 - Sanction Overlap

## 1. Objective

Detect awarded bid rows submitted within active sanction windows for the same supplier id. The submission date is a proxy and must not be presented as a verified award date.

## 2. Analytical rationale

Temporal overlap is a direct contextual signal and should be retained as high-priority evidence when recurrent.

## 3. Required fields

From `bids`:

- `bidder_id`
- `awarded_flag`
- `submission_date`
- `awarded_value`
- `tender_id`

From `sanctions`:

- `bidder_id`
- `sanction_start`
- `sanction_end`

## 4. Detection flow

1. Index sanctions by supplier.
2. Evaluate each awarded bid for date overlap.
3. Count each awarded input row and its value once if any window matches, then aggregate per supplier.
4. Assign risk by recurrence level.

## 5. Core metrics

- `overlap_awards`
- `overlap_value_proxy`
- `tender_ids`

## 6. Risk assignment guidance

- `HIGH`: repeated overlap instances.
- `MEDIUM`: at least one overlap instance with context.

## 7. Evidence structure

- overlap count,
- value proxy,
- event references.

## 8. Edge cases

1. Invalid sanction windows must be excluded.
2. Null submission dates prevent overlap evaluation.
3. Multiple matching windows never multiply the same awarded row or its amount. Separate award/lot rows remain additive; duplicated source rows must be resolved upstream.
4. A header-only sanctions input is valid and generates no overlap signals.

## 9. Adaptation levers

- overlap strictness (inclusive bounds),
- recurrence bands,
- value sensitivity in score.

## 10. Validation checklist

- all flagged rows have valid overlap dates,
- no negative value proxy,
- selected overlaps manually reproducible.
