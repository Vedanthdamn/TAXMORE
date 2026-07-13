def compute_slab_tax(taxable_income: float, slabs: list[dict]) -> float:
    """Sum of tax owed across a progressive slab table.

    Each slab dict has "rate_pct" and either "up_to" (first slab) or
    "from"/"up_to" (subsequent slabs, "up_to": null meaning no upper bound).
    """
    if taxable_income <= 0:
        return 0.0

    tax = 0.0
    for slab in slabs:
        # "from" marks the first rupee of the slab (e.g. 400001), so the
        # bracket's lower boundary for width purposes is one rupee below it
        # (i.e. the previous slab's "up_to").
        lower = slab["from"] - 1 if "from" in slab else 0
        upper = slab["up_to"]
        rate = slab["rate_pct"] / 100

        slab_top = upper if upper is not None else taxable_income
        taxable_in_slab = max(0.0, min(taxable_income, slab_top) - lower)
        tax += taxable_in_slab * rate

    return tax
