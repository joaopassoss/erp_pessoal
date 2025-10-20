import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./erp.db")

# Configurações JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Configurações de upload
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}

# Configurações de permissões
ROLES = {
    "admin": "admin",
    "membro": "membro"
}
