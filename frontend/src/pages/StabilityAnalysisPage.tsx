import { useEffect, useState } from "react";
import MetricCard from "../components/MetricCard";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import { errorMessage } from "../services/api";
import { alphaSensitivity, analyseStability, listExperiments } from "../services/optimisationService";
import type { OptimisationExperiment } from "../types";

export default function StabilityAnalysisPage() {
  const [experiments, setExperiments] = useState<OptimisationExperiment[]>([]);
  const [experimentId, setExperimentId] = useState<number | "">("");
  const [analysis, setAnalysis] = useState<Record<string, any> | null>(null);
  const [alpha, setAlpha] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const rows = await listExperiments();
        setExperiments(rows);
        setExperimentId(rows[0]?.id ?? "");
      } catch (err) {
        setError(errorMessage(err));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function run() {
    const experiment = experiments.find((item) => item.id === Number(experimentId));
    if (!experiment) return;
    setAnalysis(await analyseStability(experiment.convergence_curves));
    setAlpha(await alphaSensitivity(experiment.function_name, experiment.learning_rate, experiment.iterations));
  }

  if (loading) return <Loading label="Loading stability analysis" />;
  if (!experiments.length) return <EmptyState title="No optimisation experiments" body="Run an optimiser experiment to inspect oscillation, smoothness, divergence, and alpha sensitivity." />;

  const metrics = analysis?.metrics ? Object.entries(analysis.metrics as Record<string, Record<string, any>>) : [];

  return (
    <div className="space-y-6">
      <div><p className="text-sm uppercase tracking-[0.18em] text-cyan">Stability diagnostics</p><h2 className="text-3xl font-semibold text-white">Stability Analysis</h2></div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <section className="app-surface flex flex-wrap items-end gap-4 p-5">
        <label className="min-w-[260px] flex-1"><span className="text-sm text-slate-300">Experiment</span><select className="field mt-2" value={experimentId} onChange={(event) => setExperimentId(Number(event.target.value))}>{experiments.map((item) => <option key={item.id} value={item.id}>{item.function_name} #{item.id}</option>)}</select></label>
        <button className="btn-primary" onClick={run}>Run stability analysis</button>
      </section>
      {metrics.length ? (
        <div className="grid gap-4 md:grid-cols-4">
          {metrics.map(([name, item]) => (
            <MetricCard key={name} label={name} value={item.stability_score} helper={`osc ${item.oscillation_score}, smooth ${item.smoothness_score}`} />
          ))}
        </div>
      ) : <EmptyState title="No stability output yet" body="Run stability analysis to calculate smoothness, oscillation, and divergence flags." />}
      {alpha ? (
        <section className="app-surface overflow-x-auto p-5">
          <h3 className="font-semibold text-white">Alpha sensitivity: best alpha {alpha.best_alpha}</h3>
          <table className="mt-4 w-full min-w-[720px]"><tbody>{(alpha.results as Array<Record<string, any>>).map((row) => <tr key={row.alpha}><td className="table-cell text-slate-100">alpha {row.alpha}</td><td className="table-cell">best {row.best_loss}</td><td className="table-cell">final {row.final_loss}</td><td className="table-cell">stability {row.stability_score}</td><td className="table-cell">diverged {String(row.divergence_flag)}</td></tr>)}</tbody></table>
        </section>
      ) : null}
    </div>
  );
}

