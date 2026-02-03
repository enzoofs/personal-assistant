# Integrações

## OpenAI API

**Tipo:** REST API
**Uso:** Classificação de intenção, geração de resposta, embeddings
**Dependência:** Crítica — sem ela o ATLAS não funciona

### Modelos utilizados
| Modelo | Uso | Custo estimado |
|---|---|---|
| `gpt-4o-mini` | Chat completions (classificação + resposta) | ~$0.15/1M tokens input |
| `text-embedding-3-small` | Embeddings para indexação no ChromaDB | ~$0.02/1M tokens |

### Padrão de uso
- 2 chamadas por request: classificação + resposta com persona
- SDK: `openai` Python (`>=1.60`)
- Autenticação: API key via `OPENAI_API_KEY` env var

### Tratamento de falhas
- Timeout: 30s por chamada
- Rate limit: retry com backoff exponencial
- Erro: retorna mensagem genérica ao usuário

---

## Google Calendar API

**Tipo:** REST API (Google Workspace)
**Uso:** CRUD de eventos do calendário
**Dependência:** Alta — briefing e gestão de agenda dependem dela

### Autenticação
- OAuth2 via `google-auth-oauthlib`
- Primeiro uso: abre navegador para consentimento
- Token salvo em `token.json` (auto-refresh)
- Scopes: `https://www.googleapis.com/auth/calendar`

### Operações
- `events().list()` — listar eventos
- `events().insert()` — criar evento
- `events().update()` — editar evento
- `events().delete()` — deletar evento

### Requisitos
- `credentials.json` do Google Cloud Console (OAuth 2.0 Client ID)
- Projeto no Google Cloud com Calendar API habilitada

---

## Tavily API

**Tipo:** REST API
**Uso:** Busca web otimizada para LLMs
**Dependência:** Média — funciona sem ela (perde busca web)

### Padrão de uso
- `get_search_context()` — retorna texto limpo, pronto pra injetar no prompt
- `search_depth="advanced"` para resultados melhores
- `max_tokens=4000` para limitar tamanho do contexto

### Autenticação
- API key via `TAVILY_API_KEY` env var
- Free tier disponível

---

## ChromaDB

**Tipo:** Banco vetorial local (embedded)
**Uso:** Busca semântica nas notas do vault Obsidian
**Dependência:** Alta — busca no vault depende dela

### Configuração
- `PersistentClient(path="./chroma_db")` — dados persistem no disco
- Collection: `vault_notes`
- IDs: hash SHA256 do conteúdo do arquivo

### Indexação incremental
- `upsert()` — adiciona novo ou atualiza existente baseado no ID
- Roda no startup + opcionalmente via filesystem watcher
- Reconstruível a partir do vault (não é source of truth)

---

## Obsidian Vault

**Tipo:** Filesystem (markdown)
**Uso:** Source of truth para todas as notas, hábitos, pesquisas
**Dependência:** Crítica

### Acesso
- Direto via `pathlib` + `python-frontmatter`
- Backend e vault na mesma máquina
- Compatível com Obsidian app rodando simultaneamente

### Estrutura
```
vault/
├── daily/           # YYYY-MM-DD.md
├── inbox/           # Notas não categorizadas
├── projects/        # Notas por projeto
├── people/          # Notas por pessoa
├── habits/
│   ├── health/      # Sono, exercício, humor
│   └── productivity/
├── research/        # Pesquisas salvas
├── insights/        # Padrões detectados (Fase 2)
└── templates/       # Templates markdown
```

## Mobile App (React Native / Expo)

**Tipo:** App Android (React Native + Expo SDK 54)
**Uso:** Interface de chat principal com ATLAS
**Dependência:** Consumidor da API — não é dependência do backend

### Comunicação com Backend
- HTTP REST via `fetch`
- Endpoints consumidos: `POST /chat`, `POST /voice`, `GET /health`
- Autenticação: header `X-API-Key`
- **Dev:** via ngrok tunnel (URL em `src/api/atlas.ts`)
- **Produção:** via IP público da Oracle Cloud VPS

### Funcionalidades do App
- Chat com texto e voz
- Action cards visuais por tipo de ação
- Indicador de status online/offline
- Gravação de áudio (Expo AV) + envio para transcrição

---

## Variáveis de Ambiente

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
GOOGLE_CREDENTIALS_PATH=./credentials.json
VAULT_PATH=./vault
CHROMA_DB_PATH=./chroma_db
ATLAS_API_KEY=sua-chave-para-proteger-o-endpoint
TIMEZONE=America/Sao_Paulo
```
