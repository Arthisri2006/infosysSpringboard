import type {
  BatchResponse,
  DashboardSummary,
  DashboardFilters,
  EvaluateResponse,
  EvaluationFormData,
  EvaluationResult,
} from "@/types/evaluation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, options);
  } catch {
    throw new Error("Could not connect to the evaluation API. Confirm that the backend is running and configured.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : "The request could not be completed.";
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

function payload(data: EvaluationFormData) {
  return {
    question: data.question,
    ai_response: data.ai_response,
    reference_answer: data.reference_answer || null,
    source_text: data.source_text || null,
  };
}

export function evaluateResponse(data: EvaluationFormData): Promise<EvaluateResponse> {
  return request("/api/v1/evaluations/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload(data)),
  });
}

export function evaluateBatch(items: EvaluationFormData[], batchName?: string, systemName?: string): Promise<BatchResponse> {
  return request("/api/v1/evaluations/batch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items: items.map(payload), batch_name: batchName || null, system_name: systemName || null }),
  });
}

export function evaluateCsv(csv: string, batchName: string, systemName: string): Promise<BatchResponse> {
  const query = new URLSearchParams();
  if (batchName) query.set("batch_name", batchName);
  if (systemName) query.set("system_name", systemName);
  return request(`/api/v1/evaluations/batch/csv?${query.toString()}`, {
    method: "POST",
    headers: { "Content-Type": "text/csv" },
    body: csv,
  });
}

export function getDashboard(filters: DashboardFilters = {}): Promise<DashboardSummary> {
  const query = new URLSearchParams({ limit: "50" });
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") query.set(key, String(value));
  });
  return request(`/api/v1/evaluations/dashboard?${query.toString()}`);
}

export function getEvaluation(id: string): Promise<EvaluationResult> {
  return request(`/api/v1/evaluations/${id}`);
}

export function batchReportUrl(batchId: string): string {
  return `${API_URL}/api/v1/evaluations/reports/batch/${batchId}.pdf`;
}
