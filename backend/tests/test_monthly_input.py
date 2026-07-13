import pytest

from app.engine.compare import compare_regimes
from app.engine.models import Investments, SalaryInput, annualize_input


def test_monthly_and_annual_inputs_produce_identical_tax():
    # Same underlying salary, expressed two ways: annual figures
    # directly, and their monthly/12 equivalents with input_frequency
    # set to "monthly". Both should land on the same tax.
    annual = SalaryInput(
        basic=1200000,
        hra_received=300000,
        special_allowance=120000,
        city="Mumbai",
        rent_paid=300000,
        age=45,
        employer_nps_percent=10,
        investments=Investments(**{"80C": 100000, "80D": 15000}, nps_self=20000, home_loan_interest=50000),
    )
    monthly = SalaryInput(
        basic=100000,
        hra_received=25000,
        special_allowance=10000,
        city="Mumbai",
        rent_paid=25000,
        age=45,
        employer_nps_percent=10,
        input_frequency="monthly",
        investments=Investments(**{"80C": 100000, "80D": 15000}, nps_self=20000, home_loan_interest=50000),
    )

    annual_result = compare_regimes(annual)
    monthly_result = compare_regimes(monthly)

    assert monthly_result.old_regime.total_tax == pytest.approx(
        annual_result.old_regime.total_tax
    )
    assert monthly_result.new_regime.total_tax == pytest.approx(
        annual_result.new_regime.total_tax
    )
    assert monthly_result.old_regime.taxable_income == pytest.approx(
        annual_result.old_regime.taxable_income
    )
    assert monthly_result.new_regime.taxable_income == pytest.approx(
        annual_result.new_regime.taxable_income
    )


def test_response_reports_submitted_frequency_and_annualized_figures():
    monthly = SalaryInput(
        basic=50000,
        hra_received=15000,
        special_allowance=5000,
        city="Pune",
        rent_paid=15000,
        input_frequency="monthly",
    )
    result = compare_regimes(monthly)

    assert result.input_frequency == "monthly"
    assert result.annualized_salary == {
        "basic": 600000,
        "hra_received": 180000,
        "special_allowance": 60000,
        "rent_paid": 180000,
    }


def test_response_reports_annual_frequency_when_not_monthly():
    annual = SalaryInput(basic=800000)
    result = compare_regimes(annual)

    assert result.input_frequency == "annual"
    assert result.annualized_salary["basic"] == 800000


def test_monthly_tax_breakdown_is_annual_total_over_12():
    annual = SalaryInput(basic=1000000)
    result = compare_regimes(annual)

    assert result.monthly_tax["old_regime"] == pytest.approx(
        result.old_regime.total_tax / 12
    )
    assert result.monthly_tax["new_regime"] == pytest.approx(
        result.new_regime.total_tax / 12
    )


def test_annualize_input_only_scales_recurring_salary_fields():
    monthly = SalaryInput(
        basic=50000,
        hra_received=10000,
        lta=20000,
        special_allowance=5000,
        city="Delhi",
        rent_paid=12000,
        input_frequency="monthly",
        investments=Investments(**{"80C": 150000, "80D": 25000}, nps_self=50000, home_loan_interest=200000),
    )
    annual = annualize_input(monthly)

    assert annual.input_frequency == "annual"
    assert annual.basic == 600000
    assert annual.hra_received == 120000
    assert annual.special_allowance == 60000
    assert annual.rent_paid == 144000
    # LTA and investments are already annual/lump-sum figures - untouched
    assert annual.lta == 20000
    assert annual.investments.section_80c == 150000
    assert annual.investments.section_80d == 25000
    assert annual.investments.nps_self == 50000
    assert annual.investments.home_loan_interest == 200000


def test_annualize_input_is_a_noop_for_annual_frequency():
    annual = SalaryInput(basic=900000, hra_received=200000, city="Chennai", rent_paid=180000)
    assert annualize_input(annual) is annual
