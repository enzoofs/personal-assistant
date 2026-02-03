# Métricas do Produto — ATLAS

## KPIs Primários

### 1. Uso Diário
**Definição:** ATLAS é usado pelo menos 1x por dia
**Meta:** 7/7 dias por semana após estabilização do MVP
**Por que importa:** Métrica #1 de sucesso declarada pelo usuário

### 2. Qualidade das Respostas
**Definição:** Respostas são úteis E divertidas (personalidade funciona)
**Medição:** Percepção subjetiva do usuário
**Por que importa:** Métrica #2 de sucesso declarada pelo usuário

## KPIs Secundários

### 3. Acurácia de Classificação
**Definição:** % de mensagens classificadas na intenção correta
**Meta:** > 90% para intents claras
**Medição:** Observação durante uso (logs de intent vs. ação esperada)

### 4. Cobertura de Hábitos
**Definição:** Hábitos registrados diariamente (sono, exercício, humor)
**Meta:** Registro consistente 5+/7 dias por semana
**Por que importa:** Indica que a captura sem fricção funciona

### 5. Utilidade do Briefing
**Definição:** Briefing matinal inclui informação acionável
**Meta:** Substitui checagem manual do Calendar + vault
**Por que importa:** É o workflow principal e momento de verdade #1

## Métricas Técnicas

| Métrica | Meta | Status |
|---|---|---|
| Latência por request | < 4s (MVP), < 2s (Fase 2) | ~2-4s |
| Testes passando | 100% | 152+ testes escritos |
| Uptime do backend | > 99% (quando deployado) | Em desenvolvimento |
| Custo mensal OpenAI | < $5/mês | Estimado ~$1-2/mês com GPT-4o-mini |

## Anti-Métricas

Coisas que NÃO devem acontecer:
- Classificação errada que executa ação destrutiva
- ATLAS deletar notas automaticamente
- Respostas genéricas sem personalidade
- Necessidade de abrir outro app para completar ação iniciada no ATLAS
