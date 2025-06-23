#!/usr/bin/env python3
"""
Teste funcional do navbar redesenhado
Script para verificar se todos os arquivos estão carregando corretamente
"""

import os
import requests
import sys
from urllib.parse import urljoin

def test_static_files():
    """Testa se os arquivos estáticos estão acessíveis"""
    base_url = "http://127.0.0.1:8000"
    static_files = [
        "/static/css/navbar-redesign.css",
        "/static/js/navbar-redesign.js", 
        "/static/js/navbar-config.js"
    ]
    
    print("🔍 Testando arquivos estáticos do navbar...")
    
    for file_path in static_files:
        try:
            url = urljoin(base_url, file_path)
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {file_path} - OK ({len(response.content)} bytes)")
            else:
                print(f"❌ {file_path} - HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {file_path} - Erro: {e}")

def test_main_page():
    """Testa se a página principal carrega"""
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=10)
        
        if response.status_code == 200:
            print("✅ Página principal carregada com sucesso")
            
            # Verifica se os elementos do navbar estão presentes
            content = response.text
            
            checks = [
                ("id=\"mainNavbar\"", "Navbar principal"),
                ("navbar-redesign.css", "CSS do navbar"),
                ("navbar-redesign.js", "JavaScript do navbar"),
                ("navbar-config.js", "Configuração do navbar"),
                ("mega-dropdown", "Megamenu"),
                ("class=\"brand-container\"", "Logo/Brand")
            ]
            
            print("\n📋 Verificando elementos do navbar...")
            for check, description in checks:
                if check in content:
                    print(f"✅ {description} - Encontrado")
                else:
                    print(f"❌ {description} - Não encontrado")
                    
        else:
            print(f"❌ Página principal - HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar página principal: {e}")

def main():
    print("=" * 60)
    print("🚀 TESTE FUNCIONAL - NAVBAR REDESIGN")
    print("=" * 60)
    
    print("\n1. Verificando se o servidor está rodando...")
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        print("✅ Servidor Django está rodando")
    except requests.exceptions.RequestException:
        print("❌ Servidor Django não está rodando!")
        print("   Execute: python manage.py runserver")
        return False
    
    print("\n2. Testando arquivos estáticos...")
    test_static_files()
    
    print("\n3. Testando página principal...")
    test_main_page()
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO")
    print("=" * 60)
    
    print("\n📝 Próximos passos:")
    print("   1. Acesse: http://127.0.0.1:8000")
    print("   2. Teste a responsividade (F12 > Device Toolbar)")
    print("   3. Teste os dropdowns e megamenus")
    print("   4. Verifique as animações de scroll")
    
    return True

if __name__ == "__main__":
    main()
