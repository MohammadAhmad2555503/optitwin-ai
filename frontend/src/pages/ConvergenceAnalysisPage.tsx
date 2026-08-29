import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import { errorMessage } from "../services/api";
import { analyseConvergence, listExperiments } from "../services/optimisationService";
import type { OptimisationExperiment } from "../types";

export default function ConvergenceAnalysisPage() {
  const [experiments, setExperiments] = useState<OptimisationExperiment[]>([]);
  const [experimentId, setExperimentId] = useState<number | "">("");
  const [analysis, setAnalysis] = useState<Record<string, any> | null>(null);
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
    setAnalysis(await analyseConvergence(experiment.convergence_curves));
  }

  if (loading) return <Loading label="Loading convergence analysis" />;
  if (!experiments.length) return <EmptyState title="No optimisation experiments" body="Run the optimisation lab first so this page can analyse stored curves." />;

  const selectedExperiment = experiments.find((item) => item.id === Number(experimentId));
  const curves = selectedExperiment?.convergence_curves ?? {};
  const firstCurve = Object.values(curves)[0] ?? [];
  const lossCurveData = firstCurve.map((_, index) => {
    const row: Record<string, number> = { iteration: index };
    Object.entries(curves).forEach(([name, curve]) => { row[name] = curve[index]; });
    return row;
  }).filter((_, index) => index % Math.max(1, Math.floor(firstCurve.length / 120)) === 0);
  const ranking = (analysis?.ranking ?? []) as Array<Record<string, number | string>>;
  const metricRows = analysis?.metrics ? Object.entries(analysis.metrics as Record<string, Record<string, number>>) : [];
  const finalLossData = metricRows.map(([optimiser, metrics]) => ({ optimiser, final_loss: metrics.final_loss }));
  const thresholdData = metricRows.map(([optimiser, metrics]) => ({ optimiser, iterations_to_threshold: metrics.iterations_to_threshold }));

  return (
    <div className="space-y-6">
      <div><p className="text-sm uppercase tracking-[0.18em] text-cyan">Loss dynamics</p><h2 className="text-3xl font-semibold text-white">Convergence Analysis</h2></div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <section className="app-surface flex flex-wrap items-end gap-4 p-5">
        <label className="min-w-[260px] flex-1"><span className="text-sm text-slate-300">Experiment</span><select className="field mt-2" value={experimentId} onChange={(event) => setExperimentId(Number(event.target.value))}>{experiments.map((item) => <option key={item.id} value={item.id}>{item.function_name} #{item.id}</option>)}</select></label>
        <button className="btn-primary" onClick={run}>Analyse</button>
      </section>
      {analysis ? (
        <>
          <section className="app-surface h-[360px] p-5">
            <h3 className="mb-4 font-semibold text-white">Loss curves</h3>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={lossCurveData}>
                <CartesianGrid stroke="#22313b" />
                <XAxis dataKey="iteration" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#101a22", border: "1px solid #22313b" }} />
                <Legend />
                {Object.keys(curves).map((name, index) => <Line key={name} dot={false} dataKey={name} stroke={["#4cc9f0", "#f7b955", "#39d98a", "#f87171"][index % 4]} />)}
              </LineChart>
            </ResponsiveContainer>
          </section>
          <div className="grid gap-4 lg:grid-cols-3">
            <section className="app-surface h-[300px] p-5">
              <h3 className="mb-4 font-semibold text-white">Final loss</h3>
              <ResponsiveContainer width="100%" height="82%"><BarChart data={finalLossData}><CartesianGrid stroke="#22313b" /><XAxis dataKey="optimiser" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip contentStyle={{ background: "#101a22", border: "1px solid #22313b" }} /><Bar dataKey="final_loss" fill="#4cc9f0" /></BarChart></ResponsiveContainer>
            </section>
            <section className="app-surface h-[300px] p-5">
              <h3 className="mb-4 font-semibold text-white">Iterations to threshold</h3>
              <ResponsiveContainer width="100%" height="82%"><BarChart data={thresholdData}><CartesianGrid stroke="#22313b" /><XAxis dataKey="optimiser" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip contentStyle={{ background: "#101a22", border: "1px solid #22313b" }} /><Bar dataKey="iterations_to_threshold" fill="#39d98a" /></BarChart></ResponsiveContainer>
            </section>
            <section className="app-surface h-[300px] p-5">
              <h3 className="mb-4 font-semibold text-white">Convergence ranking</h3>
              <ResponsiveContainer width="100%" height="82%"><BarChart data={ranking}><CartesianGrid stroke="#22313b" /><XAxis dataKey="optimiser" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip contentStyle={{ background: "#101a22", border: "1px solid #22313b" }} /><Bar dataKey="best_loss" fill="#f7b955" /></BarChart></ResponsiveContainer>
            </section>
          </div>
        </>
      ) : <EmptyState title="Ready for analysis" body="Choose an experiment and calculate final loss, best loss, threshold iteration, and convergence ranking." />}
    </div>
  );
}

