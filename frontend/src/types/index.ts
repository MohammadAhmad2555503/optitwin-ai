export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface Scenario {
  id: number;
  user_id: number;
  name: string;
  workers: number;
  robots: number;
  orders_per_hour: number;
  storage_zones: number;
  average_picking_time: number;
  priority_order_percentage: number;
  robot_failure_probability: number;
  worker_efficiency: number;
  shift_duration: number;
  cost_per_worker: number;
  cost_per_robot: number;
  delay_penalty: number;
  demand_variability: number;
  inventory_restock_frequency: number;
  created_at?: string;
  updated_at?: string;
}

export interface SimulationRun {
  id: number;
  scenario_id: number;
  strategy_name: string;
  total_orders: number;
  completed_orders: number;
  delayed_orders: number;
  average_completion_time: number;
  average_queue_length: number;
  worker_utilisation: number;
  robot_utilisation: number;
  throughput_per_hour: number;
  cost_per_order: number;
  total_cost: number;
  efficiency_score: number;
  bottleneck_zone: string;
  delay_reduction_vs_baseline: number;
  metrics: Record<string, number | string | boolean>;
  time_series: Array<Record<string, number | string>>;
  created_at: string;
}

export interface StrategyComparison {
  scenario_id: number;
  best_strategy: string;
  results: SimulationRun[];
}

export interface OptimisationExperiment {
  id: number;
  function_name: string;
  optimisers: string[];
  learning_rate: number;
  iterations: number;
  alpha: number;
  results: Record<string, Record<string, number | boolean | number[]>>;
  convergence_curves: Record<string, number[]>;
  stability_metrics: Record<string, number>;
  created_at: string;
}

export interface RLRun {
  id: number;
  scenario_id: number;
  algorithm: string;
  episodes: number;
  reward_function: Record<string, number>;
  training_metrics: Record<string, number | string>;
  reward_curve: number[];
  comparison_metrics: Record<string, Record<string, number>>;
  status: string;
  created_at: string;
}

export interface Report {
  id: number;
  title: string;
  report_markdown: string;
  created_at: string;
}

export interface DashboardSummary {
  total_scenarios: number;
  total_simulation_runs: number;
  best_strategy: string | null;
  average_delay_reduction: number;
  average_throughput_improvement: number;
  total_optimiser_experiments: number;
  total_rl_runs: number;
  total_reports: number;
}

