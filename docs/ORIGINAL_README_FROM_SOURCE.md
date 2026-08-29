# OptiTwinAI

**OptiTwinAI: Fractional-Order Optimisation for Digital Twin AI Systems**

OptiTwinAI is a local-first full-stack AI decision platform for warehouse and supply-chain optimisation. It combines a FastAPI backend, SQLite-first SQLAlchemy persistence, a React/Vite/Tailwind frontend, a deterministic digital twin simulation engine, optimiser comparisons, convergence/stability analysis, tabular reinforcement-learning policy training, dashboard analytics, what-if analysis, and Markdown report generation.

## Why It Is Unique

OptiTwinAI is designed as a real running application rather than a UI mockup. The product includes working mathematical, simulation, persistence, and reporting layers:

- Warehouse digital twin simulation with order arrivals, queues, priority orders, worker/robot capacity, robot failures, restocking drag, cost, throughput, utilisation, and strategy metrics.
- Optimisation lab with Sphere, Rosenbrock, and Rastrigin functions.
- Gradient Descent, noisy SGD-style updates, Adam, and an experimental fractional-inspired gradient-memory optimiser.
- Convergence and stability analytics over actual stored loss curves.
- RL policy lab with a built-in tabular Q-learning trainer, stored policy artifacts, evaluation, and rule-based strategy comparison.
- Markdown reports generated from stored scenario, simulation, optimisation, what-if, and RL records.

## Tech Stack

Backend:

- Python, FastAPI, SQLAlchemy ORM, SQLite, Pydantic, pydantic-settings
- JWT auth with python-jose and passlib password hashing
- NumPy, pandas, SciPy dependencies for analytical workloads

Frontend:

- React, TypeScript, Vite, Tailwind CSS
- React Router, Axios, Recharts, lucide-react
- Premium dark dashboard UI

## Architecture

```text
optitwinai/
  backend/
    app/
      models/          SQLAlchemy ORM tables
      schemas/         Pydantic request/response contracts
      routes/          FastAPI route modules
      services/        Business logic and persistence orchestration
      simulation/      Warehouse digital twin engine
      optimisation/    Benchmark functions, optimisers, stability math
      rl/              RL environment spec and tabular Q-learning engine
      utils/           Security and auth dependencies
  frontend/
    src/
      components/      Layout and reusable UI
      pages/           Product screens
      services/        Axios API clients
      context/         Auth context
      types/           Shared TypeScript types
```

SQLite is the first-run database. Migration to PostgreSQL is intentionally straightforward because persistence goes through SQLAlchemy and `DATABASE_URL`.

## Backend Setup

```powershell
cd optitwinai\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Backend URLs:

- API root: <http://127.0.0.1:8000>
- Health: <http://127.0.0.1:8000/health>
- Docs: <http://127.0.0.1:8000/docs>

Backend verification:

```powershell
cd optitwinai\backend
.\venv\Scripts\python.exe -m compileall app
.\venv\Scripts\python.exe -m pytest tests
```

## Frontend Setup

```powershell
cd optitwinai\frontend
npm install
npm run dev
```

Frontend URL:

- <http://127.0.0.1:5173>

Frontend verification:

```powershell
cd optitwinai\frontend
npm.cmd run lint
npm.cmd run build
```

If `npm` is not on PATH in VS Code, install Node.js LTS or open a terminal where Node/npm are available. The frontend was manually created and does not require `npm create vite`.

## API Surface

- Auth: `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`
- Scenarios: `POST /scenarios`, `GET /scenarios`, `GET /scenarios/{id}`, `PATCH /scenarios/{id}`, `DELETE /scenarios/{id}`
- Simulation: `POST /simulation/run`, `GET /simulation/runs`, `GET /simulation/runs/{id}`, `POST /simulation/compare-strategies`
- What-if: `POST /whatif/run`, `GET /whatif/results`, `GET /whatif/results/{id}`
- Optimisation: `POST /optimisation/run`, `GET /optimisation/experiments`, `GET /optimisation/experiments/{id}`, `POST /optimisation/compare`, `POST /optimisation/alpha-sensitivity`
- Analysis: `POST /analysis/convergence`, `POST /analysis/stability`
- RL: `POST /rl/train`, `GET /rl/runs`, `GET /rl/runs/{id}`, `POST /rl/evaluate`, `POST /rl/compare-with-strategies`
- Reports: `POST /reports/generate`, `GET /reports`, `GET /reports/{id}`
- Dashboard: `GET /dashboard/summary`, `GET /dashboard/recent-activity`

## Simulation Explanation

The warehouse simulation is deterministic when a seed is passed. It models:

- Poisson-like order arrivals with demand variability
- Priority order mix
- Worker and robot processing capacity
- Robot failures and restocking drag
- Queue growth, delayed orders, bottleneck zones
- Throughput, cost per order, total cost, utilisation, efficiency score

Supported strategies:

1. First-Come-First-Served
2. Priority-Based Processing
3. Nearest-Worker Assignment
4. Cost-Minimising Assignment
5. Hybrid Heuristic Strategy
6. RL Agent Strategy

## Optimisation Explanation

The optimiser engine benchmarks Sphere, Rosenbrock, and Rastrigin functions using analytical gradients. It returns loss curves, final positions, runtime, best/final loss, threshold iteration, improvement, convergence speed, oscillation, smoothness, stability score, and divergence flags.

## Fractional Optimiser Explanation

`Fractional GD` is implemented as an **experimental fractional-inspired optimiser**. It uses a memory-weighted gradient history:

- `alpha` is constrained between `0.1` and `1.0`.
- Lower `alpha` gives older gradients more influence.
- `alpha` near `1.0` behaves closer to standard gradient descent.
- It is intentionally not claimed as a complete fractional calculus implementation.

## RL Policy Training Explanation

The RL lab defines state fields, actions, and reward terms matching a warehouse control problem. The backend trains a real tabular Q-learning policy over a discretised Markov decision process:

- State: queue pressure, worker availability, robot availability, priority mix, waiting pressure, zone congestion, and time bucket.
- Actions: process standard or priority orders, assign workers, assign robots to congestion, delay low-priority work, or rebalance resources.
- Reward: completed orders, throughput, balanced utilisation, queue length, delay, and operating cost.
- Persistence: the learned Q-table policy artifact is stored in SQLite with the training run.
- Evaluation: stored policies can be re-evaluated and compared against rule-based simulation strategies.

This avoids heavyweight RL dependencies for the first Windows run while still providing a real learning loop and a clean future path to Gymnasium or Stable-Baselines3.

## Operating Workflow

1. Start the backend.
2. Start the frontend.
3. Login with the seeded sample user `demo@optitwin.ai` / `demo-password`, or signup with a local user.
4. Create a scenario in Scenario Builder.
5. Run Hybrid Heuristic simulation.
6. Run Strategy Comparison.
7. Run What-if Analysis.
8. Run Optimisation Lab with all optimisers.
9. Analyse convergence and stability.
10. Train and evaluate an RL policy.
11. Generate a Markdown report.

## Future Improvements

- Alembic migrations and PostgreSQL deployment profile
- Real warehouse telemetry ingestion
- Optional Gymnasium/Stable-Baselines3 integration for larger training jobs
- Batch scenario calibration
- Experiment versioning and shareable report links

