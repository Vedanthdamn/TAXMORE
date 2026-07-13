import type { RegimeComparison, TaxResult } from "../types";

interface ComparisonViewProps {
  comparison: RegimeComparison;
}

const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

function formatCurrency(amount: number): string {
  return currencyFormatter.format(amount);
}

function formatDeductionLabel(key: string): string {
  return key
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function RegimeCard({
  label,
  result,
  monthlyTax,
}: {
  label: string;
  result: TaxResult;
  monthlyTax: number;
}) {
  const deductions = Object.entries(result.deductions_breakdown).filter(
    ([, amount]) => amount > 0,
  );

  return (
    <div className="regime-card">
      <h3>{label}</h3>
      <dl>
        <dt>Gross income</dt>
        <dd>{formatCurrency(result.gross_income)}</dd>
        <dt>Taxable income</dt>
        <dd>{formatCurrency(result.taxable_income)}</dd>
      </dl>

      {deductions.length > 0 && (
        <>
          <h4>Deductions applied</h4>
          <dl>
            {deductions.map(([key, amount]) => (
              <div key={key} className="deduction-row">
                <dt>{formatDeductionLabel(key)}</dt>
                <dd>{formatCurrency(amount)}</dd>
              </div>
            ))}
          </dl>
        </>
      )}

      <dl>
        <dt>Tax before cess</dt>
        <dd>{formatCurrency(result.tax_before_cess)}</dd>
        <dt>Cess</dt>
        <dd>{formatCurrency(result.cess)}</dd>
      </dl>

      <p className="regime-card__total">
        Total tax: <strong>{formatCurrency(result.total_tax)}</strong>
        <br />
        <span className="regime-card__monthly">
          approx {formatCurrency(monthlyTax)} per month
        </span>
      </p>
    </div>
  );
}

export function ComparisonView({ comparison }: ComparisonViewProps) {
  const { old_regime, new_regime, better_regime, savings, monthly_tax } = comparison;

  return (
    <section className="comparison-view">
      <h2>Old regime vs new regime</h2>

      {better_regime === "equal" ? (
        <p className="callout">Both regimes result in the same tax liability.</p>
      ) : (
        <p className="callout">
          You save <strong>{formatCurrency(savings)}</strong> under the{" "}
          <strong>{better_regime}</strong> regime.
        </p>
      )}

      <div className="regime-grid">
        <RegimeCard
          label="Old regime"
          result={old_regime}
          monthlyTax={monthly_tax.old_regime}
        />
        <RegimeCard
          label="New regime"
          result={new_regime}
          monthlyTax={monthly_tax.new_regime}
        />
      </div>
    </section>
  );
}
