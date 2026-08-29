import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { User } from "../types";
import * as authService from "../services/authService";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string, confirmPassword: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("optitwinai_token"));
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function loadUser() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const current = await authService.me();
        if (active) setUser(current);
      } catch {
        localStorage.removeItem("optitwinai_token");
        setToken(null);
        setUser(null);
      } finally {
        if (active) setLoading(false);
      }
    }
    loadUser();
    return () => {
      active = false;
    };
  }, [token]);

  async function handleLogin(email: string, password: string) {
    const nextToken = await authService.login({ email, password });
    localStorage.setItem("optitwinai_token", nextToken);
    setToken(nextToken);
    setUser(await authService.me());
  }

  async function handleSignup(name: string, email: string, password: string, confirmPassword: string) {
    const nextToken = await authService.signup({ name, email, password, confirm_password: confirmPassword });
    localStorage.setItem("optitwinai_token", nextToken);
    setToken(nextToken);
    setUser(await authService.me());
  }

  function logout() {
    localStorage.removeItem("optitwinai_token");
    setToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({ user, token, loading, login: handleLogin, signup: handleSignup, logout }),
    [user, token, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}

