import { Navigate, Outlet } from "react-router-dom";
import Loading from "./Loading";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute() {
  const { token, loading } = useAuth();
  if (loading) return <Loading label="Checking session" />;
  return token ? <Outlet /> : <Navigate to="/login" replace />;
}

