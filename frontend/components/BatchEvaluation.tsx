"use client";

import { ChangeEvent, useState } from "react";
import { batchReportUrl, evaluateBatch, evaluateCsv } from "@/lib/api";
import type { BatchResponse, EvaluationFormData } from "@/types/evaluation";
import { vibrate } from "./HapticFeedback";

const sample = JSON.stringify([
  {
    question: "Who first walked on the Moon?",
    ai_response: "Neil Armstrong first walked on the Moon in 1969.",
    reference_answer: "Neil Armstrong was the first person to walk on the Moon in 1969.",
    source_text: "",
  },
], null, 2);

const csvTemplate = "question,ai_response,reference_answer,source_text\n\"Who first walked on the Moon?\",\"Neil Armstrong in 1969.\",\"Neil Armstrong was first in 1969.\",\"\"";

export function BatchEvaluation() {
  const [mode, setMode] = useState<"csv" | "json">("csv");
  const [jsonValue, setJsonValue] = useState(sample);
  const [csvValue, setCsvValue] = useState("");
  const [fileName, setFileName] = useState("");
  const [batchName, setBatchName] = useState("");
  const [systemName, setSystemName] = useState("");
  const [result, setResult] = useState<BatchResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function selectCsv(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setError("Choose a CSV file.");
      return;
    }
    setCsvValue(await file.text());
    setFileName(file.name);
    setError("");
  }

  function downloadTemplate() {
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([csvTemplate], { type: "text/csv" }));
    link.download = "evaluation-batch-template.csv";
    link.click();
    URL.revokeObjectURL(link.href);
  }

  async function submit() {
    setError("");
    setResult(null);
    setLoading(true);
    try {
      if (mode === "csv") {
        if (!csvValue.trim()) throw new Error("Choose a CSV file before running the batch.");
        setResult(await evaluateCsv(csvValue, batchName, systemName));
      } else {
        const parsed = JSON.parse(jsonValue) as EvaluationFormData[];
        if (!Array.isArray(parsed)) throw new Error("Enter a JSON array.");
        setResult(await evaluateBatch(parsed, batchName, systemName));
      }
      vibrate([16, 28, 16]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Batch evaluation failed.");
      vibrate([28, 35, 28]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <div className="border-b border-slate-200 pb-7">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8fa2ff]">Batch evaluation</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-[-0.035em] text-slate-950 sm:text-4xl">Evaluate a response set</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">Upload a CSV or paste JSON. Invalid rows are reported individually, while valid rows continue through the evaluation pipeline.</p>
      </div>

      <div className="grid gap-7 py-8 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm font-medium text-slate-700">Batch name
              <input value={batchName} onChange={(event) => setBatchName(event.target.value)} placeholder="September benchmark" className="mt-2 min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 focus:border-[#2447d8] focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="text-sm font-medium text-slate-700">AI system / response source
              <input value={systemName} onChange={(event) => setSystemName(event.target.value)} placeholder="System A" className="mt-2 min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 focus:border-[#2447d8] focus:ring-2 focus:ring-blue-100" />
            </label>
          </div>

          <div className="flex w-fit rounded-lg border border-slate-200 bg-white p-1" role="tablist" aria-label="Batch input format">
            {(["csv", "json"] as const).map((item) => <button key={item} type="button" onClick={() => setMode(item)} className={`min-h-9 rounded-md px-4 text-sm font-semibold uppercase ${mode === item ? "bg-slate-900 text-white" : "text-slate-500 hover:text-slate-900"}`}>{item}</button>)}
          </div>

          {mode === "csv" ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white p-6 sm:p-8">
              <div className="max-w-xl">
                <h2 className="text-lg font-semibold text-slate-900">Choose a CSV file</h2>
                <p className="mt-2 text-sm leading-6 text-slate-500">Required columns: <span className="font-medium text-slate-700">question</span> and <span className="font-medium text-slate-700">ai_response</span>. Optional: reference_answer and source_text.</p>
                <label className="mt-5 inline-flex min-h-11 cursor-pointer items-center rounded-lg bg-[#5b6ff5] px-5 text-sm font-semibold text-white shadow-[0_8px_24px_rgba(91,111,245,0.22)] hover:bg-[#7184ff]">
                  Browse files
                  <input type="file" accept=".csv,text/csv" onChange={selectCsv} className="sr-only" />
                </label>
                <button type="button" onClick={downloadTemplate} className="ml-3 min-h-11 px-2 text-sm font-semibold text-[#9aa9ff] hover:text-white hover:underline">Download template</button>
                {fileName && <p className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800">Selected: {fileName}</p>}
              </div>
            </div>
          ) : (
            <textarea value={jsonValue} onChange={(event) => setJsonValue(event.target.value)} rows={18} spellCheck={false} aria-label="Batch JSON" className="w-full rounded-xl border border-slate-300 bg-[#111827] p-5 font-mono text-sm leading-6 text-slate-100 focus:border-blue-400" />
          )}

          {error && <p role="alert" className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p>}
          <button onClick={submit} disabled={loading} className="min-h-12 w-full rounded-lg bg-[#5b6ff5] px-6 text-sm font-semibold text-white shadow-[0_8px_28px_rgba(91,111,245,0.28)] hover:bg-[#7184ff] disabled:cursor-wait disabled:bg-slate-400 sm:w-auto">{loading ? "Evaluating responses…" : "Run batch evaluation"}</button>
        </div>

        <aside className="h-fit rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:sticky lg:top-6">
          <h2 className="font-semibold text-slate-900">Batch summary</h2>
          {result ? <>
            <div className="mt-5 flex items-end gap-3"><p className="text-5xl font-semibold tracking-tight text-slate-950">{result.summary.count}</p><p className="pb-1 text-sm text-slate-500">evaluated</p></div>
            {result.summary.failed_count > 0 && <p className="mt-3 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">{result.summary.failed_count} row{result.summary.failed_count === 1 ? "" : "s"} skipped safely</p>}
            <dl className="mt-5 space-y-3">{Object.entries(result.summary.average_scores).map(([name, score]) => <div key={name} className="flex justify-between border-t border-slate-100 pt-3 text-sm"><dt className="capitalize text-slate-500">{name}</dt><dd className="font-semibold tabular-nums text-slate-800">{score.toFixed(1)}</dd></div>)}</dl>
            <a href={batchReportUrl(result.batch_id)} className="mt-6 flex min-h-11 items-center justify-center rounded-lg border border-[#667af4] text-sm font-semibold text-[#aab7ff] hover:bg-blue-50 hover:text-white">Download PDF report</a>
            {result.failures.length > 0 && <div className="mt-5 border-t border-slate-200 pt-4"><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Skipped rows</p>{result.failures.slice(0, 4).map((failure) => <p key={`${failure.row_number}-${failure.error}`} className="mt-2 text-xs leading-5 text-slate-600">Row {failure.row_number}: {failure.error}</p>)}</div>}
          </> : <p className="mt-4 text-sm leading-6 text-slate-500">Completed counts, score averages, row errors, and the downloadable report will appear here.</p>}
        </aside>
      </div>
    </section>
  );
}
