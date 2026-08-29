# OptiTwinAI Frontend

React + TypeScript + Vite frontend for OptiTwinAI.

## Setup

```powershell
cd optitwinai\frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The frontend expects the backend at:

```text
http://127.0.0.1:8000
```

Override with:

```powershell
$env:VITE_API_URL="http://127.0.0.1:8000"
npm run dev
```

## Verification

```powershell
cd optitwinai\frontend
npm.cmd run lint
npm.cmd run build
```

## Included Screens

- Landing
- Signup and Login
- Dashboard
- Scenario Builder and Library
- Simulation Runner
- Strategy Comparison
- What-if Analysis
- Optimisation Lab
- Convergence Analysis
- Stability Analysis
- RL Lab
- Report Generator
- Settings

