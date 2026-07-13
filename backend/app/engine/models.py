import re

from pydantic import BaseModel, ConfigDict, Field, model_validator

_CITY_NAME_PATTERN = re.compile(r"[A-Za-z ,.'-]+")


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


class TaxResult(BaseModel):
    gross_income: float
    taxable_income: float
    deductions_breakdown: dict[str, float]
    tax_before_cess: float
    cess: float
    total_tax: float
    regime: str
