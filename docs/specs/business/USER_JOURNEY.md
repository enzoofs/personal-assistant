# Jornada de Uso — ATLAS

## Workflow Diário Ideal

### Manhã — Briefing
```
Enzo: "Bom dia, o que tenho pra hoje?"
ATLAS: [Briefing com agenda + tarefas + hábitos do dia anterior]
```
- **Gatilho:** Rotina matinal
- **Valor:** Visão consolidada do dia sem abrir múltiplos apps
- **Feature:** Briefing diário

### Ao Longo do Dia — Captura
```
Enzo: "Marca almoço com a equipe sexta 12h"
ATLAS: [Cria evento no Calendar com comentário sarcástico]

Enzo: "Anota que preciso revisar o PR do auth até amanhã"
ATLAS: [Cria nota em projects/ com deadline]
```
- **Gatilho:** Pensamento, reunião, ideia, tarefa
- **Valor:** Captura instantânea via texto ou voz, sem trocar de app
- **Features:** Notas, Calendar, voz

### Noite — Review e Hábitos
```
Enzo: "Dormi 7 horas, treinei corrida, humor 8"
ATLAS: [Registra hábitos com observação sobre tendência]

Enzo: "O que anotei hoje?"
ATLAS: [Resume notas e ações do dia]
```
- **Gatilho:** Rotina noturna
- **Valor:** Registro de hábitos sem fricção + reflexão do dia
- **Features:** Hábitos, pesquisa no vault

## Ciclo de Adoção

### Fase 1: Setup (atual)
- Configurar backend + mobile
- Popular vault inicial
- Testar intents básicos
- **Risco:** Complexidade do setup pode desanimar

### Fase 2: Uso Regular
- Briefing diário vira rotina
- Captura via voz se torna natural
- Hábitos registrados consistentemente
- **Indicador de sucesso:** Uso diário por 2+ semanas

### Fase 3: Dependência Saudável
- ATLAS é o ponto de entrada para produtividade
- Vault acumula contexto rico → pesquisa semântica fica valiosa
- Padrões de hábitos revelam insights (Fase 2)
- **Indicador de sucesso:** Não precisa mais de apps separados para Calendar e hábitos

## Pontos de Fricção Identificados

| Ponto | Fase | Impacto | Mitigação |
|---|---|---|---|
| Classificação errada de intenção | Uso regular | Alto — ação errada frustra | Fallback para chat, melhorar prompt |
| Latência 2-4s por resposta | Uso regular | Médio — parece lento para captura rápida | Streaming (Fase 2) |
| Setup do Google OAuth | Setup | Alto — bloqueante | Documentação clara, token manual para VPS |
| Vault sync com Oracle Cloud | Setup | Alto — vault no server vs. local | Definir estratégia de sync |
| ngrok URL muda no dev | Setup | Médio — precisa atualizar no mobile | IP fixo na Oracle Cloud resolve |

## Momentos de Verdade

1. **Primeiro briefing matinal útil** — Se o briefing agregar valor real, o uso diário começa
2. **Primeira resposta sarcástica que diverte** — Valida o diferencial da personalidade
3. **Primeira nota capturada por voz** — Prova que a captura sem fricção funciona
4. **Primeira busca no vault que encontra algo** — Prova que o "segundo cérebro" funciona
