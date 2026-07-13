"""Validation suite against realistic salary profiles.

Separate from the synthetic unit tests elsewhere in this directory:
these profiles are meant to be checked by hand (see
fixtures/validation_dataset.json's "verified_via" field) rather than
derived from the engine's own logic. Rows whose expected values
haven't been filled in yet are skipped rather than failed, since a
null expectation means "not yet verified," not "expected to be zero."
"""

import json
import warnings
from pathlib import Path

import pytest

from app.engine.compare import compare_regimes
from app.engine.models import SalaryInput

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "validation_dataset.json"
TOLERANCE = 1.0  # rupees, to absorb rounding


def load_profiles() -> list[dict]:
    with open(FIXTURE_PATH) as f:
        return json.load(f)["profiles"]


def _unverified_ids(profiles: list[dict]) -> list[int]:
    return [
        p["id"]
        for p in profiles
        if p["expected_old_regime_tax"] is None or p["expected_new_regime_tax"] is None
    ]


PROFILES = load_profiles()
UNVERIFIED_IDS = _unverified_ids(PROFILES)

if UNVERIFIED_IDS:
    warnings.warn(
        f"Skipping {len(UNVERIFIED_IDS)} validation_dataset.json row(s) with no "
        f"verified expected values yet: profile id(s) {UNVERIFIED_IDS}",
        stacklevel=2,
    )


@pytest.mark.parametrize(
    "profile",
    PROFILES,
    ids=[f"{p['id']}_{p['category']}" for p in PROFILES],
)
def test_profile_matches_expected_tax(profile):
    if profile["id"] in UNVERIFIED_IDS:
        pytest.skip(f"profile {profile['id']} has no verified expected values yet")

    salary = SalaryInput(**profile["salary_input"])
    comparison = compare_regimes(salary)

    assert comparison.old_regime.total_tax == pytest.approx(
        profile["expected_old_regime_tax"], abs=TOLERANCE
    ), f"old regime mismatch for profile {profile['id']} ({profile['description']})"

    assert comparison.new_regime.total_tax == pytest.approx(
        profile["expected_new_regime_tax"], abs=TOLERANCE
    ), f"new regime mismatch for profile {profile['id']} ({profile['description']})"
