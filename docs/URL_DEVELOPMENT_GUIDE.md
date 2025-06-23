# Guia de Desenvolvimento de URLs para o Projeto Roar CRM

Este guia contém boas práticas, padrões e procedimentos para trabalhar com URLs no projeto Roar CRM.

## 📋 Índice
1. [Princípios Gerais](#princípios-gerais)
2. [Estrutura de Namespaces](#estrutura-de-namespaces)
3. [Convenções de Nomenclatura](#convenções-de-nomenclatura)
4. [Sistema de Compatibilidade](#sistema-de-compatibilidade)
5. [Adicionando Novas URLs](#adicionando-novas-urls)
6. [Modificando URLs Existentes](#modificando-urls-existentes)
7. [Testes de URL](#testes-de-url)
8. [Resolução de Problemas](#resolução-de-problemas)

## Princípios Gerais

- **Consistência**: Mantenha a consistência em nomes e estruturas de URLs em todo o projeto
- **Namespaces**: Sempre use namespaces para organizar e evitar conflitos de nomes
- **Legibilidade**: Nomes de URLs devem ser autoexplicativos e descrever a funcionalidade
- **Compatibilidade**: Ao alterar URLs, mantenha a compatibilidade com código existente
- **Testabilidade**: URLs devem ser facilmente testáveis

## Estrutura de Namespaces

O Roar CRM utiliza os seguintes namespaces principais:

- **main**: Funcionalidades para vendedores e dashboard principal
- **leads**: Gestão de leads e comunicação
- **gerencia**: Funcionalidades administrativas
- **automacao**: Automação de marketing e ferramentas de automação

## Convenções de Nomenclatura

### Padrão de Nomes de URLs

```
<ação>_<objeto>[_<modificador>]
```

Exemplos:
- `list` - Lista padrão
- `detail` - Visualização de detalhes
- `create` - Criação de novo objeto
- `edit` - Edição de objeto existente
- `delete` - Exclusão de objeto

### URLs Comuns por Namespace

Cada namespace deve incluir:

1. **index** - Ponto de entrada do namespace
2. **dashboard** - Dashboard específico para aquela área

### Estrutura de Paths

- Use palavras em inglês ou português consistentemente
- Separe palavras com hífens (`-`) na URL
- Separe palavras com underscores (`_`) no nome da view
- Prefira URLs no plural para listas e no singular para detalhes

```python
# Exemplo para app 'leads'
urlpatterns = [
    path('leads/', views.lead_list, name='list'),  # Nome curto e claro
    path('leads/<int:lead_id>/', views.lead_detail, name='detail'),
    path('leads/create/', views.lead_create, name='create'),
]
```

## Sistema de Compatibilidade

### Como Funciona

O sistema de compatibilidade de URLs do Roar CRM inclui:

1. **Mapeamentos Centrais**: Arquivo `roar_crm/url_mappings.py`
2. **Arquivos de Compatibilidade**: Um `urls_compatibility.py` por app
3. **Processador de Contexto**: Para uso em templates
4. **Template Tags**: Para uso avançado em templates
5. **Middleware de Recuperação**: Captura erros de URL em runtime

### Como Usar em Templates

```django
{# Opção 1: Processador de Contexto #}
<a href="{{ get_compatible_url 'vendedores:dashboard' }}">Dashboard</a>

{# Opção 2: Template Tag #}
{% load url_compat %}
<a href="{% compat_url 'leads:detail' lead_id=lead.id %}">Detalhes</a>

{# Opção 3: Verificação de Existência #}
{% if 'vendedores:calendario'|url_exists %}
    <a href="{% compat_url 'vendedores:calendario' %}">Calendário</a>
{% endif %}
```

### Como Usar em Python

```python
from roar_crm.url_mappings import get_url_name

# Obter nome mapeado da URL
new_url_name = get_url_name('vendedores:dashboard')  # Retorna 'main:dashboard'

# Usar em redirecionamento
from django.shortcuts import redirect
return redirect(get_url_name('vendedores:dashboard'))
```

## Adicionando Novas URLs

Quando adicionar novas URLs:

1. **Adicione ao arquivo urls.py da app**:
```python
path('nova-funcionalidade/', views.nova_funcionalidade, name='nova_funcionalidade'),
```

2. **Verifique a consistência de nomes**:
   - O nome deve seguir as convenções existentes
   - Deve ser único dentro do namespace
   - Deve ser descritivo sobre a funcionalidade

3. **Adicione URLs padrão**:
   - Para funcionalidades principais, adicione URLs de `list`, `create`, `detail`, etc.
   - Para dashboards, adicione uma URL chamada `dashboard`

4. **Execute o verificador de URLs**:
```
python verify_urls.py
```

## Modificando URLs Existentes

Ao modificar URLs existentes:

1. **Nunca remova uma URL sem adicionar compatibilidade**
2. **Adicione redirecionamento no arquivo urls_compatibility.py**:
```python
# Em urls_compatibility.py
router.add_redirect('url-antiga/', 'nome_url_nova')
```

3. **Atualize o mapeamento central**:
```python
# Em roar_crm/url_mappings.py
URL_MAPPINGS['namespace:nome_antigo'] = 'namespace:nome_novo'
```

4. **Execute os testes para validar**:
```
python manage.py test roar_crm.tests.test_url_routing
```

## Testes de URL

Testes devem cobrir:

1. **Existência**: Verificar se todas as URLs necessárias existem
2. **Redirecionamento**: Testar se redirecionamentos funcionam
3. **Compatibilidade**: Verificar se URLs antigas continuam funcionando

Exemplo:
```python
def test_main_urls_exist(self):
    urls_to_test = ['main:dashboard', 'main:historico_contatos']
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            self.assertTrue(True)  # A URL existe
        except NoReverseMatch:
            self.fail(f"URL '{url_name}' não existe")
```

## Resolução de Problemas

### NoReverseMatch

Este erro indica que uma URL não pôde ser resolvida. Para corrigir:

1. **Verifique a ortografia** exata do nome da URL
2. **Verifique os parâmetros** passados para a URL
3. **Verifique o namespace** utilizado
4. **Use o sistema de compatibilidade** para mapear nomes antigos

### Conflitos de Nome

Se ocorrerem conflitos de nome:

1. **Renomeie a URL** menos utilizada
2. **Adicione mapeamentos para ambos os nomes** para garantir compatibilidade

### Erros 404

Podem indicar problemas nas URLs:

1. Verifique o **path registrado** em `urls.py`
2. Confirme que a **view está funcionando** corretamente
3. Verifique as **permissões** necessárias para acessar a URL

### Ferramenta de Diagnóstico

Para diagnosticar problemas de URL, use:
```
python verify_urls.py
```

Isso verificará todas as URLs referenciadas no código e mostrará problemas potenciais.

---

## 📝 Nota Final

Ao seguir estas diretrizes, mantemos o sistema de URLs organizado, consistente e compatível com o código existente. Em caso de dúvida, consulte os demais desenvolvedores antes de fazer alterações estruturais nas URLs.

Para uma referência completa sobre a estrutura de URLs, consulte [docs/URL_STRUCTURE_AND_NAMING.md](docs/URL_STRUCTURE_AND_NAMING.md).
