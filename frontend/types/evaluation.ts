export interface EvidenceChunk {
  chunk_id: string;
  text: string;
  source: string;
  dataset: string | null;
  document_id: string;
  similarity_score: number | null;
  distance: number | null;
  metadata: Record<string, unknown>;
}

export interface EvidencePackage {
  evaluation_id: string;
  question: string;
  ai_response: string;
  reference_answer: string | null;
  evidence_source_type: "reference_answer" | "source_text" | "knowledge_base" | "combined" | "none";
  retrieved_evidence: EvidenceChunk[];
  source_text_evidence: EvidenceChunk[];
  retrieval_metadata: {
    query: string;
    requested_top_k: number;
    returned_count: number;
    collection: string | null;
    benchmark_retrieval_attempted: boolean;
    warnings: string[];
  };
}

export interface AgentResult {
  agent: string;
  score: number | null;
  label: "excellent" | "good" | "mixed" | "poor" | "unavailable";
  explanation: string;
  evidence_chunk_ids: string[];
  warnings: string[];
}

export interface ClaimAssessment {
  claim: string;
  status: "supported" | "unsupported" | "contradicted";
  confidence: number;
  best_evidence_text: string | null;
  evidence_chunk_id: string | null;
  explanation: string;
}

export interface EvaluationResult {
  evaluation_id: string;
  status: "completed";
  created_at: string;
  evidence_package: EvidencePackage;
  relevance: AgentResult;
  accuracy: AgentResult;
  hallucination: AgentResult & {
    hallucination_rate: number | null;
    supported_claims: number;
    unsupported_claims: number;
    contradicted_claims: number;
    claims: ClaimAssessment[];
  };
  completeness: AgentResult & {
    covered_aspects: string[];
    missing_aspects: string[];
  };
  verdict: {
    overall_score: number;
    verdict: "strong" | "acceptable" | "needs_review" | "poor";
    explanation: string;
    weights: Record<string, number>;
    component_scores: Record<string, number | null>;
  };
}

export interface EvaluateResponse {
  status: "completed";
  message: string;
  result: EvaluationResult;
}

export interface EvaluationFormData {
  question: string;
  ai_response: string;
  reference_answer: string;
  source_text: string;
}

export interface BatchResponse {
  batch_id: string;
  status: "completed";
  results: EvaluationResult[];
  summary: {
    count: number;
    average_scores: Record<string, number>;
    verdict_counts: Record<string, number>;
  };
}

export interface DashboardSummary {
  total_evaluations: number;
  average_scores: Record<string, number>;
  verdict_counts: Record<string, number>;
  recent_evaluations: Array<{
    evaluation_id: string;
    created_at: string;
    question: string;
    evidence_source_type: string;
    relevance_score: number | null;
    accuracy_score: number | null;
    groundedness_score: number | null;
    completeness_score: number | null;
    overall_score: number;
    verdict: string;
  }>;
}
