import type { EvidenceChunk } from "@/types/evaluation";

export function EvidenceCard({ item, index }: { item: EvidenceChunk; index: number }) {
  return (
    <article className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div className="flex items-center justify-between gap-3 border-b border-slate-100 bg-slate-50 px-4 py-3 sm:px-5">
        <div className="flex min-w-0 items-center gap-3">
          <span className="grid h-7 w-7 shrink-0 place-items-center rounded-md border border-slate-200 bg-white text-xs font-bold text-slate-600">{index + 1}</span>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-800">{item.dataset?.replaceAll("_", " ") ?? "Submitted source"}</p>
            <p className="truncate text-xs text-slate-500">{item.source}</p>
          </div>
        </div>
        {item.similarity_score !== null && (
          <div className="shrink-0 text-right">
            <p className="text-[10px] font-medium uppercase tracking-wide text-slate-400">Similarity</p>
            <p className="mt-0.5 text-sm font-semibold tabular-nums text-slate-700">{item.similarity_score.toFixed(3)}</p>
          </div>
        )}
      </div>
      <p className="px-4 py-4 text-[15px] leading-7 text-slate-700 sm:px-5">{item.text}</p>
      <dl className="grid gap-x-6 gap-y-3 border-t border-slate-100 px-4 py-3 text-xs sm:grid-cols-2 sm:px-5">
        <div className="min-w-0"><dt className="text-slate-400">Document ID</dt><dd className="mt-0.5 truncate font-mono text-slate-600" title={item.document_id}>{item.document_id}</dd></div>
        <div><dt className="text-slate-400">Cosine distance</dt><dd className="mt-0.5 tabular-nums text-slate-600">{item.distance?.toFixed(4) ?? "Not applicable"}</dd></div>
      </dl>
    </article>
  );
}
