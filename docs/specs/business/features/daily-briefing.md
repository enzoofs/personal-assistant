# Feature: Briefing Diário

## Propósito
Resumo consolidado do dia agregando múltiplas fontes, entregue com a personalidade ATLAS. Resolve o pain point principal: falta de visão geral.

## Fontes Agregadas
1. **Google Calendar** — Compromissos do dia, ordenados
2. **Daily note** — Conteúdo da nota do dia
3. **Inbox** — Últimas 5 notas não categorizadas
4. **Hábitos** — Registros do dia

## Exemplo
```
Enzo: "Bom dia, o que tenho pra hoje?"
ATLAS: "Bom dia, prodígio. Teu dia:
- 10h: Standup (como sempre)
- 14h: Review com o time
- 15h30: Reunião com João (aquela que você já cancelou 2x)

No vault: 3 notas no inbox esperando categorização.
Hábitos de ontem: dormiu 6h (precário), não treinou.
Boa sorte."
```

## Valor para o Usuário
- **Momento de verdade #1** — Se o primeiro briefing for útil, o uso diário começa
- Elimina necessidade de checar Calendar + Obsidian + app de hábitos separadamente
- Tom sarcástico torna a rotina matinal mais leve

## Métricas de Sucesso
- Briefing inclui todas as fontes disponíveis
- Informações corretas e atualizadas
- Personalidade consistente

## Limitações
- Não inclui clima, notícias ou dados externos (Fase 3)
- Depende de vault/manager.py para ler daily notes (implementação pendente)
