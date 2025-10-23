#!/usr/bin/env python3
"""
Script de inicialização do ERP Pessoal
"""
import uvicorn
import os
import sys

def main():
    """Inicializa o servidor do ERP"""
    print("🚀 Iniciando ERP Pessoal...")
    print("📋 Funcionalidades disponíveis:")
    print("   ✅ Autenticação JWT")
    print("   ✅ Sistema de permissões (Admin/Membro)")
    print("   ✅ Upload de foto de perfil")
    print("   ✅ Painel administrativo")
    print("   ✅ Interface web responsiva")
    print()
    print("🌐 Servidor será iniciado em: http://localhost:8000")
    print("📚 Documentação da API: http://localhost:8000/docs")
    print("👤 Usuário admin padrão: admin@erp.com / admin123")
    print()
    
    # Criar diretórios necessários
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    # Iniciar servidor
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
