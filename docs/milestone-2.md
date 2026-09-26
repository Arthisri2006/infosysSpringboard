# Milestone 2 — Explainable Evaluation Agents

## Objective

Milestone 2 turns the Milestone 1 `EvidencePackage` into dimension-specific, explainable evaluation results without changing the RAG foundation.

## Implemented components

| Requirement | Implementation |
|---|---|
| Evaluation orchestration | `backend/orchestrator/evaluation_orchestrator.py` |
| Relevance evaluation | `backend/agents/relevance_agent.py` |
| Factual claim extraction | `backend/agents/claim_analyzer.py` |
| Accuracy evaluation | `backend/agents/accuracy_agent.py` |
| Hallucination detection | `backend/agents/hallucination_agent.py` |
| Shared semantic operations | `backend/agents/semantic.py` |
| Structured result contracts | `backend/models/results.py` |
| Evaluation API | `POST /api/v1/evaluations/evaluate` |
| Result UI | `frontend/components/EvaluationResults.tsx` |
| Agent tests | `tests/test_agents.py` |

## Working procedure

The orchestrator first prepares evidence through the existing Milestone 1 service. The relevance agent compares the question with the submitted response. The claim analyzer splits the response into traceable sentence-level claims, finds each claim's closest evidence, and applies explicit checks for numeric, negation, and named-entity conflicts. Accuracy summarizes support and contradiction. The hallucination result preserves every claim, its best evidence, status, and confidence.

The displayed hallucination dimension is a **groundedness score**, so higher is better. The result also includes the raw hallucination rate to avoid ambiguity.

## Validation

Automated tests cover supported claims, conflicting named entities, compatible numeric precision, score ranges, and structured verdict input. A real local MiniLM run was also checked with an Apollo 11 example and correctly classified the claim as supported.

## Limitations

Sentence-level splitting is deliberately lightweight, and contradiction detection uses transparent rules rather than full natural-language inference. Semantic similarity is evidence alignment, not proof of truth. These constraints are visible in result explanations and can later be upgraded behind the same interfaces.
