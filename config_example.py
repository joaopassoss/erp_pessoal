# Exemplo de configuração para o ERP Pessoal
# Copie este arquivo para config.py e ajuste as configurações conforme necessário

# Configurações do Banco de Dados
DATABASE_URL = "sqlite:///./erp.db"
# Para PostgreSQL: DATABASE_URL = "postgresql://usuario:senha@localhost/erp_db"

# Configurações JWT
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurações de Upload
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}

# Configurações de Permissões
ROLES = {
    "admin": "admin",
    "membro": "membro"
}
