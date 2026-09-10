# Typology 10 - Public Employee Bidder Overlap

## 1. Objective

Detect identity overlap between bidder ids and employment records and rank by recurrence and exposure.

## 2. Analytical rationale

Identity overlap across participation and employment domains can be a meaningful context signal when recurrent.

## 3. Required fields

From `bids`:

- `bidder_id`
- `tender_id`
- `awarded_flag`
- `awarded_value`

From `employment`:

- `person_id`
- `employer_name`
- `role_name`

## 4. Detection flow

1. Normalize ids in both domains.
2. Join by exact id.
3. Aggregate participation and wins per matched id.
4. Assign risk using recurrence and exposure.

## 5. Core metrics

- `participations`
- `wins`
- `awarded_value`
- `employer_context`
- `role_context`

## 6. Risk assignment guidance

- `HIGH`: repeated wins with overlap recurrence.
- `MEDIUM`: overlap with participation evidence.

## 7. Evidence structure

- participation and win counts,
- exposure proxy,
- context excerpts,
- event references.

## 8. Edge cases

1. Ambiguous ids can inflate matches.
2. Missing role/employer fields reduce context richness.
3. Domain-specific id formatting requires robust normalization.

## 9. Adaptation levers

- minimum participation gate,
- weighting between recurrence and wins,
- strictness of id matching policy.

## 10. Validation checklist

- match coverage ratio tracked,
- id normalization deterministic,
- top records include non-empty context excerpts.
