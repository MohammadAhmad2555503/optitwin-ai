import { api } from "./api";
import type { Scenario } from "../types";

export type ScenarioPayload = Omit<Scenario, "id" | "user_id" | "created_at" | "updated_at">;

export async function listScenarios(): Promise<Scenario[]> {
  const { data } = await api.get<Scenario[]>("/scenarios");
  return data;
}

export async function createScenario(payload: ScenarioPayload): Promise<Scenario> {
  const { data } = await api.post<Scenario>("/scenarios", payload);
  return data;
}

export async function updateScenario(id: number, payload: Partial<ScenarioPayload>): Promise<Scenario> {
  const { data } = await api.patch<Scenario>(`/scenarios/${id}`, payload);
  return data;
}

export async function deleteScenario(id: number): Promise<void> {
  await api.delete(`/scenarios/${id}`);
}

