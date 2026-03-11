# 🌟 La Chona — Bot de Cultura de Equipo para Slack
### Guía Completa: Arquitectura, Instalación, Configuración y Ejemplos

---

## ¿Qué es La Chona?

**La Chona** es un bot de Slack diseñado para fortalecer la cultura de equipo, fomentar la socialización y mantener al equipo motivado de forma constante, amigable y no invasiva. Publica mensajes automáticos en los canales configurados, hace preguntas dinámicas, menciona miembros aleatoriamente, y celebra cumpleaños, aniversarios laborales y logros del equipo — todo en español e inglés.

---

## Arquitectura del Sistema

La arquitectura de La Chona sigue un diseño modular de tres capas: la capa de mensajería (biblioteca de contenido), la capa de lógica (motor de programación y celebraciones), y la capa de integración (Slack via Socket Mode).

```
┌─────────────────────────────────────────────────────────┐
│                    SLACK WORKSPACE                       │
│  Canales: #equipo-social, #general, #celebraciones      │
└──────────────────────┬──────────────────────────────────┘
                       │ Socket Mode (WebSocket)
┌──────────────────────▼──────────────────────────────────┐
│                   LA CHONA BOT                           │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Scheduler  │  │   Handlers   │  │  /lachona cmd │  │
│  │ (APScheduler│  │ (Slack Bolt) │  │  Slash Command│  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                │                   │          │
│  ┌──────▼────────────────▼───────────────────▼───────┐  │
│  │              Message Library                       │  │
│  │  Motivación │ Preguntas │ Compartir │ Diversión   │  │
│  │  Reconocimiento │ Cultura │ Reflexión │ Menciones  │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Celebration Engine                      │   │
│  │  Cumpleaños │ Aniversarios │ Logros │ team.json  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Tecnologías Utilizadas

| Componente | Tecnología | Razón |
|---|---|---|
| Lenguaje | Python 3.11 | Estable, amplio ecosistema, fácil mantenimiento |
| Framework Slack | Slack Bolt for Python | SDK oficial de Slack, Socket Mode nativo |
| Programador de tareas | APScheduler | Ligero, sin dependencias externas, cron-compatible |
| Conexión Slack | Socket Mode | No requiere URL pública ni servidor web |
| Datos del equipo | JSON local | Simple, editable sin base de datos |
| Variables de entorno | python-dotenv | Seguridad de credenciales |

---

## Estructura de Archivos

```
team-culture-bot/
├── app.py                          # Punto de entrada principal
├── requirements.txt                # Dependencias Python
├── .env.example                    # Plantilla de credenciales
├── slack_app_manifest.yaml         # Manifiesto para crear la app en Slack
│
├── config/
│   └── settings.py                 # ⚙️ CONFIGURACIÓN PRINCIPAL (canales, horarios)
│
├── messages/
│   └── library.py                  # 📚 Biblioteca de mensajes (100+ mensajes)
│
├── handlers/
│   └── slack_handlers.py           # Manejadores de eventos Slack
│
├── utils/
│   ├── scheduler.py                # Motor de programación automática
│   ├── celebrations.py             # Motor de celebraciones
│   └── mentions.py                 # Motor de menciones aleatorias
│
└── data/
    └── team.json                   # 👥 DATOS DEL EQUIPO (cumpleaños, aniversarios)
```

---

## Flujo de Funcionamiento

La Chona opera en tres modos simultáneos:

**Modo Automático (Scheduler):** APScheduler ejecuta tareas según el horario configurado en `config/settings.py`. Cada mañana de lunes a viernes publica un mensaje motivacional, los martes y jueves hace preguntas dinámicas, los miércoles invita a compartir, los viernes celebra reconocimientos y reflexiones. Además, cada día a las 8:00 AM revisa si hay cumpleaños o aniversarios que celebrar.

**Modo Reactivo (Handlers):** Cuando alguien menciona `@La Chona` en un canal o le envía un mensaje directo, el bot responde de forma inteligente según el contexto del mensaje.

**Modo Manual (/lachona):** Cualquier miembro del equipo puede usar el comando `/lachona` para activar contenido inmediatamente sin esperar el horario programado.

---

## Categorías de Mensajes

La biblioteca de mensajes contiene más de **100 mensajes únicos** organizados en 7 categorías:

| Categoría | Cantidad | Frecuencia | Ejemplo |
|---|---|---|---|
| Motivación | 15 mensajes | Lun-Vie 8:30 AM | *"¡Buenos días, equipo! Cada día es una nueva oportunidad..."* |
| Preguntas Dinámicas | 20 mensajes | Mar y Jue 10:00 AM | *"¿Quién fue tu MVP de esta semana?"* |
| Compartir | 15 mensajes | Miér 11:00 AM | *"📸 ¡Momento foto! Comparte algo que te motivó hoy..."* |
| Reconocimiento | 8 mensajes | Vie 4:00 PM | *"¿Quién del equipo merece un aplauso esta semana?"* |
| Diversión | 10 mensajes | Miér 12:30 PM | *"Si nuestro equipo fuera un superhéroe, su superpoder sería..."* |
| Cultura de Equipo | 8 mensajes | Lun 9:00 AM | *"Los equipos que aprenden juntos, crecen juntos..."* |
| Reflexión | 8 mensajes | Vie 5:00 PM | *"Antes de terminar el día, escribe UNA cosa por la que estás agradecido..."* |
| Menciones Aleatorias | 10 plantillas | Lun, Miér, Vie 2:00 PM | *"@Keila, ¡te toca! Comparte algo positivo de tu semana."* |

---

## Ejemplos de Mensajes Reales

### Motivación (Lunes 8:30 AM)
> ☀️ *¡Buenos días, equipo!* Recuerden: cada día es una nueva oportunidad para hacer algo increíble. ¿Cuál es su intención para hoy?

### Pregunta Dinámica (Martes 10:00 AM)
> 🤔 *Pregunta de la semana:* ¿Quién sería el empleado del mes en tu área este mes y por qué? ¡Menciónalos!

### Invitación a Compartir (Miércoles 11:00 AM)
> 📸 *¡Momento foto!* Comparte una foto de algo que te motivó hoy — puede ser tu café, tu escritorio, tu mascota o el paisaje desde tu ventana. ¡Todo cuenta! 🌟

### Mención Aleatoria (Lunes 2:00 PM)
> 👋 *@Arturo, ¡te toca!* Comparte algo positivo que te haya pasado esta semana. ¡El equipo quiere saberlo! 🌟

### Cumpleaños (Automático)
> 🎂🎉 *¡HOY ES EL CUMPLEAÑOS DE @Keila!* 🎉🎂
> Equipo, démosle un enorme abrazo virtual a @Keila en su día especial. ¡Que este año esté lleno de éxitos, salud y mucha felicidad! 🥳🎈

### Aniversario Laboral (Automático)
> 🏆✨ *@Juan cumple 3 año(s) con nosotros hoy!* ✨🏆
> Equipo, démosle un enorme reconocimiento a @Juan por su dedicación y compromiso. ¡3 años de hacer grande a este equipo! 🙌🎉

### Reconocimiento de Logro (Manual)
> 🏆 *¡LOGRO DESBLOQUEADO!* 🏆
> *@María* acaba de lograr: *Certificación en Seguros Comerciales* 🎉
> ¡Equipo, démosle el reconocimiento que se merece!

---

## Instalación Paso a Paso

### Paso 1 — Crear la App en Slack

1. Ve a **[https://api.slack.com/apps](https://api.slack.com/apps)**
2. Haz clic en **"Create New App"** → **"From an app manifest"**
3. Selecciona tu workspace → cambia la pestaña a **YAML**
4. Borra todo el contenido y pega el contenido completo de `slack_app_manifest.yaml`
5. Haz clic en **Next** → **Create**

### Paso 2 — Habilitar Socket Mode y obtener App Token

1. En el menú izquierdo: **Settings → Socket Mode**
2. Activa **"Enable Socket Mode"**
3. Nombra el token `la-chona-socket`
4. Haz clic en **Generate** → copia el token `xapp-...`

### Paso 3 — Instalar la App y obtener Bot Token

1. En el menú izquierdo: **Settings → Install App**
2. Haz clic en **"Install to Workspace"** → **Allow**
3. Copia el **Bot User OAuth Token** (`xoxb-...`)

### Paso 4 — Obtener el Signing Secret

1. En el menú izquierdo: **Basic Information → App Credentials**
2. Haz clic en **Show** junto a **Signing Secret** → cópialo

### Paso 5 — Agregar el Slash Command /lachona

1. En el menú izquierdo: **Features → Slash Commands**
2. Haz clic en **"Create New Command"**
3. Llena los campos:
   - Command: `/lachona`
   - Short Description: `Activa La Chona manualmente`
   - Usage Hint: `help | motivacion | pregunta | mencionar | celebrar`
4. Haz clic en **Save**
5. Reinstala la app: **Settings → Install App → Reinstall**

### Paso 6 — Configurar el archivo .env

Copia `.env.example` a `.env` y llena tus credenciales:

```env
SLACK_BOT_TOKEN_CULTURE=xoxb-tu-bot-token
SLACK_APP_TOKEN_CULTURE=xapp-tu-app-token
SLACK_SIGNING_SECRET_CULTURE=tu-signing-secret
```

### Paso 7 — Configurar Canales y Horarios

Edita `config/settings.py`:

```python
# IDs de los canales donde La Chona publicará
SOCIAL_CHANNELS = [
    "C0123456789",   # #equipo-social
]

# Canal para celebraciones
CELEBRATION_CHANNEL = "C0123456789"

# Zona horaria
TIMEZONE = "America/Chicago"
```

> **¿Cómo encontrar el ID de un canal?** En Slack, haz clic derecho en el canal → "Copy link". El ID es la última parte de la URL (empieza con `C`).

### Paso 8 — Cargar Cumpleaños y Aniversarios

Edita `data/team.json` con los datos de tu equipo:

```json
{
  "members": [
    {
      "name": "Arturo Salgado",
      "slack_id": "U0123456789",
      "birthday": "01-15",
      "anniversary": "2020-03-01",
      "role": "Team Lead",
      "active": true
    }
  ]
}
```

> **¿Cómo encontrar el Slack ID de un miembro?** En Slack, haz clic en el perfil del miembro → los tres puntos (···) → **"Copy member ID"**. El ID empieza con `U`.

### Paso 9 — Iniciar La Chona

```bash
cd team-culture-bot
pip3 install -r requirements.txt
python3 app.py
```

### Paso 10 — Agregar La Chona a los Canales

En cada canal de Slack donde quieras que publique:
```
/invite @La Chona
```

---

## Comandos Disponibles (/lachona)

| Comando | Descripción |
|---|---|
| `/lachona help` | Ver todos los comandos disponibles |
| `/lachona motivacion` | Publica un mensaje motivacional ahora |
| `/lachona pregunta` | Publica una pregunta dinámica ahora |
| `/lachona compartir` | Invita al equipo a compartir algo |
| `/lachona reconocimiento` | Momento de reconocimiento entre compañeros |
| `/lachona diversion` | Contenido divertido para el equipo |
| `/lachona cultura` | Reflexión de cultura de equipo |
| `/lachona reflexion` | Reflexión de cierre de semana |
| `/lachona mencionar` | Menciona a un miembro aleatorio |
| `/lachona celebrar @nombre Logro aquí` | Celebra un logro del equipo |
| `/lachona categorias` | Ver todas las categorías disponibles |

---

## Cómo Funciona la Mención Aleatoria

La Chona obtiene la lista de todos los miembros activos del workspace directamente desde la API de Slack (excluyendo bots y cuentas eliminadas). Utiliza un sistema de memoria de corto plazo que recuerda los últimos 5 miembros mencionados para evitar repetir a la misma persona. El resultado es una rotación natural y equitativa entre todo el equipo.

Para excluir a ciertos miembros de las menciones (por ejemplo, administradores o personas que prefieren no participar), agrega sus Slack IDs a la lista `MENTION_EXCLUDE_IDS` en `config/settings.py`.

---

## Horario Semanal de Publicaciones

| Hora | Lunes | Martes | Miércoles | Jueves | Viernes |
|---|---|---|---|---|---|
| 8:00 AM | Verificación cumpleaños | Verificación cumpleaños | Verificación cumpleaños | Verificación cumpleaños | Verificación cumpleaños |
| 8:30 AM | Motivación | Motivación | Motivación | Motivación | Motivación |
| 9:00 AM | Cultura de equipo | — | — | — | — |
| 10:00 AM | — | Pregunta dinámica | — | Pregunta dinámica | — |
| 11:00 AM | — | — | Invitación a compartir | — | — |
| 12:30 PM | — | — | Contenido divertido | — | — |
| 2:00 PM | Mención aleatoria | — | Mención aleatoria | — | Mención aleatoria |
| 4:00 PM | — | — | — | — | Reconocimiento |
| 5:00 PM | — | — | — | — | Reflexión semanal |

**Máximo 4 publicaciones por día por canal** (configurable en `settings.py`).

---

## Ideas para Futuras Mejoras

La arquitectura modular de La Chona facilita agregar nuevas funcionalidades:

**A corto plazo:** Integrar un panel de administración web para configurar horarios y cargar datos del equipo sin editar archivos. Agregar soporte para encuestas interactivas con botones de Slack (Block Kit). Implementar un sistema de "rachas" que reconozca a los miembros más participativos.

**A mediano plazo:** Conectar con Google Sheets o Airtable para gestionar los datos del equipo de forma colaborativa. Agregar integración con calendarios (Google Calendar, Outlook) para sincronizar automáticamente cumpleaños y aniversarios. Implementar un sistema de puntos y recompensas por participación.

**A largo plazo:** Agregar inteligencia artificial para personalizar los mensajes según el historial de participación de cada miembro. Crear un dashboard de métricas de engagement del equipo. Desarrollar una versión multiworkspace para empresas con múltiples equipos.

---

## Solución de Problemas Comunes

| Problema | Causa | Solución |
|---|---|---|
| Bot no publica mensajes | Canales no configurados | Agrega IDs de canales en `config/settings.py → SOCIAL_CHANNELS` |
| Error de credenciales | Variables de entorno vacías | Verifica que `.env` tenga los 3 tokens correctos |
| Bot no responde a menciones | No está en el canal | Usa `/invite @La Chona` en el canal |
| Cumpleaños no se celebran | Slack ID vacío en team.json | Agrega el Slack ID del miembro en `data/team.json` |
| Zona horaria incorrecta | TIMEZONE mal configurado | Cambia `TIMEZONE` en `config/settings.py` |

---

*La Chona fue construida con ❤️ para fortalecer equipos. ¡Que viva La Chona!* 🌟
