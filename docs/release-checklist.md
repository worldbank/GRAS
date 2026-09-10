# Release Checklist

Use this checklist for a reviewed public release. It does not replace World Bank OSPO approval.

## Technical evidence

- [ ] All tests pass on every supported Python version.
- [ ] Ruff and mypy pass without ignored new findings.
- [ ] Source distribution and wheel build successfully.
- [ ] The wheel installs in a clean environment and the `gras` command runs.
- [ ] Synthetic outputs match the versioned golden files.
- [ ] `git diff --check` reports no whitespace errors.
- [ ] Repository scans find no secrets, credentials, personal paths, production data, or unexpected large files.
- [ ] README and documentation links resolve.
- [ ] `CITATION.cff` and workflow YAML parse successfully.

## Method and governance evidence

- [ ] Data-contract, package, and profile versions are intentional and consistent.
- [ ] Pseudocode, implementation, tests, and indicator catalog agree.
- [ ] Limitations and interpretation boundaries are current.
- [ ] Any algorithm or threshold change has a documented rationale and comparison run.
- [ ] Contact, authorship, copyright, citation, and release date are approved.
- [ ] License and IGO Rider are the current canonical World Bank versions.

## Repository and publication controls

- [ ] Compliance workflow passes on the candidate branch.
- [ ] Dependabot and branch protection are configured.
- [ ] Private vulnerability reporting is enabled when the repository is public.
- [ ] Repository description, website, and topics are set.
- [ ] GitHub Pages is enabled from `docs/` and the website field uses its URL.
- [ ] World Bank OSPO/public-repository review is approved before changing visibility.
- [ ] The release tag and published artifact match the reviewed commit.
