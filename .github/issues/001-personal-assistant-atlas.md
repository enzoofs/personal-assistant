# ATLAS — Assistente Pessoal "Segundo Cérebro"

## Status: Spec Ready

---

## Visão Geral do Produto

### Problema
Informações pessoais ficam fragmentadas entre múltiplos apps (calendário, notas, habit trackers, buscas). Não existe um sistema unificado que organize tudo, aprenda com padrões e dê feedback proativo com personalidade.

### Solução
ATLAS é um assistente pessoal single-user com personalidade sarcástica (estilo Jarvis), que centraliza informações em um vault Obsidian, gerencia agenda via Google Calendar e faz busca inteligente combinando web + memória pessoal. O diferencial é a proatividade — ele não apenas responde, ele observa e comenta.

### Usuário-alvo
Único usuário (projeto pessoal). Sem necessidade de multi-tenancy ou autenticação complexa.

### Métricas de Sucesso
- Uso diário consistente (briefing matinal, registro de hábitos)
- Vault Obsidian crescendo organicamente com notas bem categorizadas
- Redução de apps usados para organização pessoal

---

## Requisitos Funcionais

### MVP (Fase 1) — Texto + Obsidian + Calendar

#### US-01: Classificação automática de intenção
**Como** usuário, **quero** enviar uma mensagem de texto livre **para que** o ATLAS identifique automaticamente se é uma nota, compromisso, registro de hábito, pesquisa ou conversa casual, e aja de acordo.

**Intenções suportadas:**
- `save_note` — salvar informação no vault
- `create_event` — criar compromisso no Google Calendar
- `log_habit` — registrar dado de hábito/saúde
- `search` — buscar informação (web + vault)
- `query_calendar` — consultar agenda
- `briefing` — pedir resumo do dia
- `chat` — conversa casual

**Critérios de aceitação:**
- Classificação correta em >90% dos casos
- Fallback para `chat` quando a intenção não é clara
- Confirmação ao usuário da ação tomada

#### US-02: Briefing diário
**Como** usuário, **quero** perguntar "o que tenho pra hoje?" **para que** o ATLAS me dê um resumo completo do dia com tom sarcástico.

**O briefing inclui:**
- Compromissos do Google Calendar (ordenados por horário)
- Tarefas pendentes do vault
- Observações sobre hábitos recentes (se houver dados)
- Tom: personalidade ATLAS (sarcástico, direto)

**Exemplo:**
> "Reunião às 10h com o time, almoço com o Carlos às 12h30, e aquele deadline que você vem empurrando há 3 dias. Dormiu 5h ontem — vou fingir que não vi."

#### US-03: Gestão de notas no Obsidian
**Como** usuário, **quero** dizer "anota que preciso revisar o contrato até sexta" **para que** o ATLAS crie/atualize a nota correta no vault, na pasta certa, com metadata.

**Comportamento:**
- Classifica a nota na pasta correta (inbox, projects, people, etc.)
- Adiciona frontmatter YAML (date, tags, category)
- Cria links para notas relacionadas quando relevante
- Daily note atualizada com referência

#### US-04: Google Calendar
**Como** usuário, **quero** dizer "marca reunião com João amanhã às 15h" **para que** o ATLAS crie o evento no Google Calendar.

**Operações:**
- Criar evento (com parsing de linguagem natural para data/hora)
- Listar eventos do dia/semana
- Editar evento existente
- Deletar evento

#### US-05: Tracking de hábitos
**Como** usuário, **quero** dizer "dormi 6h", "treinei", "humor: 7/10" **para que** o ATLAS registre no vault de forma estruturada.

**Categorias:**
- Saúde: sono (horas), exercício (sim/não + tipo), humor (escala 1-10)
- Produtividade: tarefas concluídas, foco
- Custom: hábitos definidos pelo usuário

**Formato de armazenamento:** frontmatter YAML no daily note + arquivo dedicado em `habits/`

#### US-06: Pesquisa inteligente
**Como** usuário, **quero** perguntar "o que eu anotei sobre o projeto X?" ou "pesquisa sobre Y" **para que** o ATLAS busque no vault e/ou na web e me dê uma resposta contextualizada.

**Fontes:**
- Vault Obsidian via ChromaDB (busca semântica com embeddings)
- Web via API de search (Tavily ou similar)
- Combinação de ambas quando relevante

**Resposta:** texto contextualizado com a personalidade ATLAS, não links crus.

#### US-07: Personalidade ATLAS
**Em todas as interações**, o ATLAS responde com:
- Tom sarcástico mas útil
- Observações não solicitadas quando detecta algo relevante
- Referências a dados anteriores do usuário ("Você disse a mesma coisa semana passada...")
- Direto e sem rodeios

**System prompt base (a refinar na implementação):**
> "Você é ATLAS, um assistente pessoal com personalidade marcante. Você é sarcástico, inteligente e direto. Faz observações não solicitadas quando percebe algo relevante. Não é passivo — se o usuário está ignorando algo, você comenta. Sempre útil, mas nunca sem graça."

### Fase 2 — Áudio + App + Padrões + Notificações

- Áudio bidirecional (Whisper STT + OpenAI TTS)
- App Android (React Native) com dashboard: agenda, hábitos, métricas, insights, chat
- Reconhecimento de padrões em dados acumulados
- Push notifications proativas com personalidade

### Fase 3 (Futuro)

- Telegram como canal secundário
- APIs externas (notícias, clima)
- Google Fit / wearables
- Sarcasmo configurável

---

## Requisitos Não-Funcionais

- **Latência:** resposta em <5s para texto (incluindo chamada ao GPT)
- **Disponibilidade:** não crítico (projeto pessoal), mas idealmente 95%+ uptime
- **Custo:** GPT-4o-mini para manter custo baixo (~$0.15/1M tokens input)
- **Segurança:** API key simples para proteger o endpoint, dados ficam no vault local/VPS
- **Dados:** vault Obsidian é a source of truth, ChromaDB é índice reconstruível

---

## Considerações Técnicas

### Stack

| Componente | Tecnologia | Justificativa |
|---|---|---|
| Backend | Python + FastAPI | Ecossistema AI maduro, async nativo |
| LLM | OpenAI GPT-4o-mini | Custo-eficiente, qualidade suficiente |
| Busca semântica | ChromaDB (local) | Embeddings para busca no vault, sem infra extra |
| Embeddings | OpenAI text-embedding-3-small | Barato, bom para busca semântica |
| Storage | Obsidian vault (markdown) | Portável, legível, funciona com app Obsidian |
| Calendário | Google Calendar API | API madura, OAuth2 |
| Busca web | Tavily API | Feita para LLMs, retorna texto, não HTML |
| Deploy | Railway ou local | Custo mínimo, simples de manter |

### Arquitetura MVP

```
[Usuário] → [API FastAPI] → [Orquestrador ATLAS]
                                    │
                                    ├── [Intent Classifier] (GPT-4o-mini)
                                    │
                                    ├── [Tools/Actions]
                                    │     ├── ObsidianManager (CRUD no vault)
                                    │     ├── CalendarManager (Google Calendar API)
                                    │     ├── HabitTracker (parse + store)
                                    │     ├── SearchEngine (ChromaDB + Tavily)
                                    │     └── BriefingGenerator
                                    │
                                    ├── [ChromaDB] (índice vetorial do vault)
                                    │
                                    └── [Response Generator] (GPT-4o-mini + system prompt ATLAS)
```

**Fluxo:**
1. Usuário envia mensagem → API recebe
2. Orquestrador passa para o LLM com function calling para classificar intenção
3. Executa a(s) tool(s) correspondente(s)
4. Gera resposta com personalidade ATLAS usando contexto das tools
5. Retorna resposta ao usuário

### Estrutura do Vault Obsidian

```
vault/
├── daily/              # YYYY-MM-DD.md — resumo do dia, hábitos, links
├── inbox/              # Notas rápidas não categorizadas
├── projects/           # Uma nota por projeto
├── people/             # Uma nota por pessoa
├── habits/
│   ├── health/         # Logs de sono, exercício, humor
│   └── productivity/   # Logs de produtividade
├── research/           # Resultados de pesquisas salvas
├── insights/           # Padrões e observações do ATLAS (Fase 2)
└── templates/          # Templates markdown
```

### Dependências de Terceiros

- OpenAI API (GPT-4o-mini + embeddings)
- Google Calendar API (OAuth2)
- Tavily API (busca web)
- ChromaDB (local, sem custo)

---

## Riscos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Custo OpenAI cresce com uso | Médio | GPT-4o-mini + cache de respostas frequentes |
| Vault cresce, busca fica lenta | Baixo | ChromaDB com indexação incremental |
| Google Calendar quota limit | Baixo | Cache local de eventos com TTL |
| Classificação errada de intenção | Médio | Fallback para chat + pedir confirmação em ações destrutivas |
| Obsidian vault conflita com edição manual | Baixo | ATLAS só adiciona, nunca deleta automaticamente |

---

## Restrições e Suposições

**Restrições:**
- Single-user apenas (sem multi-tenancy)
- Android only para o app mobile (Fase 2)
- Dependência de APIs pagas (OpenAI, Tavily)

**Suposições:**
- Usuário terá Obsidian instalado e vault sincronizado
- Conexão com internet disponível para chamadas de API
- Usuário interage pelo menos 1x/dia para dados de hábitos terem valor
