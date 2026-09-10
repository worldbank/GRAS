# Typology 05 - Association Rules

## 1. Objective

Measure dependency strength between supplier pairs using association-rule metrics.

## 2. Analytical rationale

Raw recurrence can be misleading. Association metrics quantify whether joint behavior exceeds independent expectation.

## 3. Required fields

- Pair recurrence metrics from Typology 04
- Award flags and tender IDs for each supplier, including losing bids to define the full event universe

## 4. Derived metrics

For ordered rule `A->B` (and independently `B->A`), using award-event sets:

- `support`
- `support_a`
- `support_b`
- `confidence`
- `lift`
- `leverage`
- `conviction`
- `conviction_status` (`finite`, `infinite`, or `undefined`)

## 5. Detection flow

1. Compute event universe size.
2. Compute supplier award-event supports.
3. For each IND004 candidate pair, evaluate both directions; confidence is joint award support divided by antecedent award support.
4. Derive lift/leverage/conviction.
5. Apply support and confidence minimum gates.

## 6. Risk assignment guidance

- `HIGH`: confidence >= 0.8 and lift >= 1.5 after the profile support/confidence gates.
- `MEDIUM`: any other rule passing those gates; this is a screening heuristic, not a significance test.

## 7. Evidence structure

- full metrics bundle (`support`, `confidence`, `lift`, `leverage`, `conviction`)
- directional pair IDs and `event_basis = award`
- supporting event ids

## 8. Edge cases

1. Very low support can inflate lift instability.
2. With confidence 1, conviction is JSON null with status `infinite`, or `undefined` when consequent support is also 1; no arbitrary large sentinel is emitted.
3. Malformed pair IDs or pairs without jointly awarded events are skipped; metrics are recomputed from bids rather than copied from pair evidence.

Exact formulas and scoring are specified in the [pseudocode](../pseudocode/association_rules.md).

## 9. Adaptation levers

- support floor,
- confidence floor,
- high-lift band definition.

## 10. Validation checklist

- probability metrics in valid bounds,
- no divide-by-zero failures,
- top-lift rows reviewed for support adequacy.
