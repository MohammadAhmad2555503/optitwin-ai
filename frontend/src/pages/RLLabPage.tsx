import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import { errorMessage } from "../services/api";
import { listScenarios } from "../services/scenarioService";
import { compareRLWithStrategies, trainRL } from "../services/rlService";
import type { RLRun, Scenario } from "../types";

export default function RLLabPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState<number | "">("");
  const [episodes, setEpisodes] = useState(80);
  const [run, setRun] = useState<RLRun | null>(null);
  const [comparison, setComparison] = useState<Record<string, any> | null>(null);
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

  async function train() {
    if (!scenarioId) return;
    setBusy(true);
    setError("");
    try {
      setRun(await trainRL(Number(scenarioId), episodes));
      setComparison(await compareRLWithStrategies(Number(scenarioId)));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Loading label="Loading RL lab" />;
  if (!scenarios.length) return <EmptyState title="No scenario available" body="Create a warehouse twin before training an RL policy." />;

  const rewardData = run?.reward_curve.map((reward, episode) => ({ episode, reward })) ?? [];
  const comparisonRows = comparison ? Object.entries(comparison.comparison as Record<string, Record<string, number>>) : [];

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.18em] text-cyan">Policy learning</p>
        <h2 className="text-3xl font-semibold text-white">RL Lab</h2>
      </div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <section className="app-surface grid gap-4 p-5 md:grid-cols-[1fr_160px_auto]">
        <label>
          <span className="text-sm text-slate-300">Scenario</span>
          <select className="field mt-2" value={scenarioId} onChange={(event) => setScenarioId(Number(event.target.value))}>
            {scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
          </select>
        </label>
        <label><span className="text-sm text-slate-300">Episodes</span><input className="field mt-2" type="number" value={episodes} onChange={(event) => setEpisodes(Number(event.target.value))} /></label>
        <button className="btn-primary self-end" onClick={train} disabled={busy}>{busy ? "Training..." : "Train policy"}</button>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        <div className="app-surface p-5">
          <h3 className="font-semibold text-white">State</h3>
          <p className="mt-2 text-sm leading-6 text-slate-400">Queue length, worker availability, robot availability, priority ratio, waiting time, zone congestion, and current time step.</p>
        </div>
        <div className="app-surface p-5">
          <h3 className="font-semibold text-white">Actions</h3>
          <p className="mt-2 text-sm leading-6 text-slate-400">Process standard or priority orders, assign workers or robots, delay low-priority work, and rebalance resources.</p>
        </div>
        <div className="app-surface p-5">
          <h3 className="font-semibold text-white">Reward</h3>
          <p className="mt-2 text-sm leading-6 text-slate-400">Rewards completed orders, throughput, and balanced utilisation while penalising delay, queues, and excess cost.</p>
        </div>
      </section>
      {run ? (
        <section className="app-surface h-[360px] p-5">
          <h3 className="mb-4 font-semibold text-white">Reward curve</h3>
          <ResponsiveContainer width="100%" height="85%">
            <LineChart data={rewardData}>
              <CartesianGrid stroke="#22313b" />
              <XAxis dataKey="episode" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: "#101a22", border: "1px solid #22313b" }} />
              <Line dot={false} dataKey="reward" stroke="#39d98a" />
            </LineChart>
          </ResponsiveContainer>
        </section>
      ) : null}
      {comparisonRows.length ? (
        <section className="app-surface overflow-x-auto p-5">
          <h3 className="font-semibold text-white">RL versus rule-based strategies</h3>
          <table className="mt-4 w-full min-w-[760px]"><tbody>{comparisonRows.map(([name, row]) => <tr key={name}><td className="table-cell text-slate-100">{name}</td><td className="table-cell">delay {row.delay_rate}</td><td className="table-cell">throughput {row.throughput_per_hour}</td><td className="table-cell">cost {row.cost_per_order}</td><td className="table-cell">score {row.efficiency_score}</td></tr>)}</tbody></table>
        </section>
      ) : null}
    </div>
  );
}

