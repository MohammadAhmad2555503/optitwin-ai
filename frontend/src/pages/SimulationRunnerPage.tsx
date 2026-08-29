import { useEffect, useState } from "react";
import MetricCard from "../components/MetricCard";
import Loading from "../components/Loading";
import EmptyState from "../components/EmptyState";
import { errorMessage } from "../services/api";
import { listScenarios } from "../services/scenarioService";
import { compareStrategies, runSimulation } from "../services/simulationService";
import type { Scenario, SimulationRun, StrategyComparison } from "../types";

const strategies = [
  "First-Come-First-Served",
  "Priority-Based Processing",
  "Nearest-Worker Assignment",
  "Cost-Minimising Assignment",
  "Hybrid Heuristic Strategy",
  "RL Agent Strategy",
];

export default function SimulationRunnerPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState<number | "">("");
  const [strategy, setStrategy] = useState(strategies[4]);
  const [run, setRun] = useState<SimulationRun | null>(null);
  const [comparison, setComparison] = useState<StrategyComparison | null>(null);
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

  async function runOne() {
    if (!scenarioId) return;
    setBusy(true);
    setError("");
    try {
      setRun(await runSimulation(Number(scenarioId), strategy));
      setComparison(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function runAll() {
    if (!scenarioId) return;
    setBusy(true);
    setError("");
    try {
      setComparison(await compareStrategies(Number(scenarioId)));
      setRun(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Loading label="Loading simulation lab" />;
  if (!scenarios.length) return <EmptyState title="Create a scenario first" body="The simulation runner needs a warehouse twin to execute strategy metrics." />;

  const active = run ?? comparison?.results[0] ?? null;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.18em] text-cyan">Discrete-event simulation</p>
        <h2 className="text-3xl font-semibold text-white">Simulation Runner</h2>
      </div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <section className="app-surface grid gap-4 p-5 md:grid-cols-[1fr_1fr_auto_auto]">
        <label>
          <span className="text-sm text-slate-300">Scenario</span>
          <select className="field mt-2" value={scenarioId} onChange={(event) => setScenarioId(Number(event.target.value))}>
            {scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
          </select>
        </label>
        <label>
          <span className="text-sm text-slate-300">Strategy</span>
          <select className="field mt-2" value={strategy} onChange={(event) => setStrategy(event.target.value)}>
            {strategies.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
        <button className="btn-primary self-end" onClick={runOne} disabled={busy}>{busy ? "Running..." : "Run"}</button>
        <button className="btn-secondary self-end" onClick={runAll} disabled={busy}>Compare all</button>
      </section>
      {active ? (
        <div className="grid gap-4 md:grid-cols-4">
          <MetricCard label="Completed" value={active.completed_orders} helper={`${active.total_orders} total`} />
          <MetricCard label="Delayed" value={active.delayed_orders} helper={`${active.delay_reduction_vs_baseline}% vs FCFS`} />
          <MetricCard label="Throughput/hour" value={active.throughput_per_hour} />
          <MetricCard label="Efficiency" value={active.efficiency_score} helper={active.bottleneck_zone} />
        </div>
      ) : null}
      {comparison ? (
        <section className="app-surface overflow-x-auto p-5">
          <h3 className="font-semibold text-white">Best strategy: {comparison.best_strategy}</h3>
          <table className="mt-4 w-full min-w-[760px] border-collapse">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr><th className="table-cell">Strategy</th><th className="table-cell">Delayed</th><th className="table-cell">Throughput</th><th className="table-cell">Cost/order</th><th className="table-cell">Efficiency</th></tr>
            </thead>
            <tbody>
              {comparison.results.map((row) => (
                <tr key={row.id}>
                  <td className="table-cell text-slate-200">{row.strategy_name}</td>
                  <td className="table-cell">{row.delayed_orders}</td>
                  <td className="table-cell">{row.throughput_per_hour}</td>
                  <td className="table-cell">{row.cost_per_order}</td>
                  <td className="table-cell">{row.efficiency_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}
    </div>
  );
}

