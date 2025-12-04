from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import User, UserType
from schemas.schemas import ReportsData
from services.auth_service import get_current_user
from services.report_service import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{psychologist_id}", response_model=ReportsData)
async def get_reports(
    psychologist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verifica se é um psicólogo
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem acessar relatórios"
        )


    # Impede acesso a relatórios de outros psicólogos
    if current_user.id != psychologist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode acessar seus próprios relatórios"
        )

    # Gera o relatório
    try:
        return generate_report(db, psychologist_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )

@router.get("/{psychologist_id}/risk-analysis")
async def get_risk_analysis(
    psychologist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna análise de risco dos pacientes"""
    
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem acessar análise de risco"
        )
    
    if current_user.id != psychologist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode acessar suas próprias análises"
        )
    
    from services.ml_services import calculate_patient_risk
    
    try:
        risk_data = calculate_patient_risk(db, psychologist_id)
        
        summary = {
            "total_patients": len(risk_data),
            "high_risk": len([p for p in risk_data if p["risk"] == "Alto"]),
            "moderate_risk": len([p for p in risk_data if p["risk"] == "Moderado"]),
            "low_risk": len([p for p in risk_data if p["risk"] == "Baixo"])
        }
        
        return {
            "summary": summary,
            "patients": risk_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar análise: {str(e)}"
        )
