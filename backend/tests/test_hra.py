import pytest

from app.engine.models import SalaryInput
from app.engine.hra import calculate_hra_exemption


def test_hra_zero_when_no_rent_paid():
    salary = SalaryInput(basic=600000, hra_received=300000, city="Mumbai", rent_paid=0)
    assert calculate_hra_exemption(salary) == 0


def test_hra_bound_by_rent_minus_10pct_basic():
    salary = SalaryInput(
        basic=1000000, hra_received=600000, city="Delhi", rent_paid=150000
    )
    # rent - 10% basic = 150000 - 100000 = 50000, the smallest of the three
    assert calculate_hra_exemption(salary) == pytest.approx(50000)


def test_hra_bound_by_metro_city_percentage():
    salary = SalaryInput(
        basic=1000000, hra_received=600000, city="Delhi", rent_paid=800000
    )
    # 50% of basic = 500000, smaller than hra_received (600000) and
    # rent - 10% basic (700000)
    assert calculate_hra_exemption(salary) == pytest.approx(500000)


def test_hra_bound_by_non_metro_city_percentage():
    salary = SalaryInput(
        basic=1000000, hra_received=600000, city="Pune", rent_paid=800000
    )
    # 40% of basic = 400000 for a non-metro city
    assert calculate_hra_exemption(salary) == pytest.approx(400000)


def test_hra_bound_by_actual_hra_received():
    salary = SalaryInput(
        basic=1000000, hra_received=100000, city="Delhi", rent_paid=800000
    )
    assert calculate_hra_exemption(salary) == pytest.approx(100000)
