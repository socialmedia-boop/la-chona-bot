"""
La Chona – Main Entry Point
Team Culture & Socialization Slack Bot

Features:
  - Scheduled motivational messages (Mon-Fri)
  - Dynamic team questions (Tue, Thu)
  - Sharing invitations (Wed)
  - Recognition moments (Fri)
  - Fun content (Wed midday)
  - Random member mentions (Mon, Wed, Fri)
  - Birthday celebrations (daily check)
  - Work anniversary celebrations (daily check)
  - Achievement announcements
  - /lachona slash command for manual triggers
  - Bilingual: Spanish (default) + English

Usage:
    python3 app.py
"""

import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config.settings import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_SIGNING_SECRET
from handlers.slack_handlers import register_handlers
from utils.scheduler import setup_scheduler

# ─────────────────────────────────────────────
# Load environment variables
# ─────────────────────────────────────────────
load_dotenv()

# ─────────────────────────────────────────────
# Configure logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Validate credentials
# ─────────────────────────────────────────────
required = {
    "SLACK_BOT_TOKEN_CULTURE": SLACK_BOT_TOKEN,
    "SLACK_APP_TOKEN_CULTURE": SLACK_APP_TOKEN,
    "SLACK_SIGNING_SECRET_CULTURE": SLACK_SIGNING_SECRET,
}
missing = [k for k, v in required.items() if not v]
if missing:
    logger.error(f"❌ Missing environment variables: {', '.join(missing)}")
    logger.error("Copy .env.example to .env and fill in your Slack credentials.")
    raise SystemExit(1)

# ─────────────────────────────────────────────
# Initialize Slack Bolt App
# ─────────────────────────────────────────────
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# ─────────────────────────────────────────────
# Pre-load team profiles in background (so first response is fast)
# ─────────────────────────────────────────────
try:
    from utils.slack_profiles import preload_members_background
    preload_members_background()
except Exception as e:
    logger.warning(f"Could not start profile preloader: {e}")

# ─────────────────────────────────────────────
# Register handlers
# ─────────────────────────────────────────────
register_handlers(app)

# ─────────────────────────────────────────────
# Start scheduler
# ─────────────────────────────────────────────
scheduler = setup_scheduler(app, app.client)

# ─────────────────────────────────────────────
# Launch bot
# ─────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("🌟 Starting La Chona — Team Culture & Socialization Assistant")
    logger.info("📅 Scheduler is running with all configured jobs")
    logger.info("📡 Connecting to Slack via Socket Mode...")

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)

    logger.info("✅ La Chona is LIVE!")
    logger.info("💬 Use /lachona help in Slack to see all commands")
    logger.info("Press Ctrl+C to stop.")

    handler.start()
