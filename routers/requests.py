from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime
from core.database import get_db
from models.models import Request, User, UserType, RequestStatus
from schemas.schemas import RequestCreate, RequestUpdate, Request as RequestSchema
from services.auth_service import get_current_user
 
router = APIRouter(prefix="/requests", tags=["requests"])
 
# Rota para listar todas as solicitações (requests)
@router.get("/", response_model=List[RequestSchema])
def get_requests(
    current_user: User = Depends(get_current_user),  # Obtém o usuário logado via token
    db: Session = Depends(get_db)                    # Conexão com o banco
):
    """
    Retorna todas as solicitações de atendimento recebidas por um psicólogo específico.
    Apenas psicólogos podem acessar.
    """
    # Verifica se o usuário logado é psicólogo
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem listar solicitações"
        )
 
    # Busca todas as solicitações do psicólogo logado
    requests = db.query(Request).filter(
        Request.preferred_psychologist == current_user.id
    ).all()
 
    # Converte os campos preferred_dates e preferred_times de JSON para listas antes de retornar
    for req in requests:
        req.preferred_dates = json.loads(req.preferred_dates) if req.preferred_dates else []
        req.preferred_times = json.loads(req.preferred_times) if req.preferred_times else []
 
    return requests
 
 
# Rota para criar uma nova solicitação
@router.post("/", response_model=RequestSchema)
def create_request(
    request_data: RequestCreate,   # Dados de entrada (nome, email, psicólogo, descrição etc.)
    db: Session = Depends(get_db), # Sessão com o banco de dados
):
    print(f"[REQUEST] Dados recebidos: {request_data.dict()}")
    """
    Permite que um paciente crie uma nova solicitação de atendimento para um psicólogo.
    Verifica se já existe uma solicitação pendente entre o mesmo paciente e psicólogo.
    Os campos de data e horário são salvos como JSON no banco.
    """
    # Validar se listas estão vazias e fornecer valores padrão
    if not request_data.preferred_dates:
        request_data.preferred_dates = []
    if not request_data.preferred_times:
        request_data.preferred_times = []
    
    # Verifica se o paciente já tem uma solicitação pendente para o mesmo psicólogo
    existing_request = db.query(Request).filter(
        Request.patient_email == request_data.patient_email,
        Request.preferred_psychologist == request_data.preferred_psychologist,
        Request.status == RequestStatus.PENDENTE
    ).first()
 
    # Se houver uma solicitação pendente, retorna erro
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já possui uma solicitação pendente para este psicólogo"
        )
 
    # Cria nova solicitação
    new_request = Request(
        patient_name=request_data.patient_name,
        patient_email=request_data.patient_email,
        patient_phone=request_data.patient_phone,
        preferred_psychologist=request_data.preferred_psychologist,
        description=request_data.description,
        urgency=request_data.urgency or "media",
        preferred_dates=json.dumps(request_data.preferred_dates or []),
        preferred_times=json.dumps(request_data.preferred_times or []),
        status=RequestStatus.PENDENTE
    )
 
    # Adiciona no banco
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
 
    # Converte campos para lista (para o retorno da API)
    new_request.preferred_dates = request_data.preferred_dates
    new_request.preferred_times = request_data.preferred_times
 
    return new_request
 
# Rota para atualizar status da solicitação
@router.get("/{request_id}", response_model=RequestSchema)
def get_request_by_id(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca uma solicitação específica por ID"""
    
    request = db.query(Request).filter(Request.id == request_id).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada"
        )
    
    # Converte campos JSON para lista
    request.preferred_dates = json.loads(request.preferred_dates) if request.preferred_dates else []
    request.preferred_times = json.loads(request.preferred_times) if request.preferred_times else []
    
    return request


@router.put("/{request_id}", response_model=RequestSchema)
def update_request(
    request_id: int,               # ID da solicitação a ser atualizada
    update_data: RequestUpdate,    # Dados de atualização (status, notas)
    current_user: User = Depends(get_current_user),  # Usuário autenticado
    db: Session = Depends(get_db)                    # Sessão do banco
):
    """
    Permite que o psicólogo aceite, rejeite ou atualize uma solicitação.
    Apenas psicólogos podem realizar essa operação.
    """
    # Garante que apenas psicólogos possam atualizar solicitações
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem atualizar solicitações"
        )
 
    # Busca a solicitação pelo ID e garante que pertence ao psicólogo logado
    request = db.query(Request).filter(
        Request.id == request_id,
        Request.preferred_psychologist == current_user.id
    ).first()
 
    # Caso não exista, retorna erro 404
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada"
        )
 
    # Atualiza o status e observações da solicitação
    request.status = update_data.status
    request.notes = update_data.notes or ""  # Se não houver notas, salva string vazia
    request.updated_at = datetime.utcnow()   # Atualiza a data/hora da última modificação
 
    db.commit()
    db.refresh(request)
 
    # Converte novamente os campos JSON para lista antes de retornar
    request.preferred_dates = json.loads(request.preferred_dates) if request.preferred_dates else []
    request.preferred_times = json.loads(request.preferred_times) if request.preferred_times else []
 
    return request

@router.get("/psychologist/{psychologist_id}")
async def get_psychologist_requests(
    psychologist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca solicitações de um psicólogo"""
    
    if current_user.type != UserType.PSICOLOGO or current_user.id != psychologist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    requests = db.query(Request).filter(
        Request.preferred_psychologist == psychologist_id
    ).all()
    
    result = []
    for req in requests:
        result.append({
            "id": req.id,
            "patient_name": req.patient_name,
            "patient_email": req.patient_email,
            "patient_phone": req.patient_phone,
            "psychologist_id": req.preferred_psychologist,
            "description": req.description,
            "urgency": req.urgency,
            "status": req.status,
            "notes": req.notes,
            "is_read": False,
            "created_at": req.created_at,
            "preferred_dates": json.loads(req.preferred_dates) if req.preferred_dates else [],
            "preferred_times": json.loads(req.preferred_times) if req.preferred_times else []
        })
    
    return result

@router.get("/patient/{patient_email}")
async def get_patient_requests(
    patient_email: str,
    db: Session = Depends(get_db)
):
    """Busca solicitações de um paciente por email"""
    
    requests = db.query(Request).filter(
        Request.patient_email == patient_email
    ).all()
    
    result = []
    for req in requests:
        result.append({
            "id": req.id,
            "patient_name": req.patient_name,
            "patient_email": req.patient_email,
            "patient_phone": req.patient_phone,
            "preferred_psychologist": req.preferred_psychologist,
            "description": req.description,
            "urgency": req.urgency,
            "status": req.status,
            "created_at": req.created_at,
            "preferred_dates": json.loads(req.preferred_dates) if req.preferred_dates else [],
            "preferred_times": json.loads(req.preferred_times) if req.preferred_times else []
        })
    
    return result

@router.patch("/{request_id}/read")
async def mark_request_as_read(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca solicitação como lida"""
    
    request = db.query(Request).filter(Request.id == request_id).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada"
        )
    
    return {"id": request_id, "is_read": True}

@router.patch("/{request_id}/accept")
async def accept_patient_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aceita solicitação e cria relacionamento psicólogo-paciente"""
    
    if current_user.type != UserType.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas psicólogos podem aceitar solicitações"
        )
    
    request = db.query(Request).filter(
        Request.id == request_id,
        Request.preferred_psychologist == current_user.id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada"
        )
    
    request.status = RequestStatus.ACEITO
    request.updated_at = datetime.utcnow()
    
    from models.models import Patient
    from Utils import calculate_age
    from datetime import date
    
    existing_patient = db.query(Patient).filter(
        Patient.email == request.patient_email
    ).first()
    
    print(f"[DEBUG] Aceitando solicitação ID: {request_id}")
    print(f"[DEBUG] Paciente email: {request.patient_email}")
    print(f"[DEBUG] Psicólogo ID: {current_user.id}")
    print(f"[DEBUG] Paciente existente: {existing_patient is not None}")
    
    if not existing_patient:
        birth_date = date(1990, 1, 1)
        new_patient = Patient(
            name=request.patient_name,
            email=request.patient_email,
            phone=request.patient_phone,
            birth_date=birth_date,
            age=calculate_age(birth_date),
            psychologist_id=current_user.id,
            status="Ativo"
        )
        db.add(new_patient)
        db.flush()
        patient_id = new_patient.id
        print(f"[DEBUG] Novo paciente criado com ID: {patient_id}")
    else:
        existing_patient.psychologist_id = current_user.id
        existing_patient.status = "Ativo"
        patient_id = existing_patient.id
        print(f"[DEBUG] Paciente existente atualizado, ID: {patient_id}")
    
    db.commit()
    print(f"[DEBUG] Commit realizado com sucesso")
    
    return {
        "message": "Paciente aceito com sucesso",
        "patient_id": patient_id,
        "patient_name": request.patient_name,
        "can_message": True
    }