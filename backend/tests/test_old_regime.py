import pytest

from app.engine.models import Investments, SalaryInput
from app.engine.old_regime import calculate_old_regime_tax


def test_zero_deduction_case():
    salary = SalaryInput(basic=1000000)
    result = calculate_old_regime_tax(salary)

    assert result.gross_income == pytest.approx(1000000)
    assert result.deductions_breakdown["hra_exemption"] == 0
    assert result.deductions_breakdown["standard_deduction"] == pytest.approx(50000)
    assert result.taxable_income == pytest.approx(950000)
    # tax on 950000: 5% of 250000 (12500) + 20% of 450000 (90000) = 102500
    assert result.deductions_breakdown["rebate_87a"] == 0
    assert result.tax_before_cess == pytest.approx(102500)
    assert result.cess == pytest.approx(4100)
    assert result.total_tax == pytest.approx(106600)


def test_87a_rebate_applies_below_5L_threshold():
    salary = SalaryInput(basic=400000)
    result = calculate_old_regime_tax(salary)

    assert result.taxable_income == pytest.approx(350000)
    # tax on 350000: 5% of 100000 (above the 250000 nil band) = 5000
    assert result.deductions_breakdown["rebate_87a"] == pytest.approx(5000)
    assert result.tax_before_cess == 0
    assert result.total_tax == 0


def test_old_regime_has_no_marginal_relief_above_5L():
    # Just above the rebate threshold - old regime rebate has no
    # marginal-relief tapering, so it's simply lost entirely.
    salary = SalaryInput(basic=560000)
    result = calculate_old_regime_tax(salary)

    assert result.taxable_income == pytest.approx(510000)
    assert result.deductions_breakdown["rebate_87a"] == 0
    assert result.tax_before_cess > 0


def test_deduction_caps_are_enforced():
    salary = SalaryInput(
        basic=1500000,
        investments=Investments(
            section_80c=200000,  # exceeds combined 80CCE cap alone
            section_80d=40000,  # exceeds the 25000 base cap
            nps_self=60000,  # 50000 goes to 80CCD(1B), 10000 remains
            home_loan_interest=250000,  # exceeds the 200000 self-occupied cap
        ),
    )
    result = calculate_old_regime_tax(salary)
    breakdown = result.deductions_breakdown

    assert breakdown["section_80ccd1b"] == pytest.approx(50000)
    # 200000 (80C) + 10000 (remaining 80CCD1 eligible) capped at 150000
    assert breakdown["section_80c_combined"] == pytest.approx(150000)
    assert breakdown["section_80d"] == pytest.approx(25000)
    assert breakdown["section_24b_home_loan_interest"] == pytest.approx(200000)

    expected_taxable = 1500000 - (50000 + 150000 + 50000 + 25000 + 200000)
    assert result.taxable_income == pytest.approx(expected_taxable)
