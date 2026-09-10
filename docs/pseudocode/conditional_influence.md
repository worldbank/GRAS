# Conditional Influence - Detailed Pseudocode

## Signal intent

Detect pairwise structures where supplier A's win probability increases materially when supplier B participates.

## Inputs

- `bids`
- `profile`

## Output record

`IND007_CONDITIONAL_INFLUENCE` at `subject_type = pair`

## Probability definitions

For ordered pair `(A <- B)`:

- `P(A wins) = wins_A / total_events`
- `P(A wins | B participates) = wins_A_in_events_with_B / events_with_B`
- `influence_gap = P(A wins | B participates) - P(A wins)`
- `influence_magnitude = P(A wins | B participates) / P(A wins)` (guarded)

## Core pseudocode

```text
PROCEDURE DetectConditionalInfluence(bids, profile, run_ts):
    INIT results = []

    BUILD events_by_supplier
    BUILD wins_by_supplier
    total_events = number of distinct tenders

    suppliers = sorted list of supplier ids

    FOR each ordered pair (A, B), A != B:
        baseline = size(wins_by_supplier[A]) / max(1,total_events)

        events_with_B = events_by_supplier[B]
        IF size(events_with_B) == 0:
            CONTINUE

        wins_A_with_B = size(intersection(wins_by_supplier[A], events_with_B))
        conditional = wins_A_with_B / size(events_with_B)
        influence_gap = conditional - baseline

        IF baseline > profile.influence_baseline_max:
            CONTINUE
        IF conditional < profile.influence_conditional_min:
            CONTINUE
        IF influence_gap < profile.influence_gap_min:
            CONTINUE

        magnitude = conditional / baseline if baseline > 0 else LARGE_NUMBER

        IF magnitude in high band:
            risk_level = HIGH
            risk_score = f_high_influence(magnitude, influence_gap)
        ELSE:
            risk_level = MEDIUM
            risk_score = f_medium_influence(magnitude, influence_gap)

        evidence = {
            target_supplier: A,
            conditioning_supplier: B,
            baseline_win_probability: baseline,
            conditional_win_probability: conditional,
            influence_gap: influence_gap,
            influence_magnitude: magnitude,
            conditioning_event_count: size(events_with_B),
            tender_ids: sorted(events_with_B)
        }

        APPEND standardized indicator record to results

    RETURN sort_desc(results, by=[risk_score, subject_id])
```

## Edge-case handling

1. `baseline = 0`: magnitude uses sentinel and should be interpreted with gap and support jointly.
2. Very small `events_with_B`: require optional minimum support gate.
3. High baseline suppliers: filtered out to emphasize conditional uplift, not absolute strength.

## Quality checks

1. Ensure probability bounds `[0,1]`.
2. Track distribution of conditioning event counts.
3. Inspect top scores for support adequacy.

## Complexity

- Time: `O(N_suppliers^2 + N_bids)`
- Memory: `O(N_supplier_event_sets)`

## Evidence minimum schema

- `baseline_win_probability`
- `conditional_win_probability`
- `influence_gap`
- `influence_magnitude`
- `conditioning_event_count`
- `tender_ids`
