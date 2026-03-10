# Estratégia do Produto — ATLAS

## Visão

Um assistente pessoal com personalidade própria que centraliza vida digital (notas, agenda, hábitos, email, compras, pesquisa) num único ponto de entrada conversacional, usando o vault Obsidian como memória persistente.

## Proposta de Valor

**Para:** Enzo (único usuário)
**Que precisa de:** Visão consolidada do dia e captura sem fricção
**O ATLAS é:** Um assistente sarcástico que unifica Calendar + Obsidian + Email + Shopping + hábitos + pesquisa
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
Melhor fazer poucas coisas bem do que muitas coisas mal. Os 16 intents atuais cobrem 95% do uso diário.

### 5. Proatividade com Limites
ATLAS pode observar padrões e comentar ("Faz 3 dias que não treina"), mas nunca toma ações destrutivas sem confirmação.

### 6. Resiliência sem Custo
Fallbacks gratuitos garantem funcionamento mesmo com APIs pagas indisponíveis ou custos elevados.

## Roadmap Estratégico

| Fase | Status | Foco | Valor Principal |
|---|---|---|---|
| MVP (Fase 1) | ✓ Concluído | Funcionalidade básica | Captura + briefing + hábitos funcionando |
| Fase 1.5 | ✓ Concluído | Expansão | Áudio, email, shopping, streaming, fallbacks |
| Fase 2 | Em dev | Experiência | Dashboard, padrões, notificações proativas |
| Fase 3 | Futuro | Expansão | Telegram, APIs externas, wearables |

## Trade-offs Aceitos

| Escolha | Alternativa | Motivo |
|---|---|---|
| GPT-4o-mini + Groq fallback | GPT-4o (melhor, caro) | Custo para uso diário + resiliência gratuita |
| 2 chamadas LLM + streaming | Function calling (elegante) | Simplicidade + UX melhorada com SSE |
| API key simples | OAuth2 completo | Single-user, não precisa |
| Markdown no filesystem | Banco SQL | Compatível com Obsidian |
| ElevenLabs + Edge TTS fallback | Só OpenAI TTS | Qualidade premium com fallback gratuito |
| Tavily + DuckDuckGo fallback | Só Tavily | Resiliência sem custo adicional |

## Métricas de Sucesso (pessoais)

| Métrica | Alvo | Status |
|---|---|---|
| Uso diário | Briefing todo dia | Funcional |
| Captura de notas | Via voz sem fricção | Funcional |
| Latência percebida | < 1s para início de resposta | ✓ Streaming SSE |
| Custo mensal | < $5 | ✓ Fallbacks gratuitos disponíveis |
| Disponibilidade | 99% (projeto pessoal) | Deploy Oracle Cloud |
