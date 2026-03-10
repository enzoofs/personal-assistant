"""APScheduler setup for proactive tasks."""

import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from atlas.config import settings
from atlas.proactive.config import SCHEDULED_TASKS
from atlas.proactive.analyzers import analyze_correlations, analyze_habits, analyze_sleep
from atlas.proactive.insight_store import cleanup_old_insights, save_insight

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: AsyncIOScheduler | None = None


async def run_pattern_analysis():
    """Run all pattern analyzers and save insights."""
    logger.info("Starting scheduled pattern analysis")

    try:
        # Run analyzers in parallel
        results = await asyncio.gather(
            analyze_habits(),
            analyze_sleep(),
            analyze_correlations(),
            return_exceptions=True,
        )

        total_insights = 0
        for result in results:
            if isinstance(result, Exception):
                logger.error("Analyzer failed: %s", result)
                continue

            for insight in result.insights:
                if save_insight(insight):
                    total_insights += 1
                    logger.info("New insight: %s - %s", insight.type, insight.title)

        logger.info("Pattern analysis complete: %d new insights", total_insights)

    except Exception as e:
        logger.exception("Pattern analysis failed: %s", e)


async def run_daily_cleanup():
    """Clean up old dismissed insights."""
    logger.info("Running daily cleanup")
    try:
        cleanup_old_insights(days=30)
    except Exception as e:
        logger.exception("Cleanup failed: %s", e)


async def run_email_triage():
    """Run email triage (already implemented in email_cleaner)."""
    from atlas.proactive.email_cleaner import triage_emails

    logger.debug("Running scheduled email triage")
    try:
        await triage_emails()
    except Exception as e:
        logger.exception("Email triage failed: %s", e)


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the scheduler instance."""
    global _scheduler

    if _scheduler is None:
        tz = ZoneInfo(settings.timezone)
        _scheduler = AsyncIOScheduler(timezone=tz)

    return _scheduler


def setup_scheduler() -> AsyncIOScheduler:
    """Configure and return the scheduler with all jobs."""
    scheduler = get_scheduler()
    tz = ZoneInfo(settings.timezone)

    # Pattern analysis job (daily at configured time)
    pattern_config = SCHEDULED_TASKS.get("pattern_analysis", {})
    if pattern_config.get("enabled", True):
        scheduler.add_job(
            run_pattern_analysis,
            CronTrigger(
                hour=pattern_config.get("hour", 21),
                minute=pattern_config.get("minute", 0),
                timezone=tz,
            ),
            id="pattern_analysis",
            replace_existing=True,
            name="Daily Pattern Analysis",
        )
        logger.info(
            "Scheduled pattern analysis at %02d:%02d",
            pattern_config.get("hour", 21),
            pattern_config.get("minute", 0),
        )

    # Email triage job (every N minutes)
    email_config = SCHEDULED_TASKS.get("email_triage", {})
    if email_config.get("enabled", True):
        interval = email_config.get("interval_minutes", 30)
        scheduler.add_job(
            run_email_triage,
            IntervalTrigger(minutes=interval),
            id="email_triage",
            replace_existing=True,
            name="Email Triage",
        )
        logger.info("Scheduled email triage every %d minutes", interval)

    # Daily cleanup job (at midnight)
    scheduler.add_job(
        run_daily_cleanup,
        CronTrigger(hour=0, minute=5, timezone=tz),
        id="daily_cleanup",
        replace_existing=True,
        name="Daily Cleanup",
    )
    logger.info("Scheduled daily cleanup at 00:05")

    return scheduler


def start_scheduler():
    """Start the scheduler if not running."""
    scheduler = setup_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("Proactive scheduler started")


def stop_scheduler():
    """Stop the scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Proactive scheduler stopped")
        _scheduler = None


async def trigger_analysis_now():
    """Manually trigger pattern analysis (for testing/debugging)."""
    logger.info("Manual pattern analysis triggered")
    await run_pattern_analysis()
