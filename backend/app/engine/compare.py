from pydantic import BaseModel

from .models import SalaryInput, TaxResult
from .new_regime import calculate_new_regime_tax
from .old_regime import calculate_old_regime_tax


class RegimeComparison(BaseModel):
    old_regime: TaxResult
    new_regime: TaxResult
    better_regime: str
    savings: float


def compare_regimes(salary: SalaryInput) -> RegimeComparison:
    old_result = calculate_old_regime_tax(salary)
    new_result = calculate_new_regime_tax(salary)

    if old_result.total_tax == new_result.total_tax:
        better_regime = "equal"
        savings = 0.0
    elif old_result.total_tax < new_result.total_tax:
        better_regime = "old"
        savings = new_result.total_tax - old_result.total_tax
    else:
        better_regime = "new"
        savings = old_result.total_tax - new_result.total_tax

    return RegimeComparison(
        old_regime=old_result,
        new_regime=new_result,
        better_regime=better_regime,
        savings=savings,
    )
