import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite:///./test_optitwinai.db"
os.environ["DEMO_MODE"] = "false"
os.environ["JWT_SECRET"] = "test-secret"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _auth_headers(client: TestClient) -> dict[str, str]:
    email = f"ops-{uuid4().hex[:8]}@optitwin.local"
    password = "demo-password"
    signup = client.post(
        "/auth/signup",
        json={
            "name": "Operations Lead",
            "email": email,
            "password": password,
            "confirm_password": password,
        },
    )
    assert signup.status_code == 200, signup.text
    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _scenario_payload() -> dict[str, float | int | str]:
    return {
        "name": "Regional Fulfilment Twin",
        "workers": 18,
        "robots": 9,
        "orders_per_hour": 210,
        "storage_zones": 7,
        "average_picking_time": 3.8,
        "priority_order_percentage": 22,
        "robot_failure_probability": 0.035,
        "worker_efficiency": 0.91,
        "shift_duration": 8,
        "cost_per_worker": 25,
        "cost_per_robot": 10,
        "delay_penalty": 4.2,
        "demand_variability": 0.24,
        "inventory_restock_frequency": 2,
    }


def test_full_decision_workflow():
    with TestClient(app) as client:
        headers = _auth_headers(client)

        scenario_response = client.post("/scenarios", json=_scenario_payload(), headers=headers)
        assert scenario_response.status_code == 201, scenario_response.text
        scenario_id = scenario_response.json()["id"]

        simulation_response = client.post(
            "/simulation/run",
            json={"scenario_id": scenario_id, "strategy_name": "Hybrid Heuristic Strategy", "seed": 42},
            headers=headers,
        )
        assert simulation_response.status_code == 200, simulation_response.text
        simulation = simulation_response.json()
        assert simulation["throughput_per_hour"] > 0

        comparison_response = client.post(
            "/simulation/compare-strategies",
            json={"scenario_id": scenario_id, "seed": 42},
            headers=headers,
        )
        assert comparison_response.status_code == 200, comparison_response.text
        assert comparison_response.json()["best_strategy"]

        whatif_response = client.post(
            "/whatif/run",
            json={
                "base_scenario_id": scenario_id,
                "strategy_name": "Hybrid Heuristic Strategy",
                "modified_parameters": {"robots": 12, "workers": 20},
                "seed": 42,
            },
            headers=headers,
        )
        assert whatif_response.status_code == 200, whatif_response.text
        assert "recommendation" in whatif_response.json()

        optimisation_response = client.post(
            "/optimisation/run",
            json={
                "function_name": "sphere",
                "optimisers": ["Gradient Descent", "SGD", "Adam", "Fractional GD"],
                "learning_rate": 0.02,
                "iterations": 60,
                "alpha": 0.7,
                "seed": 42,
            },
            headers=headers,
        )
        assert optimisation_response.status_code == 200, optimisation_response.text
        optimisation = optimisation_response.json()
        assert "Fractional GD" in optimisation["results"]

        convergence_response = client.post(
            "/analysis/convergence",
            json={"curves": optimisation["convergence_curves"], "threshold": 0.001},
            headers=headers,
        )
        assert convergence_response.status_code == 200, convergence_response.text
        assert "ranking" in convergence_response.json()

        stability_response = client.post(
            "/analysis/stability",
            json={"curves": optimisation["convergence_curves"], "learning_rates": [0.01, 0.02], "alphas": [0.5, 0.7]},
            headers=headers,
        )
        assert stability_response.status_code == 200, stability_response.text
        assert "sensitivity" in stability_response.json()

        rl_response = client.post(
            "/rl/train",
            json={"scenario_id": scenario_id, "algorithm": "TabularQAgent", "episodes": 12, "seed": 42},
            headers=headers,
        )
        assert rl_response.status_code == 200, rl_response.text
        rl_run = rl_response.json()
        assert rl_run["training_metrics"]["learned_states"] > 0
        assert rl_run["training_metrics"]["policy_artifact"]["q_table"]

        rl_eval_response = client.post(
            "/rl/evaluate",
            json={"scenario_id": scenario_id, "run_id": rl_run["id"], "episodes": 3, "seed": 43},
            headers=headers,
        )
        assert rl_eval_response.status_code == 200, rl_eval_response.text
        assert rl_eval_response.json()["evaluation_metrics"]["throughput_per_hour"] > 0

        report_response = client.post(
            "/reports/generate",
            json={
                "title": "Regional Fulfilment Decision Report",
                "scenario_id": scenario_id,
                "simulation_run_id": simulation["id"],
                "optimisation_experiment_id": optimisation["id"],
                "rl_run_id": rl_run["id"],
            },
            headers=headers,
        )
        assert report_response.status_code == 200, report_response.text
        assert "Reinforcement Learning Results" in report_response.json()["report_markdown"]

        dashboard_response = client.get("/dashboard/summary", headers=headers)
        assert dashboard_response.status_code == 200, dashboard_response.text
        assert dashboard_response.json()["total_scenarios"] == 1

