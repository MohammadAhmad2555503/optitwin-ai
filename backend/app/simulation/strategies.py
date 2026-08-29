STRATEGIES = [
    "First-Come-First-Served",
    "Priority-Based Processing",
    "Nearest-Worker Assignment",
    "Cost-Minimising Assignment",
    "Hybrid Heuristic Strategy",
    "RL Agent Strategy",
]


STRATEGY_PROFILES = {
    "First-Come-First-Served": {
        "capacity_multiplier": 0.96,
        "priority_delay_multiplier": 1.14,
        "cost_multiplier": 1.0,
        "queue_discipline": 0.94,
    },
    "Priority-Based Processing": {
        "capacity_multiplier": 0.99,
        "priority_delay_multiplier": 0.72,
        "cost_multiplier": 1.03,
        "queue_discipline": 0.9,
    },
    "Nearest-Worker Assignment": {
        "capacity_multiplier": 1.08,
        "priority_delay_multiplier": 0.9,
        "cost_multiplier": 1.02,
        "queue_discipline": 0.84,
    },
    "Cost-Minimising Assignment": {
        "capacity_multiplier": 0.93,
        "priority_delay_multiplier": 1.0,
        "cost_multiplier": 0.88,
        "queue_discipline": 1.02,
    },
    "Hybrid Heuristic Strategy": {
        "capacity_multiplier": 1.14,
        "priority_delay_multiplier": 0.7,
        "cost_multiplier": 0.96,
        "queue_discipline": 0.72,
    },
    "RL Agent Strategy": {
        "capacity_multiplier": 1.18,
        "priority_delay_multiplier": 0.64,
        "cost_multiplier": 0.98,
        "queue_discipline": 0.68,
    },
}


def normalise_strategy(name: str) -> str:
    if name in STRATEGY_PROFILES:
        return name
    lowered = name.lower().strip()
    for strategy in STRATEGIES:
        if lowered in strategy.lower():
            return strategy
    return "Hybrid Heuristic Strategy"

