import { LogOut, Server, UserRound } from "lucide-react";
import { API_BASE_URL } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  return (
    <div className="space-y-6">
      <div><p className="text-sm uppercase tracking-[0.18em] text-cyan">Workspace</p><h2 className="text-3xl font-semibold text-white">Settings</h2></div>
      <section className="grid gap-4 md:grid-cols-2">
        <div className="app-surface p-5">
          <div className="flex items-center gap-3"><UserRound className="h-5 w-5 text-cyan" /><h3 className="font-semibold text-white">Profile</h3></div>
          <dl className="mt-4 space-y-3 text-sm">
            <div><dt className="text-slate-500">Name</dt><dd className="text-slate-200">{user?.name}</dd></div>
            <div><dt className="text-slate-500">Email</dt><dd className="text-slate-200">{user?.email}</dd></div>
          </dl>
          <button className="btn-secondary mt-5" onClick={logout}><LogOut className="h-4 w-4" /> Logout</button>
        </div>
        <div className="app-surface p-5">
          <div className="flex items-center gap-3"><Server className="h-5 w-5 text-mint" /><h3 className="font-semibold text-white">System</h3></div>
          <dl className="mt-4 space-y-3 text-sm">
            <div><dt className="text-slate-500">API base URL</dt><dd className="text-slate-200">{API_BASE_URL}</dd></div>
            <div><dt className="text-slate-500">Database</dt><dd className="text-slate-200">SQLite first, PostgreSQL-ready SQLAlchemy layer</dd></div>
            <div><dt className="text-slate-500">Frontend</dt><dd className="text-slate-200">React, TypeScript, Vite, Tailwind, Recharts</dd></div>
          </dl>
        </div>
      </section>
    </div>
  );
}

