import pytest

from app.engine.models import SalaryInput
from app.engine.new_regime import calculate_new_regime_tax


def test_zero_deduction_case():
    # No HRA, no investments, no employer NPS - only the standard
    # deduction applies.
    salary = SalaryInput(basic=1000000)
    result = calculate_new_regime_tax(salary)

    assert result.gross_income == pytest.approx(1000000)
    assert result.taxable_income == pytest.approx(925000)
    assert result.deductions_breakdown["standard_deduction"] == pytest.approx(75000)
    assert result.deductions_breakdown["section_80ccd2"] == 0
    # tax on 925000: 0 on first 4L, 5% on next 4L (20000), 10% on
    # remaining 1.25L (12500) = 32500, fully wiped by the 87A rebate
    # since taxable income is under the 12L limit.
    assert result.deductions_breakdown["rebate_87a"] == pytest.approx(32500)
    assert result.tax_before_cess == 0
    assert result.total_tax == 0


def test_87a_rebate_edge_case_at_exactly_12L_income():
    # basic chosen so taxable income lands exactly on the Rs 12,00,000
    # rebate threshold after the Rs 75,000 standard deduction.
    salary = SalaryInput(basic=1275000)
    result = calculate_new_regime_tax(salary)

    assert result.taxable_income == pytest.approx(1200000)
    # tax on 1200000: 20000 (4-8L @5%) + 40000 (8-12L @10%) = 60000
    assert result.deductions_breakdown["rebate_87a"] == pytest.approx(60000)
    assert result.tax_before_cess == 0
    assert result.total_tax == 0


def test_marginal_relief_just_above_12L():
    # taxable income = 1225000, Rs 25,000 above the rebate threshold.
    salary = SalaryInput(basic=1300000)
    result = calculate_new_regime_tax(salary)

    assert result.taxable_income == pytest.approx(1225000)
    # tax on 1225000: 20000 + 40000 + 15% of 25000 (3750) = 63750
    # marginal relief caps post-rebate tax at the Rs 25,000 excess income
    assert result.deductions_breakdown["rebate_87a"] == pytest.approx(38750)
    assert result.tax_before_cess == pytest.approx(25000)
    assert result.cess == pytest.approx(1000)
    assert result.total_tax == pytest.approx(26000)


def test_marginal_relief_disappears_once_slab_tax_exceeds_excess_income():
    # Far enough above 12L that the marginal relief rule no longer
    # applies (tax_before_rebate <= excess_income), so rebate is 0.
    salary = SalaryInput(basic=5000000)
    result = calculate_new_regime_tax(salary)

    assert result.deductions_breakdown["rebate_87a"] == 0
    assert result.tax_before_cess > 0


def test_employer_nps_contribution_deducted_under_80ccd2():
    salary = SalaryInput(basic=1000000, employer_nps_percent=10)
    result = calculate_new_regime_tax(salary)

    # employer contributes 10% of basic (100000), fully within the 14%
    # new-regime cap, so it's added to gross income and fully deducted
    # back out - no net effect on taxable income vs the zero-deduction case.
    assert result.gross_income == pytest.approx(1100000)
    assert result.deductions_breakdown["section_80ccd2"] == pytest.approx(100000)
    assert result.taxable_income == pytest.approx(1000000 - 75000)
