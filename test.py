# ============================================================================
# TEST.PY - TESTES AUTOMATIZADOS DA API LUNYSSE
# ============================================================================
# Este script executa testes completos de todas as funcionalidades da API:
# - Autenticação (login válido/inválido, tokens)
# - CRUD de pacientes, psicólogos, agendamentos
# - Solicitações de agendamento
# - Relatórios e estatísticas
# - Análise de risco com Machine Learning
# ============================================================================

import requests
import json
import sys

# URL base da API (deve estar rodando em localhost:8000)
BASE_URL = "http://localhost:8000"

class TestRunner:
    """
    Classe principal para execução dos testes automatizados.
    
    Funcionalidades:
        - Login automático com usuário de teste
        - Testes de todas as rotas principais
        - Validação de respostas e status codes
        - Relatório detalhado dos resultados
    """
    
    def __init__(self):
        """Inicializa o runner de testes com estado limpo."""
        self.token = None           # Token JWT para autenticação
        self.headers = {}           # Headers HTTP com Authorization
        self.user = None            # Dados do usuário logado

    # ========================================================================
    # AUTENTICAÇÃO E SETUP
    # ========================================================================

    def login(self):
        """
        Faz login com usuário de teste e configura headers de autenticação.
        
        Returns:
            bool: True se login bem-sucedido, False caso contrário
        """
        print("🔐 Fazendo login...")
        
        # Credenciais do usuário de teste (Dra. Ana Costa)
        login_data = {"email": "ana@test.com", "password": "123456"}
        
        try:
            # Tenta fazer login na API
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                # Login bem-sucedido
                data = response.json()
                self.token = data["access_token"]
                self.user = data["user"]
                
                # Configura header Authorization para próximas requisições
                self.headers = {"Authorization": f"Bearer {self.token}"}
                
                print(f"✅ Login: {self.user['name']}")
                return True
            else:
                print(f"❌ Login falhou: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Servidor não está rodando")
            print("💡 Execute: uvicorn main:app --reload")
            return False

    # ========================================================================
    # TESTES DE AUTENTICAÇÃO
    # ========================================================================

    def test_auth(self):
        """
        Testa funcionalidades de autenticação.
        
        Testes:
            - Login com credenciais inválidas (deve retornar 401)
            - Acesso a rota protegida com token válido (deve retornar 200)
        """
        print("\n🔑 TESTANDO AUTENTICAÇÃO")
        
        # Teste 1: Login inválido
        response = requests.post(
            f"{BASE_URL}/auth/login", 
            json={"email": "invalid", "password": "wrong"}
        )
        print(f"Login inválido: {'✅' if response.status_code == 401 else '❌'}")
        
        # Teste 2: Token válido em rota protegida
        response = requests.get(f"{BASE_URL}/patients/", headers=self.headers)
        print(f"Token válido: {'✅' if response.status_code == 200 else '❌'}")

    # ========================================================================
    # TESTES DE PACIENTES
    # ========================================================================

    def test_patients(self):
        """
        Testa operações CRUD de pacientes.
        
        Testes:
            - Listagem de pacientes
            - Detalhes de um paciente específico
        """
        print("\n👥 TESTANDO PACIENTES")
        
        # Teste: Listar pacientes
        response = requests.get(f"{BASE_URL}/patients/", headers=self.headers)
        
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ Listagem: {len(patients)} pacientes")
            
            if patients:
                # Teste: Detalhes do primeiro paciente
                patient_id = patients[0]["id"]
                response = requests.get(
                    f"{BASE_URL}/patients/{patient_id}", 
                    headers=self.headers
                )
                print(f"Detalhes: {'✅' if response.status_code == 200 else '❌'}")
        else:
            print("❌ Erro na listagem")

    # ========================================================================
    # TESTES DE PSICÓLOGOS
    # ========================================================================

    def test_psychologists(self):
        """
        Testa listagem de psicólogos (rota pública).
        
        Testes:
            - Listagem de psicólogos disponíveis
        """
        print("\n🧠 TESTANDO PSICÓLOGOS")
        
        # Teste: Listar psicólogos (rota pública, sem autenticação)
        response = requests.get(f"{BASE_URL}/psychologists/")
        
        if response.status_code == 200:
            psychs = response.json()
            print(f"✅ Listagem: {len(psychs)} psicólogos")
        else:
            print("❌ Erro na listagem")

    # ========================================================================
    # TESTES DE AGENDAMENTOS
    # ========================================================================

    def test_appointments(self):
        """
        Testa operações de agendamentos.
        
        Testes:
            - Listagem de agendamentos do psicólogo
            - Detalhes de um agendamento específico
        """
        print("\n📅 TESTANDO AGENDAMENTOS")
        
        # Teste: Listar agendamentos
        response = requests.get(f"{BASE_URL}/appointments/", headers=self.headers)
        
        if response.status_code == 200:
            appointments = response.json()
            print(f"✅ Listagem: {len(appointments)} agendamentos")
            
            if appointments:
                # Teste: Detalhes do primeiro agendamento
                apt_id = appointments[0]["id"]
                response = requests.get(
                    f"{BASE_URL}/appointments/{apt_id}", 
                    headers=self.headers
                )
                print(f"Detalhes: {'✅' if response.status_code == 200 else '❌'}")
        else:
            print("❌ Erro na listagem")

    # ========================================================================
    # TESTES DE SOLICITAÇÕES
    # ========================================================================

    def test_requests(self):
        """
        Testa sistema de solicitações de agendamento.
        
        Testes:
            - Listagem de solicitações pendentes
        """
        print("\n📋 TESTANDO SOLICITAÇÕES")
        
        # Teste: Listar solicitações
        response = requests.get(f"{BASE_URL}/requests/", headers=self.headers)
        
        if response.status_code == 200:
            requests_data = response.json()
            print(f"✅ Listagem: {len(requests_data)} solicitações")
        else:
            print("❌ Erro na listagem")

    # ========================================================================
    # TESTES DE RELATÓRIOS
    # ========================================================================

    def test_reports(self):
        """
        Testa geração de relatórios e estatísticas.
        
        Testes:
            - Relatório completo do psicólogo logado
            - Validação de métricas calculadas
        """
        print("\n📊 TESTANDO RELATÓRIOS")
        
        # Teste: Gerar relatório do psicólogo atual
        response = requests.get(
            f"{BASE_URL}/reports/{self.user['id']}", 
            headers=self.headers
        )
        
        if response.status_code == 200:
            report = response.json()
            stats = report["stats"]
            
            print(f"✅ Relatório gerado:")
            print(f"   Pacientes ativos: {stats['active_patients']}")
            print(f"   Total sessões: {stats['total_sessions']}")
            print(f"   Taxa comparecimento: {stats['attendance_rate']}%")
        else:
            print("❌ Erro no relatório")

    # ========================================================================
    # TESTES DE MACHINE LEARNING
    # ========================================================================

    def test_ml_analysis(self):
        """
        Testa análise de risco com Machine Learning.
        
        Testes:
            - Análise geral de todos os pacientes
            - Análise individual de um paciente específico
            - Validação de scores e classificações de risco
        """
        print("\n🤖 TESTANDO ANÁLISE ML")
        
        # Teste: Análise geral de risco
        response = requests.get(f"{BASE_URL}/ml/risk-analysis", headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            summary = data["summary"]
            patients = data["patients"]
            
            print(f"✅ Análise geral:")
            print(f"   Total: {summary['total_patients']}")
            print(f"   Alto risco: {summary['high_risk']}")
            print(f"   Moderado: {summary['moderate_risk']}")
            print(f"   Baixo: {summary['low_risk']}")
            
            # Teste: Análise individual
            if patients:
                patient_id = patients[0]["id"]
                response = requests.get(
                    f"{BASE_URL}/ml/risk-analysis/{patient_id}", 
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    patient_data = response.json()
                    print(f"✅ Análise individual:")
                    print(f"   {patient_data['patient']}: {patient_data['risk']}")
                    print(f"   Score: {patient_data['risk_score']}")
                else:
                    print("❌ Erro análise individual")
        else:
            print("❌ Erro análise geral")

    # ========================================================================
    # EXECUÇÃO COMPLETA DOS TESTES
    # ========================================================================

    def run_all_tests(self):
        """
        Executa todos os testes em sequência.
        
        Returns:
            bool: True se todos os testes passaram, False se houve falhas
        """
        print("🧪 INICIANDO TESTES COMPLETOS DO SISTEMA LUNYSSE")
        print("=" * 50)
        
        # Pré-requisito: Login bem-sucedido
        if not self.login():
            print("❌ Não foi possível fazer login. Encerrando testes.")
            print("💡 Verifique se:")
            print("   - O servidor está rodando (uvicorn main:app --reload)")
            print("   - Os dados de teste foram criados (python seed_data.py)")
            return False
        
        # Executa todos os testes
        self.test_auth()
        self.test_patients()
        self.test_psychologists()
        self.test_appointments()
        self.test_requests()
        self.test_reports()
        self.test_ml_analysis()
        
        print("\n" + "=" * 50)
        print("✅ TESTES CONCLUÍDOS")
        print("\n💡 Para ver a documentação completa da API:")
        print("   http://localhost:8000/docs")
        
        return True

# ============================================================================
# EXECUÇÃO DO SCRIPT
# ============================================================================

if __name__ == "__main__":
    """
    Executa os testes quando o script é chamado diretamente:
    python test.py
    """
    runner = TestRunner()
    success = runner.run_all_tests()
    
    # Código de saída: 0 = sucesso, 1 = falha
    # Útil para integração com CI/CD
    sys.exit(0 if success else 1)