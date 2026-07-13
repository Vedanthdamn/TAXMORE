from .models import SalaryInput, TaxResult
from ._data import load_tax_slabs
from ._slabs import compute_slab_tax

NEW_REGIME_80CCD2_CAP_PCT = 0.14  # section 124(1)-(2), 2025 Act - all employers under new regime


def calculate_new_regime_tax(salary: SalaryInput) -> TaxResult:
    """New regime: HRA exemption and Chapter VIII deductions (80C/80D/24(b)/
    80CCD(1)/80CCD(1B)) are all disallowed. Only the standard deduction and
    the employer's NPS contribution (80CCD(2)) survive, per
    tax_rules_reference.md.
    """
    data = load_tax_slabs()["new_regime"]

    employer_nps_contribution = salary.employer_nps_percent / 100 * salary.basic
    gross_income = (
        salary.basic
        + salary.hra_received
        + salary.lta
        + salary.special_allowance
        + employer_nps_contribution
    )

    standard_deduction = min(data["standard_deduction"]["amount"], gross_income)
    section_80ccd2 = min(
        employer_nps_contribution, NEW_REGIME_80CCD2_CAP_PCT * salary.basic
    )

    taxable_income = max(0.0, gross_income - standard_deduction - section_80ccd2)

    tax_before_rebate = compute_slab_tax(taxable_income, data["slabs"])

    rebate = _rebate_87a_new_regime(taxable_income, tax_before_rebate, data["rebate_87A"])

    tax_before_cess = max(0.0, tax_before_rebate - rebate)
    cess_rate = load_tax_slabs()["cess"]["rate_pct"] / 100
    cess = tax_before_cess * cess_rate
    total_tax = tax_before_cess + cess

    return TaxResult(
        gross_income=gross_income,
        taxable_income=taxable_income,
        deductions_breakdown={
            "standard_deduction": standard_deduction,
            "section_80ccd2": section_80ccd2,
            "rebate_87a": rebate,
        },
        tax_before_cess=tax_before_cess,
        cess=cess,
        total_tax=total_tax,
        regime="new",
    )


def _rebate_87a_new_regime(
    taxable_income: float, tax_before_rebate: float, rebate_data: dict
) -> float:
    income_limit = rebate_data["income_limit"]
    max_rebate = rebate_data["max_rebate"]

    if taxable_income <= income_limit:
        return min(tax_before_rebate, max_rebate)

    # Marginal relief: incremental tax above the income_limit can't exceed
    # incremental income above the income_limit.
    excess_income = taxable_income - income_limit
    if tax_before_rebate > excess_income:
        marginal_relief = tax_before_rebate - excess_income
        return min(marginal_relief, tax_before_rebate)

    return 0.0
