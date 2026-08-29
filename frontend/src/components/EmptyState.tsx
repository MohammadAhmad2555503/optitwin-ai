import { CircleDashed } from "lucide-react";

export default function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="app-surface flex min-h-[180px] flex-col items-center justify-center px-6 text-center">
      <CircleDashed className="mb-3 h-8 w-8 text-cyan" />
      <h3 className="text-base font-semibold text-slate-100">{title}</h3>
      <p className="mt-1 max-w-md text-sm text-slate-400">{body}</p>
    </div>
  );
}

