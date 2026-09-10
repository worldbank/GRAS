# 02. Data Contract

## 1. Purpose

This contract defines the minimum semantic interface required to run the method consistently.

The contract is intentionally strict on required columns and intentionally flexible on optional enrichment fields.

This candidate uses contract `2.0.0`. Each CSV must retain its required headers.
`tenders` and `bids` must contain rows; `sanctions` and `employment` may have only
headers. An empty auxiliary file means no records supplied, not proof that no
sanctions or employment relationships exist. Missing files or headers are errors.

## 2. Input tables

## 2.1 `tenders`

Required columns:

- `tender_id` (string, non-empty)
- `entity_id` (string, non-empty)
- `modality` (string)
- `publication_date` (date or parseable text)
- `participant_count` (integer >= 0)

Recommended optional columns:

- `procurement_type`
- `currency_code`
- `year`

Validation rules:

- `tender_id` should be unique in the table; adopters must check this upstream.
- `participant_count` should be consistent with bids-derived participant count when both are available.
- rows with empty `tender_id` or `entity_id` are excluded by the reference normalizer.

## 2.2 `bids`

Required columns:

- `bid_id` (string, preferably unique)
- `tender_id` (string)
- `bidder_id` (string)
- `bidder_name` (string)
- `awarded_flag` (boolean-like)
- `awarded_value` (numeric-like)
- `submission_date` (date or parseable text)
- `fiscal_address` (string)

Recommended optional columns:

- `award_id`
- `contract_id`
- `line_item_count`
- `bid_amount`

Validation rules:

- rows with empty `tender_id` or `bidder_id` are invalid for method execution.
- `awarded_flag` coercion must be deterministic.
- invalid nonblank numeric values in `awarded_value` stop execution before outputs are written; blank values default to zero.
- remove duplicated source rows upstream: distinct awarded input rows may represent separate awards or lots and their amounts are additive.

## 2.3 `sanctions`

Required columns:

- `bidder_id` (string)
- `sanction_start` (date)
- `sanction_end` (date)
- `sanction_type` (string)

Validation rules:

- `sanction_start <= sanction_end`.
- invalid windows are excluded by the reference normalizer.

## 2.4 `employment`

Required columns:

- `person_id` (string)
- `employer_name` (string)
- `role_name` (string)
- `entry_date` (date)
- `salary` (numeric-like)

Validation rules:

- `person_id` must follow same normalization strategy as `bidder_id`.

## 3. Canonical normalization

## 3.1 Identifier normalization

- trim and remove whitespace,
- preserve other characters,
- preserve case in the baseline implementation,
- apply the same source-specific alias or casing transformation before all four
  input files when local identifiers are not case-stable.

## 3.2 Date normalization

Accepted baseline formats:

- `YYYY-MM-DD`
- `YYYY/MM/DD`
- `MM/DD/YYYY`
- `DD/MM/YYYY`
- timestamp variants convertible to date

Unparseable dates become null. Sanction rows with invalid dates are excluded; other
date-dependent indicators skip records they cannot evaluate.

Slash-separated dates are parsed as `MM/DD/YYYY` before `DD/MM/YYYY`. Adopters
with ambiguous local dates should convert them to ISO `YYYY-MM-DD` upstream.

## 3.3 Numeric normalization

- use a decimal point with no currency symbols, spaces within numbers, or grouping separators;
- an optional sign and scientific exponent are accepted: `1234.56`, `-2.5`, and `1e3`;
- `1.234,56`, `1,234.56`, currency-prefixed values, booleans, nonnumeric markers, NaN and infinity are rejected;
- convert local formats upstream using a known locale; do not guess separator meaning;
- blank or null numeric values default to zero and must be assessed upstream;
- integer counts must be whole numbers (`2.0` is accepted, `1.6` is rejected).

Nonblank invalid or nonfinite numbers raise an error before the pipeline writes
outputs. Monetary values are stored as finite floating-point values and are
analytical proxies, not an accounting ledger.

## 3.4 Address normalization

- uppercase,
- remove punctuation,
- collapse multiple spaces,
- preserve alphanumeric tokens.

## 4. Indicator output contract

Columns:

- `indicator_code`
- `indicator_name`
- `subject_type`
- `subject_id`
- `risk_level`
- `risk_score`
- `evidence_json`
- `run_timestamp`

Constraints:

- `indicator_code` belongs to known catalog.
- `risk_level ∈ {LOW, MEDIUM, HIGH}`.
- `risk_score` must be numeric and bounded by implementation scale.
- `evidence_json` must be valid JSON string.

IND005 uses directional `subject_id` values such as `A->B`. Its evidence records
award-event supports, `event_basis = award`, and `conviction_status`. Conviction is
a finite number or JSON null with status `infinite`/`undefined`; the old large
numeric sentinel is not used. Threshold tests occur before metric rounding.

Generated CSVs use UTF-8, comma delimiters and LF line endings. Monetary sums are
reproducible in the pipeline because normalized rows are sorted before calculation.

## 5. Summary output contract

Applicable to supplier, tender, and entity summaries:

- `subject_id`
- `indicator_count`
- `max_risk_level`
- `weighted_score`
- `indicator_codes`

`indicator_count` is the number of emitted records, not the number of unique
families in `indicator_codes`. Accepted association directions contribute separately.
`weighted_score` is an ordinal screening index with nominal range 0–300, not a
percentage. See [roll-up mapping](../pseudocode/risk_rollup.md) for attribution limits.

Constraints:

- `indicator_count >= 1`
- `max_risk_level ∈ {LOW, MEDIUM, HIGH}`

## 6. Data quality controls

Recommended controls before execution:

1. Missingness report per required field.
2. Duplicate ratio by primary id assumptions.
3. Parse success rate for dates and numerics.
4. Invalid boolean coercion count.
5. Null or generic-marker address ratio.

## 7. Compatibility notes

To adapt another context:

1. map local columns to contract columns,
2. preserve semantics,
3. document transformations,
4. run controlled + historical smoke validations.

## 8. Versioning recommendation

Maintain contract version metadata in run logs:

- contract version,
- profile version,
- indicator package version,
- execution timestamp.

The reference runner writes these values, raw input row counts, input SHA-256
hashes, and output row counts to `run_metadata.json`. It does not currently emit
normalized-row or field-level parse-failure counters; adopters should calculate
those as part of upstream data-quality validation.
