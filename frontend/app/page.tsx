import { EvaluationForm } from "@/components/EvaluationForm";

export default function Home() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-16 max-w-[1180px] items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-[#2447d8] text-sm font-bold tracking-tight text-white">EL</span>
            <div>
              <p className="text-sm font-semibold leading-4 text-slate-900">Evidence Lab</p>
              <p className="mt-0.5 text-xs text-slate-500">LLM response evaluator</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs font-medium text-slate-600">
            <span className="h-2 w-2 rounded-full bg-emerald-500" aria-hidden="true" />
            Milestone 1
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-[1180px] px-4 py-8 sm:px-6 sm:py-12 lg:px-8 lg:py-14">
        <EvaluationForm />
      </main>
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1180px] flex-col gap-2 px-4 py-5 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <p>Evidence preparation only — no evaluation scores are generated.</p>
          <p>Explainable Multi-Agent RAG Evaluation</p>
        </div>
      </footer>
    </div>
  );
}
