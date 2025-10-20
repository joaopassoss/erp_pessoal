#!/usr/bin/env python3
"""
Script de instalação do ERP Pessoal
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Executa um comando e exibe o resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao {description.lower()}: {e}")
        print(f"   Comando: {command}")
        if e.stdout:
            print(f"   Saída: {e.stdout}")
        if e.stderr:
            print(f"   Erro: {e.stderr}")
        return False

def main():
    """Instala as dependências do ERP"""
    print("🚀 Instalando ERP Pessoal...")
    print("=" * 50)
    
    # Verificar se pip está disponível
    if not run_command("pip --version", "Verificando pip"):
        print("❌ pip não encontrado. Instale o Python com pip primeiro.")
        sys.exit(1)
    
    # Instalar dependências
    if not run_command("pip install -r requirements.txt", "Instalando dependências"):
        print("❌ Falha ao instalar dependências.")
        sys.exit(1)
    
    # Criar diretórios necessários
    print("🔄 Criando diretórios necessários...")
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    print("✅ Diretórios criados!")
    
    print("\n🎉 Instalação concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("   1. Execute: python run.py")
    print("   2. Acesse: http://localhost:8000")
    print("   3. Login: admin@erp.com / admin123")
    print("\n📚 Documentação: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
