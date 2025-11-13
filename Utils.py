# ============================================================================
# UTILS.PY - UTILITÁRIOS GERAIS DO SISTEMA LUNYSSE
# ============================================================================
# Este arquivo contém funções auxiliares utilizadas em toda a aplicação:
# - Criptografia e verificação de senhas (bcrypt)
# - Criação e validação de tokens JWT
# - Cálculo de idade
# - Configuração de variáveis de ambiente
# ============================================================================

import os  # Para acessar variáveis de ambiente do sistema
from datetime import datetime, date, timezone, timedelta  # Para manipular datas e tempos
from passlib.context import CryptContext  # Biblioteca para hash e verificação de senhas
from jose import JWTError, jwt  # Biblioteca para criação e validação de tokens JWT
from dotenv import load_dotenv  # Para carregar variáveis de ambiente do arquivo .env

# ============================================================================
# CARREGAMENTO E CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE
# ============================================================================

# Carrega as variáveis definidas no arquivo .env para o ambiente
load_dotenv()

# Recupera a chave secreta usada para assinar tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Garante que a aplicação não inicie sem uma chave segura
    raise ValueError("SECRET_KEY deve ser definida nas variáveis de ambiente")

# Define o algoritmo de criptografia a ser usado no JWT (padrão: HS256)
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Recupera o tempo de expiração do token em minutos, com tratamento de erros
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
except (ValueError, TypeError):
    # Caso o valor no .env esteja incorreto, define o padrão como 30 minutos
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================================
# CONFIGURAÇÃO DO HASH DE SENHA (Bcrypt)
# ============================================================================

# Define o contexto de criptografia usando o algoritmo bcrypt
# bcrypt é considerado um dos algoritmos mais seguros para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================================
# FUNÇÕES DE CRIPTOGRAFIA DE SENHAS
# ============================================================================

def verify_password(plain_password, hashed_password):
    """
    Verifica se a senha em texto puro corresponde ao hash armazenado.
    
    Args:
        plain_password (str): Senha digitada pelo usuário
        hashed_password (str): Hash da senha armazenado no banco
    
    Returns:
        bool: True se as senhas coincidem, False caso contrário
    
    Exemplo:
        stored_hash = "$2b$12$..."
        user_input = "123456"
        is_valid = verify_password(user_input, stored_hash)
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Gera um hash seguro da senha usando bcrypt.
    
    Args:
        password (str): Senha em texto puro
    
    Returns:
        str: Hash criptografado da senha
    
    Exemplo:
        password = "123456"
        hash_result = get_password_hash(password)
        # Retorna algo como: "$2b$12$abcd1234..."
    """
    return pwd_context.hash(password)

# ============================================================================
# FUNÇÕES DE TOKEN JWT (JSON Web Token)
# ============================================================================

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Cria um token JWT com base nos dados do usuário.
    
    Args:
        data (dict): Dados do usuário a serem codificados no token
                    Exemplo: {"sub": "user@email.com", "user_id": 123}
        expires_delta (timedelta, optional): Tempo de vida do token
    
    Returns:
        str: Token JWT codificado
    
    Exemplo:
        user_data = {"sub": "ana@test.com", "user_id": 2}
        token = create_access_token(user_data)
        # Retorna: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    """
    to_encode = data.copy()  # Copia os dados do usuário
    
    # Define o tempo de expiração do token
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Caso nenhum tempo seja definido, usa o padrão de 15 minutos
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Adiciona a data de expiração ao payload do token
    to_encode.update({"exp": expire})
    
    # Codifica os dados em um token JWT usando a SECRET_KEY e algoritmo
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# ============================================================================
# FUNÇÕES AUXILIARES DE DATA E IDADE
# ============================================================================

def calculate_age(birth_date: date) -> int:
    """
    Calcula a idade atual com base na data de nascimento.
    
    Args:
        birth_date (date): Data de nascimento do usuário
    
    Returns:
        int: Idade em anos
    
    Exemplo:
        from datetime import date
        birth = date(1990, 5, 15)
        age = calculate_age(birth)  # Retorna a idade atual
    
    Nota:
        Considera corretamente se o aniversário já passou no ano atual
    """
    today = date.today()
    age = today.year - birth_date.year
    
    # Se o aniversário ainda não chegou este ano, subtrai 1 da idade
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age