import { ArrowRight, BarChart3, BrainCircuit, FlaskConical, Warehouse } from "lucide-react";
import { Link } from "react-router-dom";

const features = [
  { icon: Warehouse, title: "Warehouse digital twins", body: "Model orders, queues, workers, robots, zones, failures, restocking, and operating cost." },
  { icon: FlaskConical, title: "Fractional optimisation", body: "Compare GD, SGD, Adam, and an experimental fractional-inspired gradient memory optimiser." },
  { icon: BrainCircuit, title: "RL policy lab", body: "Train and evaluate a tabular Q-learning policy over warehouse queue, congestion, and capacity states." },
  { icon: BarChart3, title: "Decision analytics", body: "Run what-if experiments, inspect convergence, assess stability, and generate markdown reports." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-ink">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-4 py-5 md:px-6">
        <Link to="/" className="text-lg font-semibold text-white">OptiTwinAI</Link>
        <div className="flex gap-2">
          <Link className="btn-secondary" to="/login">Login</Link>
          <Link className="btn-primary" to="/signup">Signup</Link>
        </div>
      </header>
      <section className="relative overflow-hidden border-y border-line">
        <div className="absolute inset-0 opacity-40" aria-hidden="true">
          <div className="h-full w-full bg-[linear-gradient(#22313b_1px,transparent_1px),linear-gradient(90deg,#22313b_1px,transparent_1px)] bg-[size:44px_44px]" />
        </div>
        <div className="relative mx-auto grid min-h-[78vh] max-w-7xl items-center gap-10 px-4 py-16 md:grid-cols-[1.05fr_.95fr] md:px-6">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan">Fractional-order optimisation for digital twin AI systems</p>
            <h1 className="mt-5 max-w-4xl text-5xl font-semibold leading-tight text-white md:text-7xl">
              OptiTwinAI
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
              A full-stack optimisation platform for warehouse and supply-chain decisions: simulation, what-if analysis, convergence diagnostics, stability analysis, RL policy training, dashboards, and executive reports.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link className="btn-primary" to="/signup">Build a scenario <ArrowRight className="h-4 w-4" /></Link>
              <Link className="btn-secondary" to="/login">Open dashboard</Link>
            </div>
          </div>
          <div className="app-surface p-5">
            <div className="grid gap-3">
              {["Hybrid Heuristic", "Adam", "Fractional GD", "RL Agent"].map((item, index) => (
                <div key={item} className="rounded-md border border-line bg-ink p-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-slate-100">{item}</p>
                    <span className="text-xs text-mint">{88 - index * 4}% stable</span>
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-panel">
                    <div className="h-2 rounded-full bg-cyan" style={{ width: `${88 - index * 9}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
      <section className="mx-auto grid max-w-7xl gap-4 px-4 py-10 md:grid-cols-4 md:px-6">
        {features.map(({ icon: Icon, title, body }) => (
          <article key={title} className="app-surface p-5">
            <Icon className="h-6 w-6 text-cyan" />
            <h2 className="mt-4 font-semibold text-white">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-400">{body}</p>
          </article>
        ))}
      </section>
    </div>
  );
}

