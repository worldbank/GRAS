from pathlib import Path

import pytest
import yaml

from gras.common.normalization import load_profile


def test_builtin_profile_has_explicit_name_and_version() -> None:
    profile = load_profile()

    assert profile["profile_name"] == "balanced"
    assert profile["profile_version"] == "1.0.0"


def test_missing_profile_file_fails_instead_of_using_defaults(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError, match="Profile file not found"):
        load_profile(str(missing))


def test_unknown_profile_name_fails_with_available_names(tmp_path: Path) -> None:
    profile_file = tmp_path / "profiles.yaml"
    profile_file.write_text("balanced:\n  profile_version: 1.0.0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Unknown profile 'strict'"):
        load_profile(str(profile_file), profile_name="strict")


def test_incomplete_profile_fails_with_missing_parameters(tmp_path: Path) -> None:
    profile_file = tmp_path / "profiles.yaml"
    profile_file.write_text("balanced:\n  profile_version: 1.0.0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required parameters"):
        load_profile(str(profile_file))


def test_profile_rejects_ratio_outside_probability_range(tmp_path: Path) -> None:
    profile = load_profile()
    profile.pop("profile_name")
    profile["network_min_pf_share"] = 1.5
    profile_file = tmp_path / "profiles.yaml"
    profile_file.write_text(yaml.safe_dump({"balanced": profile}), encoding="utf-8")

    with pytest.raises(ValueError, match="network_min_pf_share.*between 0 and 1"):
        load_profile(str(profile_file))


def test_profile_rejects_high_threshold_below_medium_threshold(tmp_path: Path) -> None:
    profile = load_profile()
    profile.pop("profile_name")
    profile["single_bidder_ratio_medium"] = 0.75
    profile["single_bidder_ratio_high"] = 0.50
    profile_file = tmp_path / "profiles.yaml"
    profile_file.write_text(yaml.safe_dump({"balanced": profile}), encoding="utf-8")

    with pytest.raises(ValueError, match="single_bidder_ratio_high.*greater than or equal"):
        load_profile(str(profile_file))
