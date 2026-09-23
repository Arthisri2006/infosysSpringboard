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

export interface PrepareResponse {
  status: "ready_for_evaluation";
  message: string;
  evidence_package: EvidencePackage;
}

export interface EvaluationFormData {
  question: string;
  ai_response: string;
  reference_answer: string;
  source_text: string;
}

