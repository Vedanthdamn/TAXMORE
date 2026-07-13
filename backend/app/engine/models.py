import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

_CITY_NAME_PATTERN = re.compile(r"[A-Za-z ,.'-]+")

ANNUALIZED_FIELDS = ("basic", "hra_received", "special_allowance", "rent_paid")


class Investments(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    section_80c: float = Field(default=0, alias="80C", ge=0)
    section_80d: float = Field(default=0, alias="80D", ge=0)
    nps_self: float = Field(default=0, ge=0)
    home_loan_interest: float = Field(default=0, ge=0)


class SalaryInput(BaseModel):
    basic: float = Field(ge=0)
    hra_received: float = Field(default=0, ge=0)
    lta: float = Field(default=0, ge=0)
    special_allowance: float = Field(default=0, ge=0)
    employer_nps_percent: float = Field(default=0, ge=0, le=100)
    city: str = ""
    rent_paid: float = Field(default=0, ge=0)
    age: int = Field(default=30, ge=0, le=120)
    input_frequency: Literal["monthly", "annual"] = "annual"
    investments: Investments = Field(default_factory=Investments)

    @model_validator(mode="after")
    def _validate_cross_fields(self):
        total_cash_salary = (
            self.basic + self.hra_received + self.lta + self.special_allowance
        )
        if self.rent_paid > total_cash_salary:
            raise ValueError(
                "rent_paid cannot exceed total salary "
                "(basic + HRA + LTA + special allowance)"
            )

        city = self.city.strip()
        if self.hra_received > 0 and not city:
            raise ValueError("city is required when hra_received is greater than 0")
        if city and not _CITY_NAME_PATTERN.fullmatch(city):
            raise ValueError("city must contain only letters, spaces, and punctuation")

        return self


def annualize_input(salary: SalaryInput) -> SalaryInput:
    """Convert a monthly SalaryInput to its annual equivalent.

    Tax is always computed annually, so this is the one place monthly
    figures get multiplied by 12 - old_regime.py/new_regime.py never see
    input_frequency and always operate on annual numbers. Only the
    recurring salary components (basic, HRA, special allowance, rent
    paid) are scaled; investments, LTA, and employer_nps_percent are
    already annual/lump-sum figures regardless of how the salary itself
    is entered, so they're left untouched. Annual input is returned
    unchanged.
    """
    if salary.input_frequency == "annual":
        return salary

    updates = {field: getattr(salary, field) * 12 for field in ANNUALIZED_FIELDS}
    updates["input_frequency"] = "annual"
    return salary.model_copy(update=updates)


class TaxResult(BaseModel):
    gross_income: float
    taxable_income: float
    deductions_breakdown: dict[str, float]
    tax_before_cess: float
    cess: float
    total_tax: float
    regime: str
