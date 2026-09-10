# Typology 11 - Repeated Fiscal Address

## 1. Objective

Detect recurring events where multiple supplier ids share the same normalized fiscal address.

## 2. Analytical rationale

Address-sharing recurrence may indicate structured relationships that merit review, especially with award involvement.

## 3. Required fields

- `tender_id`
- `bidder_id`
- `fiscal_address`
- `awarded_flag`

## 4. Detection flow

1. Normalize addresses.
2. Build `(event, address)` supplier sets.
3. Keep cases with multi-supplier sharing.
4. Aggregate recurrence across events by address.
5. Emit event-level indicator rows for recurring addresses.

## 5. Core metrics

- `address_event_count`
- `address_supplier_count`
- `address_award_count`
- `supplier_ids`
- `tender_ids`

## 6. Risk assignment guidance

- `HIGH`: high recurrence with high supplier multiplicity.
- `MEDIUM`: meaningful recurrence with multi-supplier evidence.

## 7. Evidence structure

- normalized address key,
- recurrence counts,
- supplier and event references.

## 8. Edge cases

1. Shared commercial locations can be benign.
2. Over-aggressive normalization can collapse distinct addresses.
3. Missing address values reduce typology coverage.

## 9. Adaptation levers

- minimum suppliers per `(event,address)`,
- minimum recurring events per address,
- score sensitivity to award overlap.

## 10. Validation checklist

- track normalization collision rates,
- inspect high-score addresses manually,
- ensure deterministic address key generation.
