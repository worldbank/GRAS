# Group Patterns - Detailed Pseudocode

## Signal intent

Detect recurrent group structures suggesting exclusivity, turn-taking, or dominance in multi-participant events.

## Inputs

- `bids`
- `profile`

## Output record

`IND006_GROUP_PATTERNS` at `subject_type = group`

## Pattern families

1. **Exclusivity**: a recurring group appears with strong closure around the same members.
2. **Turn-taking**: group members alternate wins with low dispersion.
3. **Dominance**: one member captures disproportionate win share while others recurrently co-appear.

## Core derived data

- `transactions = participants per tender` (group mining universe)
- `group_recurrence = count(transaction occurrences)`
- `events_any(group)` and `events_full(group)`
- `win_distribution(group)` over `events_full`

## Core pseudocode

```text
PROCEDURE DetectGroupPatterns(bids, profile, run_ts):
    INIT results = []

    BUILD participants_by_tender
    BUILD winners_by_tender

    transactions = [sorted(participants) FOR each tender IF 3 <= size(participants) <= 5]
    group_counts = frequency(transactions)

    FOR each group IN group_counts:
        recurrence = group_counts[group]
        IF recurrence < profile.group_min_recurrence:
            CONTINUE

        events_any = tenders where at least one group member appears
        events_full = tenders where all group members appear
        exclusivity_ratio = size(events_full) / max(1, size(events_any))

        win_counter = map<member, int>(default=0)
        FOR each tender IN events_full:
            FOR each winner IN winners_by_tender[tender]:
                IF winner IN group:
                    win_counter[winner] += 1

        total_group_wins = sum(win_counter.values)
        win_share_per_member = [win_counter[m]/max(1,total_group_wins) for m in group]

        cv = coefficient_of_variation(win_share_per_member)
        dominance_share = max(win_share_per_member)

        pattern_type = NONE
        IF exclusivity_ratio >= profile.group_exclusivity_high:
            pattern_type = EXCLUSIVITY
            risk_level = HIGH
            risk_score = f_exclusivity(recurrence, exclusivity_ratio)
        ELSE IF cv <= profile.group_turn_taking_cv AND total_group_wins high relative to events_full:
            pattern_type = TURN_TAKING
            risk_level = MEDIUM
            risk_score = f_turn_taking(recurrence, cv)
        ELSE IF dominance_share >= profile.group_dominance_share:
            pattern_type = DOMINANCE
            risk_level = MEDIUM
            risk_score = f_dominance(recurrence, dominance_share)

        IF pattern_type is NONE:
            CONTINUE

        evidence = {
            pattern_type: pattern_type,
            group_members: group,
            group_size: size(group),
            recurrence: recurrence,
            exclusivity_ratio: exclusivity_ratio,
            turn_taking_cv: cv,
            dominance_share: dominance_share,
            tender_ids: sorted(events_full)
        }

        APPEND standardized indicator record to results

    RETURN sort_desc(results, by=[risk_score, subject_id])
```

## Edge-case handling

1. Groups with recurrence only once: discard.
2. Zero win events in full-group set: keep only if exclusivity itself is strong.
3. Ties in dominance: preserve max share and include full distribution in evidence.

## Quality checks

1. Verify `events_full ⊆ events_any`.
2. Validate dispersion calculation stability for small groups.
3. Keep group-size-specific diagnostics (size 3 vs size 4/5).

## Complexity

- Mining stage: depends on transaction cardinality and the three-to-five-member limit.
- Typical bounded implementation: manageable for event sizes 3-5.

## Evidence minimum schema

- `pattern_type`
- `group_members`, `group_size`
- `recurrence`
- `exclusivity_ratio`, `turn_taking_cv`, `dominance_share`
- `tender_ids`
