import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import { errorMessage } from "../services/api";
import { listScenarios } from "../services/scenarioService";
import { compareStrategies } from "../services/simulationService";
import type { Scenario, StrategyComparison } from "../types";

export default function StrategyComparisonPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState<number | "">("");
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

  async function run() {
    if (!scenarioId) return;
    setBusy(true);
    try {
      setComparison(await compareStrategies(Number(scenarioId)));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Loading label="Loading comparison lab" />;
  if (!scenarios.length) return <EmptyState title="No scenario available" body="Create a scenario, then compare all dispatching strategies." />;

  const chartData = comparison?.results.map((row) => ({
    strategy: row.strategy_name.replace(" Strategy", "").replace(" Assignment", ""),
    delayed: row.delayed_orders,
    throughput: row.throughput_per_hour,
    cost: row.cost_per_order,
  })) ?? [];
  const queueData = comparison?.results.find((row) => row.strategy_name === comparison.best_strategy)?.time_series.map((point) => ({
    hour: point.hour,
    queue: point.queue_length,
  })) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.18em] text-cyan">Policy benchmarking</p>
        <h2 className="text-3xl font-semibold text-white">Strategy Comparison</h2>
      </div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <section className="app-surface flex flex-wrap items-end gap-4 p-5">
        <label className="min-w-[260px] flex-1">
          <span className="text-sm text-slate-300">Scenario</span>
          <select className="field mt-2" value={scenarioId} onChange={(event) => setScenarioId(Number(event.target.value))}>
            {scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
          </select>
        </label>
        <button className="btn-primary" onClick={run} disabled={busy}>{busy ? "Comparing..." : "Run comparison"}</button>
      </section>
      {comparison ? (
        <>
          <section className="app-surface h-[360px] p-5">
            <h3 className="mb-4 font-semibold text-white">Delayed orders, throughput, and cost</h3>
            <ResponsiveContainer width="100%" height="85%">
              <BarChart data={chartData}>
                <CartesianGrid stroke="#22313b" />
                <XAxis dataKey="strategy" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#101a22", border: "1px solid #22313b" }} />
                <Legend />
                <Bar dataKey="delayed" fill="#f7b955" />
                <Bar dataKey="throughput" fill="#4cc9f0" />
                <Bar dataKey="cost" fill="#39d98a" />
              </BarChart>
            </ResponsiveContainer>
          </section>
          <section className="app-surface h-[320px] p-5">
            <h3 className="mb-4 font-semibold text-white">Queue length over time for best strategy</h3>
            <ResponsiveContainer width="100%" height="84%">
              <LineChart data={queueData}>
                <CartesianGrid stroke="#22313b" />
                <XAxis dataKey="hour" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#101a22", border: "1px solid #22313b" }} />
                <Line dot={false} dataKey="queue" stroke="#39d98a" />
              </LineChart>
            </ResponsiveContainer>
          </section>
          <section className="app-surface overflow-x-auto p-5">
            <h3 className="font-semibold text-white">Best strategy: {comparison.best_strategy}</h3>
            <table className="mt-4 w-full min-w-[820px]">
              <tbody>
                {comparison.results.map((row) => (
                  <tr key={row.id}>
                    <td className="table-cell font-medium text-slate-100">{row.strategy_name}</td>
                    <td className="table-cell">Delayed {row.delayed_orders}</td>
                    <td className="table-cell">Queue {row.average_queue_length}</td>
                    <td className="table-cell">Cost/order {row.cost_per_order}</td>
                    <td className="table-cell">Score {row.efficiency_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      ) : <EmptyState title="No comparison yet" body="Run the comparison to create stored simulation runs and chart the strategies." />}
    </div>
  );
}

