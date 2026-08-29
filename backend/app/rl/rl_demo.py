from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Tuple

import numpy as np

from app.rl.warehouse_rl_env import ACTIONS, get_rl_spec


State = Tuple[int, int, int, int, int, int, int]


def _state_key(state: State) -> str:
    return "|".join(str(part) for part in state)


def _state_from_key(key: str) -> State:
    return tuple(int(part) for part in key.split("|"))  # type: ignore[return-value]


def _safe_priority_ratio(scenario: Any) -> float:
    return min(max(float(scenario.priority_order_percentage) / 100, 0.0), 1.0)


@dataclass
class EpisodeSummary:
    reward: float
    arrivals: float
    completed: float
    delayed: float
    cost: float
    worker_utilisation: float
    robot_utilisation: float


class WarehouseControlEnv:
    """Small Markov decision process used for local tabular RL training.

    The environment is intentionally lightweight so the project remains easy to
    run on Windows without GPU or external RL packages. It still performs real
    action selection, transition simulation, reward calculation, and Q updates.
    """

    def __init__(self, scenario: Any, seed: int | None = 42):
        self.scenario = scenario
        self.rng = np.random.default_rng(seed or 0)
        self.steps_per_hour = 12
        self.horizon = max(1, int(float(scenario.shift_duration) * self.steps_per_hour))
        self.step_minutes = 60 / self.steps_per_hour
        self.priority_ratio = _safe_priority_ratio(scenario)
        self.reset()

    def reset(self) -> State:
        self.time_step = 0
        self.queue_standard = 0.0
        self.queue_priority = 0.0
        self.average_wait = 0.0
        pressure = float(self.scenario.orders_per_hour) / max(self._base_capacity_per_hour(), 1.0)
        self.zone_congestion = min(0.95, 0.18 + pressure * 0.22 + self.rng.uniform(0, 0.08))
        self.total_arrivals = 0.0
        self.completed_orders = 0.0
        self.delayed_orders = 0.0
        self.operating_cost = 0.0
        self.worker_busy = 0.0
        self.robot_busy = 0.0
        return self._state()

    def step(self, action_id: int) -> tuple[State, float, bool, Dict[str, float]]:
        action_id = int(np.clip(action_id, 0, len(ACTIONS) - 1))
        action = ACTIONS[action_id]
        arrivals, priority_arrivals = self._sample_arrivals()
        standard_arrivals = arrivals - priority_arrivals
        self.queue_priority += priority_arrivals
        self.queue_standard += standard_arrivals
        self.total_arrivals += arrivals

        worker_capacity, robot_capacity, cost_multiplier = self._action_capacity(action)
        raw_capacity = max(0.0, worker_capacity + robot_capacity)
        capacity = raw_capacity * max(0.35, 1 - self.zone_congestion * 0.12)

        priority_share = self._priority_share(action)
        priority_completed = min(self.queue_priority, capacity * priority_share)
        remaining_capacity = max(0.0, capacity - priority_completed)
        standard_completed = min(self.queue_standard, remaining_capacity)

        leftover_capacity = max(0.0, capacity - priority_completed - standard_completed)
        if leftover_capacity > 0 and self.queue_priority > priority_completed:
            extra_priority = min(self.queue_priority - priority_completed, leftover_capacity)
            priority_completed += extra_priority
            leftover_capacity -= extra_priority
        if leftover_capacity > 0 and self.queue_standard > standard_completed:
            standard_completed += min(self.queue_standard - standard_completed, leftover_capacity)

        completed = priority_completed + standard_completed
        self.queue_priority -= priority_completed
        self.queue_standard -= standard_completed

        delay_threshold = max(capacity * 1.7, arrivals * 0.8, 1.0)
        priority_delay = max(0.0, self.queue_priority - capacity * 0.32) * 0.1
        standard_penalty = 0.045 if action == "delay_low_priority_order" else 0.075
        standard_delay = max(0.0, self.queue_standard - delay_threshold) * standard_penalty
        delayed = priority_delay + standard_delay
        self.delayed_orders += delayed

        queue_total = self.queue_priority + self.queue_standard
        self.average_wait = 0.84 * self.average_wait + 0.16 * (queue_total / max(capacity, 1.0))
        congestion_delta = 0.018 * arrivals / max(float(self.scenario.storage_zones), 1.0) - 0.012 * completed
        if action == "assign_robot_to_congested_zone":
            congestion_delta -= 0.065
        elif action == "rebalance_resources":
            congestion_delta -= 0.05
        elif action == "delay_low_priority_order":
            congestion_delta -= 0.018
        self.zone_congestion = float(np.clip(self.zone_congestion + congestion_delta, 0.02, 0.98))

        hourly_cost = float(self.scenario.workers) * float(self.scenario.cost_per_worker)
        hourly_cost += float(self.scenario.robots) * float(self.scenario.cost_per_robot)
        step_cost = hourly_cost / self.steps_per_hour * cost_multiplier
        step_cost += delayed * float(self.scenario.delay_penalty)
        self.operating_cost += step_cost

        worker_util = min(1.0, completed / max(worker_capacity, 1.0))
        robot_util = min(1.0, max(completed - worker_capacity, 0.0) / max(robot_capacity, 1.0)) if self.scenario.robots else 0.0
        utilisation_balance = 1 - abs(worker_util - robot_util if self.scenario.robots else worker_util)
        throughput_ratio = completed / max(arrivals, 1.0)
        reward_terms = get_rl_spec().reward_terms
        reward = (
            completed * reward_terms["completed_order"]
            + throughput_ratio * reward_terms["throughput"]
            + utilisation_balance * reward_terms["balanced_utilisation"]
            + delayed * reward_terms["delayed_order"]
            + queue_total * reward_terms["queue_length"]
            + (step_cost / 100) * reward_terms["excess_cost"]
        )

        self.completed_orders += completed
        self.worker_busy += worker_util
        self.robot_busy += robot_util
        self.time_step += 1
        done = self.time_step >= self.horizon
        info = {
            "arrivals": arrivals,
            "completed": completed,
            "delayed": delayed,
            "cost": step_cost,
            "worker_utilisation": worker_util,
            "robot_utilisation": robot_util,
        }
        return self._state(), float(reward), done, info

    def summary(self, total_reward: float) -> EpisodeSummary:
        return EpisodeSummary(
            reward=float(total_reward),
            arrivals=float(self.total_arrivals),
            completed=float(self.completed_orders),
            delayed=float(self.delayed_orders),
            cost=float(self.operating_cost),
            worker_utilisation=float(self.worker_busy / max(self.horizon, 1)),
            robot_utilisation=float(self.robot_busy / max(self.horizon, 1)),
        )

    def _base_capacity_per_hour(self) -> float:
        worker_capacity = float(self.scenario.workers) * 60 / float(self.scenario.average_picking_time)
        worker_capacity *= float(self.scenario.worker_efficiency)
        robot_capacity = float(self.scenario.robots) * 60 / max(float(self.scenario.average_picking_time) * 0.72, 0.1)
        return worker_capacity + robot_capacity

    def _sample_arrivals(self) -> tuple[float, float]:
        base = float(self.scenario.orders_per_hour) / self.steps_per_hour
        wave = 1 + 0.16 * np.sin(2 * np.pi * self.time_step / max(self.horizon, 1))
        wave += self.rng.normal(0, float(self.scenario.demand_variability) * 0.22)
        expected = max(0.05, base * wave)
        arrivals = float(self.rng.poisson(expected))
        priority_arrivals = float(self.rng.binomial(int(arrivals), self.priority_ratio)) if arrivals else 0.0
        return arrivals, priority_arrivals

    def _action_capacity(self, action: str) -> tuple[float, float, float]:
        robot_failures = self.rng.binomial(
            int(self.scenario.robots),
            min(max(float(self.scenario.robot_failure_probability), 0.0), 1.0),
        )
        active_robots = max(0, int(self.scenario.robots) - int(robot_failures))
        worker_capacity = (
            float(self.scenario.workers)
            * (self.step_minutes / float(self.scenario.average_picking_time))
            * float(self.scenario.worker_efficiency)
        )
        robot_capacity = active_robots * (self.step_minutes / max(float(self.scenario.average_picking_time) * 0.72, 0.1))
        cost_multiplier = 1.0
        if action == "assign_nearest_worker":
            worker_capacity *= 1.12
            cost_multiplier = 1.04
        elif action == "assign_robot_to_congested_zone":
            robot_capacity *= 1.18
            cost_multiplier = 1.06
        elif action == "rebalance_resources":
            worker_capacity *= 1.05
            robot_capacity *= 1.08
            cost_multiplier = 1.05
        elif action == "delay_low_priority_order":
            worker_capacity *= 0.92
            robot_capacity *= 0.9
            cost_multiplier = 0.88
        elif action == "process_priority_order":
            worker_capacity *= 0.98
            robot_capacity *= 0.98
            cost_multiplier = 1.02
        return worker_capacity, robot_capacity, cost_multiplier

    def _priority_share(self, action: str) -> float:
        if action == "process_priority_order":
            return 0.76
        if action == "delay_low_priority_order":
            return 0.82
        if action == "process_standard_order":
            return max(0.18, min(0.42, self.priority_ratio))
        if action == "rebalance_resources":
            return max(0.34, min(0.58, self.priority_ratio + 0.18))
        return max(0.28, min(0.64, self.priority_ratio + 0.12))

    def _state(self) -> State:
        queue_total = self.queue_priority + self.queue_standard
        capacity_anchor = max(self._base_capacity_per_hour() / self.steps_per_hour, 1.0)
        queue_bucket = int(np.clip(queue_total / capacity_anchor, 0, 5))
        worker_available = int(np.clip(round((1 - min(self.worker_busy / max(self.time_step, 1), 1.0)) * 4), 0, 4))
        robot_available = int(np.clip(round((1 - min(self.robot_busy / max(self.time_step, 1), 1.0)) * 4), 0, 4))
        priority_mix = self.queue_priority / max(queue_total, 1.0)
        priority_bucket = int(np.clip(priority_mix * 4, 0, 4))
        wait_bucket = int(np.clip(self.average_wait, 0, 5))
        congestion_bucket = int(np.clip(self.zone_congestion * 5, 0, 5))
        time_bucket = int(np.clip((self.time_step / max(self.horizon, 1)) * 6, 0, 6))
        return (
            queue_bucket,
            worker_available,
            robot_available,
            priority_bucket,
            wait_bucket,
            congestion_bucket,
            time_bucket,
        )


def _q_values(q_table: Dict[State, np.ndarray], state: State) -> np.ndarray:
    if state not in q_table:
        q_table[state] = np.zeros(len(ACTIONS), dtype=float)
    return q_table[state]


def _fallback_action(state: State) -> int:
    queue_bucket, _, _, priority_bucket, _, congestion_bucket, _ = state
    if congestion_bucket >= 4:
        return ACTIONS.index("assign_robot_to_congested_zone")
    if queue_bucket >= 4:
        return ACTIONS.index("rebalance_resources")
    if priority_bucket >= 2:
        return ACTIONS.index("process_priority_order")
    return ACTIONS.index("assign_nearest_worker")


def _serialise_q_table(q_table: Dict[State, np.ndarray], limit: int = 1500) -> Dict[str, list[float]]:
    ranked = sorted(q_table.items(), key=lambda item: float(np.max(np.abs(item[1]))), reverse=True)
    return {
        _state_key(state): [round(float(value), 5) for value in values]
        for state, values in ranked[:limit]
    }


def _deserialise_q_table(policy_artifact: Dict[str, Any]) -> Dict[State, np.ndarray]:
    raw = policy_artifact.get("q_table", {}) if isinstance(policy_artifact, dict) else {}
    return {
        _state_from_key(key): np.array(values, dtype=float)
        for key, values in raw.items()
        if isinstance(values, Iterable)
    }


def _evaluation_from_summaries(scenario: Any, summaries: list[EpisodeSummary]) -> Dict[str, float]:
    arrivals = sum(item.arrivals for item in summaries)
    completed = sum(item.completed for item in summaries)
    delayed = sum(item.delayed for item in summaries)
    cost = sum(item.cost for item in summaries)
    worker_util = float(np.mean([item.worker_utilisation for item in summaries])) if summaries else 0.0
    robot_util = float(np.mean([item.robot_utilisation for item in summaries])) if summaries else 0.0
    delay_rate = delayed / max(arrivals, 1.0)
    throughput = completed / max(float(scenario.shift_duration) * max(len(summaries), 1), 1.0)
    cost_per_order = cost / max(completed, 1.0)
    efficiency_score = 100 * (
        0.4 * min(completed / max(arrivals, 1.0), 1.0)
        + 0.24 * min(throughput / max(float(scenario.orders_per_hour), 1.0), 1.2) / 1.2
        + 0.22 * (1 - min(delay_rate, 1.0))
        + 0.14 * (1 / (1 + cost_per_order / 100))
    )
    return {
        "delay_rate": round(float(delay_rate), 3),
        "throughput_per_hour": round(float(throughput), 2),
        "cost_per_order": round(float(cost_per_order), 2),
        "efficiency_score": round(float(efficiency_score), 2),
        "worker_utilisation": round(worker_util, 3),
        "robot_utilisation": round(robot_util, 3),
    }


def evaluate_policy_artifact(
    scenario: Any,
    policy_artifact: Dict[str, Any],
    episodes: int = 20,
    seed: int | None = 42,
) -> Dict[str, Any]:
    q_table = _deserialise_q_table(policy_artifact)
    reward_curve: list[float] = []
    summaries: list[EpisodeSummary] = []
    for episode in range(episodes):
        env = WarehouseControlEnv(scenario, (seed or 0) + episode + 10_000)
        state = env.reset()
        total_reward = 0.0
        done = False
        while not done:
            values = q_table.get(state)
            action = int(np.argmax(values)) if values is not None else _fallback_action(state)
            state, reward, done, _ = env.step(action)
            total_reward += reward
        reward_curve.append(round(float(total_reward), 3))
        summaries.append(env.summary(total_reward))
    metrics = _evaluation_from_summaries(scenario, summaries)
    metrics.update(
        {
            "average_reward": round(float(np.mean(reward_curve)), 3) if reward_curve else 0.0,
            "final_reward": reward_curve[-1] if reward_curve else 0.0,
            "best_reward": round(float(max(reward_curve)), 3) if reward_curve else 0.0,
        }
    )
    return {"evaluation_metrics": metrics, "reward_curve": reward_curve}


def generate_training_run(
    scenario: Any,
    episodes: int,
    seed: int | None = 42,
    algorithm: str = "TabularQAgent",
) -> Dict[str, Any]:
    rng = np.random.default_rng(seed or 0)
    q_table: Dict[State, np.ndarray] = {}
    reward_curve: list[float] = []
    action_counts = {action: 0 for action in ACTIONS}
    gamma = 0.92
    base_learning_rate = 0.18

    for episode in range(episodes):
        env = WarehouseControlEnv(scenario, int(rng.integers(0, 2_000_000_000)))
        state = env.reset()
        epsilon = max(0.035, 0.35 * (1 - episode / max(episodes, 1)))
        learning_rate = max(0.035, base_learning_rate * (1 - episode / max(episodes * 1.4, 1)))
        total_reward = 0.0
        done = False
        while not done:
            values = _q_values(q_table, state)
            if rng.random() < epsilon:
                action = int(rng.integers(0, len(ACTIONS)))
            else:
                action = int(np.argmax(values))
            next_state, reward, done, _ = env.step(action)
            next_values = _q_values(q_table, next_state)
            target = reward if done else reward + gamma * float(np.max(next_values))
            values[action] += learning_rate * (target - values[action])
            action_counts[ACTIONS[action]] += 1
            total_reward += reward
            state = next_state
        reward_curve.append(round(float(total_reward), 3))

    policy_artifact = {
        "algorithm": algorithm,
        "actions": ACTIONS,
        "state_encoding": get_rl_spec().state_fields,
        "q_table": _serialise_q_table(q_table),
        "fallback_policy": "congestion/queue/priority heuristic for unseen states",
    }
    evaluation = evaluate_policy_artifact(scenario, policy_artifact, episodes=min(max(10, episodes // 5), 50), seed=(seed or 0) + 777)
    comparison = {"RL Agent Strategy": evaluation["evaluation_metrics"]}
    action_total = max(sum(action_counts.values()), 1)
    action_mix = {
        action: round(count / action_total, 3)
        for action, count in sorted(action_counts.items(), key=lambda item: item[1], reverse=True)
    }
    spec = get_rl_spec()
    return {
        "reward_function": spec.reward_terms,
        "training_metrics": {
            "average_reward": round(float(np.mean(reward_curve)), 3) if reward_curve else 0.0,
            "final_reward": reward_curve[-1] if reward_curve else 0.0,
            "best_reward": round(float(max(reward_curve)), 3) if reward_curve else 0.0,
            "delay_rate": comparison["RL Agent Strategy"]["delay_rate"],
            "throughput_per_hour": comparison["RL Agent Strategy"]["throughput_per_hour"],
            "learned_states": len(q_table),
            "stored_policy_states": len(policy_artifact["q_table"]),
            "exploration_final": round(max(0.035, 0.35 * (1 - episodes / max(episodes, 1))), 3),
            "action_mix": action_mix,
            "algorithm_note": (
                f"{algorithm} runs real tabular Q-learning over a discretised warehouse control MDP. "
                "It is dependency-light and suitable for local operational policy experiments."
            ),
            "policy_artifact": policy_artifact,
        },
        "reward_curve": reward_curve,
        "comparison_metrics": comparison,
    }

