import { useState } from "react";
import type { FormEvent } from "react";
import { CITY_OPTIONS, OTHER_CITY_OPTION } from "../data/hraCities";
import type { InputFrequency, SalaryInput } from "../types";

interface SalaryFormProps {
  onSubmit: (salary: SalaryInput) => void;
  loading: boolean;
}

interface FormState {
  inputFrequency: InputFrequency;
  basic: string;
  hraReceived: string;
  lta: string;
  specialAllowance: string;
  employerNpsPercent: string;
  citySelect: string;
  cityOther: string;
  rentPaid: string;
  section80C: string;
  section80D: string;
  npsSelf: string;
  homeLoanInterest: string;
}

const initialState: FormState = {
  inputFrequency: "annual",
  basic: "",
  hraReceived: "",
  lta: "",
  specialAllowance: "",
  employerNpsPercent: "",
  citySelect: CITY_OPTIONS[0],
  cityOther: "",
  rentPaid: "",
  section80C: "",
  section80D: "",
  npsSelf: "",
  homeLoanInterest: "",
};

function toNumber(value: string): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function SalaryForm({ onSubmit, loading }: SalaryFormProps) {
  const [form, setForm] = useState<FormState>(initialState);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const city =
      form.citySelect === OTHER_CITY_OPTION ? form.cityOther.trim() : form.citySelect;

    const salary: SalaryInput = {
      basic: toNumber(form.basic),
      hra_received: toNumber(form.hraReceived),
      lta: toNumber(form.lta),
      special_allowance: toNumber(form.specialAllowance),
      employer_nps_percent: toNumber(form.employerNpsPercent),
      city,
      rent_paid: toNumber(form.rentPaid),
      input_frequency: form.inputFrequency,
      investments: {
        "80C": toNumber(form.section80C),
        "80D": toNumber(form.section80D),
        nps_self: toNumber(form.npsSelf),
        home_loan_interest: toNumber(form.homeLoanInterest),
      },
    };

    onSubmit(salary);
  }

  const period = form.inputFrequency === "monthly" ? "monthly" : "annual";

  return (
    <form className="salary-form" onSubmit={handleSubmit}>
      <fieldset>
        <legend>Salary</legend>

        <div className="frequency-toggle" role="radiogroup" aria-label="Salary input frequency">
          <label>
            <input
              type="radio"
              name="inputFrequency"
              value="annual"
              checked={form.inputFrequency === "annual"}
              onChange={() => update("inputFrequency", "annual")}
            />
            Annual
          </label>
          <label>
            <input
              type="radio"
              name="inputFrequency"
              value="monthly"
              checked={form.inputFrequency === "monthly"}
              onChange={() => update("inputFrequency", "monthly")}
            />
            Monthly
          </label>
        </div>

        <label>
          Basic salary ({period})
          <input
            type="number"
            min="0"
            required
            value={form.basic}
            onChange={(e) => update("basic", e.target.value)}
          />
        </label>

        <label>
          HRA received ({period})
          <input
            type="number"
            min="0"
            value={form.hraReceived}
            onChange={(e) => update("hraReceived", e.target.value)}
          />
        </label>

        <label>
          LTA (annual)
          <input
            type="number"
            min="0"
            value={form.lta}
            onChange={(e) => update("lta", e.target.value)}
          />
        </label>

        <label>
          Special allowance ({period})
          <input
            type="number"
            min="0"
            value={form.specialAllowance}
            onChange={(e) => update("specialAllowance", e.target.value)}
          />
        </label>

        <label>
          Employer NPS contribution (% of basic)
          <input
            type="number"
            min="0"
            max="100"
            value={form.employerNpsPercent}
            onChange={(e) => update("employerNpsPercent", e.target.value)}
          />
        </label>
      </fieldset>

      <fieldset>
        <legend>Rent &amp; city (for HRA exemption)</legend>

        <label>
          City
          <select
            value={form.citySelect}
            onChange={(e) => update("citySelect", e.target.value)}
          >
            {CITY_OPTIONS.map((city) => (
              <option key={city} value={city}>
                {city}
              </option>
            ))}
          </select>
        </label>

        {form.citySelect === OTHER_CITY_OPTION && (
          <label>
            City name
            <input
              type="text"
              placeholder="e.g. Pune"
              required
              value={form.cityOther}
              onChange={(e) => update("cityOther", e.target.value)}
            />
          </label>
        )}

        <label>
          Rent paid ({period})
          <input
            type="number"
            min="0"
            value={form.rentPaid}
            onChange={(e) => update("rentPaid", e.target.value)}
          />
        </label>
      </fieldset>

      <fieldset>
        <legend>Investment declarations</legend>
        <p className="fieldset-note">
          Always entered as yearly amounts, even if your salary above is
          monthly - these are typically declared once a year regardless of
          how often you're paid.
        </p>

        <label>
          Section 80C (ELSS, PPF, life insurance, etc.)
          <input
            type="number"
            min="0"
            value={form.section80C}
            onChange={(e) => update("section80C", e.target.value)}
          />
        </label>

        <label>
          Section 80D (health insurance premium)
          <input
            type="number"
            min="0"
            value={form.section80D}
            onChange={(e) => update("section80D", e.target.value)}
          />
        </label>

        <label>
          NPS self-contribution (80CCD(1B))
          <input
            type="number"
            min="0"
            value={form.npsSelf}
            onChange={(e) => update("npsSelf", e.target.value)}
          />
        </label>

        <label>
          Home loan interest (24(b))
          <input
            type="number"
            min="0"
            value={form.homeLoanInterest}
            onChange={(e) => update("homeLoanInterest", e.target.value)}
          />
        </label>
      </fieldset>

      <button type="submit" disabled={loading}>
        {loading ? "Calculating..." : "Compare regimes"}
      </button>
    </form>
  );
}
