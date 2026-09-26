"use client";

import { useEffect, useState } from "react";
import { getDashboard } from "@/lib/api";
import type { DashboardSummary } from "@/types/evaluation";

export function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { getDashboard().then(setData).catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to load dashboard.")); }, []);
  if (error) return <div className="rounded-xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-800">{error}</div>;
  if (!data) return <p className="py-16 text-center text-sm text-slate-500">Loading evaluation history…</p>;
  const metrics = ["relevance", "accuracy", "groundedness", "completeness", "overall"];
  return (
    <section>
      <div className="border-b border-slate-200 pb-7"><p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#335cff]">Milestone 3 analytics</p><h1 className="mt-3 text-4xl font-semibold tracking-[-0.03em] text-slate-950">Evaluation dashboard</h1><p className="mt-3 text-sm text-slate-600">Summary of {data.total_evaluations} completed evaluations stored locally.</p></div>
      <div className="grid gap-5 py-8 sm:grid-cols-2 lg:grid-cols-5">{metrics.map((metric) => <div key={metric} className="border-t-2 border-[#335cff] pt-4"><p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{metric}</p><p className="mt-2 text-3xl font-semibold tabular-nums text-slate-900">{data.average_scores[metric]?.toFixed(0) ?? "0"}</p></div>)}</div>
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white"><div className="border-b border-slate-200 px-5 py-4"><h2 className="font-semibold text-slate-900">Recent evaluations</h2></div>{data.recent_evaluations.length ? data.recent_evaluations.map((item) => <div key={item.evaluation_id} className="grid gap-3 border-t border-slate-100 px-5 py-4 first:border-t-0 md:grid-cols-[minmax(0,1fr)_100px_100px] md:items-center"><div><p className="truncate text-sm font-medium text-slate-800">{item.question}</p><p className="mt-1 text-xs capitalize text-slate-400">{item.evidence_source_type.replaceAll("_", " ")} · {new Date(item.created_at).toLocaleString()}</p></div><p className="text-sm font-semibold capitalize text-slate-600">{item.verdict.replaceAll("_", " ")}</p><p className="text-right text-2xl font-semibold tabular-nums text-slate-900">{item.overall_score.toFixed(0)}</p></div>) : <p className="p-8 text-center text-sm text-slate-500">Run an evaluation to populate the dashboard.</p>}</div>
    </section>
  );
}
