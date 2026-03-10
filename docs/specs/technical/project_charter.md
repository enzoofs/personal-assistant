# Carta do Projeto — ATLAS

## Visão

ATLAS é um assistente pessoal inteligente estilo Jarvis que centraliza a vida digital do usuário: notas, agenda, hábitos, email, compras e pesquisas. Interação via linguagem natural (texto e voz), com personalidade sarcástica e observações proativas. Projeto pessoal, single-user.

## Problema que Resolve

Fragmentação de informações pessoais entre múltiplas ferramentas (calendário, apps de notas, planilhas de hábitos, email, listas de compras, navegador). O ATLAS unifica tudo num único ponto de entrada conversacional, usando o vault Obsidian como "segundo cérebro" persistente.

## Critérios de Sucesso (MVP) ✓ Concluído

1. ✓ Processar mensagens em linguagem natural e executar ações corretas (notas, eventos, hábitos, pesquisa, briefing)
2. ✓ Manter vault Obsidian organizado com frontmatter YAML e categorização automática
3. ✓ CRUD funcional no Google Calendar via texto natural
4. ✓ Busca semântica no vault + busca web sintetizada
5. ✓ Briefing diário agregando Calendar + vault + hábitos
6. ✓ Personalidade ATLAS consistente em todas as respostas
7. ✓ App mobile funcional com chat e voz

## Escopo

### Fase 1 — MVP ✓ Concluído
- Classificação de intenção (8 intents iniciais)
- Gestão de notas no Obsidian vault
- Google Calendar CRUD
- Tracking de hábitos
- Pesquisa inteligente (vault + web)
- Briefing diário
- API REST (`POST /chat`, `POST /voice`, `GET /health`)
- App mobile React Native com chat e voz

### Fase 1.5 — Expansão ✓ Concluído
- **16 intents** no total (dobro do MVP)
- **Áudio bidirecional** (Whisper + TTS multi-tier)
- **Streaming SSE** (`POST /chat/stream`) para menor latência percebida
- **Lista de compras** (CRUD completo via linguagem natural)
- **Email Gmail** (leitura, envio com confirmação, triagem automática)
- **Voice capture** (transcrição para notas estruturadas)
- **Fallbacks gratuitos** (Groq LLM, Edge TTS, DuckDuckGo)
- **Configuração dinâmica** de modo de resposta (text/audio/audio_premium)

### Fase 2 (em desenvolvimento)
- App Android polido com dashboard
- Reconhecimento de padrões em dados acumulados
- Notificações proativas com personalidade

### Fase 3 (futuro)
- Telegram como canal secundário
- APIs externas (clima, notícias)
- Google Fit / wearables

### Fora do Escopo
- Multi-user / multi-tenancy
- Interface web
- Edição ou deleção automática de notas sem confirmação
- Configuração de personalidade pelo usuário

## Restrições Técnicas

| Restrição | Motivo |
|---|---|
| Python 3.12+ | Ecossistema AI maduro, async nativo |
| GPT-4o-mini + Groq fallback | Custo-eficiente com resiliência gratuita |
| ChromaDB local (não Pinecone/Weaviate) | Zero custo, sem infra extra, reconstruível |
| Markdown no filesystem (não SQL) | Compatível com Obsidian, portável, legível |
| SQLite para dados transientes | Shopping list, sessões, memórias (não notas) |
| API key simples (não OAuth p/ API) | Projeto single-user, complexidade desnecessária |

## Stakeholders

| Stakeholder | Papel |
|---|---|
| Enzo (owner) | Desenvolvedor único, usuário final |
| ATLAS (sistema) | Assistente pessoal com personalidade própria |

## Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Latência 2 chamadas LLM por request | ✓ Streaming SSE implementado (TTFB ~500ms) |
| Vault cresce e ChromaDB fica lento | Indexação incremental via hash SHA256 |
| Google Calendar OAuth expira | Auto-refresh de token implementado |
| Classificação errada de intenção | Fallback para `chat` (nunca executa ação destrutiva sem certeza) |
| Custos OpenAI crescem | ✓ Fallbacks gratuitos: Groq, Edge TTS, DuckDuckGo |
| Serviço externo indisponível | ✓ Sistema de cascata com fallbacks em todos os serviços |
