# Estratégia do Produto — ATLAS

## Visão

Um assistente pessoal com personalidade própria que centraliza vida digital (notas, agenda, hábitos, pesquisa) num único ponto de entrada conversacional, usando o vault Obsidian como memória persistente.

## Proposta de Valor

**Para:** Enzo (único usuário)
**Que precisa de:** Visão consolidada do dia e captura sem fricção
**O ATLAS é:** Um assistente sarcástico que unifica Calendar + Obsidian + hábitos + pesquisa
**Diferente de:** Assistentes genéricos (Siri, Google) que não têm contexto pessoal nem personalidade
**Porque:** Tem acesso ao vault pessoal, entende contexto, e a personalidade torna o uso divertido

## Princípios de Design

### 1. Personalidade Primeiro
A personalidade sarcástica não é decoração — é o diferencial que motiva o uso diário. Sem ela, seria mais um app de produtividade genérico.

### 2. Captura Zero-Fricção
Qualquer informação deve ser capturável com uma mensagem em linguagem natural. Sem menus, sem formulários, sem passos extras.

### 3. Vault como Fonte de Verdade
O Obsidian vault é o "cérebro" do ATLAS. Tudo que importa vive como markdown. ChromaDB, Google Calendar, etc. são interfaces — não são a fonte de verdade das notas.

### 4. Simplicidade sobre Completude
Melhor fazer 7 coisas bem do que 20 coisas mal. As 8 intenções do MVP cobrem 90% do uso diário.

### 5. Proatividade com Limites
ATLAS pode observar padrões e comentar ("Faz 3 dias que não treina"), mas nunca toma ações destrutivas sem confirmação.

## Roadmap Estratégico

| Fase | Foco | Valor Principal |
|---|---|---|
| MVP (Fase 1) | Funcionalidade básica | Captura + briefing + hábitos funcionando |
| Fase 2 | Experiência | Streaming, voz bidirecional, padrões, notificações |
| Fase 3 | Expansão | Telegram, APIs externas, wearables |

## Trade-offs Aceitos

| Escolha | Alternativa | Motivo |
|---|---|---|
| GPT-4o-mini (barato, bom o suficiente) | GPT-4o (melhor, caro) | Custo para uso pessoal diário |
| 2 chamadas LLM (simples) | Function calling (elegante) | Simplicidade no MVP |
| API key simples | OAuth2 completo | Single-user, não precisa |
| Sem streaming (MVP) | SSE desde o início | Fase 2, reduz complexidade |
| Markdown no filesystem | Banco SQL | Compatível com Obsidian |
