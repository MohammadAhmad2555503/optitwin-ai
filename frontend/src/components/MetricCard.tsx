import type { LucideIcon } from "lucide-react";

export default function MetricCard({
  label,
  value,
  helper,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  helper?: string;
  icon?: LucideIcon;
}) {
  return (
    <div className="app-surface p-5">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-400">{label}</p>
        {Icon ? <Icon className="h-5 w-5 text-cyan" /> : null}
      </div>
      <p className="mt-3 text-2xl font-semibold text-white">{value}</p>
      {helper ? <p className="mt-1 text-xs text-slate-500">{helper}</p> : null}
    </div>
  );
}

