"""
Team Culture Bot – Configuration Settings
Edit this file to customize channels, schedules, and team data.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────
# SLACK CREDENTIALS
# ─────────────────────────────────────────────────────────────
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN_CULTURE", "")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN_CULTURE", "")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET_CULTURE", "")

# ─────────────────────────────────────────────────────────────
# BOT IDENTITY
# ─────────────────────────────────────────────────────────────
BOT_NAME = "La Chona"
BOT_EMOJI = "🌟"

# ─────────────────────────────────────────────────────────────
# CHANNELS CONFIGURATION
# Add the Slack channel IDs where the bot should post.
# You can find channel IDs by right-clicking a channel → "Copy link"
# The ID is the last part of the URL (e.g., C0123456789)
# ─────────────────────────────────────────────────────────────
SOCIAL_CHANNELS = [
    # "C0123456789",   # #equipo-social
    # "C9876543210",   # #general
]

# Channel for celebrations (birthdays, anniversaries, achievements)
CELEBRATION_CHANNEL = ""  # e.g., "C0123456789"

# ─────────────────────────────────────────────────────────────
# SCHEDULE CONFIGURATION
# Times are in 24-hour format. Timezone is configurable below.
# ─────────────────────────────────────────────────────────────
TIMEZONE = "America/Chicago"  # Change to your timezone

SCHEDULE = {
    # Daily morning motivation (Mon-Fri at 8:30 AM)
    "daily_motivation": {
        "enabled": True,
        "days": ["mon", "tue", "wed", "thu", "fri"],
        "hour": 8,
        "minute": 30,
        "category": "motivacion",
    },
    # Dynamic question (Tuesday and Thursday at 10:00 AM)
    "dynamic_question": {
        "enabled": True,
        "days": ["tue", "thu"],
        "hour": 10,
        "minute": 0,
        "category": "preguntas",
    },
    # Sharing invitation (Wednesday at 11:00 AM)
    "sharing_invite": {
        "enabled": True,
        "days": ["wed"],
        "hour": 11,
        "minute": 0,
        "category": "compartir",
    },
    # Recognition moment (Friday at 4:00 PM)
    "recognition": {
        "enabled": True,
        "days": ["fri"],
        "hour": 16,
        "minute": 0,
        "category": "reconocimiento",
    },
    # Fun content (Wednesday at 12:30 PM)
    "fun_content": {
        "enabled": True,
        "days": ["wed"],
        "hour": 12,
        "minute": 30,
        "category": "diversion",
    },
    # Team culture (Monday at 9:00 AM)
    "team_culture": {
        "enabled": True,
        "days": ["mon"],
        "hour": 9,
        "minute": 0,
        "category": "cultura",
    },
    # Weekly reflection (Friday at 5:00 PM)
    "weekly_reflection": {
        "enabled": True,
        "days": ["fri"],
        "hour": 17,
        "minute": 0,
        "category": "reflexion",
    },
    # Random member mention (Mon, Wed, Fri at 2:00 PM)
    "random_mention": {
        "enabled": True,
        "days": ["mon", "wed", "fri"],
        "hour": 14,
        "minute": 0,
    },
    # Birthday check (every day at 8:00 AM)
    "birthday_check": {
        "enabled": True,
        "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        "hour": 8,
        "minute": 0,
    },
    # Anniversary check (every day at 8:05 AM)
    "anniversary_check": {
        "enabled": True,
        "days": ["mon", "tue", "wed", "thu", "fri"],
        "hour": 8,
        "minute": 5,
    },
}

# ─────────────────────────────────────────────────────────────
# MENTION SETTINGS
# ─────────────────────────────────────────────────────────────
# How many members to mention at once (1 = one at a time)
MENTION_COUNT = 1

# Exclude these Slack user IDs from random mentions (e.g., bots, admins)
MENTION_EXCLUDE_IDS = []

# ─────────────────────────────────────────────────────────────
# ANTI-SPAM SETTINGS
# ─────────────────────────────────────────────────────────────
# Minimum hours between posts in the same channel
MIN_HOURS_BETWEEN_POSTS = 2

# Maximum posts per day per channel
MAX_POSTS_PER_DAY = 4
