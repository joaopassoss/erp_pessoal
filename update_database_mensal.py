#!/usr/bin/env python3
"""
Script para atualizar o banco de dados com as novas funcionalidades mensais
"""

from sqlalchemy import create_engine, text
from database import Base, engine
from models import MetaMensal
import sys

def update_database():
    """Atualizar banco de dados com novas tabelas"""
    try:
        print("🔄 Atualizando banco de dados com funcionalidades mensais...")
        
        # Criar todas as tabelas (incluindo as novas)
        Base.metadata.create_all(bind=engine)
        
        print("✅ Banco de dados atualizado com sucesso!")
        print("📊 Novas funcionalidades adicionadas:")
        print("   - Relatórios financeiros mensais")
        print("   - Metas mensais automáticas")
        print("   - Dashboard mensal consolidado")
        print("   - Alertas e notificações mensais")
        print("   - Análise de fluxo de caixa mensal")
        print("   - Comparativo mensal")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar banco de dados: {e}")
        return False

if __name__ == "__main__":
    success = update_database()
    sys.exit(0 if success else 1)

