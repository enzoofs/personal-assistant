# ATLAS — Contexto Técnico

## Perfil de Contexto do Projeto

| Campo | Valor |
|---|---|
| **Nome** | ATLAS (Assistente Pessoal Inteligente) |
| **Stack** | Python 3.12+ / FastAPI / GPT-4o-mini / ChromaDB / React Native (Expo) |
| **Equipe** | Solo developer |
| **Fase** | Fase 1.5 — concluída (Fase 2 em desenvolvimento) |
| **Deploy alvo** | Oracle Cloud VPS |
| **Repo** | https://github.com/enzoofs/personal-assistant |

## Camada 1: Contexto Central do Projeto

- [Carta do Projeto](project_charter.md) — Visão, escopo, critérios de sucesso e restrições
- [Registros de Decisões Arquiteturais](adr/) — ADRs documentando escolhas técnicas
  - [ADR-001: Pipeline com 2 chamadas LLM](adr/001-two-llm-calls.md)
  - [ADR-002: Markdown como source of truth](adr/002-markdown-source-of-truth.md)
  - [ADR-003: ChromaDB como índice reconstruível](adr/003-chromadb-reconstructible-index.md)
  - [ADR-004: GPT-4o-mini como LLM principal](adr/004-gpt4o-mini.md)
  - [ADR-005: Oracle Cloud VPS para deploy](adr/005-oracle-cloud-deploy.md)
  - [ADR-006: Sistema de Fallbacks Gratuitos](adr/006-free-fallbacks.md)
  - [ADR-007: Antecipação de Streaming SSE](adr/007-streaming-antecipado.md)

## Camada 2: Arquivos de Contexto Otimizados para IA

- [Guia de Desenvolvimento com IA](CLAUDE.meta.md) — Padrões de código, convenções, pegadinhas
- [Guia de Navegação da Base de Código](CODEBASE_GUIDE.md) — Estrutura, arquivos chave, fluxo de dados

## Camada 3: Contexto Específico do Domínio

- [Documentação da Lógica de Negócio](BUSINESS_LOGIC.md) — Regras de domínio, intents, vault, hábitos
- [Especificações da API](API_SPECIFICATION.md) — Endpoints, contratos, autenticação

## Camada 4: Contexto do Fluxo de Desenvolvimento

- [Guia de Contribuição e Desenvolvimento](CONTRIBUTING.md) — Setup, testes, deploy
- [Guia de Solução de Problemas](TROUBLESHOOTING.md) — Problemas comuns e debugging
- [Desafios Arquiteturais](ARCHITECTURE_CHALLENGES.md) — Dívidas técnicas e melhorias planejadas
