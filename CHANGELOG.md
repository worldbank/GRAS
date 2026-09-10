# Changelog

## Unreleased — 0.1.0rc1 candidate

This package has not had an institutional public release. The earlier `0.1.0`
label and August 2026 date described preparation, not an approved release.

### Corrections following internal review

- IND005 now uses award-event sets for joint and marginal supports, evaluates
  `A->B` and `B->A` independently, and calculates confidence from antecedent
  award support. IND004 still controls which pairs are considered. Infinite or
  undefined conviction is JSON null with an explicit status, not `999999`.
- IND009 counts each awarded input row at most once across overlapping sanctions.
  Multiple award/lot rows remain additive; source-row duplicates require upstream
  deduplication. Submission date remains the documented temporal proxy.
- Group evidence references are sorted. The pipeline canonicalizes normalized
  row order so reordered equivalent inputs yield identical analytical CSVs;
  raw-input hashes correctly change when file bytes change.
- Generated CSVs use explicit LF line endings across supported platforms.
- Numeric inputs require finite decimal-point values, optionally with a scientific
  exponent. Ambiguous separators, currency prefixes and invalid nonblank strings
  fail instead of being silently changed. Blank values retain the zero default;
  fractional integer counts are rejected instead of rounded.
- Sanctions and employment inputs may have zero rows but must have valid headers.
  Core tenders/bids inputs still require rows.
- Added regression cases, updated synthetic outputs and aligned methodology,
  provenance, local documentation links and unreleased citation metadata.

### Compatibility and expected output impact

Contract `2.0.0` replaces the earlier candidate's `1.0.0`: directional pair IDs,
conviction representation and strict numeric parsing are incompatible semantic
changes. Package `0.1.0rc1` identifies this unreleased candidate. The `balanced`
profile remains `1.0.0`; thresholds are unchanged, but corrected algorithms can
change which records pass them. Consumers must not compare scores across the two
candidates without rerunning the same inputs.

On the supplied synthetic example, IND005 emits two directional rules instead of
one unordered pair. Other indicator-family counts remain unchanged. The base
indicator table therefore contains 19 rows rather than 18, and affected summary
counts/scores change. Overlap deduplication affects the added regression scenario;
the synthetic example contains no overlapping sanctions. The four source CSVs
remain unchanged.

### Preparation inherited from the earlier candidate

- Existing know-how kit adapted into an installable reference package with 11
  analytical families and supplier, tender and entity summaries.
- Data contract, parameter profile, input hashes, row counts and execution metadata.
- Documentation, synthetic fixtures, tests, CI and World Bank open-source models.
- Earlier preparation corrected conditional-influence directionality, network
  propagation to summaries and repeated attribution of a source record to the
  same entity. These changes are part of the proposed baseline, not a claim of
  equivalence to every operational country implementation.

Final copyright, software attribution, repository destination, release date and
publication approval remain institutional release decisions. They do not need to
be invented to submit a reviewable PR.
