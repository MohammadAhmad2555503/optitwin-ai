from statistics import mean
from typing import Any, Dict, List


def summarise_time_series(time_series: List[Dict[str, Any]]) -> Dict[str, float]:
    if not time_series:
        return {"peak_queue": 0.0, "average_step_cost": 0.0, "max_delayed_step": 0.0}
    return {
        "peak_queue": float(max(point["queue_length"] for point in time_series)),
        "average_step_cost": float(mean(point["cost"] for point in time_series)),
        "max_delayed_step": float(max(point["delayed"] for point in time_series)),
    }

