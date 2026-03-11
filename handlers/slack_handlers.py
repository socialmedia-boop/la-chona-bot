"""
La Chona – Slack Event Handlers
Handles slash commands, mentions, DMs, and interactive actions.
Now powered by AI brain for natural language understanding.
"""

import logging
import time
from collections import OrderedDict
from messages.library import get_random_message, MENCIONES_TEMPLATES
from utils.celebrations import add_member, add_achievement, get_all_active_members
from utils.mentions import build_mention_message, format_mention
from utils.ai_brain import get_ai_response

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Deduplication cache: stores processed event ts values
# Prevents duplicate responses when Slack sends the same event twice
# ─────────────────────────────────────────────
_processed_events = OrderedDict()
_MAX_CACHE_SIZE = 500
_DEDUP_WINDOW_SECONDS = 30


def _is_duplicate(event_ts: str) -> bool:
    """Return True if this event was already processed recently."""
    now = time.time()
    # Clean up old entries
    cutoff = now - _DEDUP_WINDOW_SECONDS
    keys_to_delete = [k for k, v in _processed_events.items() if v < cutoff]
    for k in keys_to_delete:
        del _processed_events[k]
    # Trim if too large
    while len(_processed_events) > _MAX_CACHE_SIZE:
        _processed_events.popitem(last=False)
    # Check and mark
    if event_ts in _processed_events:
        return True
    _processed_events[event_ts] = now
    return False


def _get_user_name(client, user_id: str) -> str:
    """Get the first name of a Slack user."""
    try:
        user_info = client.users_info(user=user_id)
        name = user_info["user"]["profile"].get("display_name") or user_info["user"]["profile"].get("real_name", "")
        return name.split()[0] if name else ""
    except Exception:
        return ""


def register_handlers(app):
    """Register all Slack event handlers."""

    # ─────────────────────────────────────────────
    # App Home Tab
    # ─────────────────────────────────────────────
    @app.event("app_home_opened")
    def handle_app_home(client, event, logger):
        user_id = event["user"]
        try:
            client.views_publish(
                user_id=user_id,
                view={
                    "type": "home",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {"type": "plain_text", "text": "🌟 La Chona", "emoji": True}
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    "*Tu bot de cultura de equipo y socialización* 🎉\n\n"
                                    "Estoy aquí para mantener al equipo conectado, motivado y celebrado. "
                                    "Publico mensajes automáticos, hago preguntas dinámicas, menciono "
                                    "miembros aleatoriamente y celebro cumpleaños y aniversarios.\n\n"
                                    "*Comandos disponibles:*\n"
                                    "• `/lachona motivacion` — Publica un mensaje motivacional ahora\n"
                                    "• `/lachona pregunta` — Publica una pregunta dinámica ahora\n"
                                    "• `/lachona mencionar` — Menciona a un miembro aleatorio\n"
                                    "• `/lachona celebrar @nombre logro` — Celebra un logro\n"
                                    "• `/lachona agregar-miembro` — Agrega un miembro al equipo\n"
                                    "• `/lachona categorias` — Ver todas las categorías disponibles"
                                )
                            }
                        },
                        {"type": "divider"},
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "💪 Ver Motivación", "emoji": True},
                                    "value": "motivacion",
                                    "action_id": "preview_motivacion",
                                    "style": "primary"
                                },
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "🤔 Ver Pregunta", "emoji": True},
                                    "value": "preguntas",
                                    "action_id": "preview_pregunta"
                                },
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "🎉 Ver Diversión", "emoji": True},
                                    "value": "diversion",
                                    "action_id": "preview_diversion"
                                }
                            ]
                        }
                    ]
                }
            )
        except Exception as e:
            logger.error(f"App Home error: {e}")

    # ─────────────────────────────────────────────
    # /lachona Slash Command
    # ─────────────────────────────────────────────
    @app.command("/lachona")
    def handle_pulse_command(ack, body, say, client, logger):
        ack()
        text = body.get("text", "").strip().lower()
        channel_id = body.get("channel_id")
        user_id = body.get("user_id")

        if not text or text == "help" or text == "ayuda":
            say(text=(
                "🌟 *La Chona – Comandos disponibles:*\n\n"
                "• `/lachona motivacion` — Publica motivación ahora\n"
                "• `/lachona pregunta` — Publica una pregunta dinámica\n"
                "• `/lachona compartir` — Invita a compartir algo\n"
                "• `/lachona reconocimiento` — Momento de reconocimiento\n"
                "• `/lachona diversion` — Contenido divertido\n"
                "• `/lachona cultura` — Reflexión de cultura de equipo\n"
                "• `/lachona reflexion` — Reflexión de cierre\n"
                "• `/lachona mencionar` — Menciona a un miembro aleatorio\n"
                "• `/lachona celebrar @nombre Tu logro aquí` — Celebra un logro\n"
                "• `/lachona categorias` — Ver todas las categorías"
            ))
            return

        valid_categories = ["motivacion", "pregunta", "compartir", "reconocimiento", "diversion", "cultura", "reflexion"]

        if text in valid_categories or text == "preguntas":
            cat = "preguntas" if text == "pregunta" else text
            message = get_random_message(cat)
            client.chat_postMessage(channel=channel_id, text=message)

        elif text == "mencionar":
            message = build_mention_message(client)
            if message:
                client.chat_postMessage(channel=channel_id, text=message)
            else:
                say(text="⚠️ No hay miembros disponibles para mencionar.")

        elif text.startswith("celebrar"):
            parts = body.get("text", "").strip().split(" ", 2)
            if len(parts) >= 3:
                nombre = parts[1]
                logro = parts[2]
                from messages.library import get_achievement_message
                message = get_achievement_message(nombre, logro)
                client.chat_postMessage(channel=channel_id, text=message)
            else:
                say(text="⚠️ Uso: `/lachona celebrar @nombre Descripción del logro`")

        elif text == "categorias":
            say(text=(
                "📋 *Categorías disponibles:*\n\n"
                "• `motivacion` — Mensajes motivacionales diarios\n"
                "• `pregunta` — Preguntas dinámicas del equipo\n"
                "• `compartir` — Invitaciones a compartir fotos, historias y logros\n"
                "• `reconocimiento` — Momentos de reconocimiento entre compañeros\n"
                "• `diversion` — Contenido divertido y juegos\n"
                "• `cultura` — Reflexiones de cultura de equipo\n"
                "• `reflexion` — Reflexiones de cierre de semana"
            ))
        else:
            say(text=f"❓ Comando no reconocido: `{text}`.")

    # ─────────────────────────────────────────────
    # App Mention (@La Chona in channels)
    # ─────────────────────────────────────────────
    @app.event("app_mention")
    def handle_mention(event, body, say, client, logger):
        import re
        # Deduplicate using event_id (globally unique per event, same across all instances)
        event_id = body.get("event_id", event.get("ts", ""))
        if _is_duplicate(event_id):
            logger.info(f"Skipping duplicate app_mention event: {event_id}")
            return

        raw_text = event.get("text", "")
        text = re.sub(r"<@[A-Z0-9]+>", "", raw_text).strip()
        user_id = event.get("user", "")
        user_name = _get_user_name(client, user_id)

        reply = get_ai_response(text, user_name, user_id)
        say(text=reply)

    # ─────────────────────────────────────────────
    # Direct Messages to La Chona (DMs only)
    # ─────────────────────────────────────────────
    @app.event({"type": "message", "channel_type": "im"})
    def handle_dm(event, body, say, client, logger):
        # Ignore bot messages and empty messages
        if event.get("bot_id") or event.get("subtype") or not event.get("text", "").strip():
            return

        # Deduplicate using event_id (globally unique per event, same across all instances)
        event_id = body.get("event_id", event.get("ts", ""))
        if _is_duplicate(event_id):
            logger.info(f"Skipping duplicate DM event: {event_id}")
            return

        text = event.get("text", "").strip()
        user_id = event.get("user", "")
        user_name = _get_user_name(client, user_id)

        reply = get_ai_response(text, user_name, user_id)
        say(text=reply)

    # ─────────────────────────────────────────────
    # Button Action Handlers (App Home previews)
    # ─────────────────────────────────────────────
    @app.action("preview_motivacion")
    def preview_motivacion(ack, body, say):
        ack()
        say(text=get_random_message("motivacion"))

    @app.action("preview_pregunta")
    def preview_pregunta(ack, body, say):
        ack()
        say(text=get_random_message("preguntas"))

    @app.action("preview_diversion")
    def preview_diversion(ack, body, say):
        ack()
        say(text=get_random_message("diversion"))

    # ─────────────────────────────────────────────
    # Catch-all message handler (prevent unhandled event warnings)
    # ─────────────────────────────────────────────
    @app.event("message")
    def handle_message(event, logger):
        # Silently ignore — channel mentions handled by app_mention, DMs by im handler
        pass

    logger.info("✅ All La Chona handlers registered.")
