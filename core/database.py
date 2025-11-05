from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

# =======================
# Configuração do Banco
# =======================

# SQLite local (padrão)
DEFAULT_DB_URL = "sqlite:///./lunysse.db"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Detecta SQLite para aplicar configurações específicas
is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =======================
# Base do SQLAlchemy
# =======================
class Base(DeclarativeBase):
    pass

# =======================
# Dependency — DB session
# =======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
