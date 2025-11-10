from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import User, UserType
from services.auth_service import get_current_user
from services.ml_services import calculate_patient_risk
router = APIRouter(prefix="/ml", tags=["machine-learning"])
@router.get("/risk-analysis")
async def get_risk_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Endpoint para análise de risco dos pacientes de um psicólogo.
    Retorna lista de pacientes com seus níveis de risco.
    """
    if current_user.user_type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="apenas psicologos podem acessar analise de risco."
        )
    
    risk_analysis = calculate_patient_risk(db, current_user.id)
    total_patients = len(risk_analysis)
    high_risk = len([p for p in risk_analysis if p["risk"] == "Alto"])
    moderate_risk = len([p for p in risk_analysis if p["risk"] == "Moderado"])
    low_risk = len([p for p in risk_analysis if p["risk"] == "Baixo"])
    return {
        "summary": {
            "total_patients": total_patients,
            "high_risk": high_risk,
            "moderate_risk": moderate_risk,
            "low_risk": low_risk,
            "risk_distribution": {
                "Alto": f"{(high_risk/total_patients*100):.iff}%" if total_patients > 0 else "0%",
                "Moderado": f"{(moderate_risk/total_patients*100):.if}%" if total_patients > 0 else "0%",
                "Baixo": f"{(low_risk/total_patients*100):.if}%" if total_patients > 0 else "0%",
            }    
        },
        "patients": risk_analysis
    }
@router.get("/risk-analysis/{patient_id}")
async def get_patient_risk_analysis(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter análise de risco de um paciente específico.
    """
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="apenas psicologos podem acessar analise de risco."
        )
    risk_analysis = calculate_patient_risk(db, current_user.id)
    patient_risk = next((p for p in risk_analysis if p["id"] == patient_id), None)
    if not patient_risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente nao encontrado ou sem dados suficiente."
        )
    return patient_risk