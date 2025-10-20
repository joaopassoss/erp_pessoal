#!/usr/bin/env python3
"""
Script para criar avatar padrão
"""
from PIL import Image, ImageDraw
import os

def create_default_avatar():
    """Cria um avatar padrão simples"""
    # Criar imagem 150x150 com fundo cinza
    img = Image.new('RGB', (150, 150), color='#6c757d')
    draw = ImageDraw.Draw(img)
    
    # Desenhar um círculo branco
    draw.ellipse([25, 25, 125, 125], fill='white', outline='#dee2e6', width=2)
    
    # Desenhar um ícone de usuário simples
    # Cabeça
    draw.ellipse([60, 50, 90, 80], fill='#6c757d')
    # Corpo
    draw.ellipse([50, 85, 100, 120], fill='#6c757d')
    
    # Salvar imagem
    os.makedirs('static', exist_ok=True)
    img.save('static/default-avatar.png')
    print("✅ Avatar padrão criado com sucesso!")

if __name__ == "__main__":
    create_default_avatar()

