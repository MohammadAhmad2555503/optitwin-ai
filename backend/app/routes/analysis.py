from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.optimisation import ConvergenceAnalysisRequest, StabilityAnalysisRequest
from app.services.analysis_service import analyse_convergence, analyse_stability
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/convergence")
def convergence(payload: ConvergenceAnalysisRequest, current_user: User = Depends(get_current_user)):
    return analyse_convergence(payload.curves, payload.threshold)


@router.post("/stability")
def stability(payload: StabilityAnalysisRequest, current_user: User = Depends(get_current_user)):
    return analyse_stability(payload.curves, payload.learning_rates, payload.alphas)

