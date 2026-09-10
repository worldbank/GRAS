# 07. Limitations and Governance

## 1. Interpretation boundaries

The method produces risk indicators and evidence bundles for prioritization. It does not replace contextual review.

## 2. Known technical limitations

The reference runner performs required-column checks and baseline normalization,
but it does not yet produce a complete field-level data-quality report. Blank
numeric values default to zero; invalid nonblank numeric values stop the run.
Selected rows with missing identifiers or
invalid sanction windows are excluded. Operational adopters must quantify and
review these effects upstream.

## 2.1 Identity quality

- inconsistent id formatting,
- id reuse across unrelated entities,
- cross-source mapping drift.

## 2.2 Temporal quality

- missing or ambiguous dates,
- mixed date formats,
- delayed publication patterns.

## 2.3 Monetary quality

- inconsistent numeric formatting,
- null or generic-marker values,
- currency conversion inconsistency (if multi-currency context).

## 2.4 Address quality

- incomplete addresses,
- multiple real-world entities at same location,
- normalization collisions.

## 2.5 Sparse support risk

Some statistical signals may appear strong under low support sizes. Support gates are essential.

The conditional-influence baseline has no configurable minimum event-count gate;
review `conditioning_event_count` before using such signals. Its baseline uses all
observed bid events, not only events in which the target supplier participated.

Association rules use award events consistently and evaluate both directions, but
only for pairs selected by IND004. They do not enumerate all possible association
rules or establish causation. Group turn-taking is a balance-of-wins heuristic;
it does not test chronological rotation.

Sanction overlap uses bid submission dates as a proxy, not a verified award date.
Each awarded input row is counted once if any sanction matches; duplicated source
rows must be resolved upstream. Employment overlap matches identities only: it
does not establish that employment was active on the procurement date.

Roll-ups count indicator records, not distinct indicator families. Both accepted
directions of an association contribute separately. `weighted_score` is the mean
of ordinal severity times score (nominal range 0–300), not a probability. Supplier
records without tender references do not propagate to tender/entity summaries;
tender-subject address flags do not automatically propagate to suppliers.

## 3. Governance controls

## 3.1 Profile governance

- version every profile change,
- document rationale,
- compare pre/post impact before adoption.

## 3.2 Data governance

- maintain input quality reports,
- track parse success and coercion counts,
- monitor source schema drift.

## 3.3 Execution governance

- immutable run logs,
- deterministic output ordering,
- stored run metadata (profile + package version + timestamp).

## 3.4 Evidence governance

- preserve original evidence payload per row,
- avoid rewriting evidence during downstream consumption,
- keep indicator-to-summary traceability.

## 4. Drift and stability monitoring

Monitor periodically:

- indicators per family,
- risk-level distribution,
- top-score concentration,
- overlap between indicator families,
- subject churn rate across periods.

## 5. Calibration governance cycle

1. Baseline run.
2. Distribution review.
3. Profile adjustment proposal.
4. Comparative rerun.
5. Approval and version update.
6. Deployment to regular execution.

## 6. Escalation principles

When quality checks fail:

- stop downstream publication,
- isolate root cause (schema, parse, logic, profile),
- rerun with corrected inputs and documented changes.

## 7. Adaptation caution

Context adaptation should preserve:

- core metric semantics,
- evidence schema structure,
- consistent interpretation boundaries.

Only parameter ranges should change first. Logic changes should be explicit and versioned.

## 8. Minimum governance artifacts

Recommended minimum bundle per release:

- method version,
- profile version,
- data contract version,
- validation report,
- runbook,
- change log.

## 9. Privacy and disclosure safeguards

- apply data minimization and purpose limitation to every input;
- restrict row-level evidence and outputs to authorized reviewers;
- avoid publishing operational outputs that contain personal, confidential, or
  investigation-sensitive information;
- define retention, correction, challenge, and deletion procedures; and
- complete applicable legal, privacy, security, and institutional review before
  operational use.
