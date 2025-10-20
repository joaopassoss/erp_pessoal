#!/usr/bin/env python3
"""
Script para verificar o usuário admin
"""
from database import SessionLocal
from models import User
from auth import verify_password, get_password_hash

def check_admin():
    """Verifica se o usuário admin existe e testa a senha"""
    db = SessionLocal()
    
    try:
        # Buscar usuário admin
        user = db.query(User).filter(User.username == 'admin').first()
        
        if not user:
            print("❌ Usuário admin não encontrado!")
            return False
        
        print(f"✅ Usuário admin encontrado:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Role: {user.role}")
        print(f"   Ativo: {user.is_active}")
        
        # Testar senha
        test_password = "admin123"
        is_valid = verify_password(test_password, user.hashed_password)
        
        if is_valid:
            print(f"✅ Senha '{test_password}' está correta!")
        else:
            print(f"❌ Senha '{test_password}' está incorreta!")
            print("🔄 Recriando usuário admin com senha correta...")
            
            # Recriar usuário admin
            user.hashed_password = get_password_hash(test_password)
            db.commit()
            print("✅ Usuário admin atualizado com nova senha!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    check_admin()


