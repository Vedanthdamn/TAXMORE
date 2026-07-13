import json
from functools import lru_cache
from pathlib import Path

_EXTRACTED_DIR = Path(__file__).resolve().parents[3] / "docs" / "extracted"


@lru_cache
def load_tax_slabs() -> dict:
    with open(_EXTRACTED_DIR / "tax_slabs_fy2025_26.json") as f:
        return json.load(f)


@lru_cache
def load_hra_cities() -> dict:
    with open(_EXTRACTED_DIR / "hra_cities.json") as f:
        return json.load(f)
