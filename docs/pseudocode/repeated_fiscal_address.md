# Repeated Fiscal Address - Detailed Pseudocode

## Signal intent

Detect recurring address-sharing structures where multiple supplier ids use the same normalized fiscal address across events.

## Inputs

- `bids(tender_id, bidder_id, fiscal_address, awarded_flag, ...)`
- `profile`

## Output record

`IND011_REPEATED_FISCAL_ADDRESS` at `subject_type = tender`

## Address normalization baseline

1. Uppercase
2. Remove punctuation
3. Collapse whitespace
4. Optionally apply locale-specific normalization rules

## Derived metrics

For each `(tender_id, normalized_address)`:

- `supplier_count_at_event_address`
- `award_count_at_event_address`

Across events for each `normalized_address`:

- `address_event_count`
- `address_supplier_count`
- `address_award_count`

## Core pseudocode

```text
PROCEDURE DetectRepeatedFiscalAddress(bids, profile, run_ts):
    INIT results = []

    INIT suppliers_by_event_address = map<(tender,address), set<supplier_id>>()
    INIT awards_by_event_address = map<(tender,address), int>(default=0)

    FOR each bid IN bids:
        IF empty(bid.fiscal_address):
            CONTINUE

        addr = normalize_address(bid.fiscal_address)
        key = (bid.tender_id, addr)

        suppliers_by_event_address[key].add(bid.bidder_id)
        IF bid.awarded_flag == true:
            awards_by_event_address[key] += 1

    INIT address_events = map<address, set<tender_id>>()
    INIT address_suppliers = map<address, set<supplier_id>>()
    INIT address_awards = map<address, int>(default=0)
    INIT event_supplier_list = map<(tender,address), list<supplier_id>>()

    FOR each key=(tender, addr) IN suppliers_by_event_address:
        suppliers = suppliers_by_event_address[key]
        IF size(suppliers) < profile.repeated_address_min_suppliers:
            CONTINUE

        address_events[addr].add(tender)
        address_suppliers[addr].union_with(suppliers)
        address_awards[addr] += awards_by_event_address[key]
        event_supplier_list[key] = sorted(suppliers)

    FOR each addr IN address_events:
        events = address_events[addr]
        IF size(events) < profile.repeated_address_min_events:
            CONTINUE

        supplier_count = size(address_suppliers[addr])
        award_count = address_awards[addr]

        IF size(events) high and supplier_count high:
            risk_level = HIGH
            risk_score = f_high_repeated_address(size(events), supplier_count, award_count)
        ELSE:
            risk_level = MEDIUM
            risk_score = f_medium_repeated_address(size(events), supplier_count, award_count)

        FOR each tender IN events:
            evidence = {
                normalized_fiscal_address: addr,
                address_event_count: size(events),
                address_supplier_count: supplier_count,
                address_award_count: award_count,
                supplier_ids: event_supplier_list[(tender, addr)],
                tender_ids: sorted(events)
            }

            APPEND standardized indicator record to results

    RETURN sort_desc(results, by=[risk_score, subject_id])
```

## Edge-case handling

1. Shared corporate campuses may produce benign recurrence; preserve as risk indicator only.
2. Address variants with missing unit info: normalization may collapse distinct addresses.
3. Empty or generic-marker addresses: exclude early.

## Quality checks

1. Review top recurring addresses for normalization collisions.
2. Track ratio of distinct raw addresses to normalized addresses.
3. Maintain reference raw values for high-score cases.

## Complexity

- Time: `O(N_bids)`
- Memory: `O(N_event_address_keys + N_addresses)`

## Evidence minimum schema

- `normalized_fiscal_address`
- `address_event_count`
- `address_supplier_count`
- `address_award_count`
- `supplier_ids`
- `tender_ids`
