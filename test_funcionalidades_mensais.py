#!/usr/bin/env python3
"""
Script para testar todas as funcionalidades mensais implementadas
"""

import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Testar todos os endpoints implementados"""
    print("🧪 Testando Funcionalidades Mensais...")
    print("=" * 50)
    
    # Lista de endpoints para testar
    endpoints = [
        {
            "name": "Dashboard Mensal Web",
            "url": f"{BASE_URL}/dashboard-mensal",
            "method": "GET",
            "auth_required": False
        },
        {
            "name": "API Documentation",
            "url": f"{BASE_URL}/docs",
            "method": "GET",
            "auth_required": False
        },
        {
            "name": "Relatório Mensal (sem auth)",
            "url": f"{BASE_URL}/api/financeiro/relatorios/mensal",
            "method": "GET",
            "auth_required": True
        },
        {
            "name": "Fluxo de Caixa Mensal (sem auth)",
            "url": f"{BASE_URL}/api/financeiro/relatorios/fluxo-caixa-mensal",
            "method": "GET",
            "auth_required": True
        },
        {
            "name": "Comparativo Mensal (sem auth)",
            "url": f"{BASE_URL}/api/financeiro/relatorios/comparativo-mensal",
            "method": "GET",
            "auth_required": True
        },
        {
            "name": "Alertas Mensais (sem auth)",
            "url": f"{BASE_URL}/api/financeiro/relatorios/alertas-mensais",
            "method": "GET",
            "auth_required": True
        },
        {
            "name": "Metas Mensais (sem auth)",
            "url": f"{BASE_URL}/api/financeiro/metas-mensais",
            "method": "GET",
            "auth_required": True
        },
        {
            "name": "Dashboard Mensal API (sem auth)",
            "url": f"{BASE_URL}/api/financeiro/dashboard-mensal",
            "method": "GET",
            "auth_required": True
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Testando: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            response = requests.get(endpoint['url'], timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code} - OK")
                if endpoint['auth_required']:
                    print(f"   ⚠️  Requer autenticação (esperado)")
                else:
                    print(f"   🎉 Funcionando perfeitamente!")
            elif response.status_code == 401:
                print(f"   ⚠️  Status: {response.status_code} - Requer autenticação (esperado)")
            else:
                print(f"   ❌ Status: {response.status_code} - Erro inesperado")
                
            results.append({
                "name": endpoint['name'],
                "status": response.status_code,
                "success": response.status_code in [200, 401]
            })
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erro: Servidor não está rodando")
            results.append({
                "name": endpoint['name'],
                "status": "CONNECTION_ERROR",
                "success": False
            })
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            results.append({
                "name": endpoint['name'],
                "status": "ERROR",
                "success": False
            })
    
    return results

def test_database():
    """Testar se o banco de dados foi atualizado corretamente"""
    print("\n🗄️ Testando Banco de Dados...")
    print("=" * 50)
    
    try:
        from database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Verificar se a tabela metas_mensais existe
            result = conn.execute(text('SELECT name FROM sqlite_master WHERE type="table" AND name="metas_mensais"'))
            metas_table_exists = result.fetchone() is not None
            print(f"✅ Tabela 'metas_mensais' existe: {metas_table_exists}")
            
            # Verificar estrutura da tabela
            if metas_table_exists:
                result = conn.execute(text('PRAGMA table_info(metas_mensais)'))
                columns = result.fetchall()
                print(f"✅ Colunas da tabela metas_mensais: {len(columns)}")
                for col in columns:
                    print(f"   - {col[1]} ({col[2]})")
            
            # Verificar outras tabelas importantes
            tables = ['contas_pagar', 'contas_receber', 'metas_financeiras', 'investimentos', 'resumos_financeiros']
            for table in tables:
                result = conn.execute(text(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{table}"'))
                exists = result.fetchone() is not None
                print(f"✅ Tabela '{table}' existe: {exists}")
                
    except Exception as e:
        print(f"❌ Erro ao testar banco de dados: {e}")

def test_imports():
    """Testar se todas as importações estão funcionando"""
    print("\n📦 Testando Importações...")
    print("=" * 50)
    
    imports_to_test = [
        ("schemas", "RelatorioMensalResponse"),
        ("schemas", "FluxoCaixaMensalResponse"),
        ("schemas", "ComparativoMensalResponse"),
        ("schemas", "AlertasMensaisResponse"),
        ("schemas", "MetaMensalResponse"),
        ("schemas", "DashboardMensalResponse"),
        ("models", "MetaMensal"),
        ("routers.financeiro", "router"),
    ]
    
    for module, item in imports_to_test:
        try:
            exec(f"from {module} import {item}")
            print(f"✅ {module}.{item} - OK")
        except Exception as e:
            print(f"❌ {module}.{item} - Erro: {e}")

def main():
    """Função principal de teste"""
    print("🚀 TESTE DAS FUNCIONALIDADES MENSAIS")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Testar importações
    test_imports()
    
    # Testar banco de dados
    test_database()
    
    # Testar endpoints
    results = test_endpoints()
    
    # Resumo dos resultados
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    
    print(f"Total de testes: {total_tests}")
    print(f"Testes bem-sucedidos: {successful_tests}")
    print(f"Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
    
    print("\n📋 DETALHES DOS TESTES:")
    for result in results:
        status_icon = "✅" if result['success'] else "❌"
        print(f"{status_icon} {result['name']}: {result['status']}")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Acesse: http://localhost:8000/dashboard-mensal")
    print("2. Faça login no sistema")
    print("3. Teste as funcionalidades mensais")
    print("4. Verifique a documentação: http://localhost:8000/docs")

if __name__ == "__main__":
    main()

