import pytest

from app.optimizer.optimizer import (
    OptimizerInput,
    get_marginal_rate,
    optimize_deductions,
    run_optimizer,
)


def test_fully_unused_80c_headroom():
    # Nothing claimed yet - full Rs 1,50,000 80C room, Rs 25,000 80D room,
    # and the full Rs 50,000 80CCD(1B) room are all available.
    result = optimize_deductions(
        marginal_rate=0.30, headroom_80c=150000, headroom_80d=25000, headroom_80ccd1b=50000
    )

    assert result.allocation["elss"] == pytest.approx(75000)
    assert result.allocation["ppf"] == pytest.approx(75000)
    assert result.allocation["insurance_premium_80d"] == pytest.approx(25000)
    assert result.allocation["nps_80ccd1b"] == pytest.approx(50000)
    assert result.estimated_tax_savings == pytest.approx(0.30 * 225000)
    assert set(result.binding_constraints) == {"80C", "80D", "80CCD(1B)"}


def test_partially_used_headroom():
    # User already claimed Rs 1,00,000 of 80C and all of 80D elsewhere -
    # only Rs 50,000 of 80C and none of 80D remain.
    result = optimize_deductions(
        marginal_rate=0.20, headroom_80c=50000, headroom_80d=0, headroom_80ccd1b=20000
    )

    assert result.allocation["elss"] == pytest.approx(25000)
    assert result.allocation["ppf"] == pytest.approx(25000)
    assert result.allocation["insurance_premium_80d"] == 0
    assert result.allocation["nps_80ccd1b"] == pytest.approx(20000)
    assert "80D" not in result.binding_constraints
    assert "80C" in result.binding_constraints
    assert "80CCD(1B)" in result.binding_constraints


def test_zero_headroom_edge_case():
    result = optimize_deductions(
        marginal_rate=0.30, headroom_80c=0, headroom_80d=0, headroom_80ccd1b=0
    )

    assert result.allocation == {
        "elss": 0,
        "ppf": 0,
        "insurance_premium_80d": 0,
        "nps_80ccd1b": 0,
    }
    assert result.estimated_tax_savings == 0
    assert "no headroom remains" in result.reasoning.lower()


def test_zero_marginal_rate_recommends_nothing():
    result = optimize_deductions(
        marginal_rate=0.0, headroom_80c=150000, headroom_80d=25000
    )

    assert result.estimated_tax_savings == 0
    assert all(v == 0 for v in result.allocation.values())


def test_80ccd1b_headroom_clamped_to_statutory_cap():
    # Even if a caller passes more than Rs 50,000 remaining, the
    # statutory cap still wins.
    result = optimize_deductions(
        marginal_rate=0.30, headroom_80c=0, headroom_80d=0, headroom_80ccd1b=90000
    )

    assert result.allocation["nps_80ccd1b"] == pytest.approx(50000)


def test_run_optimizer_short_circuits_under_new_regime():
    params = OptimizerInput(
        income=1500000, regime="new", headroom_80c=150000, headroom_80d=25000
    )
    result = run_optimizer(params)

    assert all(v == 0 for v in result.allocation.values())
    assert result.estimated_tax_savings == 0
    assert "new regime" in result.reasoning.lower()


def test_run_optimizer_uses_marginal_rate_for_old_regime():
    params = OptimizerInput(
        income=700000, regime="old", headroom_80c=150000, headroom_80d=25000
    )
    result = run_optimizer(params)

    assert result.marginal_rate == pytest.approx(0.20)
    assert result.estimated_tax_savings > 0


def test_get_marginal_rate_matches_expected_slab():
    assert get_marginal_rate(300000, "old") == pytest.approx(0.05)
    assert get_marginal_rate(600000, "old") == pytest.approx(0.20)
    assert get_marginal_rate(100000000, "old") == pytest.approx(0.30)
    assert get_marginal_rate(500000, "new") == pytest.approx(0.05)
