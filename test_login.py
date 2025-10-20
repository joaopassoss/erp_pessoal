#!/usr/bin/env python3
"""
Script para testar o login diretamente
"""
import requests
import json

def test_login():
    """Testa o endpoint de login"""
    url = "http://localhost:80/auth/login"
    
    # Dados de login
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print("🔄 Testando login...")
        print(f"URL: {url}")
        print(f"Dados: {data}")
        
        response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login bem-sucedido!")
            print(f"Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"Tipo: {result.get('token_type', 'N/A')}")
        else:
            print("❌ Login falhou!")
            try:
                error = response.json()
                print(f"Erro: {error}")
            except:
                print(f"Resposta: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Verifique se o servidor está rodando na porta 80.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_login()


