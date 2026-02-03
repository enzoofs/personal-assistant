# Feature: Tracking de Hábitos

## Propósito
Registrar hábitos de saúde e produtividade via texto natural, substituindo apps dedicados como Habitica.

## Categorias

| Categoria | Tipo | Formato | Exemplo |
|---|---|---|---|
| Sono | health | Horas (float) | "Dormi 7 horas" |
| Exercício | health | Tipo + descrição | "Treinei corrida 5km" |
| Humor | health | Escala 1-10 | "Humor 8 hoje" |
| Produtividade | productivity | Texto livre | "Dia focado, terminei 3 PRs" |
| Custom | definido pelo usuário | Texto livre | "Tomei 2L de água" |

## Armazenamento
- Frontmatter YAML no daily note (`daily/YYYY-MM-DD.md`)
- Arquivo dedicado em `habits/health/` ou `habits/productivity/`

## Valor para o Usuário
- Registro em uma frase, sem formulários
- Dados integrados ao briefing diário
- Futuro: detecção de padrões (Fase 2)

## Métricas de Sucesso
- Hábitos registrados diariamente
- Dados estruturados corretamente no vault

## Limitações
- Sem gráficos ou visualização (MVP)
- Sem lembretes proativos (Fase 2)
- Sem validação rígida de formato
