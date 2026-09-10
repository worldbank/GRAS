# Typology 06 - Group Patterns

## 1. Objective

Detect recurrent multi-supplier structures with exclusivity, turn-taking, or dominance signatures.

## 2. Analytical rationale

Some behaviors emerge only at group level and are not visible in pair metrics alone.

## 3. Required fields

- `tender_id`
- `bidder_id`
- `awarded_flag`

## 4. Pattern subtypes

- `exclusivity`: recurring group closure.
- `turn_taking`: low-dispersion alternating wins.
- `dominance`: concentrated wins for one member within a recurring group.

## 5. Detection flow

1. Build event transactions from participant sets.
2. Count recurring groups in the baseline supported size range of three to five members.
3. For each group:

   - compute exclusivity ratio,
   - compute win-share distribution,
   - compute dispersion and dominance share.

4. Assign subtype and risk band.

## 6. Core metrics

- `recurrence`
- `exclusivity_ratio`
- `turn_taking_cv`
- `dominance_share`

## 7. Evidence structure

- `pattern_type`
- `group_members`
- `group_size`
- `recurrence`
- `exclusivity_ratio`
- `turn_taking_cv`
- `dominance_share`
- `tender_ids`

## 8. Edge cases

1. Sparse group recurrence leads to unstable subtype assignment.
2. Near-tie dominance can flip subtype with small updates.
3. Missing award flags weaken turn-taking and dominance checks.

## 9. Adaptation levers

- group recurrence minimum,
- exclusivity high range,
- turn-taking dispersion cap,
- dominance share threshold.

## 10. Validation checklist

- subtype assignment deterministic,
- recurrence and subtype counts tracked by run,
- selected group cases reproducible from raw events.
