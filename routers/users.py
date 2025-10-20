from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User
from schemas import UserResponse, UserUpdate, UserRoleUpdate, UserStatusUpdate
from auth import get_current_active_user, require_admin
from config import ROLES, UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
import os
import aiofiles
from pathlib import Path

router = APIRouter(prefix="/users", tags=["users"])

# Criar diretório de uploads se não existir
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lista todos os usuários (apenas admin)"""
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém informações de um usuário específico"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Usuários só podem ver seu próprio perfil, exceto admins
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para ver este usuário")
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualiza informações de um usuário"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Usuários só podem atualizar seu próprio perfil, exceto admins
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para atualizar este usuário")
    
    # Verificar se email já existe (se estiver sendo alterado)
    if user_update.email and user_update.email != user.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(status_code=400, detail="Email já está em uso")
    
    # Verificar se username já existe (se estiver sendo alterado)
    if user_update.username and user_update.username != user.username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(status_code=400, detail="Username já está em uso")
    
    # Atualizar campos
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Atualiza role de um usuário (apenas admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if role_update.role not in ROLES.values():
        raise HTTPException(status_code=400, detail="Role inválida")
    
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Atualiza status de um usuário (apenas admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user.is_active = status_update.is_active
    db.commit()
    db.refresh(user)
    return user

@router.post("/{user_id}/profile-picture")
async def upload_profile_picture(
    user_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload de foto de perfil"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Usuários só podem alterar sua própria foto, exceto admins
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para alterar esta foto")
    
    # Verificar tamanho do arquivo
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Arquivo muito grande")
    
    # Verificar extensão
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido")
    
    # Gerar nome único para o arquivo
    import uuid
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Salvar arquivo
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Atualizar banco de dados
    user.profile_picture = filename
    db.commit()
    
    return {"message": "Foto de perfil atualizada com sucesso", "filename": filename}

@router.delete("/{user_id}/profile-picture")
def delete_profile_picture(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove foto de perfil"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Usuários só podem alterar sua própria foto, exceto admins
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para alterar esta foto")
    
    # Remover arquivo se existir
    if user.profile_picture:
        file_path = os.path.join(UPLOAD_DIR, user.profile_picture)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Atualizar banco de dados
    user.profile_picture = None
    db.commit()
    
    return {"message": "Foto de perfil removida com sucesso"}
