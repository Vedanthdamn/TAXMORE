"""Validation suite against independently-verified salary profiles.

Separate from the synthetic unit tests elsewhere in this directory:
fixtures/validation_dataset.json's expected_old_regime_tax and
expected_new_regime_tax were verified independently of this codebase
(see each profile's "verified_via" note) and must never be
regenerated or "corrected" from here - a mismatch means the engine is
wrong (or the fixture's expectation needs the user's own review), not
that the test should be adjusted to match the engine's output.

The fixture's salary_input field names don't match SalaryInput's
schema (e.g. "section_80C" vs the alias "80C", "nps_80ccd1b" vs
"nps_self") - adapt_salary_input() below maps them, including "age",
which old_regime.py now uses to select the correct slab table and
80D cap for senior/super-senior citizens.
"""

import json
from pathlib import Path

import pytest

from app.engine.compare import compare_regimes
from app.engine.models import SalaryInput

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "validation_dataset.json"
TOLERANCE = 1.0  # rupees, to absorb rounding


def load_profiles() -> list[dict]:
    with open(FIXTURE_PATH) as f:
        return json.load(f)


def adapt_salary_input(raw: dict) -> SalaryInput:
    """Map the fixture's salary_input shape onto SalaryInput's schema.

    Field renames only.
    """
    investments = raw.get("investments", {})
    return SalaryInput(
        basic=raw["basic"],
        hra_received=raw.get("hra_received", 0),
        lta=raw.get("lta", 0),
        special_allowance=raw.get("special_allowance", 0),
        employer_nps_percent=raw.get("employer_nps_percent", 0),
        city=raw.get("city", ""),
        rent_paid=raw.get("rent_paid", 0),
        age=raw.get("age", 30),
        investments={
            "80C": investments.get("section_80C", 0),
            "80D": investments.get("section_80D", 0),
            "nps_self": investments.get("nps_80ccd1b", 0),
            "home_loan_interest": investments.get("home_loan_interest_24b", 0),
        },
    )


PROFILES = load_profiles()


def _format_mismatch(profile: dict, comparison) -> str:
    intermediate = profile.get("computed_intermediate", {})
    lines = [
        f"\nProfile: {profile['name']}",
        f"  notes: {profile.get('notes', '')}",
        f"  verified_via: {profile.get('verified_via', '')}",
        "  field-by-field (fixture computed_intermediate vs engine):",
        f"    gross_salary            expected={intermediate.get('gross_salary')!r:>12}  "
        f"actual={comparison.old_regime.gross_income!r}",
        f"    hra_exemption            expected={intermediate.get('hra_exemption')!r:>12}  "
        f"actual={comparison.old_regime.deductions_breakdown.get('hra_exemption', 0.0)!r}",
        f"    old_regime_taxable_income expected={intermediate.get('old_regime_taxable_income')!r:>11}  "
        f"actual={comparison.old_regime.taxable_income!r}",
        f"    new_regime_taxable_income expected={intermediate.get('new_regime_taxable_income')!r:>11}  "
        f"actual={comparison.new_regime.taxable_income!r}",
        "  final tax:",
        f"    old_regime_tax  expected={profile['expected_old_regime_tax']!r}  "
        f"actual={comparison.old_regime.total_tax!r}",
        f"    new_regime_tax  expected={profile['expected_new_regime_tax']!r}  "
        f"actual={comparison.new_regime.total_tax!r}",
    ]
    return "\n".join(lines)


@pytest.mark.parametrize(
    "profile",
    PROFILES,
    ids=[p["name"] for p in PROFILES],
)
def test_profile_matches_expected_tax(profile):
    salary = adapt_salary_input(profile["salary_input"])
    comparison = compare_regimes(salary)

    old_match = comparison.old_regime.total_tax == pytest.approx(
        profile["expected_old_regime_tax"], abs=TOLERANCE
    )
    new_match = comparison.new_regime.total_tax == pytest.approx(
        profile["expected_new_regime_tax"], abs=TOLERANCE
    )

    if not (old_match and new_match):
        pytest.fail(_format_mismatch(profile, comparison))
