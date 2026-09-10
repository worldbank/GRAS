# Top Loser - Detailed Pseudocode

## Signal intent

Detect suppliers with sustained participation volume and persistently low success rates.

## Inputs

- `bids(bid_id, tender_id, bidder_id, awarded_flag, awarded_value, ...)`
- `profile`

## Output record

`IND002_TOP_LOSER` at `subject_type = supplier`

## Required pre-processing

1. Normalize supplier ids.
2. Convert award flags to boolean.
3. Remove rows without supplier or tender id.

## Derived metrics per supplier

- `participations = count(distinct tender_id)`
- `wins = count(distinct tender_id where awarded_flag = true)`
- `success_rate = wins / participations`
- `awarded_value = sum(awarded_value where awarded_flag = true)`

## Core pseudocode

```text
PROCEDURE DetectTopLoser(bids, profile, run_ts):
    INIT results = []

    INIT participation_set = map<supplier_id, set<tender_id>>()
    INIT wins_set = map<supplier_id, set<tender_id>>()
    INIT awarded_value = map<supplier_id, float>(default=0)

    FOR each bid IN bids:
        supplier = bid.bidder_id
        tender = bid.tender_id
        participation_set[supplier].add(tender)

        IF bid.awarded_flag == true:
            wins_set[supplier].add(tender)
            awarded_value[supplier] += bid.awarded_value

    FOR each supplier IN participation_set:
        participations = size(participation_set[supplier])
        IF participations < profile.top_loser_min_participations:
            CONTINUE

        wins = size(wins_set[supplier])
        success_rate = wins / participations

        IF success_rate > profile.top_loser_success_medium:
            CONTINUE

        IF success_rate <= profile.top_loser_success_high:
            risk_level = HIGH
            risk_score = f_high_top_loser(participations, success_rate)
        ELSE:
            risk_level = MEDIUM
            risk_score = f_medium_top_loser(participations, success_rate)

        evidence = {
            participations: participations,
            wins: wins,
            success_rate: success_rate,
            awarded_value: awarded_value[supplier]
        }

        APPEND standardized indicator record to results

    RETURN sort_desc(results, by=[risk_score, subject_id])
```

## Recommended scoring behavior

- Reward persistence (more participations).
- Increase severity when success rate approaches zero.

## Edge-case handling

1. Participations with no winners in dataset: success remains zero.
2. Suppliers with one anomalous win after long losing sequence: remain eligible if within gate.
3. Multi-award events: count wins by distinct event.

## Quality checks

1. Ensure `participations >= wins` always.
2. Check outliers where participation is extreme but success near medium threshold.
3. Keep count of filtered suppliers by each gate.

## Complexity

- Time: `O(N_bids)`
- Memory: `O(N_suppliers + N_supplier_tender_links)`

## Evidence minimum schema

- `participations` (int)
- `wins` (int)
- `success_rate` (float)
- `awarded_value` (float)
