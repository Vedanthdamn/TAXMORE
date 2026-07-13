import pytest

from app.engine.models import Investments, SalaryInput
from app.engine.compare import compare_regimes
from app.engine.new_regime import calculate_new_regime_tax
from app.engine.old_regime import calculate_old_regime_tax


def test_compare_picks_new_regime_when_it_wins():
    # Zero-deduction, taxable income under 12L - new regime's rebate
    # wipes tax to zero while old regime still owes tax.
    salary = SalaryInput(basic=1000000)
    comparison = compare_regimes(salary)

    assert comparison.new_regime.total_tax == 0
    assert comparison.old_regime.total_tax > 0
    assert comparison.better_regime == "new"
    assert comparison.savings == pytest.approx(comparison.old_regime.total_tax)


def test_compare_picks_old_regime_when_deductions_are_large():
    salary = SalaryInput(
        basic=1200000,
        hra_received=480000,
        city="Mumbai",
        rent_paid=500000,
        investments=Investments(
            section_80c=150000,
            section_80d=25000,
            nps_self=50000,
            home_loan_interest=200000,
        ),
    )
    comparison = compare_regimes(salary)

    old_result = calculate_old_regime_tax(salary)
    new_result = calculate_new_regime_tax(salary)

    assert comparison.old_regime.total_tax == pytest.approx(old_result.total_tax)
    assert comparison.new_regime.total_tax == pytest.approx(new_result.total_tax)
    assert comparison.better_regime == "old"
    assert comparison.savings == pytest.approx(
        new_result.total_tax - old_result.total_tax
    )
