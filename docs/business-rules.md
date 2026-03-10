# Regras de Negócio

## Classificação de Intenção

- Toda mensagem passa por classificação antes de qualquer ação
- Se a intenção é ambígua, fallback para `chat` (nunca executar ação destrutiva sem certeza)
- Uma mensagem pode ter apenas uma intenção principal
- Parâmetros são extraídos na mesma chamada de classificação

## Vault Obsidian

### Escrita
- ATLAS **só adiciona e atualiza** — nunca deleta notas automaticamente
- Toda nota criada pelo ATLAS deve ter frontmatter YAML com: `date`, `tags`, `category`
- Notas sem categoria clara vão para `inbox/`
- Daily notes usam formato `YYYY-MM-DD.md` em `daily/`

### Categorização
- Notas sobre pessoas → `people/`
- Notas sobre projetos → `projects/`
- Resultados de pesquisa → `research/`
- Registros de hábitos → `habits/health/` ou `habits/productivity/`
- Tudo mais → `inbox/`

### Indexação
- ChromaDB é índice reconstruível — o vault (markdown) é o source of truth
- Indexação incremental via hash SHA256 do conteúdo
- Reindexação completa no startup do servidor

## Google Calendar

- Parsing de data/hora feito pelo LLM (linguagem natural → ISO 8601)
- Criação de evento requer no mínimo: título + data/hora
- Timezone do usuário configurada no `.env`
- Deletar evento requer confirmação explícita do usuário

## Hábitos

- Dados de hábitos são registrados no daily note + arquivo dedicado
- Categorias fixas: sono (horas), exercício (tipo), humor (1-10)
- Hábitos custom podem ser criados pelo usuário
- Não há validação rígida de formato — o LLM parseia texto natural

## Pesquisa

- Busca no vault tem prioridade sobre busca web
- Se o vault tem informação relevante, ela aparece primeiro na resposta
- Busca web é feita via Tavily `get_search_context()` — retorna texto, não HTML
- Resultados são sintetizados em resposta natural, nunca lista de links

## Personalidade ATLAS

- Personalidade é fixa — não configurável pelo usuário (MVP)
- System prompt é consistente em todas as interações
- ATLAS pode fazer observações não solicitadas baseadas em contexto
- Tom: sarcástico, inteligente, direto, nunca ofensivo
- Referencia dados anteriores do usuário quando relevante

## Segurança

- API protegida por API key simples (header `X-API-Key`)
- Credenciais Google Calendar salvas localmente (`token.json`)
- API keys de terceiros via variáveis de ambiente (`.env`)
- Vault e ChromaDB não expostos externamente
