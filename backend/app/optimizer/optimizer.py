"""LP-based deduction allocator.

Recommends how to split available tax-saving headroom across ELSS, PPF
(both Section 80C), health insurance premium (Section 80D), and the
additional NPS self-contribution (Section 80CCD(1B)) so as to maximize
the tax saved at the taxpayer's marginal rate, subject to each
section's cap from tax_rules_reference.md.

ELSS and PPF share a single combined 80C cap and are equally
tax-deductible - the tax code itself doesn't prefer one over the
other, so the LP treats them as perfect substitutes under one shared
constraint. To avoid handing back an arbitrary all-or-nothing solver
vertex (e.g. "put everything in ELSS, nothing in PPF"), the 80C
portion is split evenly between the two after solving; that split is
a presentation choice, not a tax-driven optimization. 80D and
80CCD(1B) are genuinely distinct constraints, so their amounts are
real LP outputs.

Per tax_rules_reference.md, none of these four deductions are allowed
under the new regime, so the optimizer short-circuits to a zero
allocation there rather than running the LP.
"""

from typing import Literal

from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpVariable, value
from pydantic import BaseModel, Field

from app.engine._data import load_tax_slabs

NPS_80CCD1B_STATUTORY_CAP = 50000


class OptimizerInput(BaseModel):
    income: float = Field(ge=0, description="taxable income used to derive the marginal rate")
    regime: Literal["old", "new"]
    headroom_80c: float = Field(ge=0, le=150000, description="remaining room in the combined 80C cap")
    headroom_80d: float = Field(ge=0, description="remaining room in the applicable 80D tier")
    headroom_80ccd1b: float = Field(
        default=NPS_80CCD1B_STATUTORY_CAP, ge=0, description="remaining room in the 80CCD(1B) cap"
    )


class OptimizationResult(BaseModel):
    allocation: dict[str, float]
    marginal_rate: float
    estimated_tax_savings: float
    binding_constraints: list[str]
    reasoning: str


def get_marginal_rate(taxable_income: float, regime: str) -> float:
    """Marginal tax rate for a given taxable income, read off the same
    slab tables new_regime.py/old_regime.py use (see tax_slabs_fy2025_26.json)."""
    slabs = load_tax_slabs()[f"{regime}_regime"]["slabs"]
    for slab in slabs:
        lower = slab.get("from", 0)
        upper = slab["up_to"]
        if taxable_income >= lower and (upper is None or taxable_income <= upper):
            return slab["rate_pct"] / 100
    return 0.0


def optimize_deductions(
    marginal_rate: float,
    headroom_80c: float,
    headroom_80d: float,
    headroom_80ccd1b: float = NPS_80CCD1B_STATUTORY_CAP,
) -> OptimizationResult:
    effective_80ccd1b_cap = min(headroom_80ccd1b, NPS_80CCD1B_STATUTORY_CAP)

    zero_allocation = {
        "elss": 0.0,
        "ppf": 0.0,
        "insurance_premium_80d": 0.0,
        "nps_80ccd1b": 0.0,
    }

    if marginal_rate <= 0:
        return OptimizationResult(
            allocation=zero_allocation,
            marginal_rate=marginal_rate,
            estimated_tax_savings=0.0,
            binding_constraints=[],
            reasoning="Marginal tax rate is 0% at this income, so no further deduction saves any tax.",
        )

    if headroom_80c <= 0 and headroom_80d <= 0 and effective_80ccd1b_cap <= 0:
        return OptimizationResult(
            allocation=zero_allocation,
            marginal_rate=marginal_rate,
            estimated_tax_savings=0.0,
            binding_constraints=["80C", "80D", "80CCD(1B)"],
            reasoning="No headroom remains in 80C, 80D, or 80CCD(1B) - nothing left to recommend.",
        )

    prob = LpProblem("maximize_tax_savings", LpMaximize)

    section_80c = LpVariable("section_80c", lowBound=0, upBound=headroom_80c)
    insurance_premium = LpVariable("insurance_premium_80d", lowBound=0, upBound=headroom_80d)
    nps_80ccd1b = LpVariable("nps_80ccd1b", lowBound=0, upBound=effective_80ccd1b_cap)

    prob += marginal_rate * (section_80c + insurance_premium + nps_80ccd1b)
    prob.solve(PULP_CBC_CMD(msg=0))

    section_80c_val = round(value(section_80c), 2)
    insurance_val = round(value(insurance_premium), 2)
    nps_val = round(value(nps_80ccd1b), 2)

    allocation = {
        "elss": round(section_80c_val / 2, 2),
        "ppf": round(section_80c_val - section_80c_val / 2, 2),
        "insurance_premium_80d": insurance_val,
        "nps_80ccd1b": nps_val,
    }

    estimated_tax_savings = round(
        marginal_rate * (section_80c_val + insurance_val + nps_val), 2
    )

    binding_constraints = []
    reasoning_parts = []
    if headroom_80c > 0:
        binding_constraints.append("80C")
        reasoning_parts.append(
            f"80C headroom of Rs {headroom_80c:,.0f} fully utilized "
            f"(split evenly between ELSS and PPF, which are equally deductible)"
        )
    if headroom_80d > 0:
        binding_constraints.append("80D")
        reasoning_parts.append(f"80D headroom of Rs {headroom_80d:,.0f} fully utilized")
    if effective_80ccd1b_cap > 0:
        binding_constraints.append("80CCD(1B)")
        reasoning_parts.append(
            f"80CCD(1B) headroom of Rs {effective_80ccd1b_cap:,.0f} fully utilized"
        )

    reasoning = (
        "; ".join(reasoning_parts)
        + f". Estimated tax savings: Rs {estimated_tax_savings:,.0f} at a "
        + f"{marginal_rate * 100:.0f}% marginal rate."
    )

    return OptimizationResult(
        allocation=allocation,
        marginal_rate=marginal_rate,
        estimated_tax_savings=estimated_tax_savings,
        binding_constraints=binding_constraints,
        reasoning=reasoning,
    )


def run_optimizer(params: OptimizerInput) -> OptimizationResult:
    if params.regime == "new":
        zero_allocation = {
            "elss": 0.0,
            "ppf": 0.0,
            "insurance_premium_80d": 0.0,
            "nps_80ccd1b": 0.0,
        }
        return OptimizationResult(
            allocation=zero_allocation,
            marginal_rate=get_marginal_rate(params.income, "new"),
            estimated_tax_savings=0.0,
            binding_constraints=[],
            reasoning=(
                "The new regime disallows 80C, 80D, and 80CCD(1B) deductions entirely "
                "(see tax_rules_reference.md) - there's no tax benefit to recommend "
                "these investments for under the new regime."
            ),
        )

    marginal_rate = get_marginal_rate(params.income, params.regime)
    return optimize_deductions(
        marginal_rate=marginal_rate,
        headroom_80c=params.headroom_80c,
        headroom_80d=params.headroom_80d,
        headroom_80ccd1b=params.headroom_80ccd1b,
    )
