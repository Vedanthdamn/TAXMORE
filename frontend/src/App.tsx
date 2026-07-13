import { useState } from "react";
import { ApiError, calculateTax } from "./api";
import { ComparisonView } from "./components/ComparisonView";
import { OptimizerPanel } from "./components/OptimizerPanel";
import { SalaryForm } from "./components/SalaryForm";
import { StatusBanner } from "./components/StatusBanner";
import type { Investments, RegimeComparison, SalaryInput } from "./types";
import "./App.css";

function App() {
  const [comparison, setComparison] = useState<RegimeComparison | null>(null);
  const [investments, setInvestments] = useState<Investments | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(salary: SalaryInput) {
    setLoading(true);
    setError(null);
    try {
      const result = await calculateTax(salary);
      setComparison(result);
      setInvestments(salary.investments);
    } catch (err) {
      setComparison(null);
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <h1>TAXMORE</h1>
      <p className="tagline">India salary tax optimizer</p>

      <SalaryForm onSubmit={handleSubmit} loading={loading} />

      <StatusBanner loading={loading} loadingText="Comparing regimes..." error={error} />

      {comparison && !loading && !error && (
        <>
          <ComparisonView comparison={comparison} />
          {investments && (
            <OptimizerPanel comparison={comparison} investments={investments} />
          )}
        </>
      )}
    </main>
  );
}

export default App;
