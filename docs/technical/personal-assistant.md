# Personal Assistant (ATLAS)

## Propósito e Papel

ATLAS é um assistente pessoal inteligente estilo Jarvis, construído como projeto single-user para o usuário Enzo. O sistema centraliza informações em um vault Obsidian (segundo cérebro), gerencia agenda via Google Calendar, realiza pesquisas inteligentes combinando busca semântica local e web, rastreia hábitos e gera briefings diários — tudo com uma personalidade própria inspirada em um mordomo digital sarcástico e elegante.

O repositório é um monolito composto por dois módulos principais: um backend Python (FastAPI) que concentra toda a lógica de negócio, classificação de intenção via LLM, orquestração de ferramentas e integrações externas; e um app mobile React Native (Expo) que serve como interface de chat com suporte a texto e áudio.

O projeto está em fase MVP funcional, com backend e mobile operacionais. O backend processa mensagens via pipeline: classificação de intenção → roteamento para ferramenta → execução → geração de resposta com personalidade. O mobile oferece interface de chat com gravação de áudio, action cards visuais por tipo de ação e animações.

## Funcionalidades Principais

### Classificação de Intenção
Classifica automaticamente mensagens do usuário em 8 intenções suportadas (save_note, create_event, query_calendar, delete_event, log_habit, search, briefing, chat) usando GPT-4o-mini com injeção de data/hora atual para resolução temporal correta.

### Gerenciamento de Notas (Obsidian)
Cria notas com frontmatter YAML no vault Obsidian, categorizando automaticamente em pastas (inbox, projects, people, daily, habits, research, insights). Markdown é a fonte de verdade; ChromaDB é índice reconstruível.

### Google Calendar CRUD
Integração completa via OAuth2: criar, listar e deletar eventos por linguagem natural. Suporta períodos (hoje, amanhã, semana) e busca por título para deleção.

### Briefing Diário
Gera resumo consolidado de eventos do calendário, tarefas pendentes e observações de hábitos, entregue com a personalidade ATLAS.

### Rastreamento de Hábitos
Registra hábitos de saúde (sono, exercício, humor), produtividade e categorias customizadas. Armazenado via ChromaDB para análise de padrões.

### Pesquisa Inteligente
Combina busca semântica no vault (ChromaDB + embeddings) com busca web (Tavily), sintetizando resultados em resposta unificada. Vault priorizado sobre web.

### Personalidade ATLAS
Mordomo digital com sarcasmo sutil, observações proativas sobre padrões do usuário, humor estrutural e variação de tom conforme contexto. Respostas detalhadas para temas que exigem profundidade, concisas para interações rápidas.

## Stack Básica

**Linguagem**: Python 3.12+ (backend), TypeScript (mobile)
**Framework Principal**: FastAPI (backend), React Native + Expo (mobile)
**Banco de Dados**: ChromaDB (vetorial local), Obsidian vault (filesystem markdown)
**Infraestrutura**: Local / Oracle Cloud VPS (planejado)

### Tecnologias Chave
- **OpenAI GPT-4o-mini**: Classificação de intenção e geração de respostas
- **OpenAI text-embedding-3-small**: Indexação semântica do vault
- **ChromaDB**: Busca vetorial local para notas e hábitos
- **Tavily**: Pesquisa web otimizada para LLMs
- **Google Calendar API**: OAuth2 para CRUD de eventos
- **pydantic-settings**: Configuração tipada via .env
- **python-frontmatter**: Leitura/escrita de notas Obsidian
- **Expo AV**: Gravação e reprodução de áudio no mobile
- **EAS Build**: Build de APK Android para distribuição

## Integrações e Dependências

### Serviços Externos

#### OpenAI API
- **Tipo**: API REST
- **Relação**: Consome para classificação de intenção e geração de respostas
- **Dados trocados**: Mensagens do usuário → classificação JSON + resposta textual
- **Criticidade**: Alta — sem OpenAI o sistema não funciona

#### Google Calendar API
- **Tipo**: API REST com OAuth2
- **Relação**: CRUD de eventos do calendário do usuário
- **Dados trocados**: Título, data/hora, descrição de eventos
- **Criticidade**: Alta para funcionalidades de agenda

#### Tavily API
- **Tipo**: API REST
- **Relação**: Busca web avançada
- **Dados trocados**: Query de busca → contexto textual de resultados
- **Criticidade**: Média — fallback gracioso se indisponível

#### Obsidian Vault
- **Tipo**: Filesystem local (markdown)
- **Relação**: Leitura e escrita direta via pathlib + python-frontmatter
- **Dados trocados**: Notas markdown com frontmatter YAML
- **Criticidade**: Alta — fonte de verdade para notas

### Dependências entre Módulos

#### Mobile → Backend
- **Tipo**: API REST (HTTP)
- **Endpoints consumidos**: POST /chat, POST /voice, GET /health
- **Autenticação**: X-API-Key header
- **Conectividade**: Via ngrok (dev) ou IP direto (produção)

## Arquitetura e Padrões

**Padrão Arquitetural**: Pipeline Architecture com Orchestrator central
**Principais Padrões**:
- **Pipeline**: Input → Classification → Routing → Execution → Response Generation → Output
- **Orchestrator**: Coordenador central síncrono do fluxo completo
- **Tool Registry**: Ferramentas auto-registradas por tipo de intenção
- **Schema-first**: Inputs/outputs tipados com Pydantic
- **Service Wrapper**: APIs externas encapsuladas em services/

### Estrutura do Código
```
atlas/                    # Backend Python
├── main.py              # FastAPI entry point + endpoints
├── config.py            # Settings (pydantic-settings + .env)
├── orchestrator.py      # Coordenador principal do pipeline
├── intent/              # Classificação de intenção (LLM)
├── tools/               # Ações executáveis (registry pattern)
├── persona/             # Geração de resposta com personalidade
└── services/            # Clientes de APIs externas

mobile/                   # App React Native (Expo)
├── src/api/             # Cliente HTTP para backend
├── src/components/      # UI components (MessageBubble, ActionCard, etc.)
├── src/hooks/           # useChat, useAudio
├── src/screens/         # HomeScreen
└── src/theme/           # Cores, espaçamento, fontes

tests/                    # Testes (pytest + pytest-asyncio)
```

## Regras de Negócio Críticas

- Toda mensagem deve ser classificada antes de execução
- Intenção ambígua sempre cai em "chat" (nunca executar ação destrutiva sem certeza)
- ATLAS nunca deleta notas automaticamente
- Notas criadas pelo ATLAS sempre incluem frontmatter YAML
- Busca no vault é priorizada sobre busca web
- Datas de eventos resolvidas via LLM com injeção de data/hora atual
- Respostas nunca incluem links, URLs ou markdown (compatibilidade com TTS)
- API protegida por X-API-Key header

## Informações de Referência

**Repositório**: https://github.com/enzoofs/personal-assistant
**Branch principal**: feat/atlas-mvp
**Tipo**: Monolito (Backend API + Mobile App)
**Testes**: 124 testes passando (pytest)
**Versão**: 0.1.0 (MVP)

---

*Este resumo foi gerado a partir da documentação em `docs/`. Para informações detalhadas, consulte os arquivos específicos na pasta de documentação do repositório.*
