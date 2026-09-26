"use client";

import { useCallback, useEffect, useState } from "react";
import { batchReportUrl, getDashboard, getEvaluation } from "@/lib/api";
import type { DashboardFilters, DashboardSummary, EvaluationResult } from "@/types/evaluation";

const dimensions = ["relevance", "accuracy", "groundedness", "completeness", "overall"];
const outcomeStyle: Record<string, string> = {
  pass: "bg-emerald-50 text-emerald-800 border-emerald-200",
  needs_improvement: "bg-amber-50 text-amber-800 border-amber-200",
  fail: "bg-rose-50 text-rose-800 border-rose-200",
};

function title(value: string) { return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()); }

export function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [filters, setFilters] = useState<DashboardFilters>({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<EvaluationResult | null>(null);

  const load = useCallback(async (next: DashboardFilters) => {
    setLoading(true); setError("");
    try { setData(await getDashboard(next)); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to load dashboard."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void load({}); }, [load]);

  function change(key: keyof DashboardFilters, value: string) {
    const next = { ...filters, [key]: value || undefined };
    setFilters(next);
    void load(next);
  }

  async function openEvaluation(id: string) {
    try { setSelected(await getEvaluation(id)); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to load evaluation details."); }
  }

  if (error && !data) return <div className="rounded-xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-800">{error}</div>;
  if (!data) return <p className="py-16 text-center text-sm text-slate-500">Loading evaluation analytics…</p>;
  const maxTrend = Math.max(...data.batch_trends.map((item) => item.average_scores.overall), 100);

  return (
    <section>
      <div className="flex flex-col gap-5 border-b border-slate-200 pb-7 md:flex-row md:items-end md:justify-between">
        <div><p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8fa2ff]">Scoring analytics</p><h1 className="mt-3 text-3xl font-semibold tracking-[-0.035em] text-slate-950 sm:text-4xl">Evaluation dashboard</h1><p className="mt-3 text-sm text-slate-600">Stored results only. Every total can be traced to an individual evaluation.</p></div>
        <p className="text-sm text-slate-500">{loading ? "Updating…" : `${data.total_evaluations} matching evaluations`}</p>
      </div>

      <div className="grid gap-3 border-b border-slate-200 py-5 sm:grid-cols-2 lg:grid-cols-5">
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Outcome
          <select value={filters.verdict ?? ""} onChange={(event) => change("verdict", event.target.value)} className="mt-2 min-h-10 w-full rounded-md border border-slate-300 bg-white px-2 text-sm font-normal normal-case text-slate-800"><option value="">All outcomes</option><option value="pass">Pass</option><option value="needs_improvement">Needs improvement</option><option value="fail">Fail</option></select>
        </label>
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Batch
          <select value={filters.batch_id ?? ""} onChange={(event) => change("batch_id", event.target.value)} className="mt-2 min-h-10 w-full rounded-md border border-slate-300 bg-white px-2 text-sm font-normal normal-case text-slate-800"><option value="">All batches</option>{data.available_batches.map((batch) => <option key={batch.batch_id} value={batch.batch_id}>{batch.batch_name}</option>)}</select>
        </label>
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">System
          <select value={filters.system_name ?? ""} onChange={(event) => change("system_name", event.target.value)} className="mt-2 min-h-10 w-full rounded-md border border-slate-300 bg-white px-2 text-sm font-normal normal-case text-slate-800"><option value="">All systems</option>{data.available_systems.map((system) => <option key={system}>{system}</option>)}</select>
        </label>
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Minimum score
          <input type="number" min="0" max="100" value={filters.min_score ?? ""} onChange={(event) => change("min_score", event.target.value)} className="mt-2 min-h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm font-normal text-slate-800" />
        </label>
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Maximum score
          <input type="number" min="0" max="100" value={filters.max_score ?? ""} onChange={(event) => change("max_score", event.target.value)} className="mt-2 min-h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm font-normal text-slate-800" />
        </label>
      </div>

      {error && <p className="mt-5 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p>}

      <div className="grid gap-4 py-7 md:grid-cols-3">
        {(["pass", "needs_improvement", "fail"] as const).map((outcome) => <div key={outcome} className={`rounded-xl border p-5 ${outcomeStyle[outcome]}`}><p className="text-xs font-semibold uppercase tracking-wide opacity-75">{title(outcome)}</p><div className="mt-3 flex items-end justify-between"><p className="text-4xl font-semibold tabular-nums">{data.outcomes.counts[outcome] ?? 0}</p><p className="pb-1 text-sm font-semibold tabular-nums">{(data.outcomes.percentages[outcome] ?? 0).toFixed(1)}%</p></div></div>)}
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(300px,.75fr)]">
        <div className="rounded-xl border border-slate-200 bg-white p-5 sm:p-6">
          <h2 className="font-semibold text-slate-900">Average dimension scores</h2>
          <div className="mt-6 space-y-5">{dimensions.map((dimension) => <div key={dimension}><div className="mb-2 flex justify-between text-sm"><span className="capitalize text-slate-600">{dimension}</span><span className="font-semibold tabular-nums text-slate-900">{(data.average_scores[dimension] ?? 0).toFixed(1)}</span></div><div className="h-2.5 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-gradient-to-r from-[#5b6ff5] to-[#91a2ff] shadow-[0_0_18px_rgba(124,145,255,0.34)]" style={{ width: `${Math.min(data.average_scores[dimension] ?? 0, 100)}%` }} /></div></div>)}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5 sm:p-6">
          <h2 className="font-semibold text-slate-900">Evidence quality signals</h2>
          <dl className="mt-5 space-y-5"><div><dt className="text-xs uppercase tracking-wide text-slate-500">Responses with unsupported claims</dt><dd className="mt-1 text-3xl font-semibold tabular-nums text-slate-950">{data.hallucination.response_rate.toFixed(1)}%</dd><p className="mt-1 text-xs text-slate-500">{data.hallucination.unsupported_claims} unsupported · {data.hallucination.contradicted_claims} contradicted</p></div><div className="border-t border-slate-100 pt-5"><dt className="text-xs uppercase tracking-wide text-slate-500">Responses missing information</dt><dd className="mt-1 text-3xl font-semibold tabular-nums text-slate-950">{data.completeness.response_rate.toFixed(1)}%</dd><p className="mt-1 text-xs text-slate-500">{data.completeness.total_missing_aspects} missing aspects identified</p></div></dl>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-5 sm:p-6"><h2 className="font-semibold text-slate-900">Overall score distribution</h2><div className="mt-6 grid h-44 grid-cols-4 items-end gap-3">{Object.entries(data.score_distributions.overall ?? {}).map(([band, count]) => { const percent = data.total_evaluations ? count / data.total_evaluations * 100 : 0; return <div key={band} className="flex h-full flex-col justify-end text-center"><span className="mb-2 text-xs font-semibold text-slate-700">{count}</span><div className="mx-auto w-full max-w-14 rounded-t bg-[#7992ff]" style={{ height: `${Math.max(percent, count ? 8 : 1)}%` }} /><span className="mt-2 text-xs text-slate-500">{band}</span></div>; })}</div></div>
        <div className="rounded-xl border border-slate-200 bg-white p-5 sm:p-6"><h2 className="font-semibold text-slate-900">Frequent issues</h2>{data.frequent_issues.length ? <div className="mt-5 space-y-4">{data.frequent_issues.map((item) => <div key={item.issue}><div className="flex justify-between text-sm"><span className="text-slate-600">{item.issue}</span><span className="font-semibold text-slate-900">{item.count}</span></div><div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-100"><div className="h-full bg-amber-500" style={{ width: `${Math.min(item.count / Math.max(data.total_evaluations, 1) * 100, 100)}%` }} /></div></div>)}</div> : <p className="mt-5 text-sm text-slate-500">No recurring issues in the current selection.</p>}</div>
      </div>

      <div className="mt-6 rounded-xl border border-slate-200 bg-white p-5 sm:p-6"><div className="flex items-center justify-between"><h2 className="font-semibold text-slate-900">Batch trend</h2><p className="text-xs text-slate-500">Average overall score</p></div>{data.batch_trends.length ? <div className="mt-6 space-y-4">{data.batch_trends.map((point) => <div key={point.batch_id} className="grid gap-2 sm:grid-cols-[180px_minmax(0,1fr)_52px] sm:items-center"><div><p className="truncate text-sm font-medium text-slate-800">{point.batch_name}</p><p className="text-xs text-slate-400">{point.system_name ?? "Unspecified system"}</p></div><div className="h-3 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-emerald-500" style={{ width: `${point.average_scores.overall / maxTrend * 100}%` }} /></div><p className="text-right text-sm font-semibold tabular-nums text-slate-800">{point.average_scores.overall.toFixed(1)}</p></div>)}</div> : <p className="mt-5 text-sm text-slate-500">Run at least one batch to populate the trend view.</p>}</div>

      <div className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white"><div className="flex items-center justify-between border-b border-slate-200 px-5 py-4"><h2 className="font-semibold text-slate-900">Evaluation drill-down</h2>{filters.batch_id && <a href={batchReportUrl(filters.batch_id)} className="text-sm font-semibold text-[#9aa9ff] hover:text-white hover:underline">Export selected batch PDF</a>}</div>{data.recent_evaluations.length ? data.recent_evaluations.map((item) => <button type="button" onClick={() => void openEvaluation(item.evaluation_id)} key={item.evaluation_id} className="grid w-full gap-3 border-t border-slate-100 px-5 py-4 text-left first:border-t-0 hover:bg-slate-50 md:grid-cols-[minmax(0,1fr)_170px_95px] md:items-center"><div><p className="truncate text-sm font-medium text-slate-800">{item.question}</p><p className="mt-1 text-xs text-slate-400">{item.batch_name ?? "Single evaluation"} · {item.system_name ?? title(item.evidence_source_type)}</p><div className="mt-2 flex flex-wrap gap-1">{item.issue_tags.map((tag) => <span key={tag} className="rounded bg-slate-100 px-2 py-0.5 text-[11px] text-slate-600">{tag}</span>)}</div></div><span className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold ${outcomeStyle[item.outcome]}`}>{title(item.outcome)}</span><p className="text-left text-2xl font-semibold tabular-nums text-slate-900 md:text-right">{item.overall_score.toFixed(0)}</p></button>) : <p className="p-8 text-center text-sm text-slate-500">No evaluations match the current filters.</p>}</div>

      {selected && <div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-950/45 p-0 sm:items-center sm:p-6" role="dialog" aria-modal="true" aria-label="Evaluation details"><div className="max-h-[92vh] w-full max-w-3xl overflow-y-auto rounded-t-2xl bg-white shadow-2xl sm:rounded-2xl"><div className="sticky top-0 flex items-center justify-between border-b border-slate-200 bg-white px-5 py-4"><h2 className="font-semibold text-slate-900">Evaluation details</h2><button onClick={() => setSelected(null)} className="min-h-9 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-600">Close</button></div><div className="space-y-6 p-5 sm:p-7"><div><p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Question</p><p className="mt-2 text-base font-medium text-slate-900">{selected.evidence_package.question}</p></div><div><p className="text-xs font-semibold uppercase tracking-wide text-slate-400">AI response</p><p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{selected.evidence_package.ai_response}</p></div><div className="grid grid-cols-2 gap-3 sm:grid-cols-5">{dimensions.map((dimension) => { const score = dimension === "overall" ? selected.verdict.overall_score : dimension === "groundedness" ? selected.hallucination.score : selected[dimension as "relevance" | "accuracy" | "completeness"].score; return <div key={dimension} className="rounded-lg bg-slate-50 p-3"><p className="text-[10px] uppercase text-slate-400">{dimension}</p><p className="mt-1 text-xl font-semibold">{score?.toFixed(0) ?? "—"}</p></div>; })}</div>{[["Relevance", selected.relevance.explanation], ["Accuracy", selected.accuracy.explanation], ["Hallucination", selected.hallucination.explanation], ["Completeness", selected.completeness.explanation]].map(([name, explanation]) => <div key={name}><p className="text-sm font-semibold text-slate-900">{name}</p><p className="mt-1 text-sm leading-6 text-slate-600">{explanation}</p></div>)}</div></div></div>}
    </section>
  );
}
