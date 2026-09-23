import type { EvaluationFormData, PrepareResponse } from "@/types/evaluation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function prepareEvaluation(data: EvaluationFormData): Promise<PrepareResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/v1/evaluations/prepare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: data.question,
        ai_response: data.ai_response,
        reference_answer: data.reference_answer || null,
        source_text: data.source_text || null,
      }),
    });
  } catch {
    throw new Error("Could not connect to the backend. Confirm that the API is running.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : "The request could not be prepared.";
    throw new Error(detail);
  }
  return response.json() as Promise<PrepareResponse>;
}
