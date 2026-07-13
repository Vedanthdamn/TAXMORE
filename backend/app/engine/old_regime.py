from .models import SalaryInput, TaxResult
from .hra import calculate_hra_exemption
from ._data import load_tax_slabs
from ._slabs import compute_slab_tax

OLD_REGIME_80CCD2_CAP_PCT = 0.10  # section 80CCD(2), 1961 Act text (flat 10%, no govt/private split)
SECTION_80CCD1_CAP_PCT = 0.10  # section 80CCD(1), employee's own contribution
SECTION_80CCD1B_CAP = 50000  # additional NPS self-contribution, over and above 80C
SECTION_80CCE_COMBINED_CAP = 150000  # 80C + 80CCC + 80CCD(1) combined ceiling
SECTION_80D_CAP = 25000  # self + family, non-senior-citizen base limit (see docstring)
SECTION_24B_SELF_OCCUPIED_CAP = 200000  # home loan interest, self-occupied, construction within 5 years


def calculate_old_regime_tax(salary: SalaryInput) -> TaxResult:
    """Old regime: HRA exemption, standard deduction, and Chapter VIII
    deductions from tax_rules_reference.md all apply.

    Simplifications (no corresponding input fields on SalaryInput, so a
    single conservative figure is used rather than inventing one):
    - 80D uses the base self+family non-senior-citizen limit (Rs 25,000)
      only; the senior-citizen/parent tiers (up to Rs 50,000 each) require
      inputs this model doesn't collect.
    - 24(b) home loan interest is capped as if the property is
      self-occupied (Rs 2,00,000); there's no let-out/self-occupied flag.
    - investments.nps_self is split between the 80CCD(1B) exclusive
      Rs 50,000 bucket first, then whatever remains competes with 80C
      inside the combined 80CCE Rs 1,50,000 ceiling, capped at 10% of
      basic salary per 80CCD(1).
    """
    data = load_tax_slabs()["old_regime"]

    employer_nps_contribution = salary.employer_nps_percent / 100 * salary.basic
    gross_income = (
        salary.basic
        + salary.hra_received
        + salary.lta
        + salary.special_allowance
        + employer_nps_contribution
    )

    hra_exemption = calculate_hra_exemption(salary)
    standard_deduction = min(
        data["standard_deduction"]["amount"], gross_income - hra_exemption
    )
    section_80ccd2 = min(
        employer_nps_contribution, OLD_REGIME_80CCD2_CAP_PCT * salary.basic
    )

    nps_1b = min(salary.investments.nps_self, SECTION_80CCD1B_CAP)
    nps_remaining = salary.investments.nps_self - nps_1b
    nps_1_eligible = min(nps_remaining, SECTION_80CCD1_CAP_PCT * salary.basic)
    section_80c_combined = min(
        salary.investments.section_80c + nps_1_eligible, SECTION_80CCE_COMBINED_CAP
    )

    section_80d = min(salary.investments.section_80d, SECTION_80D_CAP)
    section_24b = min(
        salary.investments.home_loan_interest, SECTION_24B_SELF_OCCUPIED_CAP
    )

    total_deductions = (
        hra_exemption
        + standard_deduction
        + section_80ccd2
        + section_80c_combined
        + nps_1b
        + section_80d
        + section_24b
    )
    taxable_income = max(0.0, gross_income - total_deductions)

    tax_before_rebate = compute_slab_tax(taxable_income, data["slabs"])

    rebate_data = data["rebate_87A"]
    rebate = (
        min(tax_before_rebate, rebate_data["max_rebate"])
        if taxable_income <= rebate_data["income_limit"]
        else 0.0
    )

    tax_before_cess = max(0.0, tax_before_rebate - rebate)
    cess_rate = load_tax_slabs()["cess"]["rate_pct"] / 100
    cess = tax_before_cess * cess_rate
    total_tax = tax_before_cess + cess

    return TaxResult(
        gross_income=gross_income,
        taxable_income=taxable_income,
        deductions_breakdown={
            "hra_exemption": hra_exemption,
            "standard_deduction": standard_deduction,
            "section_80ccd2": section_80ccd2,
            "section_80c_combined": section_80c_combined,
            "section_80ccd1b": nps_1b,
            "section_80d": section_80d,
            "section_24b_home_loan_interest": section_24b,
            "rebate_87a": rebate,
        },
        tax_before_cess=tax_before_cess,
        cess=cess,
        total_tax=total_tax,
        regime="old",
    )
