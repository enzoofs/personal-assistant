# Funcionalidades

## MVP (Fase 1)

### Classificação Automática de Intenção
Usuário envia texto livre → ATLAS classifica em uma das 7 intenções suportadas e extrai parâmetros. Usa GPT-4o-mini com prompt de classificação.

**Intenções:** `save_note`, `create_event`, `query_calendar`, `delete_event`, `log_habit`, `search`, `briefing`, `chat`

### Gestão de Notas (Obsidian)
Criar e organizar notas automaticamente no vault Obsidian:
- Categorização automática na pasta correta (inbox, projects, people, etc.)
- Frontmatter YAML (date, tags, category)
- Links entre notas relacionadas
- Atualização da daily note com referências

**Exemplo:** "Anota que preciso revisar o contrato até sexta" → cria nota em `projects/` com tag `deadline`

### Google Calendar
CRUD de eventos via linguagem natural:
- Criar: "Marca reunião com João amanhã às 15h"
- Listar: "O que tenho pra hoje?"
- Editar/deletar eventos existentes
- Parsing de data/hora via LLM

### Briefing Diário
Resumo completo do dia agregando múltiplas fontes:
- Compromissos do Google Calendar (ordenados)
- Tarefas pendentes do vault
- Observações sobre hábitos recentes
- Tudo com o tom sarcástico do ATLAS

### Tracking de Hábitos
Registro via texto natural de dados de saúde e produtividade:
- **Saúde:** sono (horas), exercício (sim/não + tipo), humor (1-10)
- **Produtividade:** tarefas, foco
- **Custom:** hábitos definidos pelo usuário

Armazenamento: frontmatter YAML no daily note + arquivo em `habits/`

### Pesquisa Inteligente
Busca combinando vault pessoal + web:
- **Vault:** busca semântica via ChromaDB (embeddings)
- **Web:** Tavily API (retorna texto contextualizado)
- Resposta sintetizada, não links crus

### Personalidade ATLAS
Em todas as interações:
- Tom sarcástico mas útil
- Observações proativas não solicitadas
- Referências a dados anteriores do usuário
- Direto e sem rodeios

### App Mobile (React Native / Expo)
Interface de chat no celular Android:
- Chat com texto e voz (gravação via Expo AV)
- Action cards visuais por tipo de ação (nota salva, evento criado, etc.)
- Indicador de status online/offline do backend
- Envio de áudio com transcrição Whisper + resposta TTS
- Animações de digitando e entrada de mensagens

**Componentes:** MessageBubble, ActionCard, ChatInput, MicButton, TypingIndicator

### Interação por Voz
Endpoint `POST /voice` aceita áudio, transcreve via Whisper, processa como /chat e retorna resposta com áudio TTS em base64.

---

## Fase 2 (Planejado)

- **Áudio bidirecional aprimorado** — Melhorias no fluxo Whisper STT + OpenAI TTS
- **App Android polido** — Dashboard com agenda/hábitos/métricas/chat
- **Reconhecimento de padrões** — analisa dados acumulados e identifica tendências
- **Notificações proativas** — push com personalidade ("Faz 3 dias que você não treina.")

## Fase 3 (Futuro)

- Telegram como canal secundário
- APIs externas (notícias, clima)
- Google Fit / wearables
- Sarcasmo configurável
