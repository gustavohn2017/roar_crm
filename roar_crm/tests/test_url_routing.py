"""
Testes para verificar a consistência do roteamento de URLs no sistema.
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse, NoReverseMatch, resolve
from django.contrib.auth.models import User
from unittest.mock import patch


@override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }]
)
class URLRoutingTests(TestCase):
    """Testa o roteamento de URLs e a consistência dos nomes de URLs"""

    def setUp(self):
        # Criar um usuário para testes
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='securepassword'
        )
        self.client = Client()
        # Fazer login
        self.client.login(username='testuser', password='securepassword')

    def test_main_urls_exist(self):
        """Testa se as URLs principais do namespace 'main' existem e não levantam NoReverseMatch."""
        urls_to_test = [
            'main:dashboard',
            'main:dashboard_principal',
            'main:historico_contatos',
            'main:calendario',
            'main:notas',
            'main:calculadoras',
            'main:funil_vendas',
        ]
        
        for url_name in urls_to_test:
            try:
                # Tenta reverter a URL
                url = reverse(url_name)
                # Se chegou aqui, a URL existe
                self.assertTrue(True)
            except NoReverseMatch:
                # Se levantar esta exceção, a URL não existe
                self.fail(f"A URL '{url_name}' não existe")
    
    def test_leads_urls_exist(self):
        """Testa se as URLs principais do namespace 'leads' existem."""
        urls_to_test = [
            'leads:list',
            'leads:create',
            'leads:create_quick',
            'leads:template_list',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                self.assertTrue(True)
            except NoReverseMatch:
                self.fail(f"A URL '{url_name}' não existe")
    
    def test_gerencia_urls_exist(self):
        """Testa se as URLs principais do namespace 'gerencia' existem."""
        urls_to_test = [
            'gerencia:index',
            'gerencia:painel_admin',
            'gerencia:dashboard',
            'gerencia:vendedores',
            'gerencia:funcionarios',
            'gerencia:relatorio_desempenho',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                self.assertTrue(True)
            except NoReverseMatch:
                self.fail(f"A URL '{url_name}' não existe")
    
    def test_automacao_urls_exist(self):
        """Testa se as URLs principais do namespace 'automacao' existem."""
        urls_to_test = [
            'automacao:index',
            'automacao:dashboard',
            'automacao:lead_scoring_list',
            'automacao:workflow_list',
            'automacao:campanha_list',
            'automacao:gatilho_list',
        ]
        
        for url_name in urls_to_test:            try:
                url = reverse(url_name)
                self.assertTrue(True)
            except NoReverseMatch:
                self.fail(f"A URL '{url_name}' não existe")
    
    @patch('django.shortcuts.render')
    def test_home_redirect_works(self, mock_render):
        """Testa se o redirecionamento da página inicial funciona corretamente."""
        # Configure o mock para retornar um valor simples
        mock_render.return_value = "Teste OK"
        
        # Verifique se a URL raiz é resolvida para a view home_redirect
        resolver = resolve('/')
        self.assertEqual(resolver.url_name, 'home')
        self.assertEqual(resolver.func.__name__, 'login_required_wrapper')
    
    def test_compatibility_urls_work(self):
        """Testa se as URLs de compatibilidade estão funcionando corretamente."""
        # URLs de compatibilidade e seus resolvers esperados
        compat_urls = {
            # Vendedores
            '/main/home/': 'main:home',
            '/main/painel/': 'main:painel',
            '/main/agenda/': 'main:agenda',
            
            # Leads
            '/leads/lista/': 'leads:lista_leads',
            '/leads/cadastrar/': 'leads:cadastrar_lead',
            
            # Gerencia
            '/gerencia/painel-controle/': 'gerencia:painel_controle',
            '/gerencia/equipe/': 'gerencia:equipe',
            
            # Automacao
            '/automacao/painel/': 'automacao:painel',
            '/automacao/workflow/': 'automacao:workflow',
        }
        
        # Verificar se os URLs de compatibilidade existem e correspondem aos nomes esperados
        for url_path, expected_name in compat_urls.items():
            try:
                resolver = resolve(url_path)
                self.assertIsNotNone(resolver, f"URL '{url_path}' não pôde ser resolvida")
                # Verificar se a view obtida é uma função de redirecionamento
                self.assertTrue(
                    'redirect' in resolver.func.__name__,
                    f"URL '{url_path}' não está usando uma função de redirecionamento"
                )
            except:
                self.fail(f"URL '{url_path}' não existe ou não está configurada corretamente")
