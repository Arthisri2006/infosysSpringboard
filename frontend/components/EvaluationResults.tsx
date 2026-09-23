import type { PrepareResponse } from "@/types/evaluation";
import { EvidenceCard } from "./EvidenceCard";

export function EvaluationResults({ result, onReset }: { result: PrepareResponse; onReset: () => void }) {
  const evidence = [...result.evidence_package.source_text_evidence, ...result.evidence_package.retrieved_evidence];
  const pkg = result.evidence_package;
  return (
    <section>
      <div className="mb-8 flex flex-col gap-5 border-b border-slate-200 pb-7 sm:flex-row sm:items-end sm:justify-between">
        <div className="max-w-2xl">
          <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-emerald-700">
            <span className="grid h-5 w-5 place-items-center rounded-full bg-emerald-100 text-[11px]" aria-hidden="true">✓</span>
            Preparation complete
          </div>
          <h1 className="text-3xl font-semibold tracking-[-0.025em] text-slate-950 sm:text-4xl">Evidence is ready for review.</h1>
          <p className="mt-3 text-[15px] leading-6 text-slate-600">Review the retrieved passages and their provenance before moving to judge-agent evaluation.</p>
        </div>
        <button onClick={onReset} className="inline-flex min-h-10 w-full items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm hover:border-slate-400 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#335cff] sm:w-auto">Start another</button>
      </div>

      <div className="grid items-start gap-8 lg:grid-cols-[minmax(0,1fr)_330px] lg:gap-10">
        <div className="min-w-0">
          {pkg.retrieval_metadata.warnings.map((warning) => <div key={warning} className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{warning}</div>)}
          <div className="mb-4 flex items-baseline justify-between gap-4">
            <h2 className="text-lg font-semibold text-slate-900">Retrieved evidence</h2>
            <span className="text-sm text-slate-500">{evidence.length} {evidence.length === 1 ? "passage" : "passages"}</span>
          </div>
          <div className="space-y-4">
            {evidence.length ? evidence.map((item, index) => <EvidenceCard key={item.chunk_id} item={item} index={index} />) : <p className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">No chunked evidence was returned. The supplied reference answer remains available as direct evidence.</p>}
          </div>
        </div>

        <aside className="order-first space-y-4 lg:order-last lg:sticky lg:top-8">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-4">
              <p className="text-sm font-semibold text-slate-900">Submission</p>
              <span className="text-xs capitalize text-slate-500">{pkg.evidence_source_type.replaceAll("_", " ")}</span>
            </div>
            <dl className="mt-4 space-y-5">
              <div><dt className="text-xs font-medium uppercase tracking-wide text-slate-400">Question</dt><dd className="mt-1.5 text-sm leading-6 text-slate-700">{pkg.question}</dd></div>
              <div><dt className="text-xs font-medium uppercase tracking-wide text-slate-400">AI response</dt><dd className="mt-1.5 text-sm leading-6 text-slate-700">{pkg.ai_response}</dd></div>
              {pkg.reference_answer && <div><dt className="text-xs font-medium uppercase tracking-wide text-slate-400">Reference answer</dt><dd className="mt-1.5 text-sm leading-6 text-slate-700">{pkg.reference_answer}</dd></div>}
            </dl>
          </div>
          <div className="rounded-lg border border-[#ccd6ff] bg-[#f4f6ff] p-4">
            <p className="text-sm font-semibold text-[#203785]">Ready for evaluation agents</p>
            <p className="mt-1.5 text-xs leading-5 text-[#52649f]">Scoring and judge-agent evaluation are intentionally deferred to Milestone 2.</p>
          </div>
        </aside>
      </div>
    </section>
  );
}
