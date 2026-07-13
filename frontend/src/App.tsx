import { useState } from "react";
import { ApiError, calculateTax } from "./api";
import { SalaryForm } from "./components/SalaryForm";
import { StatusBanner } from "./components/StatusBanner";
import type { RegimeComparison, SalaryInput } from "./types";
import "./App.css";

function App() {
  const [comparison, setComparison] = useState<RegimeComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(salary: SalaryInput) {
    setLoading(true);
    setError(null);
    try {
      const result = await calculateTax(salary);
      setComparison(result);
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
        <pre className="raw-result">{JSON.stringify(comparison, null, 2)}</pre>
      )}
    </main>
  );
}

export default App;
