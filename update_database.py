#!/usr/bin/env python3
"""
Script para atualizar o banco de dados com as novas tabelas do módulo financeiro
"""

from database import engine, Base
from models import *
import sys

def update_database():
    """Criar todas as tabelas no banco de dados"""
    try:
        print("Criando tabelas do banco de dados...")
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")
        print("\nTabelas criadas:")
        print("- users (ja existia)")
        print("- contas_pagar")
        print("- contas_receber") 
        print("- metas_financeiras")
        print("- transacoes_meta")
        print("- investimentos")
        print("- resumos_financeiros")
        print("\nModulo financeiro esta pronto para uso!")
        
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_database()
