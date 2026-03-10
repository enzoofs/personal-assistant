"""Configuration for proactive pattern detection and notifications."""

# Habit analysis thresholds
PATTERN_THRESHOLDS = {
    # Habit gaps (days without logging)
    "habit_gap_warning": 3,      # days without logging = warning
    "habit_gap_critical": 7,     # days without logging = critical

    # Streaks (consecutive days)
    "habit_streak_celebrate": 7,  # days to celebrate
    "habit_streak_milestone": 30, # major milestone

    # Sleep analysis
    "sleep_low_threshold": 6.0,   # hours (below = alert)
    "sleep_high_threshold": 9.0,  # hours (above = alert)
    "sleep_trend_window": 7,      # days for trend calculation
    "sleep_variance_alert": 2.0,  # hours variance to alert

    # Email importance
    "email_important_keywords": [
        "urgente", "urgent", "importante", "important",
        "deadline", "prazo", "asap", "crítico", "critical"
    ],
    "email_vip_senders": [],  # Can be configured per user

    # Notification limits
    "notification_cooldown": 3600,      # 1 hour between same type
    "daily_notification_limit": 5,      # max notifications per day
    "insight_dedup_hours": 24,          # don't repeat insight within this window
}

# Scheduled tasks configuration
SCHEDULED_TASKS = {
    "briefing": {
        "hour": 8,
        "minute": 0,
        "enabled": True,
        "description": "Morning briefing notification",
    },
    "end_of_day": {
        "hour": 20,
        "minute": 0,
        "enabled": True,
        "description": "End of day summary",
    },
    "pattern_analysis": {
        "hour": 21,
        "minute": 0,
        "enabled": True,
        "description": "Daily pattern analysis",
    },
    "email_triage": {
        "interval_minutes": 30,
        "enabled": True,
        "description": "Automatic email triage",
    },
}

# Sarcastic messages templates (ATLAS personality)
SARCASTIC_TEMPLATES = {
    "exercise": {
        "gap": [
            "Faz {days} dias que não treina. Vai enferrujar.",
            "{days} dias de sofá. O corpo agradece... ou não.",
            "Academia mandou perguntar se você ainda existe. ({days} dias)",
            "Seu personal trainer deve estar chorando. {days} dias sem aparecer.",
        ],
        "streak": [
            "{days} dias seguidos treinando! Impressionante.",
            "Olha só, {days} dias de treino. Quem é você e o que fez com o Enzo?",
            "{days} dias na academia. Tá virando bodybuilder?",
        ],
    },
    "sleep": {
        "low": [
            "Dormindo {hours}h por noite? Tá querendo virar zumbi?",
            "Média de {hours}h de sono. Produtividade vai agradecer... não.",
            "{hours}h de sono? Café não resolve tudo, viu.",
        ],
        "high": [
            "{hours}h de sono? Hibernando?",
            "Dormiu {hours}h. Urso dorme menos que isso.",
        ],
        "irregular": [
            "Seu sono tá mais instável que bolsa de valores.",
            "Variação de {variance}h no sono. Escolhe um horário e fica, pelo amor.",
        ],
    },
    "meditation": {
        "gap": [
            "Faz {days} dias sem meditar. Tá precisando.",
            "{days} dias sem meditar. O estresse agradece.",
        ],
        "streak": [
            "{days} dias meditando! Namastê, meu jovem.",
        ],
    },
    "water": {
        "gap": [
            "Faz {days} dias sem registrar água. Tá ressecando?",
        ],
        "low": [
            "Média de {liters}L de água. Camelo bebe mais.",
        ],
    },
    "correlation": {
        "sleep_exercise": [
            "Você dorme melhor nos dias que treina. Coincidência? Acho que não.",
            "Padrão detectado: treino = sono bom. Ciência, bebê.",
        ],
        "sleep_productivity": [
            "Sua produtividade aumenta {percent}% quando dorme mais de {hours}h.",
        ],
    },
    "deadline": {
        "tomorrow": [
            "Amanhã: {task}. Não deixa pra última hora de novo.",
            "{task} é amanhã. Tá preparado ou vai improvisar?",
        ],
        "today": [
            "HOJE: {task}. Bora.",
            "{task} vence HOJE. Sem desculpas.",
        ],
    },
    "generic": {
        "gap": [
            "Faz {days} dias sem registrar {habit}.",
            "{habit}: sumido há {days} dias.",
        ],
        "streak": [
            "{days} dias de {habit}. Consistência é tudo.",
        ],
    },
}
