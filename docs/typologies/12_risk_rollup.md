# Typology 12 - Risk Roll-Up

## 1. Objective

Consolidate indicator-level records into subject-level summaries for suppliers, tenders, and entities.

## 2. Analytical rationale

Multi-indicator aggregation supports prioritization by combining recurrence, severity, and coverage.

## 3. Inputs

- `indicator_results` (IND001..IND011)
- `tenders` for entity mapping

## 4. Output summaries

- `supplier_risk_summary`
- `tender_risk_summary`
- `entity_risk_summary`

## 5. Aggregation flow

1. Map indicator rows to supplier ids.
2. Map indicator rows to tender ids.
3. Map each indicator row through its distinct tender-to-entity links.
4. Compute for each subject:

   - indicator count,
   - maximum risk level,
   - weighted score,
   - indicator code set.

## 6. Weighting model

Use risk-level ordinal weights:

- `LOW = 1`
- `MEDIUM = 2`
- `HIGH = 3`

Weighted summary score is the mean of `level weight * record risk score`. It is
a prioritization index, not a probability, and it can exceed 100.

## 7. Evidence strategy

Summaries store compact references, not full evidence payloads.

Detailed evidence remains in base indicator output.

## 8. Edge cases

1. Pair/group records may map to multiple suppliers.
2. Missing tender-entity mapping excludes those rows from entity summary.
3. Malformed evidence payloads should not break supplier-level aggregation.

## 9. Adaptation levers

- weighting formula,
- score normalization method,
- cross-indicator de-duplication policy.

## 10. Validation checklist

- no empty summary rows,
- summary level consistency with source records,
- reproducible ordering and scoring across reruns.
