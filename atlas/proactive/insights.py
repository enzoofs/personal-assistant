"""Insight generator using pattern analyzers."""

import asyncio
import logging
from typing import Any

from atlas.proactive.analyzers import analyze_correlations, analyze_habits, analyze_sleep
from atlas.proactive.insight_store import get_active_insights, save_insight

logger = logging.getLogger(__name__)


async def generate_insights() -> list[dict[str, Any]]:
    """Generate insights by running all pattern analyzers.

    This function is called by the dashboard API to get current insights.
    It runs all analyzers, saves new insights to the store, and returns
    active (non-dismissed) insights.

    Returns:
        List of insight dictionaries for the dashboard API.
    """
    try:
        # Run analyzers in parallel
        results = await asyncio.gather(
            analyze_habits(),
            analyze_sleep(),
            analyze_correlations(),
            return_exceptions=True,
        )

        # Save any new insights from analyzers
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Analyzer failed: %s", result)
                continue

            for insight in result.insights:
                try:
                    save_insight(insight)
                except Exception as e:
                    logger.error("Failed to save insight %s: %s", insight.id, e)

    except Exception as e:
        logger.exception("Error running analyzers: %s", e)

    # Return active insights from store
    try:
        active = get_active_insights(limit=10)
        return [_insight_to_dict(i) for i in active]
    except Exception as e:
        logger.exception("Error fetching insights: %s", e)
        return []


def _insight_to_dict(insight) -> dict[str, Any]:
    """Convert Insight model to dict for API response."""
    return {
        "id": insight.id,
        "type": insight.type,
        "priority": insight.priority,
        "title": insight.title,
        "message": insight.message,
        "data": insight.data,
        "created_at": insight.created_at.isoformat(),
        "actions": [
            {
                "label": a.label,
                "intent": a.intent,
                "parameters": a.parameters,
            }
            for a in insight.actions
        ],
    }
