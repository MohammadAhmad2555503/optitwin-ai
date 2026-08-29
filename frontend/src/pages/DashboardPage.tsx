import { useEffect, useState } from "react";
import { Boxes, BrainCircuit, ClipboardList, FlaskConical, Gauge, LineChart, TrendingDown, Zap } from "lucide-react";
import MetricCard from "../components/MetricCard";
import Loading from "../components/Loading";
import { api, errorMessage } from "../services/api";
import type { DashboardSummary } from "../types";

interface ActivityRow {
  id: number;
  activity_type: string;
  description: string;
  created_at: string;
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [activity, setActivity] = useState<ActivityRow[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [summaryResponse, activityResponse] = await Promise.all([
          api.get<DashboardSummary>("/dashboard/summary"),
          api.get<{ activities: ActivityRow[] }>("/dashboard/recent-activity"),
        ]);
        setSummary(summaryResponse.data);
        setActivity(activityResponse.data.activities);
      } catch (err) {
        setError(errorMessage(err));
      }
    }
    load();
  }, []);

  if (!summary && !error) return <Loading label="Loading dashboard" />;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.18em] text-cyan">Operations intelligence</p>
        <h2 className="text-3xl font-semibold text-white">Dashboard</h2>
      </div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      {summary ? (
        <div className="grid gap-4 md:grid-cols-4">
          <MetricCard label="Scenarios" value={summary.total_scenarios} icon={Boxes} />
          <MetricCard label="Simulation runs" value={summary.total_simulation_runs} icon={Gauge} />
          <MetricCard label="Best strategy" value={summary.best_strategy ?? "No runs"} icon={Zap} />
          <MetricCard label="Avg delay reduction" value={`${summary.average_delay_reduction}%`} icon={TrendingDown} />
          <MetricCard label="Throughput lift" value={`${summary.average_throughput_improvement}%`} icon={LineChart} />
          <MetricCard label="Optimiser experiments" value={summary.total_optimiser_experiments} icon={FlaskConical} />
          <MetricCard label="RL runs" value={summary.total_rl_runs} icon={BrainCircuit} />
          <MetricCard label="Reports" value={summary.total_reports} icon={ClipboardList} />
        </div>
      ) : null}
      <section className="app-surface p-5">
        <h3 className="font-semibold text-white">Recent activity</h3>
        <div className="mt-4 divide-y divide-line">
          {activity.length ? activity.map((item) => (
            <div key={item.id} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
              <span className="text-slate-300">{item.description}</span>
              <span className="text-xs text-slate-500">{new Date(item.created_at).toLocaleString()}</span>
            </div>
          )) : <p className="py-6 text-sm text-slate-400">Run a scenario or experiment to populate the activity stream.</p>}
        </div>
      </section>
    </div>
  );
}

