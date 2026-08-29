# OptiTwinAI Backend

FastAPI backend for the OptiTwinAI digital twin optimisation platform.

## Windows Setup

```powershell
cd optitwinai\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

The app creates SQLite tables on startup using:

```text
DATABASE_URL=sqlite:///./optitwinai.db
```

When `DEMO_MODE=true`, startup seeds a local sample workspace:

- Email: `demo@optitwin.ai`
- Password: `demo-password`
- Scenario: `Metro Fulfilment Twin`

## Useful URLs

- Root: <http://127.0.0.1:8000>
- Health: <http://127.0.0.1:8000/health>
- Swagger docs: <http://127.0.0.1:8000/docs>

## Verification

```powershell
cd optitwinai\backend
.\venv\Scripts\python.exe -m compileall app
.\venv\Scripts\python.exe -m pytest tests
```

## Notes

- Authentication is JWT-based.
- Passwords are hashed with passlib/bcrypt.
- Every product route is protected with `get_current_user`.
- JSON experiment outputs are stored as text for SQLite compatibility.
- The RL lab trains a local tabular Q-learning policy and stores the policy artifact with each run.
- PostgreSQL migration is a `DATABASE_URL` and migration-tooling step away.

