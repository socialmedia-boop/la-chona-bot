"""
Team Culture Bot – Scheduler Engine
Uses APScheduler to post messages at configured times.

Fix: Added startup check + 9 AM backup check + daily state file to prevent
     missed celebrations when the bot restarts after the scheduled time.
"""

import logging
import json
import os
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone as pytz_timezone

from config.settings import SCHEDULE, TIMEZONE, SOCIAL_CHANNELS, CELEBRATION_CHANNEL
from messages.library import get_random_message, get_birthday_message, get_anniversary_message, get_achievement_message
from utils.celebrations import get_todays_birthdays, get_todays_anniversaries, get_pending_achievements, mark_achievement_announced

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Daily state file — tracks what was already sent today
# Prevents duplicate messages if the bot restarts mid-day
# ─────────────────────────────────────────────
STATE_FILE = os.path.join(os.path.dirname(__file__), "../data/daily_state.json")


def _load_daily_state() -> dict:
    """Load today's sent-celebrations state from disk."""
    today_str = date.today().isoformat()
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            if state.get("date") != today_str:
                return {"date": today_str, "birthdays_sent": [], "anniversaries_sent": []}
            return state
    except Exception as e:
        logger.warning(f"Could not load daily state: {e}")
    return {"date": today_str, "birthdays_sent": [], "anniversaries_sent": []}


def _save_daily_state(state: dict):
    """Save today's sent-celebrations state to disk."""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Could not save daily state: {e}")


def _mark_birthday_sent(slack_id: str):
    state = _load_daily_state()
    if slack_id not in state["birthdays_sent"]:
        state["birthdays_sent"].append(slack_id)
        _save_daily_state(state)


def _mark_anniversary_sent(slack_id: str):
    state = _load_daily_state()
    if slack_id not in state["anniversaries_sent"]:
        state["anniversaries_sent"].append(slack_id)
        _save_daily_state(state)


def _was_birthday_sent_today(slack_id: str) -> bool:
    return slack_id in _load_daily_state().get("birthdays_sent", [])


def _was_anniversary_sent_today(slack_id: str) -> bool:
    return slack_id in _load_daily_state().get("anniversaries_sent", [])


# Day name to cron day-of-week mapping
DAY_MAP = {
    "mon": "mon", "tue": "tue", "wed": "wed",
    "thu": "thu", "fri": "fri", "sat": "sat", "sun": "sun"
}


def days_to_cron(days: list) -> str:
    """Convert list of day names to cron day-of-week string."""
    return ",".join([DAY_MAP.get(d, d) for d in days])


def setup_scheduler(app, client):
    """Initialize and start the APScheduler with all configured jobs."""
    tz = pytz_timezone(TIMEZONE)
    scheduler = BackgroundScheduler(timezone=tz)

    # ─── Regular Content Posts ───────────────────────────────
    for job_name, config in SCHEDULE.items():
        if not config.get("enabled", True):
            continue

        if job_name in ("birthday_check", "anniversary_check"):
            continue  # Handled separately below

        if job_name == "random_mention":
            days_cron = days_to_cron(config["days"])
            scheduler.add_job(
                func=lambda c=client: _post_random_mention(c),
                trigger=CronTrigger(
                    day_of_week=days_cron,
                    hour=config["hour"],
                    minute=config["minute"],
                    timezone=tz
                ),
                id=job_name,
                name=f"Random Mention – {job_name}",
                replace_existing=True
            )
        else:
            category = config.get("category", "motivacion")
            days_cron = days_to_cron(config["days"])
            scheduler.add_job(
                func=lambda cat=category, c=client: _post_category_message(cat, c),
                trigger=CronTrigger(
                    day_of_week=days_cron,
                    hour=config["hour"],
                    minute=config["minute"],
                    timezone=tz
                ),
                id=job_name,
                name=f"Content Post – {job_name}",
                replace_existing=True
            )

    # ─── Birthday Check — Primary (8:00 AM daily) ────────────
    bday_config = SCHEDULE.get("birthday_check", {})
    if bday_config.get("enabled", True):
        scheduler.add_job(
            func=lambda c=client: _check_birthdays(c),
            trigger=CronTrigger(
                day_of_week="mon-sun",
                hour=bday_config.get("hour", 8),
                minute=bday_config.get("minute", 0),
                timezone=tz
            ),
            id="birthday_check",
            name="Birthday Check (8 AM)",
            replace_existing=True
        )

    # ─── Birthday Check — Backup (9:00 AM daily) ─────────────
    # Safety net: runs 1 hour later in case the bot restarted after 8 AM
    scheduler.add_job(
        func=lambda c=client: _check_birthdays(c),
        trigger=CronTrigger(
            day_of_week="mon-sun",
            hour=9,
            minute=0,
            timezone=tz
        ),
        id="birthday_check_backup",
        name="Birthday Check Backup (9 AM)",
        replace_existing=True
    )

    # ─── Anniversary Check — Primary (8:05 AM weekdays) ──────
    ann_config = SCHEDULE.get("anniversary_check", {})
    if ann_config.get("enabled", True):
        scheduler.add_job(
            func=lambda c=client: _check_anniversaries(c),
            trigger=CronTrigger(
                day_of_week="mon-fri",
                hour=ann_config.get("hour", 8),
                minute=ann_config.get("minute", 5),
                timezone=tz
            ),
            id="anniversary_check",
            name="Anniversary Check (8:05 AM)",
            replace_existing=True
        )

    # ─── Anniversary Check — Backup (9:05 AM weekdays) ───────
    scheduler.add_job(
        func=lambda c=client: _check_anniversaries(c),
        trigger=CronTrigger(
            day_of_week="mon-fri",
            hour=9,
            minute=5,
            timezone=tz
        ),
        id="anniversary_check_backup",
        name="Anniversary Check Backup (9:05 AM)",
        replace_existing=True
    )

    # ─── Achievement Check (every hour) ──────────────────────
    scheduler.add_job(
        func=lambda c=client: _check_achievements(c),
        trigger=CronTrigger(minute=0, timezone=tz),
        id="achievement_check",
        name="Achievement Check",
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"✅ Scheduler started with {len(scheduler.get_jobs())} jobs | Timezone: {TIMEZONE}")
    for job in scheduler.get_jobs():
        logger.info(f"   📅 {job.name} → Next run: {job.next_run_time}")

    # ─── Startup Check ────────────────────────────────────────
    # Run immediately on startup so we never miss a celebration
    # if the bot restarts after the scheduled time
    logger.info("🔍 Running startup celebration check...")
    _check_birthdays(client)
    _check_anniversaries(client)

    return scheduler


def _get_target_channels(client) -> list[str]:
    """Get the list of channels to post to, auto-discovering if not configured."""
    if SOCIAL_CHANNELS:
        return SOCIAL_CHANNELS
    try:
        result = client.conversations_list(types="public_channel", limit=200)
        for ch in result.get("channels", []):
            if ch["name"] in ("general", "equipo-social", "social", "team-culture"):
                return [ch["id"]]
    except Exception as e:
        logger.error(f"Error discovering channels: {e}")
    return []


def _post_category_message(category: str, client):
    """Post a message from a given category to all configured channels."""
    channels = _get_target_channels(client)
    if not channels:
        logger.warning("No channels configured. Add channel IDs to config/settings.py")
        return

    message = get_random_message(category)
    for channel_id in channels:
        try:
            client.chat_postMessage(
                channel=channel_id,
                text=message,
                unfurl_links=False,
                unfurl_media=False
            )
            logger.info(f"✅ Posted [{category}] to {channel_id}")
        except Exception as e:
            logger.error(f"Error posting to {channel_id}: {e}")


def _post_random_mention(client):
    """Post a random member mention to all configured channels."""
    from utils.mentions import build_mention_message
    channels = _get_target_channels(client)
    if not channels:
        return

    message = build_mention_message(client)
    if not message:
        logger.warning("No members available for mention")
        return

    for channel_id in channels:
        try:
            client.chat_postMessage(
                channel=channel_id,
                text=message,
                unfurl_links=False
            )
            logger.info(f"✅ Posted random mention to {channel_id}")
        except Exception as e:
            logger.error(f"Error posting mention to {channel_id}: {e}")


def _check_birthdays(client):
    """Check for today's birthdays and post celebration messages.
    Uses daily state file to avoid sending duplicate messages on restart."""
    birthdays = get_todays_birthdays()
    if not birthdays:
        logger.info("🎂 No birthdays today.")
        return

    channel = CELEBRATION_CHANNEL or (_get_target_channels(client) or [None])[0]
    if not channel:
        logger.warning("No celebration channel configured.")
        return

    from utils.celebrations import build_birthday_message
    for member in birthdays:
        slack_id = member.get("slack_id") or member.get("name", "unknown")
        if _was_birthday_sent_today(slack_id):
            logger.info(f"🎂 Birthday for {member['name']} already sent today — skipping.")
            continue
        message = build_birthday_message(member)
        try:
            client.chat_postMessage(channel=channel, text=message)
            _mark_birthday_sent(slack_id)
            logger.info(f"🎂 Birthday message sent for {member['name']}")
        except Exception as e:
            logger.error(f"Error sending birthday message: {e}")


def _check_anniversaries(client):
    """Check for today's work anniversaries and post celebration messages.
    Uses daily state file to avoid sending duplicate messages on restart."""
    anniversaries = get_todays_anniversaries()
    if not anniversaries:
        logger.info("🏆 No anniversaries today.")
        return

    channel = CELEBRATION_CHANNEL or (_get_target_channels(client) or [None])[0]
    if not channel:
        logger.warning("No celebration channel configured.")
        return

    from utils.celebrations import build_anniversary_message
    for member in anniversaries:
        slack_id = member.get("slack_id") or member.get("name", "unknown")
        if _was_anniversary_sent_today(slack_id):
            logger.info(f"🏆 Anniversary for {member['name']} already sent today — skipping.")
            continue
        message = build_anniversary_message(member)
        try:
            client.chat_postMessage(channel=channel, text=message)
            _mark_anniversary_sent(slack_id)
            logger.info(f"🏆 Anniversary message sent for {member['name']} ({member['years']} years)")
        except Exception as e:
            logger.error(f"Error sending anniversary message: {e}")


def _check_achievements(client):
    """Check for pending achievements and announce them."""
    achievements = get_pending_achievements()
    if not achievements:
        return

    channel = CELEBRATION_CHANNEL or (_get_target_channels(client) or [None])[0]
    if not channel:
        return

    for achievement in achievements:
        message = get_achievement_message(achievement["member_name"], achievement["achievement"])
        if achievement.get("slack_id"):
            message = message.replace(achievement["member_name"], f"<@{achievement['slack_id']}>")
        try:
            client.chat_postMessage(channel=channel, text=message)
            mark_achievement_announced(achievement["achievement"], achievement["member_name"])
            logger.info(f"⭐ Achievement announced for {achievement['member_name']}")
        except Exception as e:
            logger.error(f"Error announcing achievement: {e}")
