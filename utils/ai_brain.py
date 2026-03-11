"""
La Chona – AI Brain
Uses OpenAI to understand and respond to natural language questions in Spanish and English.
La Chona has a fun, warm, motivating personality and knows about the team.
"""

import os
import json
import logging
from datetime import datetime, date
import pytz

logger = logging.getLogger(__name__)

# Load OpenAI — uses sandbox pre-configured client
try:
    from openai import OpenAI
    # Use sandbox default config (API key and base URL pre-configured)
    client_ai = OpenAI()
    AI_AVAILABLE = True
except Exception as e:
    logger.warning(f"OpenAI not available: {e}")
    AI_AVAILABLE = False

TIMEZONE = "America/Chicago"

# ─────────────────────────────────────────────
# Load team data — from LIVE Slack profiles (with JSON fallback)
# ─────────────────────────────────────────────
def load_team_context():
    """Load team members from live Slack profiles, fallback to team.json."""
    try:
        from utils.slack_profiles import fetch_all_members
        members = fetch_all_members()
        if members:
            return members
    except Exception as e:
        logger.warning(f"Could not fetch from Slack profiles: {e}")
    # Fallback to local JSON
    try:
        data_path = os.path.join(os.path.dirname(__file__), "../data/team.json")
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [m for m in data.get("members", []) if m.get("active", True)]
    except Exception:
        return []


def get_next_birthday(members):
    """Find who has the next upcoming birthday."""
    try:
        from utils.slack_profiles import get_next_birthday as slack_next_bday
        result = slack_next_bday(members)
        if result:
            return (result["days"], result["name"], result["date_es"])
    except Exception:
        pass
    # Fallback to manual calculation
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
            upcoming.append((days_until, m["name"], bday_this_year.strftime("%B %d")))
        except Exception:
            continue
    if upcoming:
        upcoming.sort()
        return upcoming[0]
    return None


def build_team_summary(members):
    """Build a text summary of the team for AI context."""
    try:
        from utils.slack_profiles import build_team_summary_from_slack
        summary = build_team_summary_from_slack()
        if summary and "no tiene miembros" not in summary:
            return summary
    except Exception:
        pass
    # Fallback to local data
    if not members:
        return "El equipo aún no tiene miembros registrados."
    lines = []
    today = date.today()
    for m in members:
        line = f"- {m['name']} ({m.get('role', 'Miembro')})"
        bday = m.get("birthday", "")
        if bday:
            try:
                month, day = map(int, bday.split("-"))
                bday_date = date(today.year, month, day)
                if bday_date < today:
                    bday_date = date(today.year + 1, month, day)
                days = (bday_date - today).days
                line += f", cumpleaños: {bday_date.strftime('%B %d')} (en {days} días)"
            except Exception:
                line += f", cumpleaños: {bday}"
        ann = m.get("anniversary", "")
        if ann:
            try:
                ann_date = datetime.strptime(ann, "%Y-%m-%d").date()
                years = today.year - ann_date.year
                if (today.month, today.day) < (ann_date.month, ann_date.day):
                    years -= 1
                if years >= 1:
                    line += f", lleva {years} año(s) en la empresa"
                else:
                    line += f", nuevo integrante (menos de 1 año)"
            except Exception:
                pass
        lines.append(line)
    return "\n".join(lines)


def get_scheduled_summary():
    """Return what La Chona has planned for tomorrow."""
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    tomorrow = now.strftime("%A")  # day name
    
    day_map = {
        "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
        "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"
    }
    
    schedule_info = {
        "lunes": "Mensaje motivacional a las 8:30 AM, reflexión de cultura de equipo a las 9:00 AM, y mención aleatoria a las 2:00 PM.",
        "martes": "Mensaje motivacional a las 8:30 AM y pregunta dinámica del equipo a las 10:00 AM.",
        "miércoles": "Mensaje motivacional a las 8:30 AM, invitación a compartir fotos o historias a las 11:00 AM, contenido divertido al mediodía, y mención aleatoria a las 2:00 PM.",
        "jueves": "Mensaje motivacional a las 8:30 AM y pregunta dinámica del equipo a las 10:00 AM.",
        "viernes": "Mensaje motivacional a las 8:30 AM, momento de reconocimiento a las 4:00 PM, reflexión semanal a las 5:00 PM, y mención aleatoria a las 2:00 PM.",
        "sábado": "¡Descanso! No publico mensajes los fines de semana para no interrumpir el tiempo libre del equipo. 😊",
        "domingo": "¡Descanso! No publico mensajes los fines de semana. ¡Que disfruten! 😊"
    }
    
    # Get tomorrow's day
    import calendar
    tomorrow_num = (now.weekday() + 1) % 7  # 0=Monday
    days_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    tomorrow_es = days_es[tomorrow_num]
    
    return tomorrow_es, schedule_info.get(tomorrow_es, "Tengo mensajes motivacionales y dinámicas planeadas.")


# ─────────────────────────────────────────────
# Main AI Response Function
# ─────────────────────────────────────────────
def get_ai_response(user_message: str, user_name: str = "") -> str:
    """
    Generate an intelligent, personalized response from La Chona using AI.
    Falls back to smart keyword matching if AI is unavailable.
    """
    members = load_team_context()
    team_summary = build_team_summary(members)
    next_bday = get_next_birthday(members)
    tomorrow_day, tomorrow_schedule = get_scheduled_summary()

    # Get next anniversary (1+ full years only)
    next_ann_text = ""
    try:
        from utils.slack_profiles import get_next_anniversary
        next_ann = get_next_anniversary(members)
        if next_ann:
            if next_ann["days"] == 0:
                next_ann_text = f"¡HOY {next_ann['name']} cumple {next_ann['years']} año(s) en la empresa!"
            elif next_ann["days"] == 1:
                next_ann_text = f"Mañana {next_ann['name']} cumple {next_ann['years']} año(s) en la empresa."
            else:
                next_ann_text = f"El próximo aniversario laboral es de {next_ann['name']}, quien cumplirá {next_ann['years']} año(s) el {next_ann['date_es']} (en {next_ann['days']} días)."
    except Exception:
        pass

    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    current_time = now.strftime("%A %B %d, %Y at %I:%M %p %Z")

    next_bday_text = ""
    if next_bday:
        days_until, bday_name, bday_date = next_bday
        if days_until == 0:
            next_bday_text = f"¡HOY es el cumpleaños de {bday_name}!"
        elif days_until == 1:
            next_bday_text = f"Mañana es el cumpleaños de {bday_name} ({bday_date})."
        else:
            next_bday_text = f"El próximo cumpleaños es de {bday_name} el {bday_date} (en {days_until} días)."

    system_prompt = f"""Eres La Chona, el bot de cultura de equipo y socialización de esta empresa. 
Tu personalidad es: amigable, motivadora, divertida sin exagerar, cercana y positiva. 
Hablas principalmente en español pero entiendes inglés. 
Usas emojis con moderación para ser expresiva pero profesional.
Eres como esa compañera de trabajo que siempre sabe cómo animar al equipo.

INFORMACIÓN ACTUAL:
- Fecha y hora: {current_time}
- Mañana es {tomorrow_day}
- Plan de mañana: {tomorrow_schedule}
- {next_bday_text}
- {next_ann_text}

IMPORTANTE SOBRE ANIVERSARIOS: Solo celebra aniversarios de empleados que han completado 1 o más años completos. No menciones aniversarios de personas con menos de 1 año en la empresa.

EQUIPO DE LA EMPRESA:
{team_summary}

TUS FUNCIONES:
- Publicar mensajes motivacionales automáticos de lunes a viernes
- Hacer preguntas dinámicas para fomentar la interacción
- Mencionar miembros aleatoriamente para que participen
- Celebrar cumpleaños, aniversarios laborales y logros
- Responder preguntas sobre el equipo, los horarios y la cultura de empresa

REGLAS IMPORTANTES:
- Responde siempre de forma natural, como si fuera una conversación real
- Si te preguntan sobre mañana o tus planes, menciona lo que tienes programado
- Si te preguntan sobre cumpleaños, usa la información del equipo que tienes
- Mantén las respuestas cortas y directas (máximo 3-4 oraciones)
- Si no sabes algo específico, sé honesta pero positiva
- NO repitas siempre el mismo mensaje genérico — adapta tu respuesta al contexto
- Si el usuario se llama {user_name if user_name else 'alguien del equipo'}, úsalo en la respuesta para hacerlo más personal"""

    if not AI_AVAILABLE:
        return _smart_fallback(user_message, next_bday, tomorrow_day, tomorrow_schedule, user_name)

    try:
        response = client_ai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
            temperature=0.85,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"AI response error: {e}")
        return _smart_fallback(user_message, next_bday, tomorrow_day, tomorrow_schedule, user_name)


def _smart_fallback(message: str, next_bday, tomorrow_day: str, tomorrow_schedule: str, user_name: str = "") -> str:
    """Smart keyword fallback when AI is not available."""
    msg = message.lower()
    name = f", {user_name}" if user_name else ""

    if any(w in msg for w in ["mañana", "tomorrow", "harás", "haras", "planeas", "plan"]):
        return f"¡Mañana es {tomorrow_day}! 📅 Tengo planeado: {tomorrow_schedule} ¿Listo para otro gran día{name}? 💪"

    if any(w in msg for w in ["cumpleaños", "birthday", "próximo", "siguiente", "quien cumple"]):
        if next_bday:
            days, name_bday, bday_date = next_bday
            if days == 0:
                return f"🎂 ¡HOY es el cumpleaños de *{name_bday}*! ¡Vayan a felicitarlo/a! 🎉"
            elif days == 1:
                return f"🎂 ¡Mañana es el cumpleaños de *{name_bday}*! Preparen los confetis 🎊"
            else:
                return f"🎂 El próximo cumpleaños es de *{name_bday}* el {bday_date} — ¡faltan solo {days} días! 🎉"
        return "Aún no tengo cumpleaños registrados en el equipo. ¡Pídele al admin que los agregue en `data/team.json`! 📋"

    if any(w in msg for w in ["hola", "hello", "hi", "buenos", "buenas"]):
        return f"¡Hola{name}! 👋 Soy *La Chona*, tu bot de cultura de equipo. Pregúntame lo que quieras o usa `/lachona help` para ver mis comandos. 🌟"

    if any(w in msg for w in ["motivaci", "ánimo", "animo", "inspire"]):
        from messages.library import get_random_message
        return get_random_message("motivacion")

    if any(w in msg for w in ["pregunta", "question", "dinámica"]):
        from messages.library import get_random_message
        return get_random_message("preguntas")

    if any(w in msg for w in ["equipo", "team", "miembro", "quien", "quién"]):
        members = load_team_context()
        if members:
            names = ", ".join([m["name"] for m in members])
            return f"👥 Nuestro equipo está formado por: *{names}*. ¡Un equipo increíble! 🌟"
        return "Aún no tengo los datos del equipo configurados. ¡Pídele al admin que los agregue! 📋"

    return (
        f"¡Buena pregunta{name}! 🤔 Soy *La Chona* y estoy aquí para mantener al equipo motivado y conectado. "
        "Usa `/lachona help` para ver todo lo que puedo hacer. 🌟"
    )
