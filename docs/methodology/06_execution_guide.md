# 06. Execution Guide

## 1. Scope

This guide describes offline installation, execution, validation, and interpretation for the GRAS reference package.

## 2. Prerequisites

- Python 3.10 or later
- CSV inputs matching the [data contract](02_data_contract.md)
- File-system write access for the output directory

No database, network service, or credentials are required.

## 3. Installation

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## 4. Execution command

```bash
gras \
  --tenders /path/to/tenders.csv \
  --bids /path/to/bids.csv \
  --sanctions /path/to/sanctions.csv \
  --employment /path/to/employment.csv \
  --out /path/to/output \
  --profile-name balanced
```

Use `--profile /path/to/profiles.yaml` with `--profile-name NAME` for a custom profile file. Use `--run-timestamp 2026-01-01T00:00:00Z` only when a fixed timestamp is needed for exact reproducibility; otherwise the runner records the current UTC time.

## 5. Execution stages

1. Load raw CSV records.
2. Validate every input header; allow zero rows in sanctions and employment only.
3. Normalize identifiers, dates, values, and addresses.
4. Validate and load the selected parameter profile.
5. Execute indicators in dependency-aware order.
6. Produce supplier, tender, and entity roll-ups.
7. Write outputs and run metadata.

## 6. Output artifacts

- `indicator_results.csv`
- `supplier_risk_summary.csv`
- `tender_risk_summary.csv`
- `entity_risk_summary.csv`
- `run_metadata.json`

`run_metadata.json` contains the contract, package, and profile versions; run timestamp; raw input file names, row counts, and SHA-256 hashes; and output row counts.

## 7. Reproduce the synthetic example

```bash
gras \
  --tenders examples/synthetic/tenders.csv \
  --bids examples/synthetic/bids.csv \
  --sanctions examples/synthetic/sanctions.csv \
  --employment examples/synthetic/employment.csv \
  --out output/synthetic \
  --profile-name balanced \
  --run-timestamp 2026-01-01T00:00:00Z

diff -ru examples/synthetic/expected output/synthetic
```

No `diff` output means the generated artifacts match the versioned baseline.

## 8. Validation checklist

### 8.1 Schema checks

- output columns match the contract;
- all indicator rows have an indicator code and subject identifier;
- all `evidence_json` values parse as JSON; and
- all output files listed in the metadata exist.

### 8.2 Logical checks

- `risk_level` belongs to `LOW`, `MEDIUM`, or `HIGH`;
- `indicator_count >= 1` in summaries;
- roll-up subjects and evidence links are explainable from base records; and
- fixed inputs, profile, version, and timestamp produce deterministic outputs.

### 8.3 Data-quality checks

The reference runner validates columns and performs baseline normalization, but operational adopters must separately measure invalid or excluded rows, duplicate identifiers, parse failures, identity coverage, and source-schema drift.

## 9. Troubleshooting

### 9.1 Input table is empty or columns are missing

Every input file must contain all required headers. Tenders and bids require at
least one row. Sanctions and employment may contain only headers; a zero-byte
file is not a valid replacement. Compare with the [data contract](02_data_contract.md).

### 9.1.1 Invalid numeric input

Use decimal-point numbers without currency symbols or grouping separators. Scientific
notation is supported. Normalize locale-specific amounts upstream; the runner stops
on invalid nonblank values rather than silently changing their meaning.

### 9.2 Empty or unexpectedly small outputs

Potential causes include aggressive profile gates, invalid identifiers, malformed award flags, date gaps, or insufficient recurrence in the evaluated period.

### 9.3 Unexpectedly high indicator volume

Review permissive profile values, duplicate records, identity collisions, and address normalization. Do not reduce volumes solely by tuning thresholds; first confirm the source semantics and quality.

### 9.4 Unknown or invalid profile

The selected top-level profile name must exist, contain every required parameter, include a `profile_version`, use valid probability ranges, and preserve required threshold ordering.

## 10. Add or change an indicator

1. Document the intended behavior in `docs/pseudocode/` and `docs/typologies/`.
2. Add a failing test for the behavior.
3. Create or update the module in `src/gras/typologies/`.
4. Register it in `src/gras/pipeline/run_all.py` in dependency-aware order.
5. Extend roll-up mapping when the subject or evidence schema changes.
6. Update the catalog, golden outputs, versions, and changelog as appropriate.

## 11. Interpretation boundary

Generated rows are risk indicators for structured review. Do not treat them as findings of wrongdoing or publish sensitive row-level results without the relevant legal, privacy, confidentiality, and due-process safeguards.
