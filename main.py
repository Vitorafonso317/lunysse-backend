# ============================================================================
# MAIN.PY - PONTO DE ENTRADA DA API LUNYSSE
# ============================================================================
# Este arquivo é o núcleo da aplicação FastAPI, responsável por:
# - Configurar a aplicação principal
# - Gerenciar middlewares (CORS)
# - Registrar todas as rotas dos módulos
# - Criar tabelas do banco de dados automaticamente
# ============================================================================

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import models  # Importa os modelos do banco de dados
from core.database import engine, Base  # Importa configuração do banco
from routers import auth, patients, psychologists, appointments, requests, ml_analysis, reports

# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================

# Carrega variáveis de ambiente do arquivo .env
# Inclui: SECRET_KEY, DATABASE_URL, CORS_ORIGINS, etc.
load_dotenv()

# Cria automaticamente todas as tabelas no banco de dados
# Se as tabelas já existirem, não faz nada (idempotente)
Base.metadata.create_all(bind=engine)

# ============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO FASTAPI
# ============================================================================

# Instancia a aplicação FastAPI com metadados para documentação
app = FastAPI(
    title="Lunysse API",
    description="API para sistema de agendamento psicológico",
    version="1.0.0"
)

# ============================================================================
# CONFIGURAÇÃO DE CORS (Cross-Origin Resource Sharing)
# ============================================================================

# Obtém origens permitidas do arquivo .env (frontend React)
# Padrão: http://localhost:3000 (React) e http://localhost:5173 (Vite)
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Adiciona middleware CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Origens permitidas
    allow_credentials=True,      # Permite cookies/autenticação
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Métodos HTTP permitidos
    allow_headers=["*"],         # Todos os headers permitidos
)

# ============================================================================
# REGISTRO DE ROTAS (ROUTERS)
# ============================================================================

# Registra todos os módulos de rotas da aplicação
# Cada router contém endpoints específicos de sua funcionalidade
app.include_router(auth.router)          # /auth/* - Login, registro, tokens
app.include_router(patients.router)      # /patients/* - CRUD de pacientes
app.include_router(psychologists.router) # /psychologists/* - CRUD de psicólogos
app.include_router(appointments.router)  # /appointments/* - CRUD de agendamentos
app.include_router(requests.router)      # /requests/* - Solicitações de agendamento
app.include_router(ml_analysis.router)   # /ml/* - Análise de risco com ML
app.include_router(reports.router)       # /reports/* - Relatórios e estatísticas

# ============================================================================
# ROTAS BÁSICAS DE SISTEMA
# ============================================================================

@app.get("/")
async def root():
    """Rota raiz - Retorna informações básicas da API"""
    return {"message": "Lunysse API - Sistema de Agendamento Psicológico"}

@app.get("/health")
async def health_check():
    """Endpoint de health check - Verifica se a API está funcionando"""
    return {"status": "healthy"}
