# Feature: Gestão de Notas (Obsidian)

## Propósito
Criar e organizar notas no vault Obsidian via linguagem natural, com categorização automática e frontmatter YAML.

## Workflows
- "Anota que preciso comprar remédio" → nota em `inbox/`
- "Anota sobre o projeto Atlas: implementar vault module" → nota em `projects/`
- "Salva que o João prefere café sem açúcar" → nota em `people/`

## Categorização Automática

| Categoria | Pasta | Critério |
|---|---|---|
| Projetos | `projects/` | Menciona projeto, tarefa, deadline |
| Pessoas | `people/` | Menciona pessoa específica |
| Pesquisa | `research/` | Resultado de busca salvo |
| Hábitos | `habits/` | Registro de hábito |
| Genérico | `inbox/` | Sem categoria clara (fallback) |

## Valor para o Usuário
- Captura instantânea sem abrir Obsidian
- Organização automática sem esforço manual
- Daily notes atualizadas com referências

## Métricas de Sucesso
- Notas categorizadas corretamente > 80% do tempo
- Frontmatter sempre presente e válido

## Limitações
- ATLAS nunca deleta notas automaticamente
- Slug do arquivo limitado a 50 caracteres
- Implementação vault/manager.py pendente
