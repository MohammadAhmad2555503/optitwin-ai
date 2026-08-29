import { LogOut, UserRound } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <header className="sticky top-0 z-20 border-b border-line bg-ink/90 px-4 py-3 backdrop-blur md:px-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-cyan">Digital twin control plane</p>
          <h1 className="text-lg font-semibold text-white">OptiTwinAI</h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 text-sm text-slate-300 sm:flex">
            <UserRound className="h-4 w-4 text-mint" />
            {user?.name ?? "Operator"}
          </div>
          <button className="btn-secondary px-3" onClick={logout} title="Logout">
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}

