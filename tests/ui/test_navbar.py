"""
Script de teste para validar o navbar redesenhado
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roar_crm.settings')
django.setup()

from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.test import RequestFactory

def test_navbar_rendering():
    """Testa se o navbar renderiza corretamente"""
    
    factory = RequestFactory()
    request = factory.get('/')
    
    # Criar um usuário de teste
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_user',
            email='test@roar.com',
            password='testpass123'
        )
    
    request.user = user
    
    # Tentar renderizar o template base
    try:
        context = {
            'request': request,
            'user': user
        }
        
        rendered = render_to_string('base.html', context, request=request)
        
        # Verificar elementos essenciais do navbar
        checks = [
            'id="mainNavbar"' in rendered,
            'navbar-brand' in rendered,
            'Roar CRM' in rendered,
            'navbar-collapse' in rendered,
            'main-nav' in rendered,
            'user-nav' in rendered,
        ]
        
        print("✅ Teste de renderização do navbar:")
        for i, check in enumerate(checks):
            status = "✅" if check else "❌"
            print(f"  {status} Check {i+1}: {'PASSOU' if check else 'FALHOU'}")
        
        all_passed = all(checks)
        print(f"\n{'✅ TODOS OS TESTES PASSARAM!' if all_passed else '❌ ALGUNS TESTES FALHARAM!'}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Erro ao renderizar template: {e}")
        return False

def check_static_files():
    """Verifica se os arquivos estáticos existem"""
    
    static_files = [
        'static/css/navbar-redesign.css',
        'static/js/navbar-redesign.js'
    ]
    
    print("\n📁 Verificação de arquivos estáticos:")
    all_exist = True
    
    for file_path in static_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}: {'EXISTE' if exists else 'NÃO ENCONTRADO'}")
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Função principal de teste"""
    print("🔍 TESTE DO NAVBAR REDESENHADO - ROAR CRM")
    print("=" * 50)
    
    # Teste 1: Arquivos estáticos
    static_ok = check_static_files()
    
    # Teste 2: Renderização do template
    render_ok = test_navbar_rendering()
    
    # Resultado final
    print("\n" + "=" * 50)
    if static_ok and render_ok:
        print("🎉 NAVBAR REDESENHADO IMPLEMENTADO COM SUCESSO!")
        print("\n📋 Próximos passos:")
        print("   1. Iniciar servidor: python manage.py runserver")
        print("   2. Acessar: http://localhost:8000")
        print("   3. Testar responsividade em diferentes dispositivos")
        print("   4. Verificar todas as funcionalidades de navegação")
    else:
        print("⚠️  PROBLEMAS DETECTADOS NA IMPLEMENTAÇÃO")
        print("   Verifique os arquivos e tente novamente")

if __name__ == "__main__":
    main()
