# Top Loser Winner Links - Detailed Pseudocode

## Signal intent

Detect recurrent winner-to-top-loser links across events where a known top loser repeatedly appears while the same winner secures awards.

## Inputs

- `bids`
- `top_loser_set` (supplier ids flagged by IND002)
- `profile`

## Output record

`IND003_TOP_LOSER_WINNER_LINK` at `subject_type = pair`

## Required pre-processing

1. Build `participants_by_tender`.
2. Build `winners_by_tender`.
3. Limit evaluation to events containing at least one top loser.

## Derived metrics per pair `(winner, top_loser)`

- `recurrent_links = count(events where winner wins and top_loser participates)`
- `event_ids = list of linked events`
- `link_density = recurrent_links / events_with_top_loser_participation_for_winner`

## Core pseudocode

```text
PROCEDURE DetectTopLoserWinnerLinks(bids, top_loser_set, profile, run_ts):
    INIT results = []

    INIT participants_by_tender = map<tender_id, set<supplier_id>>()
    INIT winners_by_tender = map<tender_id, set<supplier_id>>()

    FOR each bid IN bids:
        participants_by_tender[bid.tender_id].add(bid.bidder_id)
        IF bid.awarded_flag == true:
            winners_by_tender[bid.tender_id].add(bid.bidder_id)

    INIT link_count = map<(winner, top_loser), int>(default=0)
    INIT link_events = map<(winner, top_loser), list<tender_id>>()
    INIT winner_top_loser_exposure = map<winner, int>(default=0)

    FOR each tender_id IN participants_by_tender:
        participants = participants_by_tender[tender_id]
        top_losers = [s IN participants WHERE s IN top_loser_set]
        IF size(top_losers) == 0:
            CONTINUE

        winners = winners_by_tender[tender_id]
        FOR each winner IN winners:
            winner_top_loser_exposure[winner] += 1
            FOR each tl IN top_losers:
                IF winner == tl:
                    CONTINUE
                key = (winner, tl)
                link_count[key] += 1
                link_events[key].append(tender_id)

    FOR each key=(winner, tl) IN link_count:
        recurrent_links = link_count[key]
        IF recurrent_links < profile.top_loser_winner_min_links:
            CONTINUE

        exposure = max(1, winner_top_loser_exposure[winner])
        link_density = recurrent_links / exposure

        IF recurrent_links is high and link_density is high:
            risk_level = HIGH
            risk_score = f_high_link(recurrent_links, link_density)
        ELSE:
            risk_level = MEDIUM
            risk_score = f_medium_link(recurrent_links, link_density)

        evidence = {
            winner_id: winner,
            top_loser_id: tl,
            recurrent_links: recurrent_links,
            winner_exposure_to_top_loser_events: exposure,
            link_density: link_density,
            tender_ids: unique_sorted(link_events[key])
        }

        APPEND standardized indicator record to results

    RETURN sort_desc(results, by=[risk_score, subject_id])
```

## Edge-case handling

1. Multiple winners in same event: evaluate each winner independently.
2. Winner also appears as top loser in another context: skip self-link only, keep cross-links.
3. Missing awards for event: event contributes to participant context but not to link count.

## Quality checks

1. Validate all `top_loser_id` are in `top_loser_set`.
2. Verify `recurrent_links <= winner_exposure`.
3. Keep event reference slices for manual spot-check.

## Complexity

- Time: `O(N_bids + N_event_winner_toploser_pairs)`
- Memory: `O(N_events + N_links)`

## Evidence minimum schema

- `winner_id`
- `top_loser_id`
- `recurrent_links`
- `winner_exposure_to_top_loser_events`
- `link_density`
- `tender_ids`
