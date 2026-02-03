# ADR-004: GPT-4o-mini como LLM Principal

## Status
Aceito

## Contexto
O ATLAS precisa de um LLM para classificação de intenção e geração de respostas. Alternativas: GPT-4o, GPT-4o-mini, Claude, Llama local, Mistral.

## Decisão
Usar GPT-4o-mini para todas as chamadas LLM (classificação + resposta). Modelo configurável via `OPENAI_MODEL` no .env.

## Motivo
Custo-eficiente (~$0.15/1M tokens input) com qualidade suficiente para classificação e geração de texto. Para um projeto pessoal com uso diário, o custo mensal fica negligível.

## Consequências

### Positivas
- Custo muito baixo para uso pessoal
- Latência menor que GPT-4o
- Qualidade suficiente para classificação de 8 intents
- SDK OpenAI maduro e bem documentado

### Negativas
- Dependência de API externa (sem fallback offline)
- Menos capaz que GPT-4o em raciocínio complexo
- Vendor lock-in com OpenAI (mitigado: modelo configurável)
