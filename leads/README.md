# Módulo de Leads - Consolidação de Arquivos

## Sobre a consolidação

Este módulo foi submetido a uma consolidação em 18/06/2025 para reduzir a duplicidade de código e simplificar a manutenção. Arquivos com nomes semelhantes foram mesclados em uma única versão consolidada, e os arquivos originais foram preservados com fins de referência histórica.

## Arquivos consolidados

Os seguintes arquivos consolidados foram criados:

1. `models_consolidated.py` - Consolidação de modelos de dados
   - Origem: `models.py`, `models_new.py`, `models_comunicacao.py.disabled`

2. `forms_consolidated.py` - Consolidação de formulários
   - Origem: `forms.py`, `forms_new.py`, `forms_comunicacao.py.disabled`

3. `views_consolidated.py` - Consolidação de views
   - Origem: `views.py`, `views_new.py`, `views_comunicacao.py.disabled`

4. `urls_consolidated.py` - Consolidação de URLs
   - Origem: `urls.py`, `urls_new.py`, `urls_compatibility.py`

5. `admin_consolidated.py` - Consolidação de configurações admin
   - Origem: `admin.py`, `admin_new.py`

## Estrutura de importações

Os arquivos consolidados foram projetados para funcionar uns com os outros:

- `views_consolidated.py` importa de `models_consolidated.py` e `forms_consolidated.py`
- `forms_consolidated.py` importa de `models_consolidated.py`
- `admin_consolidated.py` importa de `models_consolidated.py`

## Configuração do aplicativo

O arquivo `apps.py` foi atualizado para utilizar a classe `LeadsConfig` que referencia adequadamente os arquivos consolidados.

## Próximos passos

1. Verificar a funcionalidade do sistema após a consolidação
2. Atualizar referências em outros arquivos do projeto
3. Remover os arquivos originais após período de validação
