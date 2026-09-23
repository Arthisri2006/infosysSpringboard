"use client";

import { FormEvent, useState } from "react";
import { prepareEvaluation } from "@/lib/api";
import type { EvaluationFormData, PrepareResponse } from "@/types/evaluation";
import { EvaluationResults } from "./EvaluationResults";

const initial: EvaluationFormData = { question: "", ai_response: "", reference_answer: "", source_text: "" };

const limits: Record<keyof EvaluationFormData, number> = {
  question: 20_000,
  ai_response: 100_000,
  reference_answer: 100_000,
  source_text: 1_000_000,
};

export function EvaluationForm() {
  const [form, setForm] = useState(initial);
  const [result, setResult] = useState<PrepareResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (!form.question.trim() || !form.ai_response.trim()) {
      setError("Question and AI-generated response are required.");
      return;
    }
    setLoading(true);
    try { setResult(await prepareEvaluation(form)); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Unexpected request error."); }
    finally { setLoading(false); }
  }

  if (result) return <EvaluationResults result={result} onReset={() => { setResult(null); setForm(initial); }} />;

  const field = (
    name: keyof EvaluationFormData,
    label: string,
    required: boolean,
    rows: number,
    placeholder: string,
    helper: string,
  ) => (
    <div>
      <div className="mb-2 flex items-baseline justify-between gap-4">
        <label htmlFor={name} className="text-sm font-semibold text-slate-800">
          {label}{required && <span className="ml-1 text-rose-600" aria-hidden="true">*</span>}
        </label>
        <span className="text-xs text-slate-400">{required ? "Required" : "Optional"}</span>
      </div>
      <textarea
        id={name}
        name={name}
        value={form[name]}
        onChange={(event) => setForm({ ...form, [name]: event.target.value })}
        rows={rows}
        placeholder={placeholder}
        required={required}
        maxLength={limits[name]}
        aria-describedby={`${name}-help`}
        className="w-full resize-y rounded-lg border border-slate-300 bg-white px-3.5 py-3 text-[15px] leading-6 text-slate-900 shadow-sm placeholder:text-slate-400 hover:border-slate-400 focus:border-[#335cff] focus:ring-4 focus:ring-[#335cff]/10"
      />
      <div id={`${name}-help`} className="mt-1.5 flex items-start justify-between gap-4 text-xs leading-5 text-slate-500">
        <span>{helper}</span>
        <span className="shrink-0 tabular-nums">{form[name].length.toLocaleString()}</span>
      </div>
    </div>
  );

  return (
    <div className="grid items-start gap-8 lg:grid-cols-[320px_minmax(0,1fr)] lg:gap-12">
      <aside className="lg:sticky lg:top-8">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#335cff]">Evidence preparation</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-[-0.025em] text-slate-950 sm:text-4xl">
          Start with a response. Build the evidence around it.
        </h1>
        <p className="mt-4 text-[15px] leading-7 text-slate-600">
          Submit a question and its AI-generated answer. We will organize trusted references and retrieve relevant benchmark evidence for later evaluation.
        </p>

        <ol className="mt-7 grid grid-cols-3 gap-2 lg:grid-cols-1 lg:gap-0" aria-label="Preparation workflow">
          {[
            ["01", "Submit", "Question and response"],
            ["02", "Retrieve", "Reference evidence"],
            ["03", "Review", "Inspect provenance"],
          ].map(([number, title, detail], index) => (
            <li key={number} className="relative flex min-w-0 gap-3 py-3 lg:py-3.5">
              <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full border border-slate-300 bg-white text-[10px] font-bold text-slate-600">{number}</span>
              <span className="min-w-0">
                <span className="block text-sm font-semibold text-slate-800">{title}</span>
                <span className="mt-0.5 hidden text-xs text-slate-500 sm:block">{detail}</span>
              </span>
              {index < 2 && <span className="absolute left-3.5 top-10 hidden h-4 border-l border-slate-300 lg:block" aria-hidden="true" />}
            </li>
          ))}
        </ol>
      </aside>

      <form onSubmit={submit} className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-[0_8px_30px_rgba(15,23,42,0.06)]">
        <div className="border-b border-slate-200 px-5 py-5 sm:px-7">
          <h2 className="text-lg font-semibold text-slate-900">Evaluation input</h2>
          <p className="mt-1 text-sm text-slate-500">Fields marked with an asterisk are required.</p>
        </div>

        <div className="grid gap-6 px-5 py-6 sm:px-7 sm:py-7">
          {field("question", "Question", true, 4, "Enter the original question…", "The prompt the AI response was intended to answer.")}
          {field("ai_response", "AI-generated response", true, 7, "Paste the response you want to prepare for evaluation…", "Keep the response unchanged so future evaluation remains traceable.")}

          <fieldset className="border-t border-slate-200 pt-6">
            <legend className="mb-5 pr-3 text-sm font-semibold text-slate-800">Supporting evidence <span className="font-normal text-slate-400">(optional)</span></legend>
            <div className="grid gap-6 xl:grid-cols-2">
              {field("reference_answer", "Reference answer", false, 7, "Paste a trusted answer…", "Best when an approved answer already exists.")}
              {field("source_text", "Source material", false, 7, "Paste a supporting passage…", "Relevant passages are ranked without entering the permanent index.")}
            </div>
          </fieldset>
        </div>

        {error && (
          <div role="alert" className="mx-5 mb-5 flex gap-3 rounded-lg border border-rose-200 bg-rose-50 p-3.5 text-sm text-rose-800 sm:mx-7">
            <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-rose-100 text-xs font-bold" aria-hidden="true">!</span>
            <span>{error}</span>
          </div>
        )}

        <div className="flex flex-col gap-4 border-t border-slate-200 bg-slate-50 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-7">
          <p className="max-w-md text-xs leading-5 text-slate-500">Your source text is processed temporarily and is not added to the benchmark knowledge base.</p>
          <button
            disabled={loading}
            className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-[#2447d8] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1d3cbd] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2447d8] disabled:cursor-not-allowed disabled:bg-slate-400 sm:w-auto"
          >
            {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />}
            {loading ? "Preparing evidence…" : "Prepare evidence"}
          </button>
        </div>
      </form>
    </div>
  );
}
