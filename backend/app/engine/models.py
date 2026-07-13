from pydantic import BaseModel, ConfigDict, Field


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
    investments: Investments = Field(default_factory=Investments)


class TaxResult(BaseModel):
    gross_income: float
    taxable_income: float
    deductions_breakdown: dict[str, float]
    tax_before_cess: float
    cess: float
    total_tax: float
    regime: str
