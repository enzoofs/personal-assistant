# ADR-001: Pipeline com 2 Chamadas LLM Separadas

## Status
Aceito

## Contexto
O ATLAS precisa classificar a intenção do usuário e gerar uma resposta com personalidade. As alternativas eram: (1) uma única chamada com function calling, (2) duas chamadas separadas (classificação + resposta), (3) uma chamada com structured output.

## Decisão
Usar 2 chamadas LLM separadas: uma para classificação de intenção (retorna JSON) e outra para geração de resposta com personalidade (usa contexto da ação executada).

## Motivo
Simplicidade no MVP. Duas chamadas separadas são mais fáceis de implementar, debugar e entender. Cada chamada tem um prompt focado e um formato de saída previsível.

## Consequências

### Positivas
- Debugging claro: cada etapa pode ser inspecionada isoladamente
- Prompts menores e mais focados
- Resposta com personalidade tem acesso ao resultado da ação executada
- Fácil de substituir modelos por etapa no futuro

### Negativas
- Latência maior (~2x tempo de uma única chamada)
- Custo dobrado de tokens por request
- Pode ser substituído por function calling na Fase 2

## Alternativas Consideradas
- **Function calling**: Mais elegante, mas mais complexo para o MVP
- **Structured output único**: Não permite personalidade contextual à ação executada
