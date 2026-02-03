# Carta do Projeto — ATLAS

## Visão

ATLAS é um assistente pessoal inteligente estilo Jarvis que centraliza a vida digital do usuário: notas, agenda, hábitos e pesquisas. Interação via linguagem natural (texto e voz), com personalidade sarcástica e observações proativas. Projeto pessoal, single-user.

## Problema que Resolve

Fragmentação de informações pessoais entre múltiplas ferramentas (calendário, apps de notas, planilhas de hábitos, navegador). O ATLAS unifica tudo num único ponto de entrada conversacional, usando o vault Obsidian como "segundo cérebro" persistente.

## Critérios de Sucesso (MVP)

1. Processar mensagens em linguagem natural e executar ações corretas (notas, eventos, hábitos, pesquisa, briefing)
2. Manter vault Obsidian organizado com frontmatter YAML e categorização automática
3. CRUD funcional no Google Calendar via texto natural
4. Busca semântica no vault + busca web sintetizada
5. Briefing diário agregando Calendar + vault + hábitos
6. Personalidade ATLAS consistente em todas as respostas
7. App mobile funcional com chat e voz

## Escopo

### Fase 1 — MVP (atual)
- Classificação de intenção (8 intents)
- Gestão de notas no Obsidian vault
- Google Calendar CRUD
- Tracking de hábitos
- Pesquisa inteligente (vault + web)
- Briefing diário
- API REST (`POST /chat`, `POST /voice`, `GET /health`)
- App mobile React Native com chat e voz

### Fase 2 (planejado)
- Áudio bidirecional (Whisper + TTS)
- App Android polido com dashboard
- Reconhecimento de padrões em dados acumulados
- Notificações proativas

### Fase 3 (futuro)
- Telegram como canal secundário
- APIs externas (clima, notícias)
- Google Fit / wearables

### Fora do Escopo
- Multi-user / multi-tenancy
- Interface web
- Edição ou deleção automática de notas
- Configuração de personalidade pelo usuário (MVP)

## Restrições Técnicas

| Restrição | Motivo |
|---|---|
| Python 3.12+ | Ecossistema AI maduro, async nativo |
| GPT-4o-mini (não GPT-4) | Custo-eficiente (~$0.15/1M tokens), suficiente para classificação |
| ChromaDB local (não Pinecone/Weaviate) | Zero custo, sem infra extra, reconstruível |
| Markdown no filesystem (não SQL) | Compatível com Obsidian, portável, legível |
| Sem streaming no MVP | Simplicidade; planejado para Fase 2 |
| API key simples (não OAuth) | Projeto single-user, complexidade desnecessária |

## Stakeholders

| Stakeholder | Papel |
|---|---|
| Enzo (owner) | Desenvolvedor único, usuário final |
| ATLAS (sistema) | Assistente pessoal com personalidade própria |

## Riscos

| Risco | Mitigação |
|---|---|
| Latência 2 chamadas LLM por request | Aceito no MVP; considerar function calling ou streaming na Fase 2 |
| Vault cresce e ChromaDB fica lento | Indexação incremental via hash SHA256 |
| Google Calendar OAuth expira | Auto-refresh de token implementado |
| Classificação errada de intenção | Fallback para `chat` (nunca executa ação destrutiva sem certeza) |
| Custos OpenAI crescem | GPT-4o-mini é barato; monitorar uso |
