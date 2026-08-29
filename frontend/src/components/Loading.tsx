export default function Loading({ label = "Loading" }: { label?: string }) {
  return (
    <div className="flex min-h-[180px] items-center justify-center text-sm text-slate-400">
      <div className="mr-3 h-4 w-4 animate-spin rounded-full border-2 border-cyan border-t-transparent" />
      {label}
    </div>
  );
}

