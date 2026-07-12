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

from config.settings import SCHEDULE, TIMEZONE, SOCIAL_CHANNELS, CELEBRATION_CHANNEL, PRIMARY_CHANNEL_NAME
from messages.library import get_random_message
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

    # ─── Birthday Check — Primary (configured daily time) ────
    bday_config = SCHEDULE.get("birthday_check", {})
    bday_days = days_to_cron(bday_config.get("days", ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]))
    bday_hour = bday_config.get("hour", 9)
    bday_minute = bday_config.get("minute", 0)
    bday_backup_hour = (bday_hour + ((bday_minute + 30) // 60)) % 24
    bday_backup_minute = (bday_minute + 30) % 60
    if bday_config.get("enabled", True):
        scheduler.add_job(
            func=lambda c=client: _check_birthdays(c),
            trigger=CronTrigger(
                day_of_week=bday_days,
                hour=bday_hour,
                minute=bday_minute,
                timezone=tz
            ),
            id="birthday_check",
            name=f"Birthday Check ({bday_hour:02d}:{bday_minute:02d})",
            replace_existing=True
        )

    # ─── Birthday Check — Backup (30 minutes later) ───────────
    scheduler.add_job(
        func=lambda c=client: _check_birthdays(c),
        trigger=CronTrigger(
            day_of_week=bday_days,
            hour=bday_backup_hour,
            minute=bday_backup_minute,
            timezone=tz
        ),
        id="birthday_check_backup",
        name="Birthday Check Backup",
        replace_existing=True
    )

    # ─── Anniversary Check — Primary (configured daily time) ──
    ann_config = SCHEDULE.get("anniversary_check", {})
    ann_days = days_to_cron(ann_config.get("days", ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]))
    ann_hour = ann_config.get("hour", 9)
    ann_minute = ann_config.get("minute", 0)
    ann_backup_hour = (ann_hour + ((ann_minute + 30) // 60)) % 24
    ann_backup_minute = (ann_minute + 30) % 60
    if ann_config.get("enabled", True):
        scheduler.add_job(
            func=lambda c=client: _check_anniversaries(c),
            trigger=CronTrigger(
                day_of_week=ann_days,
                hour=ann_hour,
                minute=ann_minute,
                timezone=tz
            ),
            id="anniversary_check",
            name=f"Anniversary Check ({ann_hour:02d}:{ann_minute:02d})",
            replace_existing=True
        )

    # ─── Anniversary Check — Backup (30 minutes later) ────────
    scheduler.add_job(
        func=lambda c=client: _check_anniversaries(c),
        trigger=CronTrigger(
            day_of_week=ann_days,
            hour=ann_backup_hour,
            minute=ann_backup_minute,
            timezone=tz
        ),
        id="anniversary_check_backup",
        name="Anniversary Check Backup",
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
    # if the bot restarts after the scheduled time. Force a synchronous,
    # fresh pull from Slack first — the background preloader is fire-and-
    # forget, so without this the very first check after a restart could
    # run against a stale or empty disk cache and miss someone.
    logger.info("🔍 Running startup celebration check...")
    try:
        from utils.slack_profiles import preload_members_background
        preload_members_background(force_sync=True)
    except Exception as e:
        logger.warning(f"Could not force-refresh member data at startup: {e}")
    _check_birthdays(client)
    _check_anniversaries(client)

    return scheduler


# Cached resolved channel ID for PRIMARY_CHANNEL_NAME, so we don't hit the
# Slack API on every single post.
_resolved_channel_id = None
_resolved_channel_checked = False


def _resolve_primary_channel(client) -> str:
    """Resolve PRIMARY_CHANNEL_NAME (e.g. 'company-recognition') to a channel ID.

    La Chona should only ever post in this one channel. If it can't be found,
    or the bot hasn't been invited to it, this logs a loud, actionable error
    instead of silently posting nowhere (or guessing a different channel)."""
    global _resolved_channel_id, _resolved_channel_checked

    if _resolved_channel_id:
        return _resolved_channel_id

    target_name = (PRIMARY_CHANNEL_NAME or "").lstrip("#").strip().lower()
    if not target_name:
        return ""

    try:
        cursor = None
        while True:
            kwargs = {"types": "public_channel,private_channel", "limit": 200}
            if cursor:
                kwargs["cursor"] = cursor
            result = client.conversations_list(**kwargs)
            for ch in result.get("channels", []):
                if ch.get("name", "").lower() == target_name:
                    _resolved_channel_id = ch["id"]
                    logger.info(f"✅ Resolved channel '#{target_name}' → {ch['id']}")
                    return _resolved_channel_id
            cursor = result.get("response_metadata", {}).get("next_cursor", "")
            if not cursor:
                break
    except Exception as e:
        logger.error(f"Error looking up channel '#{target_name}': {e}")

    if not _resolved_channel_checked:
        logger.error(
            f"❌ Could not find a channel named '#{target_name}'. La Chona will NOT post "
            f"anything until this is fixed. Check that the name is spelled correctly and "
            f"that La Chona has been invited to that channel (or set CELEBRATION_CHANNEL "
            f"to the channel ID directly in config/settings.py)."
        )
        _resolved_channel_checked = True
    return ""


def _get_target_channels(client) -> list[str]:
    """Get the list of channel(s) to post to. Pinned to the single configured
    channel — explicit CELEBRATION_CHANNEL/SOCIAL_CHANNELS override it if set,
    otherwise it's resolved by name from PRIMARY_CHANNEL_NAME."""
    if SOCIAL_CHANNELS:
        return SOCIAL_CHANNELS
    if CELEBRATION_CHANNEL:
        return [CELEBRATION_CHANNEL]
    channel_id = _resolve_primary_channel(client)
    return [channel_id] if channel_id else []


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


def _check_birthdays(client) -> list[str]:
    """Check for today's birthdays and post celebration messages.
    Uses daily state file to avoid sending duplicate messages on restart.
    Returns the list of member names actually posted (empty if none / already sent)."""
    posted = []
    birthdays = get_todays_birthdays()
    if not birthdays:
        logger.info("🎂 No birthdays today.")
        return posted

    channel = CELEBRATION_CHANNEL or (_get_target_channels(client) or [None])[0]
    if not channel:
        logger.warning("No celebration channel configured — birthday message(s) NOT sent.")
        return posted

    from utils.celebrations import build_birthday_message
    for member in birthdays:
        slack_id = member.get("slack_id") or member.get("name", "unknown")
        if _was_birthday_sent_today(slack_id):
            logger.info(f"🎂 Birthday for {member['name']} already sent today — skipping.")
            continue
        payload = build_birthday_message(member)
        try:
            client.chat_postMessage(channel=channel, **payload)
            _mark_birthday_sent(slack_id)
            posted.append(member["name"])
            logger.info(f"🎂 Birthday message sent for {member['name']}")
        except Exception as e:
            logger.error(f"Error sending birthday message: {e}")
    return posted


def _check_anniversaries(client) -> list[str]:
    """Check for today's work anniversaries and post celebration messages.
    Uses daily state file to avoid sending duplicate messages on restart.
    Returns the list of member names actually posted (empty if none / already sent)."""
    posted = []
    anniversaries = get_todays_anniversaries()
    if not anniversaries:
        logger.info("🏆 No anniversaries today.")
        return posted

    channel = CELEBRATION_CHANNEL or (_get_target_channels(client) or [None])[0]
    if not channel:
        logger.warning("No celebration channel configured — anniversary message(s) NOT sent.")
        return posted

    from utils.celebrations import build_anniversary_message
    for member in anniversaries:
        slack_id = member.get("slack_id") or member.get("name", "unknown")
        if _was_anniversary_sent_today(slack_id):
            logger.info(f"🏆 Anniversary for {member['name']} already sent today — skipping.")
            continue
        payload = build_anniversary_message(member)
        try:
            client.chat_postMessage(channel=channel, **payload)
            _mark_anniversary_sent(slack_id)
            posted.append(member["name"])
            logger.info(f"🏆 Anniversary message sent for {member['name']} ({member['years']} years)")
        except Exception as e:
            logger.error(f"Error sending anniversary message: {e}")
    return posted


def check_recognitions_now(client) -> dict:
    """Run an on-demand birthday + anniversary check right now.

    Used when someone @mentions or DMs La Chona asking her to check/recognize
    birthdays or anniversaries. Shares the same daily de-dup state as the
    scheduled checks, so this can't cause a double-post, and any scheduled
    run later that day will skip whoever was already covered here.
    Returns {"birthdays": [names], "anniversaries": [names]}.
    """
    return {
        "birthdays": _check_birthdays(client),
        "anniversaries": _check_anniversaries(client),
    }


def _check_achievements(client):
    """Check for pending achievements and announce them."""
    achievements = get_pending_achievements()
    if not achievements:
        return

    channel = CELEBRATION_CHANNEL or (_get_target_channels(client) or [None])[0]
    if not channel:
        return

    from utils.celebrations import build_achievement_message
    for achievement in achievements:
        payload = build_achievement_message(
            achievement["member_name"],
            achievement["achievement"],
            slack_id=achievement.get("slack_id", ""),
            image_url=achievement.get("image_url", "")
        )
        try:
            client.chat_postMessage(channel=channel, **payload)
            mark_achievement_announced(achievement["achievement"], achievement["member_name"])
            logger.info(f"⭐ Achievement announced for {achievement['member_name']}")
        except Exception as e:
            logger.error(f"Error announcing achievement: {e}")
