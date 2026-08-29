import { api } from "./api";
import type { OptimisationExperiment } from "../types";

export interface OptimisationPayload {
  function_name: string;
  optimisers: string[];
  learning_rate: number;
  iterations: number;
  alpha: number;
  seed?: number;
}

export async function runExperiment(payload: OptimisationPayload): Promise<OptimisationExperiment> {
  const { data } = await api.post<OptimisationExperiment>("/optimisation/run", payload);
  return data;
}

export async function listExperiments(): Promise<OptimisationExperiment[]> {
  const { data } = await api.get<OptimisationExperiment[]>("/optimisation/experiments");
  return data;
}

export async function alphaSensitivity(functionName: string, learningRate: number, iterations: number) {
  const { data } = await api.post("/optimisation/alpha-sensitivity", {
    function_name: functionName,
    learning_rate: learningRate,
    iterations,
    alphas: [0.3, 0.5, 0.7, 0.9],
    seed: 42,
  });
  return data;
}

export async function analyseConvergence(curves: Record<string, number[]>) {
  const { data } = await api.post("/analysis/convergence", { curves, threshold: 0.001 });
  return data;
}

export async function analyseStability(curves: Record<string, number[]>) {
  const { data } = await api.post("/analysis/stability", { curves });
  return data;
}

