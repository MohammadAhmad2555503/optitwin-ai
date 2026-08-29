from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import *  # noqa: F401,F403 - registers SQLAlchemy models
from app.routes import analysis, auth, dashboard, optimisation, reports, rl, scenarios, simulation, whatif
from app.services.demo_data_service import seed_demo_data


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.demo_mode:
        db = SessionLocal()
        try:
            seed_demo_data(db)
        finally:
            db.close()
    yield


app = FastAPI(
    title="OptiTwinAI",
    description="AI Digital Twin and Fractional-Order Optimisation Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "OptiTwinAI",
        "description": "Fractional-Order Optimisation for Digital Twin AI Systems",
        "status": "ready",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "environment": settings.environment}


app.include_router(auth.router)
app.include_router(scenarios.router)
app.include_router(simulation.router)
app.include_router(whatif.router)
app.include_router(optimisation.router)
app.include_router(analysis.router)
app.include_router(rl.router)
app.include_router(reports.router)
app.include_router(dashboard.router)

