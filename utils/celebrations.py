"""
La Chona – Celebration Engine
Handles birthdays, work anniversaries, and achievement announcements.
Now reads directly from live Slack profiles with team.json fallback.
"""

import json
import logging
from datetime import datetime, date
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent.parent / "data" / "team.json"


# ─────────────────────────────────────────────
# Team data loading — Slack profiles first, JSON fallback
# ─────────────────────────────────────────────

def get_all_active_members() -> list[dict]:
    """Return all active team members from Slack profiles (with JSON fallback)."""
    try:
        from utils.slack_profiles import fetch_all_members
        members = fetch_all_members()
        if members:
            return members
    except Exception as e:
        logger.warning(f"Could not fetch from Slack: {e}")
    # Fallback to JSON
    return _load_json_members()


def _load_json_members() -> list[dict]:
    """Load members from local team.json file."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [m for m in data.get("members", []) if m.get("active", True)]
    except Exception as e:
        logger.error(f"Error loading team.json: {e}")
        return []


def load_team_data() -> dict:
    """Load full team data from JSON file (for achievements)."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading team data: {e}")
        return {"members": [], "achievements": []}


def save_team_data(data: dict):
    """Save team data back to JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving team data: {e}")


# ─────────────────────────────────────────────
# Birthday celebrations
# ─────────────────────────────────────────────

def get_todays_birthdays() -> list[dict]:
    """Return list of members whose birthday is today (from Slack profiles)."""
    today = date.today()
    today_str = f"{today.month:02d}-{today.day:02d}"
    members = get_all_active_members()
    celebrants = []
    for member in members:
        bday = member.get("birthday", "")
        if bday == today_str:
            celebrants.append(member)
    return celebrants


def build_birthday_message(member: dict) -> str:
    """Build a celebratory birthday message for a team member."""
    name = member.get("name", "")
    first_name = member.get("first_name", name.split()[0] if name else "")
    slack_id = member.get("slack_id", "")
    mention = f"<@{slack_id}>" if slack_id else f"*{first_name}*"

    messages = [
        f"🎂🎉 ¡Hoy es el cumpleaños de {mention}! ¡Feliz cumpleaños! Que este día esté lleno de alegría, amor y muchas sorpresas. ¡Todo el equipo te desea lo mejor! 🥳🎈",
        f"🎊🎂 ¡Atención equipo! Hoy celebramos el cumpleaños de {mention}. ¡Que tengas un día increíble y un año lleno de éxitos! 🌟 ¡Felicidades! 🎁",
        f"🥳🎉 ¡Feliz cumpleaños {mention}! Eres una parte especial de este equipo y hoy es TU día. ¡Que lo disfrutes al máximo! 🎂🎈",
        f"🎈🎂 ¡Hoy es un día muy especial porque {mention} está de cumpleaños! Desde todo el equipo, ¡te deseamos un día maravilloso y un año lleno de bendiciones! 🌟🎊",
    ]
    import random
    return random.choice(messages)


# ─────────────────────────────────────────────
# Work anniversary celebrations
# ─────────────────────────────────────────────

def get_todays_anniversaries() -> list[dict]:
    """Return list of members whose work anniversary is today, with years count."""
    today = date.today()
    today_mmdd = f"{today.month:02d}-{today.day:02d}"
    members = get_all_active_members()
    anniversaries = []

    for member in members:
        ann_date_str = member.get("anniversary", "")
        if not ann_date_str:
            continue
        try:
            ann_date = datetime.strptime(ann_date_str, "%Y-%m-%d").date()
            ann_mmdd = f"{ann_date.month:02d}-{ann_date.day:02d}"
            if ann_mmdd == today_mmdd and ann_date.year < today.year:
                years = today.year - ann_date.year
                anniversaries.append({**member, "years": years})
        except ValueError:
            continue

    return anniversaries


def build_anniversary_message(member: dict) -> str:
    """Build a celebratory work anniversary message for a team member."""
    name = member.get("name", "")
    first_name = member.get("first_name", name.split()[0] if name else "")
    slack_id = member.get("slack_id", "")
    years = member.get("years", 1)
    mention = f"<@{slack_id}>" if slack_id else f"*{first_name}*"

    # Determine milestone type
    if years == 1:
        year_text = "¡1 año!"
        emoji = "🌱🎉"
        msg = f"¡Hoy {mention} cumple *1 año* con nosotros! 🌱🎉 ¡Gracias por ser parte de este equipo desde el primer día! Tu dedicación y esfuerzo hacen la diferencia. ¡Feliz aniversario! 🥂"
    elif years == 5:
        year_text = "¡5 años!"
        emoji = "⭐🎊"
        msg = f"🌟⭐ ¡FELIZ ANIVERSARIO {mention}! Hoy celebramos *5 años* de tenerte en el equipo. ¡5 años de dedicación, crecimiento y éxitos juntos! Eres un pilar fundamental de esta empresa. ¡Muchas gracias! 🥂🎊"
    elif years == 10:
        year_text = "¡10 años!"
        emoji = "🏆👑"
        msg = f"🏆👑 ¡INCREÍBLE! {mention} cumple hoy *10 años* con nosotros. ¡Una década de compromiso, lealtad y excelencia! Eres una leyenda de este equipo. ¡Todo el equipo te celebra con mucho cariño! 🎉🥂"
    elif years >= 15:
        msg = f"🏆🌟 ¡{mention} cumple hoy *{years} años* con nosotros! ¡Una trayectoria extraordinaria que inspira a todo el equipo! Gracias por tu lealtad, dedicación y todo lo que aportas cada día. ¡Feliz aniversario! 🥂🎊"
    else:
        msg = f"🎊🥂 ¡Feliz aniversario {mention}! Hoy celebramos *{years} año{'s' if years > 1 else ''}* de tenerte en el equipo. ¡Gracias por tu dedicación y todo lo que aportas! El equipo te aprecia mucho. 🌟"

    return msg


# ─────────────────────────────────────────────
# Upcoming birthdays (for proactive announcements)
# ─────────────────────────────────────────────

def get_upcoming_birthdays(days_ahead: int = 3) -> list[dict]:
    """Return members with birthdays in the next N days (for advance notice)."""
    today = date.today()
    members = get_all_active_members()
    upcoming = []

    for member in members:
        bday_str = member.get("birthday", "")
        if not bday_str:
            continue
        try:
            month, day = map(int, bday_str.split("-"))
            bday_this_year = date(today.year, month, day)
            if bday_this_year < today:
                bday_this_year = date(today.year + 1, month, day)
            days_until = (bday_this_year - today).days
            if 0 < days_until <= days_ahead:
                upcoming.append({**member, "days_until": days_until, "bday_date": bday_this_year})
        except Exception:
            continue

    upcoming.sort(key=lambda x: x["days_until"])
    return upcoming


# ─────────────────────────────────────────────
# Achievements (still stored in JSON)
# ─────────────────────────────────────────────

def get_pending_achievements() -> list[dict]:
    """Return achievements that haven't been announced yet."""
    data = load_team_data()
    pending = [
        a for a in data.get("achievements", [])
        if not a.get("announced", False) and a.get("member_name") != "Example Member"
    ]
    return pending


def mark_achievement_announced(achievement_name: str, member_name: str):
    """Mark an achievement as announced so it's not repeated."""
    data = load_team_data()
    for a in data.get("achievements", []):
        if a.get("achievement") == achievement_name and a.get("member_name") == member_name:
            a["announced"] = True
    save_team_data(data)


def add_achievement(member_name: str, slack_id: str, achievement: str):
    """Add a new achievement to be announced."""
    data = load_team_data()
    new_achievement = {
        "member_name": member_name,
        "slack_id": slack_id,
        "achievement": achievement,
        "date": date.today().isoformat(),
        "announced": False
    }
    data["achievements"].append(new_achievement)
    save_team_data(data)
    logger.info(f"Added achievement for {member_name}: {achievement}")


def add_member(name: str, slack_id: str, birthday: str = "", anniversary: str = "", role: str = "Team Member"):
    """Add a new team member to the data file (backup only — Slack is the source of truth)."""
    data = load_team_data()
    new_member = {
        "name": name,
        "slack_id": slack_id,
        "birthday": birthday,
        "anniversary": anniversary,
        "role": role,
        "active": True
    }
    data["members"].append(new_member)
    save_team_data(data)
    logger.info(f"Added new member: {name}")
