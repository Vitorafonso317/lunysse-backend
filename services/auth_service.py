# ============================================================================
# AUTH_SERVICE.PY - SERVIÇOS DE AUTENTICAÇÃO E AUTORIZAÇÃO
# ============================================================================
# Este arquivo contém a lógica de negócio para autenticação:
# - Verificação de credenciais (email/senha)
# - Validação de tokens JWT
# - Extração do usuário atual das requisições
# - Middleware de segurança para rotas protegidas
# ============================================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from models.models import User
from Utils import verify_password, create_access_token, SECRET_KEY, ALGORITHM
from core.database import get_db

# ============================================================================
# CONFIGURAÇÃO DE SEGURANÇA
# ============================================================================

# Configura o esquema de autenticação Bearer Token
# Automaticamente extrai o token do header "Authorization: Bearer <token>"
security = HTTPBearer()

# ============================================================================
# FUNÇÕES DE AUTENTICAÇÃO
# ============================================================================

def authenticate_user(db: Session, email: str, password: str):
    """
    Autentica um usuário verificando email e senha.
    
    Args:
        db (Session): Sessão do banco de dados
        email (str): Email do usuário
        password (str): Senha em texto puro
    
    Returns:
        User | None: Objeto User se credenciais válidas, None caso contrário
    
    Processo:
        1. Busca usuário pelo email no banco
        2. Verifica se a senha confere com o hash armazenado
        3. Retorna o usuário ou None
    
    Exemplo:
        user = authenticate_user(db, "ana@test.com", "123456")
        if user:
            print(f"Login válido: {user.name}")
        else:
            print("Credenciais inválidas")
    """
    # Busca usuário pelo email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None  # Email não encontrado
    
    # Verifica se a senha está correta
    if not verify_password(password, user.password):
        return None  # Senha incorreta
    
    return user  # Credenciais válidas

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Extrai e valida o usuário atual a partir do token JWT.
    
    Esta função é usada como dependency em rotas protegidas:
    
    @app.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        return {"user": current_user.name}
    
    Args:
        credentials: Token JWT extraído automaticamente do header
        db: Sessão do banco de dados
    
    Returns:
        User: Usuário autenticado
    
    Raises:
        HTTPException: 401 se token inválido ou usuário não encontrado
    
    Processo:
        1. Decodifica o token JWT
        2. Extrai o email do payload
        3. Busca o usuário no banco
        4. Retorna o usuário ou erro 401
    """
    # Exceção padrão para credenciais inválidas
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica o token JWT usando a chave secreta
        payload = jwt.decode(
            credentials.credentials,  # Token extraído do header
            SECRET_KEY,              # Chave para validar assinatura
            algorithms=[ALGORITHM]   # Algoritmo usado (HS256)
        )
        
        # Extrai o email do campo "sub" (subject) do token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        # Token malformado, expirado ou assinatura inválida
        raise credentials_exception
    
    # Busca o usuário no banco pelo email
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        # Usuário não existe (pode ter sido deletado após criação do token)
        raise credentials_exception
    
    return user