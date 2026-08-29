import { FormEvent, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import EmptyState from "../components/EmptyState";
import { errorMessage } from "../services/api";
import { runExperiment } from "../services/optimisationService";
import type { OptimisationExperiment } from "../types";

const optimisers = ["Gradient Descent", "SGD", "Adam", "Fractional GD"];
const colours = ["#4cc9f0", "#f7b955", "#39d98a", "#f87171"];

export default function OptimisationLabPage() {
  const [functionName, setFunctionName] = useState("rosenbrock");
  const [learningRate, setLearningRate] = useState(0.01);
  const [iterations, setIterations] = useState(250);
  const [alpha, setAlpha] = useState(0.7);
  const [selected, setSelected] = useState<string[]>(optimisers);
  const [experiment, setExperiment] = useState<OptimisationExperiment | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      setExperiment(await runExperiment({ function_name: functionName, optimisers: selected, learning_rate: learningRate, iterations, alpha, seed: 42 }));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const curves = experiment?.convergence_curves ?? {};
  const firstCurve = Object.values(curves)[0] ?? [];
  const chartData = firstCurve.map((_, index) => {
    const row: Record<string, number> = { iteration: index };
    Object.entries(curves).forEach(([name, curve]) => { row[name] = curve[index]; });
    return row;
  }).filter((_, index) => index % Math.max(1, Math.floor(iterations / 120)) === 0);

  return (
    <form onSubmit={submit} className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.18em] text-cyan">Mathematical optimisation</p>
        <h2 className="text-3xl font-semibold text-white">Optimisation Lab</h2>
      </div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <section className="app-surface grid gap-4 p-5 md:grid-cols-5">
        <label>
          <span className="text-sm text-slate-300">Benchmark</span>
          <select className="field mt-2" value={functionName} onChange={(event) => setFunctionName(event.target.value)}>
            <option value="sphere">Sphere</option>
            <option value="rosenbrock">Rosenbrock</option>
            <option value="rastrigin">Rastrigin</option>
          </select>
        </label>
        <label><span className="text-sm text-slate-300">Learning rate</span><input className="field mt-2" type="number" step="0.001" value={learningRate} onChange={(event) => setLearningRate(Number(event.target.value))} /></label>
        <label><span className="text-sm text-slate-300">Iterations</span><input className="field mt-2" type="number" value={iterations} onChange={(event) => setIterations(Number(event.target.value))} /></label>
        <label><span className="text-sm text-slate-300">Alpha</span><input className="field mt-2" type="number" min="0.1" max="1" step="0.05" value={alpha} onChange={(event) => setAlpha(Number(event.target.value))} /></label>
        <button className="btn-primary self-end" disabled={busy}>{busy ? "Running..." : "Run experiment"}</button>
        <div className="md:col-span-5 flex flex-wrap gap-3">
          {optimisers.map((name) => (
            <label key={name} className="flex items-center gap-2 rounded-md border border-line bg-ink px-3 py-2 text-sm text-slate-300">
              <input type="checkbox" checked={selected.includes(name)} onChange={() => setSelected((current) => current.includes(name) ? current.filter((item) => item !== name) : [...current, name])} />
              {name}
            </label>
          ))}
        </div>
      </section>
      {experiment ? (
        <>
          <section className="app-surface h-[380px] p-5">
            <h3 className="mb-4 font-semibold text-white">Loss curves</h3>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={chartData}>
                <CartesianGrid stroke="#22313b" />
                <XAxis dataKey="iteration" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" domain={["auto", "auto"]} />
                <Tooltip contentStyle={{ background: "#101a22", border: "1px solid #22313b" }} />
                <Legend />
                {Object.keys(experiment.convergence_curves).map((name, index) => <Line key={name} dot={false} dataKey={name} stroke={colours[index % colours.length]} />)}
              </LineChart>
            </ResponsiveContainer>
          </section>
          <section className="app-surface overflow-x-auto p-5">
            <table className="w-full min-w-[820px]">
              <thead className="text-left text-xs uppercase text-slate-500"><tr><th className="table-cell">Optimiser</th><th className="table-cell">Best</th><th className="table-cell">Final</th><th className="table-cell">Threshold iter</th><th className="table-cell">Stability</th></tr></thead>
              <tbody>
                {Object.entries(experiment.results).map(([name, metrics]) => (
                  <tr key={name}><td className="table-cell text-slate-100">{name}</td><td className="table-cell">{metrics.best_loss as number}</td><td className="table-cell">{metrics.final_loss as number}</td><td className="table-cell">{metrics.iterations_to_threshold as number}</td><td className="table-cell">{metrics.stability_score as number}</td></tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      ) : <EmptyState title="No experiment yet" body="Select a function and compare optimisers, including the fractional-inspired memory update." />}
    </form>
  );
}

