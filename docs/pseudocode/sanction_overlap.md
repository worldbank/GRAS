# Sanction Overlap - Detailed Pseudocode

## Signal intent

Detect awarded bid rows whose submission date falls inside a sanction window.
Submission date is a proxy; it does not establish the date of the award itself.

## Inputs

- `bids(bidder_id, tender_id, awarded_flag, submission_date, awarded_value, ...)`
- `sanctions(bidder_id, sanction_start, sanction_end, sanction_type)`

## Output record

`IND009_SANCTION_OVERLAP` at `subject_type = supplier`

## Matching logic

A bid contributes to overlap evidence when:

1. `awarded_flag = true`
2. `bidder_id` matches sanctions table id
3. `submission_date` falls inside `[sanction_start, sanction_end]`

Each awarded input row contributes at most once, regardless of the number of
matching sanction windows. Separate input rows remain separate awards/lots;
source-row deduplication is an upstream responsibility.

## Core pseudocode

```text
PROCEDURE DetectSanctionOverlap(bids, sanctions, run_ts):
    INIT results = []

    INIT sanctions_by_supplier = map<supplier_id, list<sanction_rows>>()
    FOR each sanction_row IN sanctions:
        sanctions_by_supplier[sanction_row.bidder_id].append(sanction_row)

    INIT overlap_count = map<supplier_id, int>(default=0)
    INIT overlap_value = map<supplier_id, float>(default=0)
    INIT overlap_tenders = map<supplier_id, set<tender_id>>()

    FOR each bid IN bids:
        IF bid.awarded_flag != true:
            CONTINUE

        supplier = bid.bidder_id
        FOR each sanction_row IN sanctions_by_supplier[supplier]:
            IF date_overlap(bid.submission_date, sanction_row.start, sanction_row.end):
                overlap_count[supplier] += 1
                overlap_value[supplier] += bid.awarded_value
                overlap_tenders[supplier].add(bid.tender_id)
                BREAK the sanction loop for this bid

    FOR each supplier IN overlap_count:
        count = overlap_count[supplier]

        IF count >= 2:
            risk_level = HIGH
        ELSE:
            risk_level = MEDIUM
        risk_score = 75 + min(20, count * 8)

        evidence = {
            overlap_awards: count,
            overlap_value_proxy: overlap_value[supplier],
            tender_ids: sorted(overlap_tenders[supplier])
        }

        APPEND standardized indicator record to results

    RETURN sort_desc(results, by=[risk_score, subject_id])
```

## Edge-case handling

1. Missing submission date: cannot evaluate overlap, skip row.
2. Open-ended sanctions: require explicit end date in this baseline method.
3. Overlapping or duplicate sanctions do not duplicate an awarded row or its value.
4. A valid sanctions header without data rows produces no sanction indicators.

## Quality checks

1. Validate date parse success before overlap check.
2. Ensure non-negative value proxy.
3. Keep overlap reference slice for review.

## Complexity

- Time: `O(N_awarded_bids * avg_sanctions_per_supplier)`
- Memory: `O(N_sanctions + N_flagged_suppliers)`

## Evidence minimum schema

- `overlap_awards`
- `overlap_value_proxy`
- `tender_ids`
