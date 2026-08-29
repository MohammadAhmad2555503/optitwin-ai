import { FormEvent, useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import { errorMessage } from "../services/api";
import { listScenarios } from "../services/scenarioService";
import { runWhatIf } from "../services/simulationService";
import type { Scenario } from "../types";

export default function WhatIfAnalysisPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState<number | "">("");
  const [mods, setMods] = useState({ workers: 22, robots: 10, orders_per_hour: 210, robot_failure_probability: 0.03 });
  const [result, setResult] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const rows = await listScenarios();
        setScenarios(rows);
        setScenarioId(rows[0]?.id ?? "");
      } catch (err) {
        setError(errorMessage(err));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!scenarioId) return;
    setBusy(true);
    try {
      setResult(await runWhatIf(Number(scenarioId), mods));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Loading label="Loading what-if lab" />;
  if (!scenarios.length) return <EmptyState title="No scenario available" body="Create a baseline scenario before exploring parameter deltas." />;

  return (
    <form onSubmit={submit} className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.18em] text-cyan">Decision sensitivity</p>
        <h2 className="text-3xl font-semibold text-white">What-if Analysis</h2>
      </div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <section className="app-surface grid gap-4 p-5 md:grid-cols-5">
        <label className="md:col-span-2">
          <span className="text-sm text-slate-300">Scenario</span>
          <select className="field mt-2" value={scenarioId} onChange={(event) => setScenarioId(Number(event.target.value))}>
            {scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
          </select>
        </label>
        {Object.entries(mods).map(([key, value]) => (
          <label key={key}>
            <span className="text-sm capitalize text-slate-300">{key.replace(/_/g, " ")}</span>
            <input className="field mt-2" type="number" step="0.01" value={value} onChange={(event) => setMods({ ...mods, [key]: Number(event.target.value) })} />
          </label>
        ))}
        <button className="btn-primary self-end" disabled={busy}>{busy ? "Running..." : "Run what-if"}</button>
      </section>
      {result ? (
        <section className="grid gap-4 md:grid-cols-3">
          {["delayed_orders", "throughput_per_hour", "cost_per_order"].map((metric) => (
            <div key={metric} className="app-surface p-5">
              <p className="text-sm capitalize text-slate-400">{metric.replace(/_/g, " ")}</p>
              <p className="mt-2 text-xl text-white">
                {result.baseline_metrics[metric]} {" -> "} {result.new_metrics[metric]}
              </p>
              <p className="mt-1 text-sm text-mint">{result.percentage_changes[metric]}%</p>
            </div>
          ))}
          <div className="app-surface p-5 md:col-span-3">
            <h3 className="font-semibold text-white">Recommendation</h3>
            <p className="mt-2 text-sm leading-6 text-slate-300">{result.recommendation}</p>
          </div>
        </section>
      ) : <EmptyState title="No what-if result yet" body="Change a few parameters, run the analysis, and compare baseline versus modified metrics." />}
    </form>
  );
}

