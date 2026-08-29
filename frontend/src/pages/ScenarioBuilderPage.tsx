import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createScenario } from "../services/scenarioService";
import type { ScenarioPayload } from "../services/scenarioService";
import { errorMessage } from "../services/api";

const initialScenario: ScenarioPayload = {
  name: "Metro Fulfilment Twin",
  workers: 18,
  robots: 8,
  orders_per_hour: 180,
  storage_zones: 6,
  average_picking_time: 4.2,
  priority_order_percentage: 22,
  robot_failure_probability: 0.04,
  worker_efficiency: 0.9,
  shift_duration: 8,
  cost_per_worker: 24,
  cost_per_robot: 9,
  delay_penalty: 3.5,
  demand_variability: 0.24,
  inventory_restock_frequency: 2,
};

type NumericScenarioField = Exclude<keyof ScenarioPayload, "name">;

const fields: Array<[NumericScenarioField, string, number, number]> = [
  ["workers", "Workers", 1, 500],
  ["robots", "Robots", 0, 500],
  ["orders_per_hour", "Orders per hour", 1, 10000],
  ["storage_zones", "Storage zones", 1, 100],
  ["average_picking_time", "Average picking time", 0.2, 120],
  ["priority_order_percentage", "Priority order percentage", 0, 100],
  ["robot_failure_probability", "Robot failure probability", 0, 1],
  ["worker_efficiency", "Worker efficiency", 0.1, 1.5],
  ["shift_duration", "Shift duration", 1, 24],
  ["cost_per_worker", "Cost per worker", 0, 1000],
  ["cost_per_robot", "Cost per robot", 0, 1000],
  ["delay_penalty", "Delay penalty", 0, 1000],
  ["demand_variability", "Demand variability", 0, 2],
  ["inventory_restock_frequency", "Inventory restock frequency", 0.25, 24],
];

export default function ScenarioBuilderPage() {
  const [form, setForm] = useState<ScenarioPayload>(initialScenario);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await createScenario(form);
      navigate("/scenarios");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.18em] text-cyan">Digital twin inputs</p>
        <h2 className="text-3xl font-semibold text-white">Scenario Builder</h2>
      </div>
      {error ? <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <section className="app-surface grid gap-4 p-5 md:grid-cols-2">
        <label className="md:col-span-2">
          <span className="text-sm text-slate-300">Scenario name</span>
          <input className="field mt-2" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
        </label>
        {fields.map(([key, label, min, max]) => (
          <label key={key}>
            <span className="text-sm text-slate-300">{label}</span>
            <input
              className="field mt-2"
              type="number"
              min={min}
              max={max}
              step="0.01"
              value={form[key]}
              onChange={(event) => setForm({ ...form, [key]: Number(event.target.value) })}
            />
          </label>
        ))}
      </section>
      <button className="btn-primary" disabled={loading}>{loading ? "Saving..." : "Create scenario"}</button>
    </form>
  );
}

