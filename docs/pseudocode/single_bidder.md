# Single Bidder Concentration - Detailed Pseudocode

## Signal intent

Detect suppliers whose award profile is strongly concentrated in events with a single effective bidder.

## Inputs

- `tenders(tender_id, entity_id, participant_count, ...)`
- `bids(bid_id, tender_id, bidder_id, awarded_flag, awarded_value, ...)`
- `profile` with configurable ranges

## Output record

`IND001_SINGLE_BIDDER` at `subject_type = supplier`

## Required pre-processing

1. Normalize identifiers to canonical string format.
2. Convert `awarded_flag` to boolean.
3. Convert `awarded_value` to numeric.
4. Drop records with empty `tender_id` or `bidder_id`.

## Derived datasets

- `effective_bidders_per_tender[tender_id] = count(distinct bidder_id)`
- `single_bidder_tenders = {tender_id | effective_bidders_per_tender == 1}`
- `awards_per_supplier[supplier] = count(distinct tender_id where awarded_flag = true)`
- `single_awards_per_supplier[supplier] = count(distinct tender_id where awarded_flag = true and tender in single_bidder_tenders)`
- `single_awarded_value_per_supplier[supplier] = sum(awarded_value where awarded_flag = true and tender in single_bidder_tenders)`

## Core pseudocode

```text
PROCEDURE DetectSingleBidderConcentration(tenders, bids, profile, run_ts):
    INIT results = []

    INIT bidders_by_tender = map<tender_id, set<supplier_id>>()
    FOR each bid IN bids:
        bidders_by_tender[bid.tender_id].add(bid.bidder_id)

    INIT single_tenders = set()
    FOR each tender_id IN bidders_by_tender:
        IF size(bidders_by_tender[tender_id]) == 1:
            single_tenders.add(tender_id)

    INIT awards_total = map<supplier_id, int>(default=0)
    INIT awards_single = map<supplier_id, int>(default=0)
    INIT value_single = map<supplier_id, float>(default=0)

    FOR each bid IN bids:
        IF bid.awarded_flag != true:
            CONTINUE
        supplier = bid.bidder_id
        awards_total[supplier] += 1

        IF bid.tender_id IN single_tenders:
            awards_single[supplier] += 1
            value_single[supplier] += bid.awarded_value

    FOR each supplier IN awards_total:
        total = awards_total[supplier]
        IF total < profile.single_bidder_min_awards:
            CONTINUE

        single = awards_single[supplier]
        ratio = single / total

        IF ratio < profile.single_bidder_ratio_medium:
            CONTINUE

        IF ratio >= profile.single_bidder_ratio_high:
            risk_level = HIGH
            risk_score = f_high_single_bidder(total, ratio)
        ELSE:
            risk_level = MEDIUM
            risk_score = f_medium_single_bidder(total, ratio)

        evidence = {
            awards_total: total,
            awards_single_bidder: single,
            single_bidder_ratio: ratio,
            single_bidder_awarded_value: value_single[supplier]
        }

        APPEND standardized indicator record to results

    RETURN sort_desc(results, by=[risk_score, subject_id])
```

## Scoring guidance

- `f_high_single_bidder(total, ratio)` should increase with both ratio and award count.
- `f_medium_single_bidder(total, ratio)` should prioritize ratio first, then volume.

## Edge-case handling

1. Supplier with awards but zero monetary values: keep signal, value proxy can be zero.
2. Duplicate bid rows: deduplicate by `(bid_id)` if available; otherwise `(tender_id, bidder_id, awarded_flag)`.
3. Mixed boolean encodings: coerce (`1`, `true`, `yes`) consistently.
4. Missing tender table row: still compute from bids universe.

## Quality checks

1. Verify denominator safety (`total > 0`).
2. Verify at least one single-bidder event exists before emitting records.
3. Log total suppliers evaluated vs flagged.

## Complexity

- Time: `O(N_bids)`
- Memory: `O(N_tenders + N_suppliers)`

## Evidence minimum schema

- `awards_total` (int)
- `awards_single_bidder` (int)
- `single_bidder_ratio` (float)
- `single_bidder_awarded_value` (float)
