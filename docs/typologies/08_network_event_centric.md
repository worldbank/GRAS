# Typology 08 - Event-Centric Suspicious Network

## 1. Objective

Detect suspicious connected components in event-supplier graphs after filtering events by composition-based criteria.

## 2. Analytical rationale

Some risk patterns emerge as network structures rather than isolated pair events.

## 3. Required fields

- `tender_id`
- `bidder_id`
- `awarded_flag`
- top-loser and linked-winner sets from prior typologies

## 4. Event suspiciousness filters

Per event:

- minimum PF-like count,
- minimum PF-like share,
- presence of linked winner profile.

## 5. Detection flow

1. Build participants and winners by event.
2. Apply suspiciousness filters.
3. Build bipartite graph on filtered events.
4. Extract connected components.
5. Score components by size and edge structure.

## 6. Core metrics

Per component:

- `event_count`
- `supplier_count`
- `edge_count`
- `size_score`

## 7. Evidence structure

- `component_index`
- `event_ids`
- `supplier_ids`
- composition counts

## 8. Edge cases

1. No filtered events -> no network records.
2. Tiny fragments may have low interpretive value.
3. Duplicate participation edges should be deduplicated.

## 9. Adaptation levers

- minimum PF-like count/share,
- requirement strictness for linked winners,
- component size bands for risk assignment.

## 10. Validation checklist

- bipartite integrity of graph edges,
- deterministic component extraction,
- stable score ordering across reruns.
