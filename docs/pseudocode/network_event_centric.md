# Event-Centric Suspicious Network - Detailed Pseudocode

## Signal intent

Detect suspicious connected components in an event-supplier bipartite graph using composition-based event filters.

## Inputs

- `bids`
- `top_loser_set`
- `top_loser_winner_set`
- `profile`

## Output record

`IND008_EVENT_CENTRIC_NETWORK` at `subject_type = network_component`

## Event suspiciousness criteria

Per event:

- `pf_count >= profile.network_min_pf_count`
- `pf_share >= profile.network_min_pf_share`
- at least one winner appears in `top_loser_winner_set`

## Core graph model

- Bipartite nodes:
- Event nodes: `E:tender_id`
- Supplier nodes: `S:bidder_id`
- Edges connect supplier participation in suspicious events.

## Core pseudocode

```text
PROCEDURE DetectEventCentricNetwork(bids, top_loser_set, top_loser_winner_set, profile, run_ts):
    INIT results = []

    BUILD participants_by_tender
    BUILD winners_by_tender

    INIT suspicious_events = set()

    FOR each tender IN participants_by_tender:
        participants = participants_by_tender[tender]
        winners = winners_by_tender[tender]

        pf_count = count(s IN participants WHERE s IN top_loser_set)
        pf_share = pf_count / max(1, size(participants))
        has_linked_winner = exists(w IN winners WHERE w IN top_loser_winner_set)

        IF pf_count >= min_pf_count AND pf_share >= min_pf_share AND has_linked_winner:
            suspicious_events.add(tender)

    BUILD bipartite adjacency on suspicious_events:
        E:tender <-> S:supplier for each participation

    components = connected_components(adjacency)

    idx = 0
    FOR each component IN sort_desc(components, by=size):
        idx += 1

        event_ids = nodes in component with prefix E:
        supplier_ids = nodes in component with prefix S:
        IF size(event_ids)==0 OR size(supplier_ids)==0:
            CONTINUE

        edge_count = count_component_edges(component)
        size_score = size(event_ids) + size(supplier_ids)

        IF size_score in high band:
            risk_level = HIGH
            risk_score = f_high_component(size_score, edge_count)
        ELSE:
            risk_level = MEDIUM
            risk_score = f_medium_component(size_score, edge_count)

        evidence = {
            component_index: idx,
            event_count: size(event_ids),
            supplier_count: size(supplier_ids),
            edge_count: edge_count,
            event_ids: sorted(event_ids),
            supplier_ids: sorted(supplier_ids)
        }

        APPEND standardized indicator record to results

    RETURN results
```

## Edge-case handling

1. No suspicious events: return empty list.
2. Single-node fragments: discard unless both event and supplier sides are present.
3. Repeated duplicate edges: deduplicate by `(event, supplier)`.

## Quality checks

1. Verify bipartite integrity (`E:` only connects to `S:`).
2. Ensure component metrics are deterministic for same input.
3. Track suspicious-event ratio vs total events.

## Complexity

- Event filter stage: `O(N_bids)`
- Graph build: `O(N_edges)`
- Component extraction: `O(N_nodes + N_edges)`

## Evidence minimum schema

- `component_index`
- `event_count`, `supplier_count`, `edge_count`
- `event_ids`, `supplier_ids`
