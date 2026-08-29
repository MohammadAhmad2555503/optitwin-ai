import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import { errorMessage } from "../services/api";
import { deleteScenario, listScenarios, updateScenario } from "../services/scenarioService";
import { runSimulation } from "../services/simulationService";
import type { Scenario } from "../types";

export default function ScenarioLibraryPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    try {
      setScenarios(await listScenarios());
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function remove(id: number) {
    await deleteScenario(id);
    await load();
  }

  async function quickTune(scenario: Scenario) {
    await updateScenario(scenario.id, { robots: scenario.robots + 1, worker_efficiency: Math.min(1.5, scenario.worker_efficiency + 0.02) });
    setMessage("Scenario tuned: added one robot and lifted worker efficiency.");
    await load();
  }

  async function runHybrid(id: number) {
    const result = await runSimulation(id, "Hybrid Heuristic Strategy");
    setMessage(`Simulation complete: ${result.efficiency_score} efficiency score.`);
  }

  if (loading) return <Loading label="Loading scenarios" />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.18em] text-cyan">Scenario inventory</p>
          <h2 className="text-3xl font-semibold text-white">Scenario Library</h2>
        </div>
        <Link className="btn-primary" to="/scenarios/new">New scenario</Link>
      </div>
      {message ? <p className="rounded-md border border-mint/40 bg-mint/10 p-3 text-sm text-mint">{message}</p> : null}
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      {!scenarios.length ? <EmptyState title="No scenarios yet" body="Create a warehouse twin to unlock simulation, optimisation, RL, and reports." /> : null}
      <div className="grid gap-4 lg:grid-cols-2">
        {scenarios.map((scenario) => (
          <article key={scenario.id} className="app-surface p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-white">{scenario.name}</h3>
                <p className="mt-1 text-sm text-slate-400">{scenario.workers} workers, {scenario.robots} robots, {scenario.orders_per_hour} orders/hour</p>
              </div>
              <span className="rounded-md border border-line px-2 py-1 text-xs text-slate-300">{scenario.storage_zones} zones</span>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div><dt className="text-slate-500">Picking time</dt><dd className="text-slate-200">{scenario.average_picking_time} min</dd></div>
              <div><dt className="text-slate-500">Priority mix</dt><dd className="text-slate-200">{scenario.priority_order_percentage}%</dd></div>
              <div><dt className="text-slate-500">Failure prob.</dt><dd className="text-slate-200">{scenario.robot_failure_probability}</dd></div>
              <div><dt className="text-slate-500">Shift</dt><dd className="text-slate-200">{scenario.shift_duration}h</dd></div>
            </dl>
            <div className="mt-5 flex flex-wrap gap-2">
              <button className="btn-primary" onClick={() => runHybrid(scenario.id)}>Run simulation</button>
              <button className="btn-secondary" onClick={() => quickTune(scenario)}>Quick edit</button>
              <button className="btn-secondary" onClick={() => remove(scenario.id)}>Delete</button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

