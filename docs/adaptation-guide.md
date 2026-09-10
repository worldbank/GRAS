# Adaptation Guide

## Purpose

This guide describes how to evaluate and adapt the generic GRAS reference package to another procurement context without silently changing the method.

## 1. Establish the use and governance boundary

Before technical work, document:

- the institutional decision the indicators will support;
- the authorized users and reviewers;
- the legal basis and permitted data uses;
- retention, access, and disclosure rules;
- the human-review and escalation process; and
- how affected data can be corrected or challenged.

The reference outputs are prioritization signals. They are not automatic findings or enforcement decisions.

## 2. Map source data to the contract

Create an explicit mapping from local source fields to the four logical inputs in the [data contract](methodology/02_data_contract.md). Preserve semantics, not just column names. In particular, confirm what counts as a tender, bidder, participation, award, contracting entity, sanction window, and identity match.

Keep extraction and transformation code outside the core typology modules. Record source-system versions, extraction dates, transformations, exclusions, and quality statistics. Do not commit operational or personal data to this repository.

## 3. Measure data quality before calibration

At minimum, measure:

- missing and duplicate identifiers;
- date and numeric parse success;
- award-flag consistency;
- tender-to-entity mapping coverage;
- bidder identity stability across sources;
- address normalization collisions; and
- sanctions and employment coverage periods.

The reference normalizer excludes selected rows with missing identifiers or invalid sanction dates. Blank numeric fields default to zero; invalid nonblank numeric values stop execution. Supply canonical decimal-point values without currency/group separators, optionally using scientific notation. This validation does not replace an upstream data-quality process.

## 4. Create a versioned profile

Copy [`parameter_profiles.yaml`](../src/gras/config/parameter_profiles.yaml), add a new top-level profile name, and change thresholds only after reviewing distributions on representative historical periods. Update `profile_version` whenever any value changes.

Run the custom profile with:

```bash
gras \
  --tenders /path/to/tenders.csv \
  --bids /path/to/bids.csv \
  --sanctions /path/to/sanctions.csv \
  --employment /path/to/employment.csv \
  --profile /path/to/local_profiles.yaml \
  --profile-name local_v1 \
  --out /path/to/output
```

Adjust minimum-volume gates first, then concentration or probability thresholds. Avoid tuning against a single period or optimizing only for the number of flags.

## 5. Validate on three layers

### Functional validation

Use controlled cases where expected behavior is known. Add tests for boundary values, missing fields, duplicate rows, directionality, ordering, and cross-entity roll-ups.

### Historical validation

Run representative time windows and inspect indicator distributions, overlap among families, stability, and explainability. Compare versions using the same frozen input snapshots.

### Operational validation

Test the complete review process with authorized users: access, triage, evidence retrieval, false-positive handling, correction, audit trail, and escalation. A successful pipeline run alone is not proof that an operational deployment is ready.

## 6. Change algorithms only when necessary

If local semantics require an algorithm change:

1. state the methodological reason;
2. update the indicator pseudocode and typology documentation;
3. add a failing test that represents the intended behavior;
4. implement the smallest coherent change;
5. update the package and contract versions when compatibility changes; and
6. compare results against the previous version on frozen inputs.

## 7. Release and monitor

For every approved release, retain the code version, profile, data-contract version, input snapshot identifiers or hashes, validation record, and change log. Monitor data drift, flag volumes, score distributions, subject churn, and source-schema changes. Recalibration should follow the same review and approval process as the initial profile.
