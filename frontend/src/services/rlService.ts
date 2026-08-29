import { api } from "./api";
import type { RLRun } from "../types";

export async function trainRL(scenarioId: number, episodes: number, algorithm = "TabularQAgent"): Promise<RLRun> {
  const { data } = await api.post<RLRun>("/rl/train", {
    scenario_id: scenarioId,
    algorithm,
    episodes,
    seed: 42,
  });
  return data;
}

export async function listRLRuns(): Promise<RLRun[]> {
  const { data } = await api.get<RLRun[]>("/rl/runs");
  return data;
}

export async function evaluateRL(scenarioId: number) {
  const { data } = await api.post("/rl/evaluate", { scenario_id: scenarioId, episodes: 30, seed: 43 });
  return data;
}

export async function compareRLWithStrategies(scenarioId: number) {
  const { data } = await api.post("/rl/compare-with-strategies", { scenario_id: scenarioId, episodes: 20, seed: 42 });
  return data;
}

