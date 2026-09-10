# 01. Method Overview

## 1. Purpose

The GRAS method transforms event-participant transactional data into structured risk indicators. The method is designed to be reusable across contexts with similar behavioral signals, while preserving neutral interpretation boundaries.

The method does not produce final conclusions. It produces prioritized evidence for structured review.

## 2. Conceptual architecture

The method has five layers:

1. **Data contract and normalization layer**

   - Canonical identifiers.
   - Robust date parsing.
   - Numeric coercion for amount fields.
   - Address normalization.

1. **Indicator computation layer**

   - Family-specific detectors.
   - Shared recurrence and concentration primitives.
   - Statistical strength metrics where relevant.

1. **Risk scoring layer**

   - Band assignment (`LOW`, `MEDIUM`, `HIGH`).
   - Range-based configurable profiles.
   - Comparable score scale across indicators.

1. **Evidence packaging layer**

   - Standard output schema.
   - Explicit metric snapshots in `evidence_json`.
   - Reproducible run timestamping.

1. **Cross-entity aggregation layer**

   - Supplier-level summary.
   - Tender-level summary.
   - Entity-level summary.

## 3. Data model abstraction

The method assumes four logical input domains:

- **Events domain** (`tenders`): event-level metadata.
- **Participation domain** (`bids`): who participated, who won, and value proxies.
- **Restriction domain** (`sanctions`): temporal restriction windows.
- **Identity domain** (`employment`): role and organizational overlap reference.

The method can be extended with additional domains when needed, while maintaining the same output interface.

## 4. Indicator logic families

### 4.1 Concentration family

- Single bidder concentration.
- Detects suppliers whose awards are concentrated in low-competition settings.

### 4.2 Persistence and asymmetry family

- Top loser behavior.
- Top loser winner links.
- Detects persistent low-success participants and recurrent winner-link structures.

### 4.3 Pair and group structure family

- Co-award pairs.
- Association rules.
- Group exclusivity, turn-taking, dominance.
- Detects recurrence and dependence structures across pairs/groups.

### 4.4 Conditional behavior family

- Conditional influence.
- Detects probability uplift patterns tied to joint participation.

### 4.5 Network composition family

- Event-centric suspicious components.
- Detects connected structures built from suspicious event filters.

### 4.6 Constraint overlap family

- Sanction overlap.
- Public employee bidder overlap.
- Repeated fiscal address.
- Detects context-sensitive overlap and recurrence signals.

### 4.7 Consolidation family

- Risk roll-up (supplier, tender, entity).

## 5. Method execution lifecycle

1. Validate input schemas against contract.
2. Normalize and clean fields.
3. Execute indicators in dependency-aware order.
4. Produce standardized indicator records.
5. Produce roll-up summaries.
6. Perform quality checks and drift checks.

## 6. Explainability principles

Each indicator record must include:

- explicit metric values,
- recurrence context,
- subject identifier,
- run timestamp,
- level and score.

This allows downstream review without re-computation.

## 7. Portability principles

The method is portable when the target context can provide:

- event id,
- participant id,
- award signal,
- optional value proxy,
- optional overlap reference datasets.

Field names can change; semantics must be preserved.

## 8. Adaptation strategy

Adaptation should occur through profiles, not algorithm rewrites, whenever possible.

Priority adaptation levers:

1. minimum recurrence gates,
2. concentration ranges,
3. confidence/support ranges,
4. overlap strictness,
5. risk scoring weights.

## 9. Validation philosophy

The method expects two validation classes:

- **Functional validation**: indicator logic behaves as designed on controlled data.
- **Operational validation**: hit-rate distribution and stability are monitored over time.

## 10. Interpretation boundary

Outputs are risk indicators suitable for triage and prioritization. They are not direct conclusions and should be interpreted within contextual review workflows.
