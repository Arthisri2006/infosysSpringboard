"use client";

import { useState } from "react";
import { evaluateBatch } from "@/lib/api";
import type { BatchResponse, EvaluationFormData } from "@/types/evaluation";

const sample = JSON.stringify([{ question: "Who first walked on the Moon?", ai_response: "Neil Armstrong first walked on the Moon in 1969.", reference_answer: "Neil Armstrong was the first person to walk on the Moon in 1969.", source_text: "" }], null, 2);

export function BatchEvaluation() {
  const [value, setValue] = useState(sample);
  const [result, setResult] = useState<BatchResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit() {
    setError(""); setLoading(true);
    try { const parsed = JSON.parse(value) as EvaluationFormData[]; if (!Array.isArray(parsed)) throw new Error("Enter a JSON array."); setResult(await evaluateBatch(parsed)); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Batch evaluation failed."); }
    finally { setLoading(false); }
  }
  return (
    <section className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div><p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#335cff]">Milestone 3 batch workflow</p><h1 className="mt-3 text-4xl font-semibold tracking-[-0.03em] text-slate-950">Batch evaluation</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">Submit up to 50 evaluation records as JSON. Every item uses the same evidence and agent pipeline as the single-response workflow.</p><textarea value={value} onChange={(event) => setValue(event.target.value)} rows={18} spellCheck={false} className="mt-7 w-full rounded-xl border border-slate-300 bg-[#111827] p-5 font-mono text-sm leading-6 text-slate-100" /><button onClick={submit} disabled={loading} className="mt-4 min-h-11 rounded-lg bg-[#2447d8] px-5 text-sm font-semibold text-white disabled:bg-slate-400">{loading ? "Evaluating batch…" : "Run batch"}</button>{error && <p className="mt-4 text-sm text-rose-700">{error}</p>}</div>
      <aside className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:mt-20"><h2 className="font-semibold text-slate-900">Batch summary</h2>{result ? <><p className="mt-5 text-5xl font-semibold text-slate-950">{result.summary.count}</p><p className="mt-1 text-sm text-slate-500">responses evaluated</p><dl className="mt-6 space-y-3">{Object.entries(result.summary.average_scores).map(([name, score]) => <div key={name} className="flex justify-between border-t border-slate-100 pt-3 text-sm"><dt className="capitalize text-slate-500">{name}</dt><dd className="font-semibold tabular-nums text-slate-800">{score.toFixed(1)}</dd></div>)}</dl></> : <p className="mt-4 text-sm leading-6 text-slate-500">Results and average dimension scores will appear here.</p>}</aside>
    </section>
  );
}
