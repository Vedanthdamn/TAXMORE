export interface Investments {
  "80C": number;
  "80D": number;
  nps_self: number;
  home_loan_interest: number;
}

export interface SalaryInput {
  basic: number;
  hra_received: number;
  lta: number;
  special_allowance: number;
  employer_nps_percent: number;
  city: string;
  rent_paid: number;
  investments: Investments;
}

export interface TaxResult {
  gross_income: number;
  taxable_income: number;
  deductions_breakdown: Record<string, number>;
  tax_before_cess: number;
  cess: number;
  total_tax: number;
  regime: string;
}

export interface RegimeComparison {
  old_regime: TaxResult;
  new_regime: TaxResult;
  better_regime: string;
  savings: number;
}

export interface OptimizerInput {
  income: number;
  regime: "old" | "new";
  headroom_80c: number;
  headroom_80d: number;
  headroom_80ccd1b?: number;
}

export interface OptimizationResult {
  allocation: Record<string, number>;
  marginal_rate: number;
  estimated_tax_savings: number;
  binding_constraints: string[];
  reasoning: string;
}
