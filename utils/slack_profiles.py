"""
La Chona – Slack Profile Reader
Fetches team member data (names, birthdays, anniversaries) directly from Slack profiles.
Slack stores birthday in the custom profile field "birthday" (if configured).
Falls back to team.json if Slack profile data is not available.
"""

import os
import json
import logging
from datetime import date, datetime
from functools import lru_cache

logger = logging.getLogger(__name__)

# Cache duration in seconds (refresh every 30 minutes)
_cache = {}
_cache_time = {}
CACHE_TTL = 1800  # 30 minutes

# Disk cache file path
DISK_CACHE_PATH = os.path.join(os.path.dirname(__file__), "../data/members_cache.json")

# Pre-loaded members stored in memory at startup
_preloaded_members = []
_preload_done = False


def _save_to_disk(members: list):
    """Save members list to disk cache for instant startup."""
    try:
        import time
        cache_data = {"timestamp": time.time(), "members": members}
        os.makedirs(os.path.dirname(DISK_CACHE_PATH), exist_ok=True)
        with open(DISK_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Saved {len(members)} members to disk cache")
    except Exception as e:
        logger.warning(f"Could not save disk cache: {e}")


def _load_from_disk():
    """Load members from disk cache if it exists and is fresh enough (under 2 hours).
    Also logs clearly whenever the cache is stale enough that it's likely hiding
    recently-added or recently-corrected birthdays/anniversaries."""
    try:
        import time
        if not os.path.exists(DISK_CACHE_PATH):
            return None
        with open(DISK_CACHE_PATH, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        age = time.time() - cache_data.get("timestamp", 0)
        if age >= 1800:  # 30+ min old — flag it, even if we still use it below
            logger.warning(
                f"⚠️ Disk member cache is {int(age // 60)}min old. If someone's birthday/anniversary "
                f"was just added or fixed in Slack, it may not show up until the next successful refresh."
            )
        if age < 7200:  # 2 hours
            members = cache_data.get("members", [])
            if members:
                logger.info(f"⚡ Loaded {len(members)} members from disk cache (age: {int(age//60)}min)")
                return members
    except Exception as e:
        logger.warning(f"Could not load disk cache: {e}")
    return None


def preload_members_background(force_sync: bool = False):
    """Pre-load all member profiles.

    Normally: loads from disk instantly (non-blocking), then refreshes from
    Slack in a background thread.

    If force_sync=True (used at bot startup): blocks and fetches fresh data
    directly from Slack first, so the very first birthday/anniversary check
    of the day doesn't run against a stale or missing disk cache. Falls back
    to the disk cache / team.json automatically if the live fetch fails.
    """
    import time
    import threading
    global _preloaded_members, _preload_done

    if force_sync:
        logger.info("🔄 Startup: fetching fresh team profiles from Slack before first celebration check...")
        members = _fetch_from_slack()
        if members:
            _preloaded_members = members
            _preload_done = True
            logger.info(f"✅ Startup fetch got {len(members)} members directly from Slack")
            return
        logger.warning("Startup Slack fetch returned nothing — falling back to disk cache/team.json")
        # _fetch_from_slack() already falls back to team.json internally when it
        # can't reach Slack at all, so _preloaded_members may already be set here.
        if _preloaded_members:
            return

    # Step 1: Load from disk immediately (instant, no API calls)
    disk_members = _load_from_disk()
    if disk_members:
        _preloaded_members = disk_members
        _preload_done = True
        _cache["members"] = disk_members
        _cache_time["members"] = time.time()
        logger.info(f"⚡ Instant startup: {len(disk_members)} members loaded from disk cache")

    # Step 2: Refresh from Slack API in background thread
    def _refresh():
        global _preloaded_members, _preload_done
        try:
            logger.info("🔄 Refreshing team profiles from Slack API in background...")
            members = _fetch_from_slack()
            if members:
                _preloaded_members = members
                _preload_done = True
                _save_to_disk(members)  # Save to disk for next startup
                logger.info(f"✅ Refreshed {len(members)} team profiles from Slack")
        except Exception as e:
            logger.warning(f"Background Slack refresh failed: {e}")
            _preload_done = True
    t = threading.Thread(target=_refresh, daemon=True)
    t.start()


def get_slack_client():
    """Get a Slack WebClient instance."""
    from slack_sdk import WebClient
    token = os.environ.get("SLACK_BOT_TOKEN_CULTURE", "")
    return WebClient(token=token)


def fetch_all_members():
    """
    Fetch all workspace members. Returns preloaded cache instantly if available,
    otherwise fetches from Slack API (slow, only on first call).
    """
    import time
    now = time.time()

    # Return in-memory preloaded data if available (fastest)
    if _preloaded_members:
        # Refresh cache in background if stale
        if (now - _cache_time.get("members", 0)) > CACHE_TTL:
            preload_members_background()
        return _preloaded_members

    # Return time-based cache if fresh
    if "members" in _cache and (now - _cache_time.get("members", 0)) < CACHE_TTL:
        return _cache["members"]

    # First time — fetch synchronously and cache
    members = _fetch_from_slack()
    if members:
        return members
    return _load_from_json()


def _get_full_profile_with_retry(client, user_id: str, max_retries: int = 3):
    """Fetch a user's full profile (custom fields incl. birthday/anniversary).

    Slack rate-limits users.profile.get fairly aggressively, and when this
    workspace refreshes every member's profile in a loop, hitting that limit
    used to fail *silently* — the code would just fall back to the basic
    profile (no custom fields), so the person's birthday/anniversary quietly
    disappeared for that refresh. This now respects Retry-After and retries,
    and logs clearly if it truly fails.
    """
    import time
    try:
        from slack_sdk.errors import SlackApiError
    except Exception:
        SlackApiError = Exception  # pragma: no cover - slack_sdk always available in prod

    for attempt in range(1, max_retries + 1):
        try:
            full = client.users_profile_get(user=user_id)
            return full.get("profile")
        except SlackApiError as e:
            response = getattr(e, "response", None)
            error_code = response.get("error") if response else str(e)
            if error_code == "ratelimited" and attempt < max_retries:
                retry_after = 1
                try:
                    retry_after = int(response.headers.get("Retry-After", "1"))
                except Exception:
                    pass
                logger.warning(
                    f"Rate-limited fetching profile for {user_id} (attempt {attempt}/{max_retries}); "
                    f"retrying in {retry_after}s"
                )
                time.sleep(retry_after)
                continue
            logger.warning(f"Could not fetch full profile for {user_id}: {error_code}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error fetching full profile for {user_id}: {e}")
            return None
    return None


def _fetch_from_slack():
    """Internal: fetch all member profiles from Slack API."""
    import time
    now = time.time()
    try:
        client = get_slack_client()
        members = []
        cursor = None
        profile_fetch_failures = []
        missing_birthday = []
        missing_anniversary = []

        while True:
            kwargs = {"limit": 200}
            if cursor:
                kwargs["cursor"] = cursor

            response = client.users_list(**kwargs)
            users = response.get("members", [])

            for user in users:
                # Skip bots, deleted users, and Slackbot
                if user.get("is_bot") or user.get("deleted") or user.get("id") == "USLACKBOT":
                    continue
                if user.get("is_app_user"):
                    continue

                user_id = user.get("id", "")
                profile = user.get("profile", {})
                name = profile.get("display_name") or profile.get("real_name") or user.get("name", "")
                if not name:
                    continue

                # Fetch full profile with custom fields (birthday, anniversary)
                full_profile = _get_full_profile_with_retry(client, user_id)
                if full_profile is not None:
                    profile = full_profile
                else:
                    profile_fetch_failures.append(f"{name} ({user_id})")

                # Extract birthday and anniversary from custom fields
                birthday = _extract_birthday(profile)
                anniversary = _extract_anniversary(profile)
                if not birthday:
                    missing_birthday.append(name)
                if not anniversary:
                    missing_anniversary.append(name)

                members.append({
                    "name": name,
                    "first_name": name.split()[0] if name else "",
                    "slack_id": user_id,
                    "birthday": birthday,  # MM-DD format or empty
                    "anniversary": anniversary,  # YYYY-MM-DD or empty
                    "role": profile.get("title", "Team Member") or "Team Member",
                    "email": profile.get("email", ""),
                    "image_url": (
                        profile.get("image_original")
                        or profile.get("image_512")
                        or profile.get("image_192")
                        or profile.get("image_72")
                        or ""
                    ),
                    "active": True
                })

            # Handle pagination
            next_cursor = response.get("response_metadata", {}).get("next_cursor", "")
            if next_cursor:
                cursor = next_cursor
            else:
                break

        # Cache the results in memory, global, and disk
        global _preloaded_members, _preload_done
        _cache["members"] = members
        _cache_time["members"] = now
        _preloaded_members = members
        _preload_done = True
        _save_to_disk(members)  # Persist to disk for instant next startup

        logger.info(f"✅ Fetched {len(members)} members from Slack profiles")
        if profile_fetch_failures:
            logger.warning(
                f"⚠️ Could not fetch full profile (birthday/anniversary fields invisible) for "
                f"{len(profile_fetch_failures)} member(s): {', '.join(profile_fetch_failures)}"
            )
        if missing_birthday:
            logger.info(f"🎂 No birthday on file for {len(missing_birthday)} member(s): {', '.join(missing_birthday)}")
        if missing_anniversary:
            logger.info(f"🏆 No anniversary/start date on file for {len(missing_anniversary)} member(s): {', '.join(missing_anniversary)}")
        return members

    except Exception as e:
        logger.error(f"Error fetching Slack members: {e}")
        # Fall back to team.json
        return _load_from_json()


# Known custom field IDs for this workspace
BIRTHDAY_FIELD_ID = "Xf07M352NBGF"   # Label: Birthday
ANNIVERSARY_FIELD_ID = "Xf07MKT22PHB"  # Label: Since (work anniversary)


def _extract_birthday(profile: dict) -> str:
    """
    Extract birthday from Slack profile custom fields.
    Uses the known field ID for this workspace: Xf07M352NBGF (Birthday)
    Returns MM-DD format string or empty string.
    """
    # First try the known field ID for this workspace
    fields = profile.get("fields", {})
    if isinstance(fields, dict):
        # Try known birthday field ID
        if BIRTHDAY_FIELD_ID in fields:
            value = fields[BIRTHDAY_FIELD_ID].get("value", "")
            if value:
                return _normalize_birthday(value)

        # Fallback: search by label
        for field_id, field_data in fields.items():
            if isinstance(field_data, dict):
                label = field_data.get("label", "").lower()
                value = field_data.get("value", "")
                if any(kw in label for kw in ["birthday", "birth", "cumpleaños", "cumpleanos", "nacimiento"]):
                    if value:
                        return _normalize_birthday(value)

    # Check standard profile fields
    for field_name in ["birthday", "date_of_birth", "bday", "birth_date"]:
        value = profile.get(field_name, "")
        if value:
            return _normalize_birthday(value)

    return ""


def _extract_anniversary(profile: dict) -> str:
    """
    Extract work anniversary/start date from Slack profile.
    Uses the known field ID for this workspace: Xf07MKT22PHB (Since)
    Returns YYYY-MM-DD format string or empty string.
    """
    # Try known anniversary field ID
    fields = profile.get("fields", {})
    if isinstance(fields, dict):
        if ANNIVERSARY_FIELD_ID in fields:
            value = fields[ANNIVERSARY_FIELD_ID].get("value", "")
            if value:
                return value  # Already in YYYY-MM-DD format

        # Fallback: search by label
        for field_id, field_data in fields.items():
            if isinstance(field_data, dict):
                label = field_data.get("label", "").lower()
                value = field_data.get("value", "")
                if any(kw in label for kw in ["since", "start", "anniversary", "aniversario", "inicio", "ingreso"]):
                    if value:
                        return value

    # Fallback to standard start_date field
    return profile.get("start_date", "")


def _normalize_birthday(value: str) -> str:
    """
    Normalize a birthday string to MM-DD format.
    Handles: MM-DD, MM/DD, YYYY-MM-DD, Month DD, DD/MM/YYYY, etc.
    """
    if not value:
        return ""

    value = value.strip()

    # MM-DD or M-D style (with or without zero-padding), e.g. "03-18", "3/18"
    # Previously this only matched a 5-character string (zero-padded), so a
    # birthday entered as "3/18" instead of "03/18" was silently dropped.
    import re as _re
    bare_match = _re.match(r"^(\d{1,2})[-/](\d{1,2})$", value)
    if bare_match:
        try:
            month, day = int(bare_match.group(1)), int(bare_match.group(2))
            if 1 <= month <= 12 and 1 <= day <= 31:
                return f"{month:02d}-{day:02d}"
        except Exception:
            pass

    # YYYY-MM-DD format
    if len(value) == 10 and value[4] == "-":
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            return dt.strftime("%m-%d")
        except Exception:
            pass

    # MM/DD/YYYY format
    if len(value) == 10 and value[2] == "/" and value[5] == "/":
        try:
            dt = datetime.strptime(value, "%m/%d/%Y")
            return dt.strftime("%m-%d")
        except Exception:
            pass

    # Try various date formats
    for fmt in ["%B %d", "%b %d", "%B %d, %Y", "%b %d, %Y", "%d/%m/%Y", "%d-%m-%Y"]:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%m-%d")
        except Exception:
            continue

    return ""


def _load_from_json() -> list:
    """Fallback: load team data from local team.json file."""
    try:
        data_path = os.path.join(os.path.dirname(__file__), "../data/team.json")
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [m for m in data.get("members", []) if m.get("active", True)]
    except Exception as e:
        logger.error(f"Error loading team.json: {e}")
        return []


def get_next_birthday(members: list = None):
    """
    Find the team member with the next upcoming birthday.
    Returns (days_until, name, slack_id, date_str) or None.
    """
    if members is None:
        members = fetch_all_members()

    today = date.today()
    upcoming = []

    for m in members:
        bday_str = m.get("birthday", "")
        if not bday_str:
            continue
        try:
            month, day = map(int, bday_str.split("-"))
            bday_this_year = date(today.year, month, day)
            if bday_this_year < today:
                bday_this_year = date(today.year + 1, month, day)
            days_until = (bday_this_year - today).days
            upcoming.append({
                "days": days_until,
                "name": m["name"],
                "first_name": m.get("first_name", m["name"].split()[0]),
                "slack_id": m.get("slack_id", ""),
                "date_str": bday_this_year.strftime("%B %d"),
                "date_es": _month_es(bday_this_year.month) + f" {day}"
            })
        except Exception:
            continue

    if upcoming:
        upcoming.sort(key=lambda x: x["days"])
        return upcoming[0]
    return None


def get_todays_birthdays(members: list = None) -> list:
    """Return list of members whose birthday is today."""
    if members is None:
        members = fetch_all_members()

    today = date.today()
    celebrants = []
    for m in members:
        bday_str = m.get("birthday", "")
        if not bday_str:
            continue
        try:
            month, day = map(int, bday_str.split("-"))
            if month == today.month and day == today.day:
                celebrants.append(m)
        except Exception:
            continue
    return celebrants


def get_todays_anniversaries(members: list = None) -> list:
    """Return list of members whose work anniversary is today (only 1+ full years)."""
    if members is None:
        members = fetch_all_members()

    today = date.today()
    celebrants = []
    for m in members:
        ann_str = m.get("anniversary", "")
        if not ann_str:
            continue
        try:
            ann_date = datetime.strptime(ann_str, "%Y-%m-%d").date()
            # Only celebrate if they have completed at least 1 full year
            if ann_date.month == today.month and ann_date.day == today.day:
                years = today.year - ann_date.year
                if years >= 1:  # Must have at least 1 full year
                    celebrants.append({**m, "years": years})
        except Exception:
            continue
    return celebrants


def get_next_anniversary(members: list = None):
    """
    Find the team member with the next upcoming work anniversary (1+ full years only).
    Returns a dict with days, name, slack_id, years, date_es or None.
    """
    if members is None:
        members = fetch_all_members()

    today = date.today()
    upcoming = []

    for m in members:
        ann_str = m.get("anniversary", "")
        if not ann_str:
            continue
        try:
            ann_date = datetime.strptime(ann_str, "%Y-%m-%d").date()

            # Calculate next anniversary date
            next_ann = ann_date.replace(year=today.year)
            if next_ann <= today:
                next_ann = ann_date.replace(year=today.year + 1)

            # Years they will have completed on that anniversary
            years_at_next = next_ann.year - ann_date.year

            # Only include employees who will have completed at least 1 full year
            if years_at_next < 1:
                continue

            days_until = (next_ann - today).days
            upcoming.append({
                "days": days_until,
                "name": m["name"],
                "first_name": m.get("first_name", m["name"].split()[0]),
                "slack_id": m.get("slack_id", ""),
                "years": years_at_next,
                "start_date": ann_str,
                "date_es": _month_es(next_ann.month) + f" {next_ann.day}"
            })
        except Exception:
            continue

    if upcoming:
        upcoming.sort(key=lambda x: x["days"])
        return upcoming[0]
    return None


def build_team_summary_from_slack() -> str:
    """Build a text summary of the team from live Slack data."""
    members = fetch_all_members()
    if not members:
        return "El equipo aún no tiene miembros registrados."

    today = date.today()
    lines = []
    for m in members:
        line = f"- {m['name']} ({m.get('role', 'Team Member')})"
        bday = m.get("birthday", "")
        if bday:
            try:
                month, day = map(int, bday.split("-"))
                bday_date = date(today.year, month, day)
                if bday_date < today:
                    bday_date = date(today.year + 1, month, day)
                days = (bday_date - today).days
                line += f", cumpleaños: {_month_es(month)} {day} (en {days} días)"
            except Exception:
                line += f", cumpleaños: {bday}"
        ann = m.get("anniversary", "")
        if ann:
            try:
                ann_date = datetime.strptime(ann, "%Y-%m-%d").date()
                # Correct years: only count if anniversary has passed this year
                years = today.year - ann_date.year
                if (today.month, today.day) < (ann_date.month, ann_date.day):
                    years -= 1  # Anniversary hasn't happened yet this year
                if years >= 1:
                    line += f", aniversario laboral: {_month_es(ann_date.month)} {ann_date.day} ({years} año(s) en la empresa)"
                else:
                    line += f", nuevo integrante, fecha de inicio: {_month_es(ann_date.month)} {ann_date.day} de {ann_date.year}"
            except Exception:
                pass
        lines.append(line)

    return "\n".join(lines)


def invalidate_cache():
    """Force refresh of cached member data."""
    _cache.clear()
    _cache_time.clear()


def _month_es(month: int) -> str:
    """Return Spanish month name."""
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
              "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return months[month - 1] if 1 <= month <= 12 else ""
