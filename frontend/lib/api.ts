import type {
  BatchResponse,
  DashboardSummary,
  EvaluateResponse,
  EvaluationFormData,
} from "@/types/evaluation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

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

export function evaluateBatch(items: EvaluationFormData[]): Promise<BatchResponse> {
  return request("/api/v1/evaluations/batch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items: items.map(payload) }),
  });
}

export function getDashboard(): Promise<DashboardSummary> {
  return request("/api/v1/evaluations/dashboard?limit=20");
}
