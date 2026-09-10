# Typology 01 - Single Bidder Concentration

## 1. Objective

Identify suppliers with elevated concentration of awards in events where effective competition is minimal.

## 2. Analytical rationale

A high share of awards obtained in one-bidder events can indicate structurally concentrated outcomes. On its own, this is not a conclusion; combined with recurrence and exposure it becomes a prioritization signal.

## 3. Required fields

From `bids`:

- `tender_id`
- `bidder_id`
- `awarded_flag`
- `awarded_value`

From `tenders` (optional for cross-check):

- `participant_count`

## 4. Derived metrics

Per supplier:

- `awards_total`
- `awards_single_bidder`
- `single_bidder_ratio = awards_single_bidder / awards_total`
- `single_bidder_awarded_value`

## 5. Detection flow

1. Build bidder count per event from bids.
2. Mark events with exactly one effective bidder.
3. Aggregate awards and single-bidder awards per supplier.
4. Apply minimum awards gate.
5. Apply medium and high ratio bands.
6. Emit standardized indicator rows.

## 6. Risk assignment guidance

- `HIGH`: high ratio with sufficient awarded volume.
- `MEDIUM`: meaningful ratio with recurrence support.
- no signal: below recurrence or below concentration entry range.

## 7. Evidence structure

Minimum keys:

- `awards_total`
- `awards_single_bidder`
- `single_bidder_ratio`
- `single_bidder_awarded_value`

Recommended optional keys:

- `reference_tender_ids`
- `period_window`

## 8. Edge cases

1. Duplicate bid rows can inflate bidder counts.
2. Event corrections may temporarily misstate participant counts.
3. Zero-value awards still contribute to recurrence.

## 9. Adaptation levers

- minimum awards requirement,
- medium/high concentration ranges,
- score weighting between ratio and volume.

## 10. Validation checklist

- Ratio bounded in `[0,1]`.
- `awards_single_bidder <= awards_total`.
- Top scored cases contain non-empty evidence payload.
