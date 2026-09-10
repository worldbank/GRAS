# Typology 03 - Top Loser Winner Links

## 1. Objective

Identify recurrent links between specific winners and suppliers already flagged as top losers.

## 2. Analytical rationale

A repeated winner-top-loser pattern may reveal stable relational structure in event outcomes and participant composition.

## 3. Required fields

From `bids`:

- `tender_id`
- `bidder_id`
- `awarded_flag`

From indicator outputs:

- `top_loser_set` from Typology 02

## 4. Derived metrics

For each `(winner, top_loser)` pair:

- `recurrent_links`
- `winner_exposure_to_top_loser_events`
- `link_density`

## 5. Detection flow

1. Build event participants and winners.
2. Restrict to events containing at least one top loser.
3. Build winner-to-top-loser pairs per event.
4. Count recurrence and exposure.
5. Apply minimum link gate and risk assignment.

## 6. Risk assignment guidance

- `HIGH`: high recurrence and high density.
- `MEDIUM`: recurrence above entry gate with moderate density.

## 7. Evidence structure

- `winner_id`
- `top_loser_id`
- `recurrent_links`
- `winner_exposure_to_top_loser_events`
- `link_density`
- `tender_ids`

## 8. Edge cases

1. Winners lists with multiple entities require per-winner evaluation.
2. Self-links (`winner == top_loser`) must be excluded.
3. Sparse exposure can create unstable densities.

## 9. Adaptation levers

- minimum recurrent links,
- minimum link density,
- weighting of recurrence vs density in score.

## 10. Validation checklist

- `recurrent_links <= winner_exposure`.
- all `top_loser_id` values belong to top-loser input set.
- selected event ids reproduce pair formation.
