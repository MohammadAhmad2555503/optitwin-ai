import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import ConvergenceAnalysisPage from "./pages/ConvergenceAnalysisPage";
import DashboardPage from "./pages/DashboardPage";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import OptimisationLabPage from "./pages/OptimisationLabPage";
import RLLabPage from "./pages/RLLabPage";
import ReportGeneratorPage from "./pages/ReportGeneratorPage";
import ScenarioBuilderPage from "./pages/ScenarioBuilderPage";
import ScenarioLibraryPage from "./pages/ScenarioLibraryPage";
import SettingsPage from "./pages/SettingsPage";
import SignupPage from "./pages/SignupPage";
import SimulationRunnerPage from "./pages/SimulationRunnerPage";
import StabilityAnalysisPage from "./pages/StabilityAnalysisPage";
import StrategyComparisonPage from "./pages/StrategyComparisonPage";
import WhatIfAnalysisPage from "./pages/WhatIfAnalysisPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/scenarios/new" element={<ScenarioBuilderPage />} />
          <Route path="/scenarios" element={<ScenarioLibraryPage />} />
          <Route path="/simulation" element={<SimulationRunnerPage />} />
          <Route path="/strategies" element={<StrategyComparisonPage />} />
          <Route path="/what-if" element={<WhatIfAnalysisPage />} />
          <Route path="/optimisation" element={<OptimisationLabPage />} />
          <Route path="/convergence" element={<ConvergenceAnalysisPage />} />
          <Route path="/stability" element={<StabilityAnalysisPage />} />
          <Route path="/rl" element={<RLLabPage />} />
          <Route path="/reports" element={<ReportGeneratorPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

