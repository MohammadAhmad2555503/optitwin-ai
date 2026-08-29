import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { errorMessage } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("demo@optitwin.ai");
  const [password, setPassword] = useState("demo-password");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <form onSubmit={submit} className="app-surface w-full max-w-md p-6">
        <h1 className="text-2xl font-semibold text-white">Login</h1>
        <p className="mt-2 text-sm text-slate-400">Access the OptiTwinAI control plane.</p>
        {error ? <p className="mt-4 rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
        <label className="mt-5 block text-sm text-slate-300">Email</label>
        <input className="field mt-2" value={email} onChange={(event) => setEmail(event.target.value)} />
        <label className="mt-4 block text-sm text-slate-300">Password</label>
        <input className="field mt-2" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        <button className="btn-primary mt-6 w-full" disabled={loading}>{loading ? "Signing in..." : "Login"}</button>
        <p className="mt-4 text-center text-sm text-slate-400">
          New here? <Link className="text-cyan" to="/signup">Create an account</Link>
        </p>
      </form>
    </main>
  );
}

