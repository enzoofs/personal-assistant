# Arquitetura da Fase 2 — ATLAS

## Visão Geral

A Fase 2 transforma o ATLAS de um assistente reativo em um assistente **proativo**, capaz de:
- Apresentar informações consolidadas visualmente (Dashboard)
- Identificar padrões nos dados do usuário (Motor de Padrões)
- Notificar proativamente sobre insights relevantes (Push Notifications)

```
┌─────────────────────────────────────────────────────────────────┐
│                         FASE 2 - ATLAS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │  Dashboard  │◄───│   Backend   │◄───│  Motor de Padrões   │ │
│  │   Mobile    │    │    API      │    │   (Background)      │ │
│  └──────┬──────┘    └──────┬──────┘    └──────────┬──────────┘ │
│         │                  │                      │             │
│         │                  │                      │             │
│         ▼                  ▼                      ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │    Push     │◄───│  Notif.     │◄───│   Triggers &        │ │
│  │Notifications│    │  Service    │    │   Thresholds        │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Dashboard Mobile

### 1.1 Estado Atual

O `DashboardScreen.tsx` já existe com 6 seções:
- Alertas de Email
- Agenda do Dia
- Hábitos de Hoje
- Estatísticas do Vault
- Emails Não Lidos
- Memórias Recentes

**Problemas identificados:**
- Layout não otimizado para visualização rápida
- Sem ações rápidas (tudo requer ir ao chat)
- Refresh manual ou polling de 60s
- Sem persistência local (flicker ao recarregar)

### 1.2 Arquitetura Proposta

#### Estrutura de Componentes

```
mobile/src/
├── components/
│   └── dashboard/
│       ├── WidgetCard.tsx        # Container base para widgets
│       ├── AgendaWidget.tsx      # Eventos do dia com ações
│       ├── HabitsWidget.tsx      # Hábitos com quick-log
│       ├── VaultWidget.tsx       # Stats + notas recentes
│       ├── AlertsWidget.tsx      # Alertas com dismiss
│       ├── EmailWidget.tsx       # Preview de emails
│       └── InsightsWidget.tsx    # NEW: Padrões detectados
├── context/
│   └── DashboardContext.tsx      # Estado global do dashboard
└── hooks/
    └── useDashboard.ts           # Refatorado para usar Context
```

#### Layout Visual

```
┌────────────────────────────────┐
│  ATLAS Dashboard               │
│  Segunda, 3 de Fevereiro       │
├────────────────────────────────┤
│ ┌────────────────────────────┐ │
│ │ 💡 INSIGHTS                │ │  ← NEW: Padrões detectados
│ │ "Faz 3 dias sem treino"    │ │
│ │ [Registrar] [Ignorar]      │ │
│ └────────────────────────────┘ │
│                                │
│ ┌────────────────────────────┐ │
│ │ 📅 HOJE                    │ │
│ │ • 10:00 Reunião standup    │ │
│ │ • 14:00 Dentista           │ │
│ │ + Adicionar evento         │ │
│ └────────────────────────────┘ │
│                                │
│ ┌───────────┐ ┌───────────┐   │
│ │ 😴 Sono   │ │ 🏃 Treino │   │  ← Grid 2x2 para hábitos
│ │ 7.5h     │ │ ❌        │   │
│ │ [Editar]  │ │ [Logar]   │   │
│ └───────────┘ └───────────┘   │
│                                │
│ ┌────────────────────────────┐ │
│ │ 📧 EMAILS (3 não lidos)   │ │
│ │ • João: Sobre o projeto   │ │
│ │ • Maria: Reunião amanhã   │ │
│ └────────────────────────────┘ │
│                                │
│ ┌────────────────────────────┐ │
│ │ 📝 VAULT                   │ │
│ │ 142 notas • 3 hoje        │ │
│ │ Órfãs: 12                 │ │
│ └────────────────────────────┘ │
└────────────────────────────────┘
```

#### DashboardContext

```typescript
// mobile/src/context/DashboardContext.tsx

interface DashboardState {
  data: DashboardData | null
  insights: Insight[]          // NEW
  loading: boolean
  lastUpdated: Date | null
  error: string | null
}

interface DashboardContextType extends DashboardState {
  refresh: () => Promise<void>
  logHabit: (type: string, value: any) => Promise<void>
  dismissInsight: (id: string) => Promise<void>
  dismissAlert: (id: string) => Promise<void>
}

// Persiste em AsyncStorage para evitar flicker
// Sync com backend via polling (60s) ou push notification trigger
```

#### Ações Rápidas

| Widget | Ação | Implementação |
|--------|------|---------------|
| Agenda | Adicionar evento | Modal → `POST /chat` com intent `create_event` |
| Hábitos | Quick-log | `POST /chat` com intent `log_habit` |
| Insights | Registrar/Ignorar | Ação customizada ou dismiss |
| Alerts | Dismiss | `DELETE /email-alerts` |

### 1.3 Arquivos a Modificar/Criar

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `mobile/src/context/DashboardContext.tsx` | Criar | Estado global + persistência |
| `mobile/src/components/dashboard/*.tsx` | Criar | Widgets componentizados |
| `mobile/src/screens/DashboardScreen.tsx` | Refatorar | Usar novos widgets + Context |
| `mobile/src/hooks/useDashboard.ts` | Refatorar | Usar Context ao invés de estado local |
| `atlas/api/dashboard.py` | Modificar | Adicionar `insights` no response |

---

## 2. Sistema de Notificações

### 2.1 Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE NOTIFICAÇÕES                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BACKEND (FastAPI)                 MOBILE (Expo)                │
│  ┌─────────────────────┐          ┌─────────────────────┐      │
│  │ NotificationService │          │ expo-notifications  │      │
│  │                     │          │                     │      │
│  │ • schedule()        │─────────▶│ • Local notifs      │      │
│  │ • send_push()       │          │ • Push token        │      │
│  │ • cancel()          │          │ • Handlers          │      │
│  └─────────────────────┘          └─────────────────────┘      │
│           │                                │                    │
│           ▼                                ▼                    │
│  ┌─────────────────────┐          ┌─────────────────────┐      │
│  │ Expo Push Server    │◀─────────│ Push Token          │      │
│  │ (HTTP API)          │          │ Registration        │      │
│  └─────────────────────┘          └─────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Tipos de Notificação

| Tipo | Trigger | Exemplo | Prioridade |
|------|---------|---------|------------|
| **Briefing Matinal** | Agendado (8:00) | "Bom dia! Você tem 3 reuniões hoje..." | Normal |
| **Hábito Quebrado** | Padrão detectado | "Faz 3 dias que você não treina. Vai enferrujar." | Normal |
| **Deadline Próximo** | 24h antes | "Amanhã: Entregar relatório" | Alta |
| **Email Importante** | Triagem detecta | "Email de [Boss] sobre [Projeto]" | Alta |
| **Insight Diário** | Agendado (20:00) | "Você dormiu melhor nos dias que treinou." | Baixa |

### 2.3 Implementação Mobile

```typescript
// mobile/src/services/notifications.ts

import * as Notifications from 'expo-notifications'
import { Platform } from 'react-native'

export async function registerForPushNotifications(): Promise<string | null> {
  const { status } = await Notifications.requestPermissionsAsync()
  if (status !== 'granted') return null

  const token = await Notifications.getExpoPushTokenAsync({
    projectId: 'atlas-personal-assistant'
  })

  // Enviar token para o backend
  await api.registerPushToken(token.data)

  return token.data
}

export function setupNotificationHandlers() {
  // Notificação recebida com app aberto
  Notifications.addNotificationReceivedListener(notification => {
    // Atualizar badge, refresh dashboard, etc.
  })

  // Usuário clicou na notificação
  Notifications.addNotificationResponseReceivedListener(response => {
    const { type, data } = response.notification.request.content.data

    switch (type) {
      case 'briefing':
        navigation.navigate('Chat', { autoSend: 'briefing' })
        break
      case 'habit':
        navigation.navigate('Dashboard')
        break
      case 'email':
        navigation.navigate('Chat', { autoSend: `mostra email de ${data.from}` })
        break
    }
  })
}
```

### 2.4 Implementação Backend

```python
# atlas/services/notifications.py

import httpx
from atlas.config import settings

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

async def send_push_notification(
    push_token: str,
    title: str,
    body: str,
    data: dict = None,
    priority: str = "default"  # default | high
) -> bool:
    """Envia push notification via Expo Push Server."""

    message = {
        "to": push_token,
        "title": title,
        "body": body,
        "data": data or {},
        "priority": priority,
        "sound": "default" if priority == "high" else None,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            EXPO_PUSH_URL,
            json=message,
            headers={"Content-Type": "application/json"}
        )
        return response.status_code == 200
```

### 2.5 Personalidade nas Notificações

As notificações mantêm o tom sarcástico do ATLAS:

| Evento | Notificação Genérica | Notificação ATLAS |
|--------|---------------------|-------------------|
| 3 dias sem treino | "Você não treinou recentemente" | "Faz 3 dias que não treina. Vai enferrujar." |
| Sono ruim | "Qualidade de sono baixa" | "5h de sono? Tá querendo virar zumbi?" |
| Deadline amanhã | "Lembrete: Relatório" | "O relatório é amanhã. Não deixa pra última hora de novo." |
| Email importante | "Novo email de João" | "João mandou email. Parece importante. Ou não." |

### 2.6 Arquivos a Criar

| Arquivo | Descrição |
|---------|-----------|
| `mobile/src/services/notifications.ts` | Setup e handlers de notificações |
| `mobile/src/context/NotificationContext.tsx` | Estado de permissões e token |
| `atlas/services/notifications.py` | Envio via Expo Push |
| `atlas/api/notifications.py` | Endpoints: register token, preferences |
| `atlas/models/notifications.py` | Schema: push_tokens, preferences |

---

## 3. Motor de Padrões

### 3.1 Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                     MOTOR DE PADRÕES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    SCHEDULER (APScheduler)               │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ Daily 08:00  │  │ Daily 20:00  │  │ Every 30min  │  │   │
│  │  │ Briefing     │  │ End-of-day   │  │ Email triage │  │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │   │
│  │         │                 │                 │           │   │
│  └─────────┼─────────────────┼─────────────────┼───────────┘   │
│            │                 │                 │                │
│            ▼                 ▼                 ▼                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    ANALYZERS                             │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ HabitAnalyzer│  │ SleepAnalyzer│  │EmailAnalyzer │  │   │
│  │  │              │  │              │  │              │  │   │
│  │  │ • streaks    │  │ • avg hours  │  │ • patterns   │  │   │
│  │  │ • gaps       │  │ • quality    │  │ • important  │  │   │
│  │  │ • trends     │  │ • correlate  │  │ • spam       │  │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │   │
│  │         │                 │                 │           │   │
│  └─────────┼─────────────────┼─────────────────┼───────────┘   │
│            │                 │                 │                │
│            ▼                 ▼                 ▼                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    INSIGHT GENERATOR                     │   │
│  │                                                          │   │
│  │  • Filtra por relevância (threshold)                    │   │
│  │  • Aplica personalidade ATLAS                           │   │
│  │  • Dedup (não repetir insight recente)                  │   │
│  │  • Persiste em SQLite                                   │   │
│  │  • Trigger notificação se importante                    │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Configuração de Thresholds

```python
# atlas/proactive/config.py

PATTERN_THRESHOLDS = {
    # Hábitos
    "habit_gap_warning": 3,      # dias sem registrar hábito
    "habit_gap_critical": 7,     # dias sem registrar (crítico)
    "habit_streak_celebrate": 7, # dias consecutivos para celebrar

    # Sono
    "sleep_low_threshold": 6,    # horas (abaixo = alerta)
    "sleep_high_threshold": 9,   # horas (acima = alerta)
    "sleep_trend_window": 7,     # dias para calcular tendência

    # Email
    "email_important_keywords": ["urgente", "deadline", "importante"],
    "email_triage_interval": 1800,  # 30 minutos

    # Notificações
    "notification_cooldown": 3600,  # 1 hora entre notifs do mesmo tipo
    "daily_notification_limit": 5,  # máximo por dia
}

SCHEDULED_TASKS = {
    "briefing": {"hour": 8, "minute": 0},
    "end_of_day": {"hour": 20, "minute": 0},
    "pattern_analysis": {"hour": 21, "minute": 0},
}
```

### 3.3 Estrutura de Insights

```python
# atlas/proactive/schemas.py

from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class InsightType(str, Enum):
    HABIT_GAP = "habit_gap"           # "Faz X dias sem treinar"
    HABIT_STREAK = "habit_streak"      # "7 dias seguidos treinando!"
    SLEEP_TREND = "sleep_trend"        # "Dormindo menos que o normal"
    CORRELATION = "correlation"        # "Dorme melhor quando treina"
    EMAIL_IMPORTANT = "email_important"
    DEADLINE_REMINDER = "deadline_reminder"

class InsightPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class Insight(BaseModel):
    id: str
    type: InsightType
    priority: InsightPriority
    title: str              # "Hábito: Exercício"
    message: str            # "Faz 3 dias que não treina. Vai enferrujar."
    data: dict              # {"habit": "exercise", "days": 3}
    created_at: datetime
    dismissed: bool = False
    notified: bool = False

class InsightAction(BaseModel):
    label: str              # "Registrar treino"
    intent: str             # "log_habit"
    parameters: dict        # {"habit": "exercise", "value": true}
```

### 3.4 Analyzers

```python
# atlas/proactive/analyzers/habits.py

async def analyze_habits() -> list[Insight]:
    """Analisa padrões de hábitos e gera insights."""
    insights = []

    # Buscar dados dos últimos 30 dias
    habits = await get_habit_history(days=30)

    for habit_type in ["exercise", "sleep", "meditation"]:
        data = habits.get(habit_type, [])

        # Detectar gaps
        days_since_last = calculate_gap(data)
        if days_since_last >= PATTERN_THRESHOLDS["habit_gap_warning"]:
            insights.append(Insight(
                id=f"habit_gap_{habit_type}_{date.today()}",
                type=InsightType.HABIT_GAP,
                priority=InsightPriority.NORMAL,
                title=f"Hábito: {habit_type.title()}",
                message=generate_sarcastic_message(habit_type, days_since_last),
                data={"habit": habit_type, "days": days_since_last},
            ))

        # Detectar streaks
        current_streak = calculate_streak(data)
        if current_streak >= PATTERN_THRESHOLDS["habit_streak_celebrate"]:
            insights.append(Insight(
                id=f"habit_streak_{habit_type}_{date.today()}",
                type=InsightType.HABIT_STREAK,
                priority=InsightPriority.LOW,
                title=f"Parabéns!",
                message=f"{current_streak} dias seguidos de {habit_type}. Impressionante.",
                data={"habit": habit_type, "streak": current_streak},
            ))

    return insights
```

### 3.5 Arquivos a Criar

| Arquivo | Descrição |
|---------|-----------|
| `atlas/proactive/config.py` | Thresholds e configurações |
| `atlas/proactive/schemas.py` | Modelos de Insight |
| `atlas/proactive/scheduler.py` | APScheduler setup |
| `atlas/proactive/analyzers/habits.py` | Análise de hábitos |
| `atlas/proactive/analyzers/sleep.py` | Análise de sono |
| `atlas/proactive/analyzers/correlations.py` | Correlações entre dados |
| `atlas/proactive/insight_generator.py` | Geração e persistência |
| `atlas/api/insights.py` | Endpoints: list, dismiss |

---

## 4. API Endpoints (Novos/Modificados)

### 4.1 Novos Endpoints

```python
# Notificações
POST   /notifications/register    # Registrar push token
PATCH  /notifications/preferences # Configurar tipos de notificação
DELETE /notifications/token       # Remover token (logout)

# Insights
GET    /insights                  # Listar insights ativos
POST   /insights/{id}/dismiss     # Marcar como visto
POST   /insights/{id}/action      # Executar ação sugerida

# Dashboard (modificar)
GET    /dashboard                 # Adicionar campo "insights"
```

### 4.2 Response do Dashboard (Atualizado)

```json
{
  "date": "2026-02-03",
  "events": [...],
  "habits": [...],
  "vault": {...},
  "emails": [...],
  "email_alerts": [...],
  "memories": [...],
  "insights": [
    {
      "id": "habit_gap_exercise_2026-02-03",
      "type": "habit_gap",
      "priority": "normal",
      "title": "Hábito: Exercício",
      "message": "Faz 3 dias que não treina. Vai enferrujar.",
      "data": {"habit": "exercise", "days": 3},
      "actions": [
        {"label": "Registrar treino", "intent": "log_habit", "parameters": {...}}
      ]
    }
  ]
}
```

---

## 5. Dependências Novas

### Backend

```toml
# pyproject.toml
apscheduler = "^3.10"  # Scheduler para tarefas periódicas
```

### Mobile

```json
{
  "expo-notifications": "~0.28.0"
}
```

---

## 6. Plano de Implementação

### Fase 2.1 — Dashboard Refinado (1-2 semanas)
1. Criar DashboardContext com persistência
2. Componentizar widgets
3. Adicionar ações rápidas (log habit, add event)
4. Melhorar layout visual

### Fase 2.2 — Motor de Padrões (1-2 semanas)
1. Implementar analyzers (habits, sleep)
2. Criar scheduler com APScheduler
3. Gerar insights e persistir
4. Expor via API `/insights`

### Fase 2.3 — Notificações Push (1 semana)
1. Setup expo-notifications no mobile
2. Implementar registro de token
3. Criar serviço de envio no backend
4. Integrar com scheduler (briefing, insights)

### Fase 2.4 — Polish (1 semana)
1. Testes end-to-end
2. Rate limiting de notificações
3. Configurações de usuário (horários, tipos)
4. Refinamento de mensagens com personalidade

---

## 7. Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Notificações em excesso irritam usuário | Rate limiting + configuração de preferências |
| Análise de padrões consome recursos | Rodar em horários específicos, não em tempo real |
| Push token pode expirar | Re-registro automático no app open |
| Insights repetitivos | Dedup por ID + cooldown period |
| Personalidade pode ofender | Toggle para "modo formal" (fora do escopo inicial) |

---

## 8. Métricas de Sucesso

| Métrica | Alvo |
|---------|------|
| Engajamento com notificações | > 30% tap rate |
| Uso do dashboard | Visita diária |
| Ações rápidas | > 5 quick-actions/semana |
| Insights úteis | > 70% não dismissados imediatamente |
