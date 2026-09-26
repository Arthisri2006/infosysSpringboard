import type { AgentResult, EvaluateResponse } from "@/types/evaluation";
import { EvidenceCard } from "./EvidenceCard";

const scoreTone = (score: number | null) =>
  score === null ? "text-slate-500" : score >= 85 ? "text-emerald-700" : score >= 70 ? "text-blue-700" : score >= 45 ? "text-amber-700" : "text-rose-700";

function ScoreBlock({ title, result, detail }: { title: string; result: AgentResult; detail?: string }) {
  return (
    <article className="border-t border-slate-200 py-5 first:border-t-0 first:pt-0">
      <div className="flex items-start justify-between gap-4"><div><h3 className="text-sm font-semibold text-slate-900">{title}</h3><p className="mt-1 text-xs capitalize text-slate-500">{result.label}</p></div><p className={`text-3xl font-semibold tabular-nums ${scoreTone(result.score)}`}>{result.score?.toFixed(0) ?? "—"}</p></div>
      <p className="mt-3 text-sm leading-6 text-slate-600">{result.explanation}</p>
      {detail && <p className="mt-2 text-xs font-medium text-slate-500">{detail}</p>}
    </article>
  );
}

export function EvaluationResults({ result, onReset }: { result: EvaluateResponse; onReset: () => void }) {
  const evaluation = result.result;
  const pkg = evaluation.evidence_package;
  const evidence = [...pkg.source_text_evidence, ...pkg.retrieved_evidence];
  const verdict = evaluation.verdict.verdict.replaceAll("_", " ");
  return (
    <section>
      <div className="mb-8 flex flex-col gap-5 border-b border-slate-200 pb-7 sm:flex-row sm:items-end sm:justify-between">
        <div className="max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#8fa2ff]">Evaluation complete</p><div className="mt-3 flex flex-wrap items-end gap-x-5 gap-y-2"><h1 className="text-4xl font-semibold tracking-[-0.03em] text-slate-950 sm:text-5xl">{evaluation.verdict.overall_score.toFixed(0)}</h1><p className="pb-1 text-lg font-semibold capitalize text-slate-700">{verdict}</p></div><p className="mt-3 text-[15px] leading-6 text-slate-600">{evaluation.verdict.explanation}</p></div>
        <button onClick={onReset} className="inline-flex min-h-10 items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">New evaluation</button>
      </div>
      <div className="grid items-start gap-8 xl:grid-cols-[minmax(0,1fr)_360px] xl:gap-10">
        <div className="min-w-0 space-y-9">
          <section><div className="mb-4 flex items-baseline justify-between gap-4"><h2 className="text-xl font-semibold text-slate-950">Claim analysis</h2><span className="text-sm text-slate-500">{evaluation.hallucination.claims.length} claims</span></div><div className="overflow-hidden rounded-xl border border-slate-200 bg-white">{evaluation.hallucination.claims.map((claim, index) => <article key={`${claim.claim}-${index}`} className="border-t border-slate-100 p-5 first:border-t-0"><div className="flex flex-wrap items-start justify-between gap-3"><p className="max-w-3xl text-sm font-medium leading-6 text-slate-800">{claim.claim}</p><span className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${claim.status === "supported" ? "bg-emerald-50 text-emerald-700" : claim.status === "contradicted" ? "bg-rose-50 text-rose-700" : "bg-amber-50 text-amber-700"}`}>{claim.status}</span></div><p className="mt-2 text-xs leading-5 text-slate-500">{claim.explanation} Confidence {claim.confidence.toFixed(2)}.</p>{claim.best_evidence_text && <p className="mt-3 border-l-2 border-slate-200 pl-3 text-xs leading-5 text-slate-600">{claim.best_evidence_text}</p>}</article>)}</div></section>
          <section><h2 className="mb-4 text-xl font-semibold text-slate-950">Completeness gaps</h2><div className="rounded-xl border border-slate-200 bg-white p-5">{evaluation.completeness.missing_aspects.length ? <ul className="space-y-3 text-sm leading-6 text-slate-700">{evaluation.completeness.missing_aspects.map((aspect) => <li key={aspect} className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />{aspect}</li>)}</ul> : <p className="text-sm text-emerald-700">All derived evidence aspects are covered.</p>}</div></section>
          <section><div className="mb-4 flex items-baseline justify-between gap-4"><h2 className="text-xl font-semibold text-slate-950">Evidence</h2><span className="text-sm text-slate-500">{evidence.length} passages</span></div><div className="space-y-4">{evidence.length ? evidence.map((item, index) => <EvidenceCard key={item.chunk_id} item={item} index={index} />) : <p className="rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500">No chunked evidence was returned.</p>}</div></section>
        </div>
        <aside className="space-y-5 xl:sticky xl:top-8"><div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><ScoreBlock title="Relevance" result={evaluation.relevance} /><ScoreBlock title="Accuracy" result={evaluation.accuracy} /><ScoreBlock title="Groundedness" result={evaluation.hallucination} detail={`Hallucination rate ${((evaluation.hallucination.hallucination_rate ?? 0) * 100).toFixed(0)}%`} /><ScoreBlock title="Completeness" result={evaluation.completeness} /></div><div className="rounded-xl border border-slate-200 bg-slate-50 p-5"><p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Question</p><p className="mt-2 text-sm leading-6 text-slate-700">{pkg.question}</p><p className="mt-5 text-xs font-semibold uppercase tracking-wide text-slate-400">Evidence source</p><p className="mt-2 text-sm capitalize text-slate-700">{pkg.evidence_source_type.replaceAll("_", " ")}</p></div></aside>
      </div>
    </section>
  );
}
