from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

import numpy as np

from app.simulation.metrics import summarise_time_series
from app.simulation.strategies import STRATEGY_PROFILES, normalise_strategy


@dataclass
class WarehouseScenario:
    name: str
    workers: int
    robots: int
    orders_per_hour: float
    storage_zones: int
    average_picking_time: float
    priority_order_percentage: float
    robot_failure_probability: float
    worker_efficiency: float
    shift_duration: float
    cost_per_worker: float
    cost_per_robot: float
    delay_penalty: float
    demand_variability: float
    inventory_restock_frequency: float


def scenario_to_dict(scenario: Any) -> Dict[str, Any]:
    fields = WarehouseScenario.__dataclass_fields__.keys()
    return {field: getattr(scenario, field) for field in fields}


def _stable_strategy_offset(strategy_name: str) -> int:
    return sum(ord(char) for char in strategy_name) % 997


def run_warehouse_simulation(
    scenario: WarehouseScenario | Dict[str, Any] | Any,
    strategy_name: str,
    seed: int | None = 42,
) -> Dict[str, Any]:
    data = scenario_to_dict(scenario) if not isinstance(scenario, dict) else dict(scenario)
    strategy = normalise_strategy(strategy_name)
    profile = STRATEGY_PROFILES[strategy]
    rng = np.random.default_rng((seed or 0) + _stable_strategy_offset(strategy))

    steps_per_hour = 12
    steps = max(1, int(data["shift_duration"] * steps_per_hour))
    step_minutes = 60 / steps_per_hour
    queue = 0.0
    delayed_orders = 0.0
    completed_orders = 0.0
    total_orders = 0.0
    total_completion_minutes = 0.0
    worker_busy = 0.0
    robot_busy = 0.0
    zone_load = np.zeros(int(data["storage_zones"]), dtype=float)
    time_series: list[dict[str, Any]] = []

    worker_capacity_per_step = (
        data["workers"] * (step_minutes / data["average_picking_time"]) * data["worker_efficiency"]
    )
    robot_capacity_per_step = data["robots"] * 0.85
    variability = max(0.01, data["demand_variability"])
    restock_interval_steps = max(1, int(data["inventory_restock_frequency"] * steps_per_hour))
    priority_ratio = data["priority_order_percentage"] / 100

    for step in range(steps):
        hour = step / steps_per_hour
        demand_wave = 1 + 0.18 * np.sin(2 * np.pi * hour / max(data["shift_duration"], 1))
        demand_wave += rng.normal(0, variability * 0.16)
        expected_arrivals = max(0.1, data["orders_per_hour"] / steps_per_hour * demand_wave)
        arrivals = float(rng.poisson(expected_arrivals))
        priority_orders = rng.binomial(int(arrivals), min(max(priority_ratio, 0), 1))

        robot_failures = rng.binomial(int(data["robots"]), min(max(data["robot_failure_probability"], 0), 1))
        active_robot_capacity = max(0, data["robots"] - robot_failures) * robot_capacity_per_step
        restock_drag = 0.88 if step and step % restock_interval_steps == 0 else 1.0
        available_capacity = (
            (worker_capacity_per_step + active_robot_capacity)
            * profile["capacity_multiplier"]
            * restock_drag
            * rng.uniform(0.93, 1.06)
        )

        queue += arrivals
        zone_load += rng.multinomial(int(arrivals), [1 / len(zone_load)] * len(zone_load))
        processable = min(queue, max(0.0, available_capacity))
        queue -= processable
        completed_orders += processable
        total_orders += arrivals

        delay_pressure = max(0.0, queue - available_capacity * profile["queue_discipline"])
        step_delayed = delay_pressure * (0.16 + priority_ratio * profile["priority_delay_multiplier"] * 0.08)
        delayed_orders += step_delayed
        total_completion_minutes += processable * (
            data["average_picking_time"] * (1 + min(queue / max(available_capacity, 1), 3.5) * 0.28)
        )

        worker_share = min(processable, worker_capacity_per_step)
        robot_share = max(0.0, processable - worker_share)
        worker_busy += worker_share / max(worker_capacity_per_step, 1)
        robot_busy += min(1.0, robot_share / max(active_robot_capacity, 1)) if data["robots"] else 0.0

        congestion_zone = int(np.argmax(zone_load))
        zone_load[congestion_zone] *= 0.92
        step_cost = (
            (data["workers"] * data["cost_per_worker"] + data["robots"] * data["cost_per_robot"])
            / steps_per_hour
            * profile["cost_multiplier"]
            + step_delayed * data["delay_penalty"]
        )
        time_series.append(
            {
                "time_step": step,
                "hour": round(hour, 2),
                "arrivals": round(arrivals, 2),
                "completed": round(processable, 2),
                "delayed": round(step_delayed, 2),
                "queue_length": round(queue, 2),
                "throughput": round(processable * steps_per_hour, 2),
                "cost": round(step_cost, 2),
                "worker_utilisation": round(min(worker_share / max(worker_capacity_per_step, 1), 1), 3),
                "robot_utilisation": round(min(robot_share / max(active_robot_capacity, 1), 1) if data["robots"] else 0, 3),
            }
        )

    completed_orders = min(completed_orders, total_orders)
    delayed_orders = min(total_orders - completed_orders + delayed_orders, total_orders)
    throughput_per_hour = completed_orders / max(data["shift_duration"], 1)
    fixed_cost = data["shift_duration"] * (data["workers"] * data["cost_per_worker"] + data["robots"] * data["cost_per_robot"])
    total_cost = fixed_cost * profile["cost_multiplier"] + delayed_orders * data["delay_penalty"]
    cost_per_order = total_cost / max(completed_orders, 1)
    avg_completion = total_completion_minutes / max(completed_orders, 1)
    avg_queue = float(np.mean([point["queue_length"] for point in time_series])) if time_series else 0.0
    completion_rate = completed_orders / max(total_orders, 1)
    delay_rate = delayed_orders / max(total_orders, 1)
    cost_efficiency = 1 / (1 + cost_per_order / 100)
    efficiency_score = 100 * (
        0.42 * completion_rate
        + 0.26 * min(throughput_per_hour / max(data["orders_per_hour"], 1), 1.2) / 1.2
        + 0.2 * (1 - min(delay_rate, 1))
        + 0.12 * cost_efficiency
    )
    bottleneck_zone = f"Zone {int(np.argmax(zone_load)) + 1}"
    summary = summarise_time_series(time_series)

    metrics = {
        "total_orders": int(round(total_orders)),
        "completed_orders": int(round(completed_orders)),
        "delayed_orders": int(round(delayed_orders)),
        "average_completion_time": round(float(avg_completion), 2),
        "average_queue_length": round(avg_queue, 2),
        "worker_utilisation": round(min(worker_busy / steps, 1), 3),
        "robot_utilisation": round(min(robot_busy / steps, 1), 3) if data["robots"] else 0.0,
        "throughput_per_hour": round(float(throughput_per_hour), 2),
        "cost_per_order": round(float(cost_per_order), 2),
        "total_cost": round(float(total_cost), 2),
        "efficiency_score": round(float(efficiency_score), 2),
        "bottleneck_zone": bottleneck_zone,
        "delay_reduction_vs_baseline": 0.0,
        "completion_rate": round(float(completion_rate), 3),
        "delay_rate": round(float(delay_rate), 3),
        "peak_queue": round(summary["peak_queue"], 2),
    }
    return {"strategy_name": strategy, "metrics": metrics, "time_series": time_series, "scenario": asdict(WarehouseScenario(**data))}

