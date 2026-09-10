# Association Rules - Detailed Pseudocode

## Signal intent

Measure directional associations between supplier awards, restricted to candidate
pairs selected by IND004. This is not an exhaustive association-rule miner.

## Event universe and metrics

`N` is the number of distinct tender IDs in bids, including those without awards.
`W(A)` is the set of those tenders in which supplier A has an awarded bid. Multiple
awarded rows for A in the same tender count once in these sets.

For each direction `A->B`:

- `support_a = |W(A)| / N`;
- `support_b = |W(B)| / N`;
- `support = |W(A) intersection W(B)| / N`;
- `confidence = |W(A) intersection W(B)| / |W(A)|`;
- `lift = support / (support_a * support_b)`;
- `leverage = support - support_a * support_b`;
- `conviction = (1 - support_b) / (1 - confidence)` when confidence is below 1.

All probabilities use award events, never a mixture of awards and participations.
The formulas follow the standard definitions described in the
[mlxtend association-rule documentation](https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/).
mlxtend is a methodological reference, not a runtime dependency.

## Core pseudocode

```text
BUILD all_events and award-event sets W(supplier) from bids
N = max(1, size(all_events))
candidate_pairs = unique unordered pairs from IND004 records

FOR each candidate pair (A, B):
    joint_events = intersection(W(A), W(B))
    support = size(joint_events) / N
    IF joint_events is empty OR support < profile.association_min_support:
        CONTINUE
    FOR each direction (antecedent, consequent) in [(A, B), (B, A)]:
        COMPUTE support_a, support_b, confidence, lift, leverage as above
        IF confidence < profile.association_min_confidence:
            CONTINUE
        IF confidence < 1:
            conviction = (1 - support_b) / (1 - confidence)
            conviction_status = finite
        ELSE:
            conviction = null
            conviction_status = undefined if support_b == 1 else infinite
        risk_level = HIGH if confidence >= 0.8 AND lift >= 1.5 else MEDIUM
        risk_score = 65 + min(30, confidence * 20 + max(0, lift - 1) * 10)
        EMIT IND005_ASSOCIATION_RULES, subject_type=pair,
             subject_id=antecedent + "->" + consequent, metrics and evidence
RETURN records sorted by (risk_score, subject_id) descending
```

## Evidence and interpretation

Evidence contains `supplier_a` (antecedent), `supplier_b` (consequent),
`event_basis = award`, the metrics above, `conviction_status`, and sorted jointly
awarded `tender_ids`. Metrics are calculated before rounding to six decimals.
No numeric sentinel or nonstandard JSON Infinity is used. Undefined conviction
means the formula is 0/0; infinite conviction has a positive numerator and zero
denominator. Neither is a measured finite score or proof of wrongdoing.

Both directions may pass, one may pass, or neither may pass. Their confidence and
conviction may differ; support, lift, and leverage are symmetric. Roll-ups include
each accepted direction as a separate indicator record for both suppliers.

## Validation and cost

Test asymmetric award histories, losing participations, both directions, threshold
filtering, zero joint awards, and finite/infinite/undefined conviction. Sparse
support and the IND004 candidate filter must remain explicit in interpretation.
Storage is proportional to supplier-event memberships; computation additionally
requires one award-set intersection per candidate pair.
