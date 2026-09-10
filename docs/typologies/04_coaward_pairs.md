# Typology 04 - Co-Award Pairs

## 1. Objective

Detect supplier pairs that repeatedly receive awards together relative to their joint participation opportunities.

## 2. Analytical rationale

Repeated joint awards can indicate structured pair behavior, especially when recurrence and co-award rate are both elevated.

## 3. Required fields

- `tender_id`
- `bidder_id`
- `awarded_flag`
- `awarded_value`

## 4. Derived metrics

Per pair `(A,B)`:

- `events_together`
- `co_awards`
- `co_award_rate`
- `value_proxy`

## 5. Detection flow

1. Build participant and winner sets by event.
2. Generate unordered participant pairs per event.
3. Generate unordered winner pairs per event.
4. Count `events_together` and `co_awards`.
5. Apply minimum recurrence and rate gates.

## 6. Risk assignment guidance

- `HIGH`: high co-award rate with strong recurrence.
- `MEDIUM`: meaningful rate with minimum recurrence.

## 7. Evidence structure

- `supplier_a`
- `supplier_b`
- `events_together`
- `co_awards`
- `co_award_rate`
- `value_proxy`
- `tender_ids`

## 8. Edge cases

1. Events with fewer than two winners cannot generate co-award pairs.
2. Large winner sets can produce many low-support pairs; recurrence gate is mandatory.
3. Pair direction must remain unordered.

## 9. Adaptation levers

- minimum events together,
- medium/high co-award rate ranges,
- optional event-size restriction.

## 10. Validation checklist

- `co_awards <= events_together`.
- non-negative value proxies.
- pair ids deterministic and stable.
