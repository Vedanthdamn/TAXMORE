from .models import SalaryInput
from ._data import load_hra_cities


def calculate_hra_exemption(salary: SalaryInput) -> float:
    """HRA exemption under Rule 2A, only applicable under the old regime.

    Exemption = least of:
      (a) actual HRA received
      (b) rent paid minus 10% of basic salary
      (c) 50% of basic salary (metro city) or 40% (non-metro)

    Uses basic salary alone as the "salary" base (no DA field exists on
    SalaryInput). If rent_paid is 0, exemption is 0 regardless of HRA
    received, since (b) would be negative.
    """
    if salary.hra_received <= 0:
        return 0.0

    hra_data = load_hra_cities()
    is_metro = salary.city.strip().lower() in {
        c.lower() for c in hra_data["metro_cities"]
    }
    city_pct = (
        hra_data["metro_exemption_pct_of_basic_salary"]
        if is_metro
        else hra_data["non_metro_exemption_pct_of_basic_salary"]
    ) / 100

    rent_minus_10pct_basic = salary.rent_paid - 0.10 * salary.basic
    city_limit = city_pct * salary.basic

    exemption = min(salary.hra_received, max(rent_minus_10pct_basic, 0), city_limit)
    return max(exemption, 0.0)
