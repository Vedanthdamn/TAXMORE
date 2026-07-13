import { useEffect, useState } from "react";
import { ApiError, optimizeDeductions } from "../api";
import type { Investments, OptimizationResult, RegimeComparison } from "../types";
import { StatusBanner } from "./StatusBanner";

interface OptimizerPanelProps {
  comparison: RegimeComparison;
  investments: Investments;
}

const SECTION_80C_CAP = 150000;
const SECTION_80D_CAP = 25000;
const SECTION_80CCD1B_CAP = 50000;

const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

function formatCurrency(amount: number): string {
  return currencyFormatter.format(amount);
}

const ALLOCATION_LABELS: Record<string, string> = {
  elss: "ELSS",
  ppf: "PPF",
  insurance_premium_80d: "Health insurance premium (80D)",
  nps_80ccd1b: "NPS self-contribution (80CCD(1B))",
};

export function OptimizerPanel({ comparison, investments }: OptimizerPanelProps) {
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const regime = comparison.better_regime === "new" ? "new" : "old";
  const taxableIncome = comparison.old_regime.taxable_income;

  const headroom80C = Math.max(0, SECTION_80C_CAP - investments["80C"]);
  const headroom80D = Math.max(0, SECTION_80D_CAP - investments["80D"]);
  const headroom80Ccd1B = Math.max(0, SECTION_80CCD1B_CAP - investments.nps_self);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    optimizeDeductions({
      income: taxableIncome,
      regime,
      headroom_80c: headroom80C,
      headroom_80d: headroom80D,
      headroom_80ccd1b: headroom80Ccd1B,
    })
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Could not fetch a recommendation.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [regime, taxableIncome, headroom80C, headroom80D, headroom80Ccd1B]);

  return (
    <section className="optimizer-panel">
      <h2>Where to invest your remaining headroom</h2>

      <StatusBanner loading={loading} loadingText="Finding the best allocation..." error={error} />

      {!loading && !error && result && (
        <>
          <ul className="allocation-list">
            {Object.entries(result.allocation)
              .filter(([, amount]) => amount > 0)
              .map(([key, amount]) => (
                <li key={key}>
                  <span>{ALLOCATION_LABELS[key] ?? key}</span>
                  <strong>{formatCurrency(amount)}</strong>
                </li>
              ))}
          </ul>

          {result.estimated_tax_savings > 0 && (
            <p className="callout">
              Estimated additional tax savings:{" "}
              <strong>{formatCurrency(result.estimated_tax_savings)}</strong>
            </p>
          )}

          <p className="optimizer-panel__reasoning">{result.reasoning}</p>
        </>
      )}
    </section>
  );
}
