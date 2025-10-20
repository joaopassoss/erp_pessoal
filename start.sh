#!/bin/bash

echo "🚀 Iniciando ERP Pessoal..."
echo

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python primeiro."
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale o pip primeiro."
    exit 1
fi

# Verificar se as dependências estão instaladas
if ! pip3 show fastapi &> /dev/null; then
    echo "📦 Instalando dependências..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao instalar dependências."
        exit 1
    fi
fi

# Criar diretórios necessários
mkdir -p uploads static

# Iniciar servidor
echo "🌐 Iniciando servidor em http://localhost:8000"
echo "👤 Usuário admin: admin@erp.com / admin123"
echo
python3 run.py
