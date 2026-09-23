# Research and Technical Understanding

## LLM response evaluation dimensions

These dimensions overlap, but they answer different questions and must not be treated as synonyms.

| Dimension | Question answered | Evidence needed |
|---|---|---|
| Relevance | Does the response directly address the user's question? | Question and response |
| Accuracy | Are the response's factual claims correct? | Trusted reference answer or external evidence |
| Factuality | Do claims agree with facts in the world? | Authoritative ground truth; broader than the supplied context |
| Faithfulness | Can each claim be supported by the evidence the model was given? | Response and supplied/retrieved context |
| Hallucination | Is a claim unsupported or contradicted by available evidence? | Atomic claims plus provenance-bearing evidence |
| Completeness | Does the response cover every material part of the request? | Question, expected aspects, reference/evidence, and response |

A faithful response can still be factually wrong if its source is wrong. A factually correct response can be unfaithful if it introduces true information absent from the permitted evidence. Relevance does not imply completeness: a response may discuss the right topic but omit a required sub-question.

## LLM-as-a-Judge

LLM-as-a-Judge uses a capable language model to apply an explicit rubric to another model's response. A judge receives the question, response, evidence, and scoring instructions; it returns a structured decision with reasons and citations.

Advantages include semantic understanding, tolerance of valid paraphrases, flexible natural-language rubrics, and lower cost than exhaustive human review. Limitations include judge hallucination, prompt sensitivity, nondeterminism, position/verbosity/style biases, self-preference, and poor calibration in specialized domains. A model can also confuse absence of evidence with contradiction.

The future agents therefore need:

- dimension-specific rubrics rather than one vague quality prompt;
- structured machine-validated outputs;
- claim-level evidence citations;
- stable prompts, model/version records, and low-variance settings;
- benchmark comparison and periodic human calibration;
- explicit handling of insufficient evidence.

Milestone 1 does not call a judge model. It builds the typed, provenance-rich evidence input needed to do that responsibly.

## Retrieval-Augmented Generation for evaluation

RAG normally retrieves documents and gives them to a model that generates an answer. Here, retrieval is instead an **evidence-grounding layer for evaluation**. The submitted answer already exists. The system retrieves passages against which future judges can test its claims.

The pipeline is:

1. **Ingestion:** load benchmark records from their maintained dataset source.
2. **Cleaning:** normalize Unicode and whitespace; reject empty values and duplicates without destroying punctuation or sentence structure.
3. **Chunking:** divide long context into overlapping windows so passages fit the embedding model while retaining local continuity.
4. **Embeddings:** map chunks and a query into vectors whose geometry captures semantic relatedness.
5. **Vector database:** persist vectors, text, stable identifiers, and provenance metadata.
6. **Semantic similarity:** compare the query vector with stored chunk vectors using cosine distance.
7. **Top-K retrieval:** return the best K candidates. K is a configurable recall/noise trade-off.
8. **Evidence packaging:** preserve text, dataset, source, document ID, score/distance, and other metadata for downstream judges.

Metadata is not decoration: without provenance, an evaluator cannot explain or audit why a passage was used. User-pasted source text is embedded and ranked in memory for that request, not inserted into the permanent benchmark collection.

## Ideas from evaluation frameworks

### RAGAS

[RAGAS documents](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/) component-level measures such as context precision/recall, response relevancy, faithfulness, factual correctness, and rubric-based scoring. Its faithfulness concept decomposes an answer into claims and checks whether retrieved context supports them. Ideas adopted here are separation of retrieval quality from answer quality, explicit inputs for question/response/context/reference, and benchmarkable metrics. We do not copy RAGAS implementations or include RAGAS as a dependency.

### TruLens

[TruLens' RAG Triad](https://www.trulens.org/getting_started/core_concepts/rag_triad/) separates context relevance, answer relevance, and groundedness. This illustrates why one aggregate score cannot diagnose whether failure came from retrieval or generation. Our future agent boundary mirrors that separation, and the `EvidencePackage` keeps the traceable context needed for groundedness checks. We do not copy TruLens or add its instrumentation layer.

## Benchmark datasets

### SQuAD

The Stanford Question Answering Dataset supplies questions, human reference answers, and Wikipedia context passages. It is valuable for testing whether retrieval returns the known supporting document and later for accuracy/completeness cases with extractive evidence. This project uses the SQuAD 1.1 validation split through Hugging Face (`rajpurkar/squad`). Its domain and extractive-answer format do not represent every real evaluation task.

### TruthfulQA

[TruthfulQA](https://arxiv.org/abs/2109.07958) contains questions designed to expose common human misconceptions and imitative falsehoods, with correct and incorrect answer sets. It is useful for future factuality and hallucination validation. Milestone 1 indexes the generation configuration's questions and best answers as evidence records. TruthfulQA is deliberately adversarial and small, so it is not a general-purpose knowledge base.

Together the datasets exercise two different evidence shapes: passage-grounded extractive QA and misconception-focused factual QA. They provide development benchmarks, not universal truth coverage.

