# Batch CSV Guide

Save the file as UTF-8 CSV with one response per row.

```csv
question,ai_response,reference_answer,source_text
"What is RAG?","RAG retrieves evidence before generation.","Retrieval-augmented generation grounds output in retrieved context.",""
```

`question` and `ai_response` are required. `reference_answer` and `source_text` may be empty. Quotes are recommended when text contains commas. The upload limit is 200 rows per request. Invalid rows are skipped and shown in the batch summary; valid rows continue.

Use the interface fields to label the batch and identify the AI system or response source. This metadata powers dashboard filtering and cross-system comparison.
