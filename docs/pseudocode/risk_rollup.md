# Risk Roll-Up - Detailed Pseudocode

## Signal intent

Consolidate all indicator-level records into supplier-, tender-, and entity-level summaries while preserving traceability.

## Inputs

- `indicator_results` from `IND001..IND011`
- `tenders(tender_id, entity_id, ...)`

## Output tables

- `supplier_risk_summary`
- `tender_risk_summary`
- `entity_risk_summary`

## Normalization rules

1. Map risk levels to ordinal weights (`LOW=1`, `MEDIUM=2`, `HIGH=3`).
2. Preserve original indicator records unchanged.
3. Use evidence references rather than full evidence payload in summary rows.

## Subject mapping logic

- Supplier summary includes records with a direct supplier subject, supplier ids
  derivable from pair/group subjects, and `supplier_ids` found in network evidence.
- Directional association IDs `A->B` and conditional influence IDs `A<-B` map to
  both suppliers. Each emitted direction is a separate record, not a separate family.
- Tender summary includes direct tender subjects and tender ids found inside
  `evidence_json.tender_ids` or `evidence_json.event_ids`.
- Entity summary maps every source indicator to the distinct entities reached
  through its tender ids. One indicator record contributes at most once to the
  same entity, even when it references multiple tenders from that entity.

## Core pseudocode

```text
PROCEDURE BuildRiskRollups(indicator_results, tenders):
    INIT supplier_bucket = map<supplier_id, list<records>>()
    INIT tender_bucket = map<tender_id, list<records>>()

    FOR each record IN indicator_results:
        supplier_ids = extract_supplier_ids(record)
        FOR each sid IN supplier_ids:
            supplier_bucket[sid].append(record)

        tender_ids = extract_tender_ids(record)
        FOR each tid IN tender_ids:
            tender_bucket[tid].append(record)

    supplier_summary = SummarizeBucket(supplier_bucket)
    tender_summary = SummarizeBucket(tender_bucket)

    INIT tender_to_entity = map from tenders table
    INIT entity_bucket = map<entity_id, list<records>>()

    FOR each record IN indicator_results:
        entity_ids = empty set
        FOR each tender_id IN extract_tender_ids(record):
            entity_id = tender_to_entity[tender_id]
            IF not empty(entity_id):
                entity_ids.add(entity_id)

        FOR each entity_id IN entity_ids:
            entity_bucket[entity_id].append(record)

    entity_summary = SummarizeBucket(entity_bucket)

    RETURN supplier_summary, tender_summary, entity_summary


PROCEDURE SummarizeBucket(bucket):
    INIT out = []
    FOR each subject_id IN bucket:
        records = bucket[subject_id]

        indicator_count = size(records)
        max_risk_level = max_by_weight(records.risk_level)
        weighted_score = avg(level_weight(record.risk_level) * record.risk_score)
        indicator_codes = unique_sorted(records.indicator_code)

        APPEND {
            subject_id,
            indicator_count,
            max_risk_level,
            weighted_score,
            indicator_codes
        } to out

    RETURN sorted(out by [weighted_score desc, subject_id asc])
```

## Edge-case handling

1. Pair records without parseable ids: ignore for supplier roll-up and keep in base results only.
2. Records with malformed evidence JSON: skip tender extraction but keep record otherwise.
3. Tenders missing entity mapping: exclude from entity roll-up, keep supplier/tender summaries.

## Quality checks

1. Ensure no summary subject has zero indicator count.
2. Validate `max_risk_level` consistency with source records.
3. Compare roll-up totals with base indicator totals for sanity.

## Complexity

- Time: `O(N_indicator_records + N_summary_links)`
- Memory: `O(N_subject_buckets)`

## Evidence contract for summaries

`indicator_count` counts records, whereas `indicator_codes` lists unique families.
`weighted_score` is a severity-weighted screening index (nominal range 0–300), not
a probability. Supplier signals without tender references remain supplier-only;
tender-subject signals are not automatically propagated to suppliers.

Summary outputs keep compact columns only:

- `subject_id`
- `indicator_count`
- `max_risk_level`
- `weighted_score`
- `indicator_codes`
