import type {
  OptimizationResult,
  OptimizerInput,
  RegimeComparison,
  SalaryInput,
} from "./types";

const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function postJson<TResponse>(
  path: string,
  body: unknown,
): Promise<TResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "Could not reach the server. Is the backend running?");
  }

  if (!response.ok) {
    throw new ApiError(response.status, await extractErrorMessage(response));
  }

  return response.json() as Promise<TResponse>;
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (Array.isArray(data?.detail)) {
      return data.detail
        .map((item: { loc?: string[]; msg?: string }) =>
          item.loc ? `${item.loc.at(-1)}: ${item.msg}` : item.msg,
        )
        .join("; ");
    }
    if (typeof data?.detail === "string") {
      return data.detail;
    }
  } catch {
    // fall through to generic message below
  }
  return `Request failed with status ${response.status}`;
}

export function calculateTax(salary: SalaryInput): Promise<RegimeComparison> {
  return postJson<RegimeComparison>("/calculate", salary);
}

export function optimizeDeductions(
  params: OptimizerInput,
): Promise<OptimizationResult> {
  return postJson<OptimizationResult>("/optimize", params);
}
