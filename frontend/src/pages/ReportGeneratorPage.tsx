import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import { errorMessage } from "../services/api";
import { listExperiments } from "../services/optimisationService";
import { generateReport, listReports } from "../services/reportService";
import { listRLRuns } from "../services/rlService";
import { listScenarios } from "../services/scenarioService";
import { listSimulationRuns } from "../services/simulationService";
import type { OptimisationExperiment, Report, RLRun, Scenario, SimulationRun } from "../types";

export default function ReportGeneratorPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [simulations, setSimulations] = useState<SimulationRun[]>([]);
  const [experiments, setExperiments] = useState<OptimisationExperiment[]>([]);
  const [rlRuns, setRlRuns] = useState<RLRun[]>([]);
  const [active, setActive] = useState<Report | null>(null);
  const [title, setTitle] = useState("OptiTwinAI Decision Support Report");
  const [selected, setSelected] = useState({ scenario_id: "", simulation_run_id: "", optimisation_experiment_id: "", rl_run_id: "" });
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    try {
      const [rows, scenarioRows, simulationRows, experimentRows, rlRows] = await Promise.all([
        listReports(),
        listScenarios(),
        listSimulationRuns(),
        listExperiments(),
        listRLRuns(),
      ]);
      setReports(rows);
      setScenarios(scenarioRows);
      setSimulations(simulationRows);
      setExperiments(experimentRows);
      setRlRuns(rlRows);
      setActive(rows[0] ?? null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function create() {
    setBusy(true);
    setError("");
    try {
      const report = await generateReport({
        title,
        scenario_id: selected.scenario_id ? Number(selected.scenario_id) : undefined,
        simulation_run_id: selected.simulation_run_id ? Number(selected.simulation_run_id) : undefined,
        optimisation_experiment_id: selected.optimisation_experiment_id ? Number(selected.optimisation_experiment_id) : undefined,
        rl_run_id: selected.rl_run_id ? Number(selected.rl_run_id) : undefined,
      });
      setActive(report);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function copy() {
    if (!active) return;
    await navigator.clipboard.writeText(active.report_markdown);
    setMessage("Markdown copied to clipboard.");
  }

  function download() {
    if (!active) return;
    const blob = new Blob([active.report_markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${active.title.replace(/\W+/g, "-").toLowerCase()}.md`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  if (loading) return <Loading label="Loading reports" />;

  return (
    <div className="space-y-6">
      <div><p className="text-sm uppercase tracking-[0.18em] text-cyan">Decision support</p><h2 className="text-3xl font-semibold text-white">Report Generator</h2></div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      {message ? <p className="rounded-md border border-mint/40 bg-mint/10 p-3 text-sm text-mint">{message}</p> : null}
      <section className="app-surface grid gap-4 p-5 md:grid-cols-5">
        <label className="min-w-[280px] flex-1"><span className="text-sm text-slate-300">Report title</span><input className="field mt-2" value={title} onChange={(event) => setTitle(event.target.value)} /></label>
        <label><span className="text-sm text-slate-300">Scenario</span><select className="field mt-2" value={selected.scenario_id} onChange={(event) => setSelected({ ...selected, scenario_id: event.target.value })}><option value="">Latest</option>{scenarios.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
        <label><span className="text-sm text-slate-300">Simulation</span><select className="field mt-2" value={selected.simulation_run_id} onChange={(event) => setSelected({ ...selected, simulation_run_id: event.target.value })}><option value="">Latest</option>{simulations.map((item) => <option key={item.id} value={item.id}>{item.strategy_name} #{item.id}</option>)}</select></label>
        <label><span className="text-sm text-slate-300">Optimisation</span><select className="field mt-2" value={selected.optimisation_experiment_id} onChange={(event) => setSelected({ ...selected, optimisation_experiment_id: event.target.value })}><option value="">Latest</option>{experiments.map((item) => <option key={item.id} value={item.id}>{item.function_name} #{item.id}</option>)}</select></label>
        <label><span className="text-sm text-slate-300">RL run</span><select className="field mt-2" value={selected.rl_run_id} onChange={(event) => setSelected({ ...selected, rl_run_id: event.target.value })}><option value="">Latest</option>{rlRuns.map((item) => <option key={item.id} value={item.id}>{item.algorithm} #{item.id}</option>)}</select></label>
        <button className="btn-primary" onClick={create} disabled={busy}>{busy ? "Generating..." : "Generate report"}</button>
        <button className="btn-secondary" type="button" onClick={copy} disabled={!active}>Copy</button>
        <button className="btn-secondary" type="button" onClick={download} disabled={!active}>Download</button>
      </section>
      <section className="grid gap-4 lg:grid-cols-[300px_1fr]">
        <div className="app-surface p-4">
          <h3 className="font-semibold text-white">Reports</h3>
          <div className="mt-3 grid gap-2">
            {reports.map((report) => <button key={report.id} className="rounded-md border border-line bg-ink p-3 text-left text-sm text-slate-300 hover:border-cyan" onClick={() => setActive(report)}>{report.title}</button>)}
          </div>
        </div>
        {active ? (
          <article className="app-surface max-h-[720px] overflow-auto whitespace-pre-wrap p-5 text-sm leading-6 text-slate-300">
            {active.report_markdown}
          </article>
        ) : <EmptyState title="No reports yet" body="Generate a report after creating scenarios and running experiments." />}
      </section>
    </div>
  );
}

