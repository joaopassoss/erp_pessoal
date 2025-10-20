#!/usr/bin/env python3
"""
Script para criar avatar padrão simples
"""
import os

def create_simple_avatar():
    """Cria um avatar padrão simples em SVG"""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="150" height="150" viewBox="0 0 150 150" xmlns="http://www.w3.org/2000/svg">
  <rect width="150" height="150" fill="#6c757d"/>
  <circle cx="75" cy="75" r="50" fill="white" stroke="#dee2e6" stroke-width="2"/>
  <circle cx="75" cy="65" r="15" fill="#6c757d"/>
  <ellipse cx="75" cy="100" rx="25" ry="20" fill="#6c757d"/>
</svg>'''
    
    os.makedirs('static', exist_ok=True)
    with open('static/default-avatar.svg', 'w') as f:
        f.write(svg_content)
    print("✅ Avatar padrão SVG criado com sucesso!")

if __name__ == "__main__":
    create_simple_avatar()

