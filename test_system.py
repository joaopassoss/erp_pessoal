#!/usr/bin/env python3
"""
Script de teste do sistema ERP
"""
import sys
import os

def test_imports():
    """Testa se todas as importações funcionam"""
    print("🔄 Testando importações...")
    
    try:
        from fastapi import FastAPI
        from sqlalchemy import create_engine
        from jose import jwt
        from passlib.context import CryptContext
        from database import get_db
        from models import User
        from auth import get_password_hash
        print("✅ Todas as importações funcionaram!")
        return True
    except Exception as e:
        print(f"❌ Erro nas importações: {e}")
        return False

def test_database_creation():
    """Testa se o banco de dados pode ser criado"""
    print("🔄 Testando criação do banco de dados...")
    
    try:
        from database import engine, Base
        from models import User
        
        # Criar tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Banco de dados criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar banco de dados: {e}")
        return False

def test_auth_system():
    """Testa o sistema de autenticação"""
    print("🔄 Testando sistema de autenticação...")
    
    try:
        from auth import get_password_hash, verify_password
        
        # Testar hash de senha
        password = "test123"
        hashed = get_password_hash(password)
        
        # Testar verificação
        is_valid = verify_password(password, hashed)
        
        if is_valid:
            print("✅ Sistema de autenticação funcionando!")
            return True
        else:
            print("❌ Erro na verificação de senha")
            return False
    except Exception as e:
        print(f"❌ Erro no sistema de autenticação: {e}")
        return False

def test_app_creation():
    """Testa se a aplicação pode ser criada"""
    print("🔄 Testando criação da aplicação...")
    
    try:
        from main import app
        print("✅ Aplicação criada com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar aplicação: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 Testando Sistema ERP Pessoal")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database_creation,
        test_auth_system,
        test_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O sistema está pronto para uso.")
        print("\n📋 Para iniciar o servidor:")
        print("   python run.py")
        print("\n🌐 Acesse: http://localhost:8000")
        print("👤 Login admin: admin@erp.com / admin123")
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()

