# Feature: Google Calendar

## Propósito
CRUD de eventos no Google Calendar via linguagem natural, substituindo a interação direta com o app Calendar.

## Operações

| Operação | Exemplo | Detalhes |
|---|---|---|
| Criar | "Marca reunião com João amanhã 15h" | Título + datetime obrigatórios, duração padrão 1h |
| Listar | "O que tenho pra hoje?" | Períodos: today, tomorrow, week |
| Deletar | "Cancela a reunião de sexta" | Busca por título + data, requer confirmação |

## Valor para o Usuário
- Gerencia agenda sem sair do chat
- Parsing de data/hora natural ("amanhã às 15h", "sexta que vem")
- Integrado ao briefing diário

## Métricas de Sucesso
- Eventos criados com data/hora corretos
- Listagem reflete calendário real
- Deleção funciona por busca de título

## Limitações
- Não edita eventos existentes (só cria e deleta no MVP)
- OAuth requer navegador no primeiro uso
- Timezone fixa configurada no .env
