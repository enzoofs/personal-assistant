# Feature: Classificação de Intenção

## Propósito
Classificar automaticamente mensagens em linguagem natural em uma das 8 intenções suportadas, extraindo parâmetros relevantes. É o "cérebro" de roteamento do ATLAS.

## Intents Suportadas

| Intent | Exemplo | Parâmetros Extraídos |
|---|---|---|
| `save_note` | "Anota que preciso revisar o contrato" | title, content, category, tags |
| `create_event` | "Marca reunião amanhã 15h" | title, datetime, duration |
| `query_calendar` | "O que tenho pra hoje?" | period (today/tomorrow/week) |
| `delete_event` | "Cancela reunião de sexta" | title, date |
| `log_habit` | "Dormi 7 horas" | habit, value, category |
| `search` | "O que anotei sobre o projeto X?" | query, source (vault/web/both) |
| `briefing` | "Bom dia" / "Resumo do dia" | — |
| `chat` | "Qual a capital da França?" | — (fallback) |

## Valor para o Usuário
- Não precisa navegar menus ou escolher ação — fala naturalmente
- Data/hora relativa resolvida automaticamente ("amanhã" → data correta)

## Métricas de Sucesso
- Acurácia de classificação > 90% para intents claras
- Fallback para `chat` em caso de ambiguidade (segurança)

## Limitações
- Uma mensagem = uma intenção (sem multi-intent)
- Depende da qualidade do prompt de classificação
- Latência de 1-2s por classificação (chamada LLM)
