import { EvaluatorApp } from "@/components/EvaluatorApp";
import { HapticFeedback } from "@/components/HapticFeedback";

export default function Home() {
  return (
    <div className="min-h-screen">
      <HapticFeedback />
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-[1180px] items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-[#2447d8] text-sm font-bold tracking-tight text-white">EL</span>
            <div>
              <p className="text-sm font-semibold leading-4 text-slate-900">Evidence Lab</p>
              <p className="mt-0.5 text-xs text-slate-500">LLM response evaluator</p>
            </div>
          </div>
          <div className="hidden items-center gap-2 text-xs font-medium text-slate-500 sm:flex">
            <span className="h-2 w-2 rounded-full bg-emerald-500" aria-hidden="true" />
            Local evaluation workspace
          </div>
        </div>
      </header>
      <EvaluatorApp />
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1180px] flex-col gap-2 px-4 py-5 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <p>Explainable semantic evaluation grounded in retrieved evidence.</p>
          <p>Private by design · Local-first implementation</p>
        </div>
      </footer>
    </div>
  );
}
