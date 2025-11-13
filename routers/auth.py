# ============================================================================
# AUTH.PY - ROTAS DE AUTENTICAÇÃO
# ============================================================================
# Este arquivo define as rotas relacionadas à autenticação:
# - POST /auth/login - Login de usuários existentes
# - POST /auth/register - Registro de novos usuários
# - Geração de tokens JWT
# - Criação automática de pacientes quando necessário
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import User, Patient, UserType
from schemas.schemas import UserCreate, UserLogin, Token, User as UserSchema
from services.auth_service import authenticate_user
from Utils import get_password_hash, create_access_token, calculate_age
from datetime import timedelta

# ============================================================================
# CONFIGURAÇÃO DO ROUTER
# ============================================================================

# Cria router com prefixo /auth e tag para documentação
router = APIRouter(prefix="/auth", tags=["auth"])

# ============================================================================
# ROTA DE LOGIN
# ============================================================================

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica um usuário existente e retorna token JWT.
    
    Processo:
        1. Valida credenciais (email/senha)
        2. Gera token JWT com expiração de 30 minutos
        3. Retorna token e dados do usuário
    
    Args:
        user_data: Email e senha do usuário
        db: Sessão do banco de dados
    
    Returns:
        Token: Objeto contendo access_token, token_type e dados do user
    
    Raises:
        HTTPException 401: Se credenciais inválidas
    
    Exemplo de uso:
        POST /auth/login
        {
            "email": "ana@test.com",
            "password": "123456"
        }
    
    Resposta:
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
            "user": {
                "id": 2,
                "email": "ana@test.com",
                "name": "Dra. Ana Costa",
                "type": "psicologo"
            }
        }
    """
    # Autentica usuário usando o serviço de autenticação
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Gera token JWT com email do usuário e expiração de 30 minutos
    access_token = create_access_token(
        data={"sub": user.email},  # "sub" (subject) é padrão JWT para identificar usuário
        expires_delta=timedelta(minutes=30)
    )
    
    # Retorna token e dados do usuário (sem a senha)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserSchema.from_orm(user)  # Converte modelo SQLAlchemy para Pydantic
    )

# ============================================================================
# ROTA DE REGISTRO
# ============================================================================

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.
    
    Processo:
        1. Verifica se email já existe
        2. Cria usuário com senha hasheada
        3. Se for paciente, cria registro na tabela patients
        4. Gera token JWT automaticamente
        5. Retorna token para login automático
    
    Args:
        user_data: Dados do novo usuário (email, senha, nome, tipo, etc.)
        db: Sessão do banco de dados
    
    Returns:
        Token: Token JWT e dados do usuário criado
    
    Raises:
        HTTPException 400: Se email já cadastrado
    
    Exemplo de uso:
        POST /auth/register
        {
            "email": "novo@test.com",
            "password": "123456",
            "name": "João Silva",
            "type": "paciente",
            "birth_date": "1990-05-15"
        }
    """
    # Verifica se usuário já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Cria hash seguro da senha
    hashed_password = get_password_hash(user_data.password)
    
    # Cria novo usuário na tabela users
    db_user = User(
        email=user_data.email,
        password=hashed_password,  # Armazena apenas o hash, nunca a senha pura
        name=user_data.name,
        type=user_data.type,
        specialty=user_data.specialty,  # Apenas para psicólogos
        crp=user_data.crp,             # Apenas para psicólogos
        phone=user_data.phone
    )
    
    # Salva usuário no banco
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Atualiza objeto com ID gerado
    
    # ========================================================================
    # CRIAÇÃO AUTOMÁTICA DE PACIENTE
    # ========================================================================
    
    # Se for paciente, cria registro adicional na tabela patients
    # Isso permite armazenar informações clínicas específicas
    if user_data.type == UserType.PACIENTE:
        # Se birth_date não foi fornecida, usa uma data padrão
        if user_data.birth_date:
            age = calculate_age(user_data.birth_date)
            birth_date = user_data.birth_date
        else:
            # Data padrão para pacientes sem data de nascimento
            from datetime import date
            birth_date = date(1990, 1, 1)
            age = calculate_age(birth_date)
        
        db_patient = Patient(
            id=db_user.id,  # Mesmo ID do usuário (relacionamento 1:1)
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone or "",
            birth_date=birth_date,
            age=age,
            status="Ativo"  # Status inicial do tratamento
        )
        
        db.add(db_patient)
        db.commit()
    
    # ========================================================================
    # LOGIN AUTOMÁTICO APÓS REGISTRO
    # ========================================================================
    
    # Gera token JWT para login automático
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=30)
    )
    
    # Retorna token para que usuário seja logado automaticamente
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserSchema.from_orm(db_user)
    )