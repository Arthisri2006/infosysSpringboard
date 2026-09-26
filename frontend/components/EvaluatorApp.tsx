"use client";

import { useState } from "react";
import { BatchEvaluation } from "./BatchEvaluation";
import { Dashboard } from "./Dashboard";
import { EvaluationForm } from "./EvaluationForm";

type View = "evaluate" | "batch" | "dashboard";

export function EvaluatorApp() {
  const [view, setView] = useState<View>("evaluate");
  return <><nav className="border-b border-slate-200 bg-white"><div className="mx-auto flex max-w-[1180px] gap-1 px-4 sm:px-6 lg:px-8">{(["evaluate", "batch", "dashboard"] as View[]).map((item) => <button type="button" key={item} onClick={() => setView(item)} className={`border-b-2 px-4 py-3 text-sm font-semibold capitalize ${view === item ? "border-[#2447d8] text-[#2447d8]" : "border-transparent text-slate-500 hover:text-slate-800"}`}>{item}</button>)}</div></nav><main className="mx-auto max-w-[1180px] px-4 py-8 sm:px-6 sm:py-12 lg:px-8 lg:py-14">{view === "evaluate" ? <EvaluationForm /> : view === "batch" ? <BatchEvaluation /> : <Dashboard />}</main></>;
}
