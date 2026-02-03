# Padrões de Design

## Padrão Arquitetural: Pipeline com Orquestrador

O fluxo segue um pipeline sequencial:

```
Input → Classificação → Routing → Execução → Geração de Resposta → Output
```

O `Orchestrator` coordena todo o fluxo. Não há event-driven ou filas — é síncrono e direto.

## Organização de Código

```
atlas/
├── main.py              # Ponto de entrada, FastAPI app
├── config.py            # Settings centralizadas
├── orchestrator.py      # Coordenação do fluxo principal
├── intent/              # Classificação de intenção (LLM)
├── tools/               # Ações executáveis (calendar, obsidian, etc.)
├── persona/             # Personalidade e geração de resposta
├── vault/               # Abstração do filesystem Obsidian
└── services/            # Clientes de serviços externos (OpenAI, Google)
```

**Princípio:** cada pasta é uma responsabilidade. `tools/` não sabe sobre persona. `intent/` não sabe sobre vault. O `orchestrator` conecta tudo.

## Padrões de Código

### Manager Pattern
Cada integração tem um "Manager" que encapsula CRUD:
- `ObsidianManager` — CRUD de notas no vault
- `CalendarManager` — CRUD de eventos no Google Calendar
- `VaultManager` — Leitura/escrita de markdown no filesystem

### Schema-first (Pydantic)
Todas as entradas e saídas tipadas com Pydantic models:
- `IntentResult` — resultado da classificação
- `ChatRequest` / `ChatResponse` — contratos da API
- `HabitEntry`, `NoteMetadata` — dados estruturados

### Service Wrapper
Clientes de API externa encapsulados em `services/`:
- `openai_client.py` — abstrai OpenAI SDK
- `google_auth.py` — abstrai OAuth2 flow

## Convenções

### Nomenclatura
- Arquivos: `snake_case.py`
- Classes: `PascalCase`
- Funções/variáveis: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`

### Config
- Todas as configs via `pydantic-settings` lendo `.env`
- Sem hardcode de API keys ou paths

### Markdown (vault)
- Frontmatter YAML obrigatório em toda nota criada pelo ATLAS
- Campos mínimos: `date`, `tags`, `category`
- Nomes de arquivo: `kebab-case.md` ou `YYYY-MM-DD.md` (daily notes)

## Padrões de Teste

- `pytest` + `pytest-asyncio`
- Testes unitários por tool (mock de APIs externas)
- `httpx` AsyncClient para testes de integração do endpoint

## Tratamento de Erros

- APIs externas: try/except com fallback gracioso (ex: se Google Calendar falha, informa o usuário)
- Classificação ambígua: fallback para `chat`
- Vault: ATLAS só adiciona/atualiza, nunca deleta automaticamente
