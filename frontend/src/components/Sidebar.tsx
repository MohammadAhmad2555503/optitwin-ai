import {
  Activity,
  BarChart3,
  Boxes,
  BrainCircuit,
  ClipboardList,
  FlaskConical,
  Gauge,
  Home,
  Library,
  LineChart,
  PlayCircle,
  Settings,
  SlidersHorizontal,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: Gauge },
  { to: "/scenarios/new", label: "Scenario Builder", icon: Boxes },
  { to: "/scenarios", label: "Scenario Library", icon: Library },
  { to: "/simulation", label: "Simulation Runner", icon: PlayCircle },
  { to: "/strategies", label: "Strategy Comparison", icon: BarChart3 },
  { to: "/what-if", label: "What-if Analysis", icon: SlidersHorizontal },
  { to: "/optimisation", label: "Optimisation Lab", icon: FlaskConical },
  { to: "/convergence", label: "Convergence", icon: TrendingUp },
  { to: "/stability", label: "Stability", icon: LineChart },
  { to: "/rl", label: "RL Lab", icon: BrainCircuit },
  { to: "/reports", label: "Reports", icon: ClipboardList },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="border-r border-line bg-panel/80 md:min-h-screen md:w-72">
      <div className="flex items-center gap-3 border-b border-line px-5 py-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan text-ink">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">OptiTwinAI</p>
          <p className="text-xs text-slate-400">Fractional optimisation lab</p>
        </div>
      </div>
      <nav className="grid gap-1 p-3">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-md px-3 py-2 text-sm ${isActive ? "bg-cyan text-ink" : "text-slate-300 hover:bg-ink"}`
          }
        >
          <Home className="h-4 w-4" />
          Landing
        </NavLink>
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm ${isActive ? "bg-cyan text-ink" : "text-slate-300 hover:bg-ink"}`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="mx-3 mb-4 mt-2 rounded-lg border border-line bg-ink p-3 text-xs text-slate-400">
        <div className="mb-2 flex items-center gap-2 text-slate-200">
          <Activity className="h-4 w-4 text-mint" />
          Live local stack
        </div>
        FastAPI on 8000, Vite on 5173, SQLite first.
      </div>
    </aside>
  );
}

