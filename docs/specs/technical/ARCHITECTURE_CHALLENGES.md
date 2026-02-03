# Desafios Arquiteturais — ATLAS

## Dívidas Técnicas Atuais

### 1. Módulos vault/ não implementados (CRÍTICO)

**Situação:** `vault/manager.py`, `vault/indexer.py` e `vault/templates.py` são referenciados em imports, testes e no startup do FastAPI, mas não existem. Os testes foram escritos antecipadamente (TDD), mas a implementação está pendente.

**Impacto:** O backend não consegue completar o startup corretamente. Tools que dependem do vault (obsidian, briefing, search, habits) não funcionam end-to-end.

**Ação necessária:** Implementar os 3 módulos seguindo os contratos definidos nos testes existentes (`test_vault_manager.py`, `test_templates.py`).

### 2. CI/CD inexistente

**Situação:** Sem GitHub Actions, sem pipeline de testes automatizados, sem deploy automático.

**Impacto:** Testes rodam apenas manualmente. Deploy é manual. Sem garantia de que o código no repo está sempre funcional.

**Ação necessária:** Configurar GitHub Actions com: pytest, lint (ruff/flake8), type check (mypy), deploy automático para Oracle Cloud VPS.

## Desafios de Design

### 3. Sincronização Vault ↔ ChromaDB

**Problema:** Como manter o índice ChromaDB sincronizado com o vault de forma eficiente? A reindexação completa no startup funciona para vaults pequenos, mas não escala.

**Abordagens possíveis:**
- **Filesystem watcher:** Detectar mudanças em tempo real (inotify/watchdog)
- **Hash incremental:** Já parcialmente implementado (SHA256 por arquivo), mas precisa comparar hashes antes de reindexar
- **Lazy indexing:** Indexar sob demanda quando uma busca é feita
- **Background task:** Reindexação periódica em background (asyncio task)

**Trade-off:** Complexidade vs. freshness dos dados. Para uso pessoal, reindexação no startup + incremental pode ser suficiente.

### 4. Latência do Pipeline (2 chamadas LLM)

**Problema:** Cada request faz 2 chamadas sequenciais ao OpenAI (~1-2s cada), resultando em ~2-4s de latência total. Para uso conversacional, especialmente com voz, isso é perceptível.

**Abordagens possíveis:**
- **Streaming:** SSE para enviar resposta incrementalmente (planejado Fase 2)
- **Function calling:** Uma única chamada com tools/functions (elimina classificação separada)
- **Cache de classificação:** Se a mesma intenção for detectada, reutilizar
- **Modelo menor para classificação:** Usar modelo mais leve para classify, mais pesado para response
- **Classificação local:** Modelo leve local (distilbert fine-tuned) para classificação

**Trade-off:** A simplicidade de 2 chamadas separadas facilita debugging e iteração. Otimizar quando se tornar gargalo real.

### 5. Deploy Oracle Cloud — Vault Sync

**Problema:** Com deploy na Oracle Cloud, o vault Obsidian não fica mais na mesma máquina. O Obsidian roda no desktop/mobile do usuário, mas o ATLAS precisa acessar o vault no servidor.

**Abordagens possíveis:**
- **Git sync:** Vault como repo git, sync via push/pull
- **Rsync periódico:** Cron job sincronizando vault local → VPS
- **Obsidian Sync:** Plugin oficial da Obsidian
- **ATLAS gerencia sozinho:** Vault no servidor, Obsidian acessa via remote vault
- **API de sync:** Endpoint no ATLAS para receber notas atualizadas

**Trade-off:** Qualquer solução adiciona complexidade. Para o MVP, manter vault apenas no servidor e acessar Obsidian via remote pode ser o mais simples.

### 6. OAuth em Servidor Headless

**Problema:** Google Calendar OAuth requer navegador para consentimento no primeiro uso. Em VPS sem GUI, isso não funciona diretamente.

**Soluções:**
- Gerar `token.json` em máquina local com navegador, copiar para o servidor
- Usar fluxo OAuth "out-of-band" (deprecated pelo Google)
- Implementar endpoint no ATLAS que redireciona para OAuth e captura o callback
- Usar Service Account (não suporta calendários pessoais)

## Melhorias Futuras Identificadas

| Melhoria | Prioridade | Fase |
|---|---|---|
| Implementar vault/ modules | Crítica | MVP |
| CI/CD (GitHub Actions) | Alta | MVP |
| Streaming (SSE) | Alta | Fase 2 |
| Function calling (1 chamada LLM) | Média | Fase 2 |
| Filesystem watcher para vault | Média | Fase 2 |
| Type checking (mypy) | Média | MVP |
| Linting (ruff) | Média | MVP |
| Rate limiting na API | Baixa | Fase 2 |
| Monitoramento/observabilidade | Baixa | Fase 2 |
