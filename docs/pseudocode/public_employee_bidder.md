# Public Employee Bidder Overlap - Detailed Pseudocode

## Signal intent

Detect identity overlap between bidder ids and employment records, then measure recurrence and award exposure.

## Inputs

- `bids`
- `employment(person_id, employer_name, role_name, entry_date, salary)`
- `profile`

## Output record

`IND010_PUBLIC_EMPLOYEE_BIDDER` at `subject_type = supplier`

## Matching approach

- Exact id match after canonical normalization.
- Optional future extension: deterministic alias maps.

## Derived metrics per matched id

- `participations = distinct tenders where id appears in bids`
- `wins = awarded events`
- `awarded_value = sum of awarded value`
- context excerpts: employers and roles

## Core pseudocode

```text
PROCEDURE DetectPublicEmployeeBidderOverlap(bids, employment, profile, run_ts):
    INIT results = []

    INIT employment_by_person = map<person_id, list<employment_rows>>()
    FOR each row IN employment:
        employment_by_person[row.person_id].append(row)

    INIT participation_set = map<id, set<tender_id>>()
    INIT wins_count = map<id, int>(default=0)
    INIT awarded_value = map<id, float>(default=0)

    FOR each bid IN bids:
        id = bid.bidder_id
        IF id NOT IN employment_by_person:
            CONTINUE

        participation_set[id].add(bid.tender_id)

        IF bid.awarded_flag == true:
            wins_count[id] += 1
            awarded_value[id] += bid.awarded_value

    FOR each id IN participation_set:
        participations = size(participation_set[id])
        IF participations < profile.employee_bidder_min_participations:
            CONTINUE

        wins = wins_count[id]

        IF wins in high band:
            risk_level = HIGH
            risk_score = f_high_employee_overlap(participations, wins)
        ELSE:
            risk_level = MEDIUM
            risk_score = f_medium_employee_overlap(participations, wins)

        employers = unique_sorted(first_n(employment_by_person[id].employer_name, limit=3))
        roles = unique_sorted(first_n(employment_by_person[id].role_name, limit=3))

        evidence = {
            participations: participations,
            wins: wins,
            awarded_value: awarded_value[id],
            employer_context: employers,
            role_context: roles,
            tender_ids: sorted(participation_set[id])
        }

        APPEND standardized indicator record to results

    RETURN sort_desc(results, by=[risk_score, subject_id])
```

## Edge-case handling

1. Reused ids across distinct persons: flag as data quality risk in governance logs.
2. Employment rows without role/employer text: keep record with partial context.
3. Zero awarded value wins: still count wins.

## Quality checks

1. Validate id normalization consistency across sources.
2. Track match coverage rate (`matched_bidders / total_bidders`).
3. Monitor false positives from malformed ids.

## Complexity

- Time: `O(N_bids + N_employment)`
- Memory: `O(N_matched_ids + N_employment)`

## Evidence minimum schema

- `participations`, `wins`, `awarded_value`
- `employer_context`, `role_context`
- `tender_ids`
