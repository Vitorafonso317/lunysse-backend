# ============================================================================
# DATABASE.PY - CONFIGURAÇÃO DO BANCO DE DADOS
# ============================================================================
# Este arquivo gerencia toda a configuração do banco de dados:
# - Conexão com SQLite (ou outros bancos via variável de ambiente)
# - Criação do engine SQLAlchemy
# - Configuração de sessões do banco
# - Dependency injection para FastAPI
# ============================================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

# ============================================================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ============================================================================

# URL padrão do banco SQLite local
# Cria o arquivo lunysse.db na raiz do projeto
DEFAULT_DB_URL = "sqlite:///./lunysse.db"

# Obtém URL do banco das variáveis de ambiente
# Permite trocar para PostgreSQL/MySQL em produção
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Detecta se está usando SQLite para aplicar configurações específicas
# SQLite precisa de "check_same_thread: False" para funcionar com FastAPI
is_sqlite = DATABASE_URL.startswith("sqlite")

# ============================================================================
# ENGINE DO SQLALCHEMY
# ============================================================================

# Cria o engine de conexão com o banco
# Para SQLite: adiciona check_same_thread=False (necessário para async)
# Para outros bancos: usa configuração padrão
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {}
)

# ============================================================================
# CONFIGURAÇÃO DE SESSÕES
# ============================================================================

# Factory para criar sessões do banco de dados
# autocommit=False: transações manuais (mais controle)
# autoflush=False: não faz flush automático (melhor performance)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================================
# CLASSE BASE PARA MODELOS ORM
# ============================================================================

# Classe base para todos os modelos SQLAlchemy
# Todos os modelos (User, Patient, etc.) herdam desta classe
class Base(DeclarativeBase):
    """Classe base para todos os modelos do banco de dados"""
    pass

# ============================================================================
# DEPENDENCY INJECTION PARA FASTAPI
# ============================================================================

def get_db():
    """
    Dependency para injeção de sessão do banco nas rotas FastAPI.
    
    Uso:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    Garante que:
    - Uma nova sessão é criada para cada requisição
    - A sessão é fechada automaticamente após a requisição
    - Em caso de erro, a sessão ainda é fechada (finally)
    """
    db = SessionLocal()  # Cria nova sessão
    try:
        yield db  # Fornece a sessão para a rota
    finally:
        db.close()  # Sempre fecha a sessão