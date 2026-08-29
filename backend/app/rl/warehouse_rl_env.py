from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


ACTIONS = [
    "process_standard_order",
    "process_priority_order",
    "assign_nearest_worker",
    "assign_robot_to_congested_zone",
    "delay_low_priority_order",
    "rebalance_resources",
]


STATE_FIELDS = [
    "queue_length",
    "worker_availability",
    "robot_availability",
    "priority_order_ratio",
    "average_waiting_time",
    "zone_congestion",
    "current_time_step",
]


@dataclass
class WarehouseRLSpec:
    state_fields: List[str]
    actions: List[str]
    reward_terms: Dict[str, float]


def get_rl_spec() -> WarehouseRLSpec:
    return WarehouseRLSpec(
        state_fields=STATE_FIELDS,
        actions=ACTIONS,
        reward_terms={
            "completed_order": 2.0,
            "delayed_order": -2.5,
            "queue_length": -0.08,
            "excess_cost": -0.04,
            "throughput": 1.5,
            "balanced_utilisation": 0.7,
        },
    )

