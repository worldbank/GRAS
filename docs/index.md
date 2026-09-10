---
layout: default
---

# Governance Risk Assessment System (GRAS)

GRAS helps public institutions prioritize where a closer review may be useful by identifying repeated, structured risk signals in procurement and related data. It does not determine that wrongdoing occurred. Its outputs are evidence-backed red flags that must remain subject to contextual and human review.

This site documents a generic, offline reference implementation. The package is intended for integrity, procurement, audit, data, and research teams evaluating or adapting the GRAS method. It is not an operational country system and contains no production data.

## What the package does

The reference pipeline accepts four contract-aligned CSV files—tenders, bids, sanctions, and employment records—then:

1. checks the required columns;
2. normalizes identifiers, dates, numeric values, and addresses;
3. computes 11 deterministic indicator families;
4. emits standardized indicator records with evidence;
5. creates supplier, tender, and contracting-entity roll-ups; and
6. records the versions, timestamp, file hashes, and row counts needed to reproduce a run.

## Start here

- [Getting started and command-line usage](methodology/06_execution_guide.md)
- [Method overview](methodology/01_method_overview.md)
- [Architecture and data flow](architecture.md)
- [Input and output data contract](methodology/02_data_contract.md)
- [Indicator catalog](methodology/03_indicator_catalog.md)
- [Parameter profiles](methodology/04_parameter_ranges.md)
- [Execution and validation guide](methodology/06_execution_guide.md)
- [Adaptation guide](adaptation-guide.md)
- [Limitations and governance](methodology/07_limitations_and_governance.md)
- [Public-package provenance](provenance.md)

The detailed [typology notes](typologies/README.md) explain the analytical intent, and the [indicator-level pseudocode](pseudocode/) specifies the executable behavior.

## Responsible interpretation

GRAS indicators support triage and prioritization. They should never be treated as automatic findings, sanctions, rankings of integrity, or substitutes for due process. Before operational use, document data provenance and quality; validate thresholds on representative data; define authorized reviewers; establish correction and challenge procedures; and assess privacy, confidentiality, and legal requirements in the target jurisdiction.

## Contact

- Ariza Atifan Gusti — [agusti@worldbank.org](mailto:agusti@worldbank.org)
- Juan Pablo Guerrero Amparan — [jguerreroampara1@worldbankgroup.org](mailto:jguerreroampara1@worldbankgroup.org)
