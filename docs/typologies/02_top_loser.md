# Typology 02 - Top Loser

## 1. Objective

Detect suppliers that repeatedly participate but rarely convert participation into awards.

## 2. Analytical rationale

Persistent low conversion at medium-to-high participation levels may reveal asymmetric competitive behavior patterns that deserve review.

## 3. Required fields

- `tender_id`
- `bidder_id`
- `awarded_flag`
- `awarded_value`

## 4. Derived metrics

Per supplier:

- `participations`
- `wins`
- `success_rate = wins / participations`
- `awarded_value`

## 5. Detection flow

1. Build distinct participation sets per supplier.
2. Build distinct win sets per supplier.
3. Apply minimum participation gate.
4. Keep suppliers below low-success entry range.
5. Assign risk by success severity and recurrence volume.

## 6. Risk assignment guidance

- `HIGH`: extremely low success with strong recurrence.
- `MEDIUM`: low success with recurrence support.

## 7. Evidence structure

- `participations`
- `wins`
- `success_rate`
- `awarded_value`

Recommended:

- `reference_tender_ids`
- `period_window`

## 8. Edge cases

1. Multi-winner events require distinct-event counting.
2. Supplier merges/splits can distort history.
3. Missing award flags can understate wins.

## 9. Adaptation levers

- participation gate,
- low-success medium and high ranges,
- scoring blend for recurrence vs severity.

## 10. Validation checklist

- `wins <= participations`.
- `success_rate` monotonic with wins at fixed participation.
- flag volume stable under minor profile perturbation.
