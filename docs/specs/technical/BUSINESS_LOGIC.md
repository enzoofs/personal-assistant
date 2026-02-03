# Lógica de Negócio — ATLAS

## Conceitos de Domínio

### Intenções (Intents)
Toda mensagem do usuário é classificada em exatamente uma intenção. A classificação é feita por LLM e determina qual tool handler executa.

| Intent | Descrição | Handler |
|---|---|---|
| `save_note` | Criar/salvar nota no vault | `tools/obsidian.py` |
| `create_event` | Criar evento no Calendar | `tools/calendar.py` |
| `query_calendar` | Listar eventos | `tools/calendar.py` |
| `delete_event` | Deletar evento | `tools/calendar.py` |
| `log_habit` | Registrar hábito | `tools/habits.py` |
| `search` | Buscar no vault ou web | `tools/search.py` |
| `briefing` | Resumo do dia | `tools/briefing.py` |
| `chat` | Conversa geral (fallback) | Nenhum tool — direto para persona |

### Vault Obsidian
O vault é o armazenamento central de todas as informações do usuário. Estrutura de pastas fixa:

| Pasta | Conteúdo |
|---|---|
| `daily/` | Daily notes (`YYYY-MM-DD.md`) |
| `inbox/` | Notas sem categoria definida |
| `projects/` | Notas sobre projetos |
| `people/` | Notas sobre pessoas |
| `habits/health/` | Sono, exercício, humor |
| `habits/productivity/` | Tarefas, foco |
| `research/` | Resultados de pesquisa salvos |
| `insights/` | Padrões detectados (Fase 2) |
| `templates/` | Templates markdown |

### Hábitos
Dados de saúde e produtividade registrados via texto natural.

| Categoria | Tipo | Formato |
|---|---|---|
| Sono | health | Horas (float) |
| Exercício | health | Sim/não + tipo |
| Humor | health | 1-10 (escala) |
| Tarefas | productivity | Texto livre |
| Custom | definido pelo usuário | Texto livre |

## Regras de Negócio

### Classificação
1. Toda mensagem passa por classificação antes de qualquer ação
2. Uma mensagem tem exatamente uma intenção principal
3. Parâmetros são extraídos na mesma chamada de classificação
4. Se a intenção é ambígua → fallback para `chat` (nunca executar ação sem certeza)
5. Data/hora atual é injetada no prompt para resolução temporal ("amanhã" → data correta)

### Vault — Escrita
1. ATLAS **só adiciona e atualiza** — nunca deleta notas automaticamente
2. Toda nota criada deve ter frontmatter YAML com: `date`, `tags`, `category`
3. Notas sem categoria clara → `inbox/`
4. Daily notes: formato `YYYY-MM-DD.md` em `daily/`
5. Nomes de arquivo: `kebab-case.md` (máximo 50 caracteres no slug)

### Vault — Indexação
1. ChromaDB é índice reconstruível — vault (markdown) é o source of truth
2. Indexação incremental via hash SHA256 do conteúdo
3. Reindexação completa no startup do servidor
4. IDs no ChromaDB = hash SHA256 do conteúdo do arquivo

### Google Calendar
1. Parsing de data/hora feito pelo LLM (linguagem natural → ISO 8601)
2. Criação requer no mínimo: título + data/hora
3. Duração padrão: 1 hora (se não especificada)
4. Timezone configurada em `.env` (`TIMEZONE`)
5. Deleção requer confirmação explícita do usuário
6. Token OAuth auto-refresh; primeiro uso requer navegador

### Pesquisa
1. Busca no vault tem prioridade sobre busca web
2. Se o vault tem informação relevante, aparece primeiro
3. Busca web via Tavily retorna texto (não HTML/links)
4. Resultados são sintetizados em resposta natural
5. Se Tavily API key não configurada → busca web silenciosamente ignorada

### Personalidade
1. Personalidade é fixa — não configurável pelo usuário (MVP)
2. System prompt consistente em todas as interações
3. Tom: sarcástico, inteligente, direto, nunca ofensivo
4. Pode fazer observações não solicitadas baseadas em contexto
5. Referencia dados anteriores do usuário quando relevante
6. Respostas sem markdown, URLs ou emojis (compatível com TTS)
7. Temperatura: 0.8 (resposta criativa)

### Segurança
1. API protegida por header `X-API-Key`
2. Credenciais Google Calendar em `token.json` (local, não commitado)
3. API keys via variáveis de ambiente (`.env`)
4. Vault e ChromaDB não expostos externamente
5. `.env`, `token.json`, `credentials.json` no `.gitignore`
