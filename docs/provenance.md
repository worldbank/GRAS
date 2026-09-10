# Public-Package Provenance

## What this repository represents

This repository is a generic, self-contained reference implementation of the Governance Risk Assessment System method. Its technical starting point is Rafael Martins' earlier GRAS know-how kit, which generalized analytical logic and documentation from the experience of implementing GRAS in Guatemala. This candidate reorganizes that existing work into an installable package and adds validation, reproducibility tests, documentation, and publication materials.

The report cited below supplies public methodological context; it is not the sole source of the executable algorithms or a validation of the exact scoring formulas in this package. Implementation changes made during preparation are described in the [changelog](../CHANGELOG.md). Source lineage does not itself establish ownership or authorization to redistribute; the final attribution and licensing must be reviewed by the responsible institutions.

It is not a publication of any country's operational GRAS system. Country-specific source code, deployment configuration, credentials, original data, investigation material, internal correspondence, and operational history are outside this repository's scope.

## Public methodological source

The primary public reference is:

> World Bank. 2023. *Governance Risk Assessment System (GRAS): Advanced Data Analytics for Detecting Fraud, Corruption, and Collusion in Public Expenditures.* Washington, DC: World Bank. <https://doi.org/10.1596/40640>.

See [`bibliography.bib`](bibliography.bib) and [`CITATION.cff`](../CITATION.cff) for reusable citation metadata.

## Executable specification

Within this repository, the canonical executable behavior is the combination of:

- indicator-level pseudocode in [`docs/pseudocode/`](pseudocode/);
- the Python modules in [`src/gras/`](../src/gras/); and
- the tests and versioned synthetic outputs in [`tests/`](../tests/) and [`examples/synthetic/expected/`](../examples/synthetic/expected/).

A method change is complete only when these sources agree. The consolidated outputs are illustrative risk signals, not validated country findings.

## Version lineage

Version `0.1.0rc1` is an unreleased candidate for the first public baseline. Contract `2.0.0` identifies the revised directional association evidence and stricter numeric input rules; profile `balanced` remains `1.0.0` because its numeric thresholds have not changed. `run_metadata.json` records these versions for each run. Review the [changelog](../CHANGELOG.md) when comparing results with earlier candidate outputs. A release date and immutable release tag will be assigned after institutional review.
