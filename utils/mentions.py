"""
Team Culture Bot – Random Member Mention Engine
Selects random members to mention, avoiding repetition.
"""

import random
import logging
from collections import deque
from utils.celebrations import get_all_active_members
from config.settings import MENTION_EXCLUDE_IDS, MENTION_COUNT

logger = logging.getLogger(__name__)

# Track recently mentioned users to avoid repetition (last 5 mentions)
_recently_mentioned = deque(maxlen=5)


def get_workspace_members(client) -> list[dict]:
    """Fetch all active, non-bot workspace members from Slack API."""
    try:
        result = client.users_list()
        members = []
        for user in result.get("members", []):
            if (
                not user.get("is_bot")
                and not user.get("deleted")
                and not user.get("is_app_user")
                and user.get("id") != "USLACKBOT"
                and user.get("id") not in MENTION_EXCLUDE_IDS
            ):
                members.append({
                    "id": user["id"],
                    "name": user.get("real_name") or user.get("name", ""),
                    "display_name": user.get("profile", {}).get("display_name", ""),
                })
        return members
    except Exception as e:
        logger.error(f"Error fetching workspace members: {e}")
        return []


def get_random_members_from_slack(client, count: int = 1) -> list[dict]:
    """Get random members from the Slack workspace, avoiding recent repeats."""
    all_members = get_workspace_members(client)
    if not all_members:
        # Fall back to team.json members
        all_members = [
            {"id": m.get("slack_id", ""), "name": m["name"]}
            for m in get_all_active_members()
            if m.get("slack_id")
        ]

    # Filter out recently mentioned
    available = [m for m in all_members if m["id"] not in _recently_mentioned]
    if len(available) < count:
        available = all_members  # Reset if pool is too small

    selected = random.sample(available, min(count, len(available)))

    # Track mentions
    for member in selected:
        _recently_mentioned.append(member["id"])

    return selected


def format_mention(slack_id: str) -> str:
    """Format a Slack user mention."""
    if slack_id:
        return f"<@{slack_id}>"
    return "@equipo"


def build_mention_message(client) -> str:
    """Build a message with a random member mention."""
    from messages.library import get_random_mention_template

    members = get_random_members_from_slack(client, count=MENTION_COUNT)
    if not members:
        return None

    template = get_random_mention_template()
    member = members[0]
    mention_str = format_mention(member["id"]) if member.get("id") else f"*{member['name']}*"

    return template.replace("{mencion}", mention_str)
