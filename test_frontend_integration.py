import requests
import json

BASE_URL = "http://localhost:8000"

def test_cors():
    """1. Testar CORS"""
    print("\n=== 1. TESTANDO CORS ===")
    try:
        response = requests.options(f"{BASE_URL}/auth/login", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        })
        print(f"Status: {response.status_code}")
        print(f"CORS Headers: {response.headers.get('Access-Control-Allow-Origin')}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_login():
    """2. Testar Login"""
    print("\n=== 2. TESTANDO LOGIN ===")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "ana@test.com",
            "password": "123456"
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Token recebido: {data['access_token'][:20]}...")
            print(f"Usuario: {data['user']['name']}")
            return data['access_token']
        else:
            print(f"Erro: {response.text}")
            return None
    except Exception as e:
        print(f"ERRO: {e}")
        return None

def test_protected_route(token):
    """3. Testar Rota Protegida"""
    print("\n=== 3. TESTANDO ROTA PROTEGIDA ===")
    try:
        response = requests.get(f"{BASE_URL}/patients/", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Pacientes retornados: {len(data)}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_patient_profile(token):
    """4. Testar Perfil do Paciente"""
    print("\n=== 4. TESTANDO PERFIL DO PACIENTE ===")
    try:
        response = requests.get(f"{BASE_URL}/patients/1/profile", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Paciente: {data['patient']['name']}")
            print(f"Sessoes: {data['stats']['total_sessions']}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_messages(token):
    """5. Testar Mensagens"""
    print("\n=== 5. TESTANDO MENSAGENS ===")
    try:
        # Listar conversas
        response = requests.get(f"{BASE_URL}/messages/conversations", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Status conversas: {response.status_code}")
        
        # Enviar mensagem
        response = requests.post(f"{BASE_URL}/messages/", 
            headers={"Authorization": f"Bearer {token}"},
            json={"receiver_id": 1, "content": "Teste de mensagem"}
        )
        print(f"Status envio: {response.status_code}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_appointments(token):
    """6. Testar Agendamentos"""
    print("\n=== 6. TESTANDO AGENDAMENTOS ===")
    try:
        response = requests.get(f"{BASE_URL}/appointments/", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Agendamentos: {len(data)}")
            return True
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_reports(token):
    """7. Testar Relatorios"""
    print("\n=== 7. TESTANDO RELATORIOS ===")
    try:
        response = requests.get(f"{BASE_URL}/reports/1", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Pacientes ativos: {data['stats']['active_patients']}")
            return True
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_ml_analysis(token):
    """8. Testar Analise ML"""
    print("\n=== 8. TESTANDO ANALISE ML ===")
    try:
        response = requests.get(f"{BASE_URL}/ml/risk-analysis", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total analisados: {data['summary']['total_patients']}")
            return True
        else:
            print(f"Erro: {response.text}")
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_health():
    """9. Testar Health Check"""
    print("\n=== 9. TESTANDO HEALTH CHECK ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_docs():
    """10. Testar Documentacao"""
    print("\n=== 10. TESTANDO DOCUMENTACAO ===")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status: {response.status_code}")
        print(f"Swagger disponivel: {response.status_code == 200}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE INTEGRACAO FRONTEND <-> BACKEND")
    print("=" * 60)
    
    results = []
    
    # Testes basicos
    results.append(("Health Check", test_health()))
    results.append(("Documentacao", test_docs()))
    results.append(("CORS", test_cors()))
    
    # Login e autenticacao
    token = test_login()
    results.append(("Login", token is not None))
    
    if token:
        # Testes com autenticacao
        results.append(("Rota Protegida", test_protected_route(token)))
        results.append(("Perfil Paciente", test_patient_profile(token)))
        results.append(("Mensagens", test_messages(token)))
        results.append(("Agendamentos", test_appointments(token)))
        results.append(("Relatorios", test_reports(token)))
        results.append(("Analise ML", test_ml_analysis(token)))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    for name, result in results:
        status = "OK" if result else "FALHOU"
        print(f"{name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{total} testes passaram")
    print("=" * 60)
