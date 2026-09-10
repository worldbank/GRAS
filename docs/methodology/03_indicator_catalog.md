# 03. Indicator Catalog

## 1. Purpose

This catalog defines indicator scope, subject granularity, principal metrics, and expected evidence outputs.

## 2. Catalog summary table

| Code | Name | Subject Type | Primary Signal |
|---|---|---|---|
| IND001 | Single Bidder Concentration | supplier | Award concentration in one-bidder events |
| IND002 | Top Loser | supplier | High recurrence + low success |
| IND003 | Top Loser Winner Link | pair | Repeated winner-top-loser coupling |
| IND004 | Co-Award Pairs | pair | Repeated joint awards |
| IND005 | Association Rules | directional pair | Association between award events, evaluated in both directions |
| IND006 | Group Patterns | group | Exclusivity, turn-taking, dominance |
| IND007 | Conditional Influence | pair | Conditional probability uplift |
| IND008 | Event-Centric Suspicious Network | network_component | Suspicious event composition clusters |
| IND009 | Sanction Overlap | supplier | Awards inside sanction windows |
| IND010 | Public Employee Bidder Overlap | supplier | Bidder id overlaps employment records |
| IND011 | Repeated Fiscal Address | tender | Multi-supplier recurrent shared address |
| IND012 | Risk Roll-Up | supplier/tender/entity | Cross-indicator consolidation |

## 3. Detailed definitions

## 3.1 IND001 - Single Bidder Concentration

Objective:

- Detect concentration of supplier awards in one-bidder events.

Core metrics:

- total awards,
- single-bidder awards,
- concentration ratio,
- value proxy.

Evidence highlights:

- ratio and count context for explainability.

## 3.2 IND002 - Top Loser

Objective:

- Detect persistent participation with weak win conversion.

Core metrics:

- participation count,
- wins,
- success rate,
- awarded value.

Evidence highlights:

- conversion ratio and recurrence context.

## 3.3 IND003 - Top Loser Winner Link

Objective:

- Detect repeated links between specific winners and known low-success participants.

Core metrics:

- recurrent link count,
- winner exposure to top-loser events,
- link density.

Evidence highlights:

- explicit event ids and pair identity.

## 3.4 IND004 - Co-Award Pairs

Objective:

- Detect pairs that repeatedly receive awards together.

Core metrics:

- events together,
- co-awards,
- co-award rate,
- value proxy.

Evidence highlights:

- recurrence and concentration simultaneously.

## 3.5 IND005 - Association Rules

Objective:

- Measure directional association between supplier award-event sets, restricted to IND004 candidate pairs. All supports and confidence use the same award-event semantics.

Core metrics:

- support,
- confidence,
- lift,
- leverage,
- conviction.

Evidence highlights:

- antecedent/consequent IDs, joint award references, metrics and an explicit conviction status. Nonfinite or undefined conviction is represented by JSON null rather than a large numeric sentinel.

## 3.6 IND006 - Group Patterns

Objective:

- Detect recurrent multi-party structures with exclusivity or asymmetric outcomes.

Subtypes:

- exclusivity,
- turn-taking,
- dominance.

Core metrics:

- recurrence,
- exclusivity ratio,
- win-share dispersion,
- dominance share.

Evidence highlights:

- subtype tag and group member list.

## 3.7 IND007 - Conditional Influence

Objective:

- Detect material uplift in A's win probability when B participates.

Core metrics:

- baseline probability,
- conditional probability,
- gap,
- magnitude,
- support count.

Evidence highlights:

- pair directionality and conditioning support.

## 3.8 IND008 - Event-Centric Suspicious Network

Objective:

- Detect suspicious connected components built from filtered events.

Core metrics:

- event count,
- supplier count,
- edge count,
- component size score.

Evidence highlights:

- explicit component composition.

## 3.9 IND009 - Sanction Overlap

Objective:

- Detect awards occurring inside sanction windows.

Core metrics:

- overlap count,
- overlap value proxy,
- event references.

Evidence highlights:

- temporal overlap traceability.

## 3.10 IND010 - Public Employee Bidder Overlap

Objective:

- Detect id overlap between bidder and employment domains.

Core metrics:

- participations,
- wins,
- value proxy,
- role/employer context excerpts.

Evidence highlights:

- identity overlap and recurrence context.

## 3.11 IND011 - Repeated Fiscal Address

Objective:

- Detect recurrent multi-supplier sharing of normalized addresses.

Core metrics:

- address recurrence across events,
- supplier count per address,
- award involvement.

Evidence highlights:

- normalized address key and event set.

## 3.12 IND012 - Risk Roll-Up

Objective:

- Consolidate indicator footprint by subject level.

Core metrics:

- indicator count,
- max risk level,
- weighted score,
- code set.

Evidence highlights:

- compact summary of indicator presence.

## 4. Dependency ordering

Recommended order:

1. IND001, IND002
2. IND003 (depends on IND002)
3. IND004
4. IND005 (depends on IND004)
5. IND006, IND007
6. IND008 (benefits from IND002 + IND003)
7. IND009, IND010, IND011
8. IND012

## 5. Evidence consistency requirements

Across all indicators:

- include primary recurrence metric,
- include primary concentration/statistical metric,
- include context references (event ids where relevant),
- keep deterministic JSON key naming.
