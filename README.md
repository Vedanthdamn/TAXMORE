# TAXMORE

TAXMORE is an India salary tax optimizer. Give it a salary breakdown and it
compares your tax liability under the old and new income tax regimes for
FY 2025-26, and recommends how to split your remaining 80C/80D/NPS
investment headroom (via a linear program) to minimize what you owe. It's
aimed at salaried individuals in India trying to decide which regime to pick
and where to put their tax-saving investments, rather than tax
professionals or businesses.

## Features

- Side-by-side old regime vs new regime tax calculation for FY 2025-26
- HRA exemption under Rule 2A (metro/non-metro, least-of-three formula)
- Section 87A rebate, including new-regime marginal relief above Rs 12,00,000
- Deduction allocation optimizer (ELSS, PPF, health insurance premium, NPS
  80CCD(1B)) solved as a linear program with PuLP
- Senior citizen (60-80) and super senior citizen (80+) old-regime slabs and
  the higher 80D cap

## Tech stack

**Backend**: Python 3.13, FastAPI, Pydantic v2, PuLP (linear programming),
scipy, uvicorn. Dependencies are listed unpinned in
`backend/requirements.txt` (fastapi, uvicorn, pydantic, scipy, pulp,
python-dotenv); the versions actually installed in this project's venv are
fastapi 0.139.0, pydantic 2.13.4, scipy 1.18.0, PuLP 3.3.2, uvicorn 0.51.0.
Test dependencies (pytest, httpx) are in `backend/requirements-dev.txt`.

**Frontend**: React 19.2.7, TypeScript ~6.0.2, Vite ^8.1.1, oxlint for
linting. No CSS framework - plain CSS with light/dark theme support via
CSS variables.

## Project structure

```
backend/
  app/
    engine/        tax calculation logic - HRA exemption, old regime,
                    new regime, and the regime comparison
    optimizer/      deduction allocation LP (optimizer.py)
    rag/            empty placeholder, not yet built
    main.py         FastAPI app and routes
  tests/            pytest suite, including fixtures/validation_dataset.json
  requirements.txt
  requirements-dev.txt
  .env.example
frontend/
  src/
    components/     SalaryForm, ComparisonView, OptimizerPanel, StatusBanner
    data/            hraCities.ts (mirrors docs/extracted/hra_cities.json)
    api.ts           fetch wrappers for /calculate and /optimize
    types.ts         TypeScript types matching the backend's pydantic schemas
  .env.example
docs/
  source-pdfs/       the Income Tax Act and Finance Act PDFs tax rules were extracted from
  extracted/         tax_slabs_fy2025_26.json, tax_rules_reference.md, hra_cities.json
```

## Setup and running locally

### Backend

From the `backend/` directory:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --port 8000
```

The API is then available at `http://localhost:8000`. `.env` controls
`FRONTEND_ORIGIN`, which the backend uses for its CORS allow-list (defaults
to `http://localhost:5173` if unset).

To also run tests, install `requirements-dev.txt` instead of
`requirements.txt`.

### Frontend

From the `frontend/` directory:

```
npm install
cp .env.example .env
npm run dev
```

Vite's dev server runs on `http://localhost:5173` by default. `.env`
controls `VITE_API_BASE_URL`, which the frontend uses to reach the backend
(defaults to `http://localhost:8000` if unset).

## API reference

### `GET /health`

Health check.

Response:
```json
{ "status": "ok" }
```

### `POST /calculate`

Accepts a `SalaryInput` and returns a `RegimeComparison` - both regimes'
tax results plus which one wins and by how much.

Request:
```json
{
  "basic": 1000000,
  "hra_received": 300000,
  "lta": 0,
  "special_allowance": 0,
  "employer_nps_percent": 10,
  "city": "Mumbai",
  "rent_paid": 300000,
  "age": 30,
  "investments": {
    "80C": 100000,
    "80D": 15000,
    "nps_self": 0,
    "home_loan_interest": 0
  }
}
```

Response:
```json
{
  "old_regime": {
    "gross_income": 1400000.0,
    "taxable_income": 935000.0,
    "deductions_breakdown": {
      "hra_exemption": 200000.0,
      "standard_deduction": 50000.0,
      "section_80ccd2": 100000.0,
      "section_80c_combined": 100000.0,
      "section_80ccd1b": 0.0,
      "section_80d": 15000.0,
      "section_24b_home_loan_interest": 0.0,
      "rebate_87a": 0.0
    },
    "tax_before_cess": 99500.0,
    "cess": 3980.0,
    "total_tax": 103480.0,
    "regime": "old"
  },
  "new_regime": {
    "gross_income": 1400000.0,
    "taxable_income": 1225000.0,
    "deductions_breakdown": {
      "standard_deduction": 75000.0,
      "section_80ccd2": 100000.0,
      "rebate_87a": 38750.0
    },
    "tax_before_cess": 25000.0,
    "cess": 1000.0,
    "total_tax": 26000.0,
    "regime": "new"
  },
  "better_regime": "new",
  "savings": 77480.0
}
```

`investments` accepts either the field aliases shown above (`80C`, `80D`)
or the underlying field names (`section_80c`, `section_80d`) - both work.
`age` defaults to 30 if omitted. `city` is required only if `hra_received`
is greater than 0.

### `POST /optimize`

Accepts an `OptimizerInput` (income, regime, remaining headroom in each
section) and returns the LP's recommended allocation plus the reasoning
behind it.

Request:
```json
{
  "income": 850000,
  "regime": "old",
  "headroom_80c": 50000,
  "headroom_80d": 25000,
  "headroom_80ccd1b": 50000
}
```

Response:
```json
{
  "allocation": {
    "elss": 25000.0,
    "ppf": 25000.0,
    "insurance_premium_80d": 25000.0,
    "nps_80ccd1b": 50000.0
  },
  "marginal_rate": 0.2,
  "estimated_tax_savings": 25000.0,
  "binding_constraints": ["80C", "80D", "80CCD(1B)"],
  "reasoning": "80C headroom of Rs 50,000 fully utilized (split evenly between ELSS and PPF, which are equally deductible); 80D headroom of Rs 25,000 fully utilized; 80CCD(1B) headroom of Rs 50,000 fully utilized. Estimated tax savings: Rs 25,000 at a 20% marginal rate."
}
```

`regime` must be `"old"` or `"new"`; under the new regime the optimizer
short-circuits to a zero allocation, since none of these deductions apply
there. `headroom_80ccd1b` defaults to 50000 (the statutory cap) if omitted.

## Data sources

Tax rules are sourced from the Income-tax Act, 1961 and the relevant
CBDT-published rates and rules for FY 2025-26 (see `docs/source-pdfs/` for
the source documents and `docs/extracted/` for what was pulled from them -
`tax_slabs_fy2025_26.json`, `tax_rules_reference.md`, and `hra_cities.json`).
Figures that weren't present in either source document (old-regime slabs,
the cess rate, senior/super-senior slabs) were filled in separately and are
marked with a `source` note in the relevant file rather than left
unattributed.

## Testing

From `backend/`, with `requirements-dev.txt` installed:

```
pytest
```

This runs the full suite - unit tests for the HRA/old-regime/new-regime
calculators and the optimizer, plus `tests/fixtures/validation_dataset.json`:
25 salary profiles with expected tax outcomes verified independently of
this codebase, used to check the engine's output against real-world
numbers rather than just its own internal logic.

## Known limitations

- No surcharge calculation for income above Rs 50,00,000 - only the base
  slab tax and cess are computed.
- Professional tax (the small state-level deduction under section 16(iii))
  isn't modeled.
- LTA is accepted as its own input field but has no exemption logic of its
  own (Section 10(5)) - it's treated as fully taxable, the same as special
  allowance.
- Only FY 2025-26 is supported; there's no notion of a selectable
  assessment year.
