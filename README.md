# ROAR CRM - Sistema de Gestão de Relacionamento com Clientes

## Visão Geral

ROAR CRM é um sistema completo de gestão de relacionamento com clientes, específico para equipes comerciais no setor financeiro. Este sistema permite o gerenciamento de leads, contatos, vendedores e métricas de desempenho através de uma interface intuitiva e moderna.

## Recursos Principais

- **Gestão de Leads**: Cadastro, importação, classificação e acompanhamento completo
- **Funil de Vendas Kanban**: Interface visual para acompanhamento do progresso de vendas
- **Dashboard Analítico**: Métricas de desempenho e visualizações para gerentes e vendedores
- **Agenda e Lembretes**: Sistema de agendamento e lembretes para atividades comerciais
- **Controle de Acesso**: Três níveis de permissão (Admin, Supervisor, Vendedor)
- **Exportação de Dados**: Geração de relatórios personalizados em diversos formatos
- **Interface Moderna**: Design responsivo com tema Dark Gold

## Estrutura do Projeto

O projeto segue o padrão MVC do Django e está organizado nos seguintes aplicativos, após refatoração para seguir melhores práticas:

- **leads**: Gerenciamento de leads/prospects e comunicações
- **vendedores**: Gerenciamento de equipe comercial e métricas
- **gerencia**: Funcionalidades administrativas e relatórios
- **automacao**: Automação de marketing e comunicação

### Organização de Código

```
roar/
    ├── docs/                    # Documentação organizada do projeto
    │   ├── features/            # Documentação de funcionalidades
    │   └── ui/                  # Documentação de interface
    ├── templates/               # Templates globais
    │   ├── components/          # Componentes reutilizáveis HTML
    │   │   ├── cards/           # Componentes de cards
    │   │   ├── forms/           # Componentes de formulários
    │   │   └── navigation/      # Componentes de navegação
    │   └── [apps]/              # Templates específicos por aplicação
    ├── static/                  # Arquivos estáticos globais
    │   ├── css/                 # Folhas de estilo
    │   │   ├── components/      # CSS para componentes específicos
    │   │   └── themes/          # Temas visuais
    │   └── js/                  # JavaScript
    │       ├── charts/          # Scripts para gráficos e visualizações
    │       ├── forms/           # Scripts para formulários
    │       └── nav/             # Scripts para navegação
    ├── leads/                   # App de gestão de leads
    ├── vendedores/              # App de gestão de vendedores
    ├── gerencia/                # App de administração
    ├── automacao/               # App de automação de marketing
    └── tests/                   # Testes organizados por módulo
        ├── ui/                  # Testes de interface
        └── leads/               # Testes de funcionalidades de leads
```

## Arquivos de Configuração

- **utils.py**: Funções utilitárias para o sistema
- **setup.py**: Script de configuração inicial do ambiente

## Documentação

Para documentação mais detalhada sobre recursos específicos e uso do sistema, consulte os arquivos em `docs/`:

- [Documentação de Refatoração](docs/REFACTOR_DOCUMENTATION.md)
- [Documentos de Funcionalidades](docs/features/)
- [Documentos de Interface](docs/ui/)

## Desenvolvimento

### Scripts de Manutenção

Para manutenção e refatoração do projeto, os seguintes scripts estão disponíveis:

- `python refactor_project.py` - Executa o processo completo de refatoração
- `python migrate_leads_app.py` - Migra os módulos consolidados da app leads
- `python organize_static_files.py` - Reorganiza os arquivos estáticos

### Convenções de Código

Este projeto segue as convenções PEP 8 para código Python e utiliza metodologias modernas de desenvolvimento Django. Para mais detalhes sobre as convenções específicas adotadas, consulte a [Documentação de Refatoração](docs/REFACTOR_DOCUMENTATION.md).

## Configuração do Ambiente

### Requisitos
- Python 3.8+
- Django 5.2
- SQLite (desenvolvimento) ou PostgreSQL (produção)

### Instalação

1. Clone o repositório
2. Crie e ative um ambiente virtual
3. Instale as dependências
4. Configure as variáveis de ambiente
5. Execute as migrações
6. Execute o script de configuração inicial
7. Inicie o servidor de desenvolvimento

```bash
# Exemplo para Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python setup.py
python manage.py runserver
```

## Estrutura de URLs e Namespaces

O projeto utiliza namespaces para organizar as URLs das diferentes aplicações:

- **Raiz (`/`)**: Redireciona para o dashboard principal
- **main**: Namespace para a aplicação de vendedores
  - `main:dashboard_principal` - Dashboard do vendedor (`/main/`)
  - `main:dashboard_principal_alt` - Rota alternativa do dashboard (`/main/dashboard/`)
  - `main:historico_contatos` - Histórico de contatos (`/main/historico/`)
- **leads**: Namespace para gestão de leads
  - `leads:list` - Listagem de leads (`/leads/list/`)
  - `leads:detail` - Detalhes de um lead específico (`/leads/<id>/`)
- **gerencia**: Namespace para funcionalidades administrativas
- **automacao**: Namespace para funcionalidades de automação

> **Nota**: Para compatibilidade, foi adicionada uma URL `main:dashboard` que também redireciona para o dashboard principal.

Para documentação detalhada sobre a estrutura de URLs e convenções de nomenclatura, consulte [docs/URL_STRUCTURE_AND_NAMING.md](docs/URL_STRUCTURE_AND_NAMING.md).

## Sistema de Compatibilidade de URLs

Para garantir a compatibilidade com código existente durante a migração e refatoração, implementamos um sistema abrangente de compatibilidade de URLs:

### Camadas de Compatibilidade

1. **Mapeamentos de URL**: Sistema central que mapeia nomes antigos para novos nomes de URL
2. **Processador de Contexto**: Adiciona helpers de URL em todos os templates
3. **Tags de Template**: Oferece tags para criar URLs compatíveis em templates
4. **Redirecionamentos Automáticos**: Redireciona automaticamente URLs antigas para novas
5. **Verificador de URLs**: Script para identificar problemas de URLs no projeto

### Como Trabalhar com URLs

Para incluir um link em um template, use as seguintes abordagens:

```django
{# Método 1: Usar o processador de contexto #}
<a href="{{ get_compatible_url 'vendedores:dashboard' }}">Dashboard</a>

{# Método 2: Usar as tags de template #}
{% load url_compat %}
<a href="{% compat_url 'leads:detalhes_lead' lead_id=lead.id %}">Ver Lead</a>
```

Para verificar inconsistências de URL, execute o script:
```
python verify_urls.py
```

Para mais detalhes sobre as ferramentas de compatibilidade, veja a [documentação completa de URLs](docs/URL_STRUCTURE_AND_NAMING.md).

## Contas de Usuário

O sistema cria automaticamente um usuário supervisor:

- **Username**: supervisor
- **Senha**: senha123

## Segurança

Em ambiente de produção, certifique-se de:

1. Alterar a SECRET_KEY
2. Definir DEBUG=False
3. Configurar ALLOWED_HOSTS adequadamente
4. Usar um banco de dados robusto como PostgreSQL
5. Configurar HTTPS

## Resolução de conflitos de modelos

Durante o processo de refatoração, você pode encontrar erros relacionados a conflitos de modelos, especialmente quando modelos são definidos em mais de um arquivo. Estes erros podem aparecer como:

```
RuntimeError: Conflicting 'templatewhatsapp' models in application 'leads': <class 'leads.models.TemplateWhatsApp'> and <class 'leads.models_comunicacao.TemplateWhatsApp'>.
```

Se isso acontecer, siga estas etapas:

1. Execute a migração completa para substituir todos os arquivos relevantes:
```bash
python refactor_project.py
```

2. Se ainda encontrar conflitos, verifique se há importações incorretas em:
   - Arquivos admin.py
   - Arquivos de views que podem estar importando de dois lugares diferentes
   - Scripts de gerenciamento personalizados

Para resolver manualmente:
```bash
# Remover arquivos redundantes para evitar a duplicação
rm leads/models_comunicacao.py
rm leads/forms_comunicacao.py
rm leads/views_comunicacao.py
```

Os modelos consolidados agora incluem toda a funcionalidade dos arquivos separados anteriores em uma estrutura mais limpa e organizada.

## Licença

Todos os direitos reservados © 2025 ROAR CRM
