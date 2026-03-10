# Funcionalidades

## MVP (Fase 1) - Concluido

### Classificacao Automatica de Intencao
Usuario envia texto livre -> ATLAS classifica em uma das 16 intencoes suportadas e extrai parametros. Usa GPT-4o-mini com prompt de classificacao, com fallback para Groq (gratuito).

**Intencoes:** `save_note`, `create_event`, `query_calendar`, `delete_event`, `edit_event`, `log_habit`, `read_email`, `send_email`, `confirm_send_email`, `trash_email`, `search`, `briefing`, `shopping_add`, `shopping_list`, `shopping_complete`, `chat`

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
Busca combinando vault pessoal + web com fallbacks gratuitos:
- **Vault:** busca semantica via ChromaDB (embeddings)
- **Web:** Tavily API -> DuckDuckGo (fallback gratuito)
- Resposta sintetizada, nao links crus

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

### Interacao por Voz
Endpoint `POST /voice` aceita audio, transcreve via Whisper, processa como /chat e retorna resposta com audio TTS.

**Sistema de TTS Multi-tier:**
- `text` — Sem audio (gratuito)
- `audio` — Edge TTS (gratuito, voz pt-BR)
- `audio_premium` — ElevenLabs -> OpenAI -> Edge TTS (cascata com fallback)

---

## Fase 1.5 - Concluido

### Lista de Compras
CRUD completo de lista de compras via linguagem natural e API REST:
- "Adiciona leite e pao na lista de compras"
- "O que tem na minha lista?"
- "Comprei o leite"
- Categorias (mercado, farmacia, etc.)
- Persistencia em SQLite

**Endpoints:** `GET/POST/PATCH/DELETE /shopping`

### Integracao de Email (Gmail)
Leitura, triagem automatica e envio de emails:
- "Mostra meus emails nao lidos"
- "Manda email pro Joao sobre a reuniao"
- Confirmacao antes de enviar
- Triagem automatica de spam/newsletters em background
- "Limpa os emails de promocao"

**Intents:** `read_email`, `send_email`, `confirm_send_email`, `trash_email`

### Voice Capture
Transcricao de voz para notas estruturadas no vault:
- Estruturacao automatica via LLM (titulo, categoria, tags)
- Extracao de action items
- Auto-linking com notas relacionadas
- Quick capture para notas rapidas

**Endpoint:** `POST /vault/voice-capture`

### Streaming de Resposta (SSE)
Server-Sent Events para menor latencia percebida:
- Tokens enviados conforme gerados
- Fallback automatico para Groq se OpenAI falhar
- Headers: `text/event-stream`, `no-cache`

**Endpoint:** `POST /chat/stream`

### Sistema de Fallbacks Gratuitos
Resiliencia com alternativas sem custo:

| Servico | Principal | Fallback (gratuito) |
|---|---|---|
| LLM | OpenAI GPT-4o-mini | Groq Llama 3.1 |
| TTS | ElevenLabs | Edge TTS |
| Busca Web | Tavily | DuckDuckGo |

### Configuracao de Modo de Resposta
Controle dinamico do modo de audio:
- `GET /settings` — Ver modo atual
- `PATCH /settings` — Alterar modo em runtime
- Modos: `text`, `audio`, `audio_premium`

---

## Fase 2 (Em Desenvolvimento)

- **App Android polido** — Dashboard com agenda/habitos/metricas/chat
- **Reconhecimento de padroes** — analisa dados acumulados e identifica tendencias
- **Notificacoes proativas** — push com personalidade ("Faz 3 dias que voce nao treina.")

## Fase 3 (Futuro)

- Telegram como canal secundário
- APIs externas (notícias, clima)
- Google Fit / wearables
- Sarcasmo configurável
