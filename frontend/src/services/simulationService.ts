import { api } from "./api";
import type { SimulationRun, StrategyComparison } from "../types";

export async function runSimulation(scenarioId: number, strategyName: string): Promise<SimulationRun> {
  const { data } = await api.post<SimulationRun>("/simulation/run", {
    scenario_id: scenarioId,
    strategy_name: strategyName,
    seed: 42,
  });
  return data;
}

export async function listSimulationRuns(): Promise<SimulationRun[]> {
  const { data } = await api.get<SimulationRun[]>("/simulation/runs");
  return data;
}

export async function compareStrategies(scenarioId: number): Promise<StrategyComparison> {
  const { data } = await api.post<StrategyComparison>("/simulation/compare-strategies", {
    scenario_id: scenarioId,
    seed: 42,
  });
  return data;
}

export async function runWhatIf(
  scenarioId: number,
  modifiedParameters: Record<string, number>,
  strategyName = "Hybrid Heuristic Strategy",
) {
  const { data } = await api.post("/whatif/run", {
    base_scenario_id: scenarioId,
    strategy_name: strategyName,
    modified_parameters: modifiedParameters,
    seed: 42,
  });
  return data;
}

export async function listWhatIfResults() {
  const { data } = await api.get("/whatif/results");
  return data;
}

