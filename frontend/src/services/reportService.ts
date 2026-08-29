import { api } from "./api";
import type { Report } from "../types";

export interface ReportPayload {
  title: string;
  scenario_id?: number;
  simulation_run_id?: number;
  optimisation_experiment_id?: number;
  rl_run_id?: number;
}

export async function generateReport(payload: ReportPayload): Promise<Report> {
  const { data } = await api.post<Report>("/reports/generate", payload);
  return data;
}

export async function listReports(): Promise<Report[]> {
  const { data } = await api.get<Report[]>("/reports");
  return data;
}

