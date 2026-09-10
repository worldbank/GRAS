# Co-Award Pairs - Detailed Pseudocode

## Signal intent

Detect supplier pairs that repeatedly receive awards together in constrained-competition events.

## Inputs

- `bids`
- `profile`

## Output record

`IND004_COAWARD_PAIRS` at `subject_type = pair`

## Universe strategy

1. Build participant set per event.
2. Build winner set per event.
3. Optionally restrict to event size band for stronger comparability.

## Derived metrics per pair `(A, B)`

- `events_together`: number of events where A and B both participate.
- `co_awards`: number of events where A and B both win.
- `co_award_rate = co_awards / events_together`.
- `value_proxy`: sum of awarded values from events where both win.
- `tender_ids`: events supporting co-award evidence.

## Core pseudocode

```text
PROCEDURE DetectCoAwardPairs(bids, profile, run_ts):
    INIT results = []

    INIT participants_by_tender = map<tender_id, set<supplier_id>>()
    INIT winners_by_tender = map<tender_id, set<supplier_id>>()
    INIT awarded_value_by_tender = map<tender_id, float>(default=0)

    FOR each bid IN bids:
        tender = bid.tender_id
        supplier = bid.bidder_id
        participants_by_tender[tender].add(supplier)

        IF bid.awarded_flag == true:
            winners_by_tender[tender].add(supplier)
            awarded_value_by_tender[tender] += bid.awarded_value

    INIT events_together = map<(A,B), int>(default=0)
    INIT co_awards = map<(A,B), int>(default=0)
    INIT value_proxy = map<(A,B), float>(default=0)
    INIT tender_refs = map<(A,B), list<tender_id>>()

    FOR each tender IN participants_by_tender:
        participants = sorted(participants_by_tender[tender])
        FOR each unordered pair (A,B) in combinations(participants, 2):
            events_together[(A,B)] += 1

        winners = sorted(winners_by_tender[tender])
        FOR each unordered pair (A,B) in combinations(winners, 2):
            co_awards[(A,B)] += 1
            value_proxy[(A,B)] += awarded_value_by_tender[tender]
            tender_refs[(A,B)].append(tender)

    FOR each pair=(A,B) IN events_together:
        together = events_together[pair]
        IF together < profile.coaward_min_events_together:
            CONTINUE

        co = co_awards[pair]
        IF co == 0:
            CONTINUE

        rate = co / together
        IF rate < profile.coaward_rate_medium:
            CONTINUE

        IF rate >= profile.coaward_rate_high AND co >= profile.coaward_min_events_together:
            risk_level = HIGH
            risk_score = f_high_coaward(co, rate)
        ELSE:
            risk_level = MEDIUM
            risk_score = f_medium_coaward(co, rate)

        evidence = {
            supplier_a: A,
            supplier_b: B,
            events_together: together,
            co_awards: co,
            co_award_rate: rate,
            value_proxy: value_proxy[pair],
            tender_ids: unique_sorted(tender_refs[pair])
        }

        APPEND standardized indicator record to results

    RETURN sort_desc(results, by=[risk_score, subject_id])
```

## Edge-case handling

1. Events with one or zero winners: cannot form co-award pair.
2. Events with many winners: keep logic but consider profile narrowing.
3. Sparse pairs with high rate from tiny support: blocked by minimum together gate.

## Quality checks

1. `co_awards <= events_together` for every pair.
2. Rate bounded in `[0,1]`.
3. Value proxy non-negative.

## Complexity

- Time: `O(sum_t C(P_t,2) + sum_t C(W_t,2))`
- Memory: `O(N_pairs)`

## Evidence minimum schema

- `supplier_a`
- `supplier_b`
- `events_together`
- `co_awards`
- `co_award_rate`
- `value_proxy`
- `tender_ids`
