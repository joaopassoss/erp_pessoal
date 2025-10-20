@echo off
echo 🚀 Iniciando ERP Pessoal...
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale o Python primeiro.
    pause
    exit /b 1
)

REM Verificar se as dependências estão instaladas
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependências...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Erro ao instalar dependências.
        pause
        exit /b 1
    )
)

REM Criar diretórios necessários
if not exist "uploads" mkdir uploads
if not exist "static" mkdir static

REM Iniciar servidor
echo 🌐 Iniciando servidor em http://localhost:8000
echo 👤 Usuário admin: admin@erp.com / admin123
echo.
python run.py

pause
