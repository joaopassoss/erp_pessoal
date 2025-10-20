from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base, User
from routers import auth, users, web, financeiro
from config import ROLES
from auth import get_password_hash
import os

# Criar tabelas do banco de dados
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title="ERP Pessoal",
    description="Sistema ERP com autenticação JWT e gerenciamento de usuários",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(web.router)
app.include_router(financeiro.router, prefix="/api")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
async def startup_event():
    """Criar usuário admin padrão se não existir"""
    db = next(get_db())
    
    # Verificar se já existe um admin
    admin_user = db.query(User).filter(User.role == ROLES["admin"]).first()
    
    if not admin_user:
        # Criar usuário admin padrão
        admin_user = User(
            email="admin@erp.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrador",
            role=ROLES["admin"],
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("Usuário admin criado: admin@erp.com / admin123")

@app.get("/")
def read_root():
    return {
        "message": "ERP Pessoal API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
