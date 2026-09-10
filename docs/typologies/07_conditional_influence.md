# Typology 07 - Conditional Influence

## 1. Objective

Detect directional pair patterns where one supplier's participation materially increases another supplier's win probability.

## 2. Analytical rationale

This typology captures conditional behavior not observable from static recurrence alone.

## 3. Required fields

- `tender_id`
- `bidder_id`
- `awarded_flag`

## 4. Core metrics

For ordered pair `(A <- B)`:

- `baseline_win_probability`
- `conditional_win_probability`
- `influence_gap`
- `influence_magnitude`
- `conditioning_event_count`

## 5. Detection flow

1. Build event and win sets per supplier.
2. Iterate ordered supplier pairs.
3. Compute baseline and conditional probabilities.
4. Apply three gates:

   - baseline upper gate,
   - conditional lower gate,
   - minimum gap.

5. Assign risk and score.

## 6. Risk assignment guidance

- `HIGH`: strong uplift magnitude with sufficient support.
- `MEDIUM`: material uplift with moderate magnitude.

## 7. Evidence structure

- `target_supplier`
- `conditioning_supplier`
- `baseline_win_probability`
- `conditional_win_probability`
- `influence_gap`
- `influence_magnitude`
- `conditioning_event_count`
- `tender_ids`

## 8. Edge cases

1. Zero baseline values can inflate magnitude; gap and support must be considered jointly.
2. Very low support conditioning sets can produce unstable probabilities.
3. Directionality is essential: `(A <- B)` differs from `(B <- A)`.

## 9. Adaptation levers

- baseline max range,
- conditional min range,
- gap minimum,
- optional support minimum.

## 10. Validation checklist

- probability bounds in `[0,1]`.
- directional pairs preserved.
- top scores include strong support context.
