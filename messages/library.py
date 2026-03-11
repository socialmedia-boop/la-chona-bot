"""
Team Culture Bot – Message Library
All message templates organized by category.
Supports Spanish (default) and English.
"""

import random

# ─────────────────────────────────────────────────────────────
# CATEGORY: MOTIVACIÓN / MOTIVATION
# ─────────────────────────────────────────────────────────────
MOTIVACION = [
    "☀️ *¡Buenos días, equipo!* Recuerden: cada día es una nueva oportunidad para hacer algo increíble. ¿Cuál es su intención para hoy?",
    "💪 *El éxito no llega de la noche a la mañana, pero sí llega.* Sigan adelante, su esfuerzo vale más de lo que creen.",
    "🌟 *Dato del día:* Los equipos que se apoyan mutuamente son un 25% más productivos. ¡Ustedes ya lo están haciendo! 🙌",
    "🚀 *Pequeños pasos, grandes resultados.* ¿Qué pequeña acción puedes tomar hoy que te acerque a tu meta?",
    "🎯 *Recuerda:* No se trata de ser perfecto, se trata de ser constante. ¡Sigan así!",
    "🌈 *Hoy es un buen día para aprender algo nuevo.* ¿Qué habilidad te gustaría desarrollar este mes?",
    "💡 *Frase del día:* \"El trabajo en equipo hace que el sueño funcione.\" — John Maxwell",
    "🔥 *¡Mitad de semana!* Ya llegaron hasta aquí, ahora a terminar fuerte. ¿Qué les falta por lograr esta semana?",
    "🌻 *Recuerden tomarse un descanso hoy.* Una mente descansada es una mente creativa. ☕",
    "⭐ *Cada uno de ustedes aporta algo único a este equipo.* Hoy los invito a reconocer el talento de un compañero.",
    "🎉 *¡Viernes!* Antes de cerrar la semana, piensen: ¿de qué están más orgullosos de esta semana?",
    "🧠 *Tip de productividad:* Empieza el día con la tarea más difícil. Todo lo demás se sentirá más fácil después.",
    "💬 *\"Solo porque algo es difícil no significa que debes rendirte.\"* ¡Ustedes pueden con esto y más!",
    "🌍 *Trabajar en equipo es un superpoder.* Hoy, busca a un compañero y dile algo positivo.",
    "🏆 *El camino al éxito está pavimentado con pequeñas victorias diarias.* ¿Cuál fue la tuya hoy?",
]

# ─────────────────────────────────────────────────────────────
# CATEGORY: PREGUNTAS DINÁMICAS / DYNAMIC QUESTIONS
# ─────────────────────────────────────────────────────────────
PREGUNTAS_DINAMICAS = [
    "🤔 *Pregunta de la semana:* ¿Quién sería el empleado del mes en tu área este mes y por qué? ¡Menciónalos!",
    "🏅 *¿Quién crees que ganará la competencia de la compañía este mes?* ¡Vota en los comentarios!",
    "🌴 *¿Cuándo fue la última vez que tomaste vacaciones reales?* ¡Cuéntanos a dónde fuiste o a dónde quieres ir!",
    "🤝 *¿Qué compañero te ayudó más esta semana?* Dale un reconocimiento público aquí 👇",
    "🎯 *¿Qué meta te gustaría lograr este mes?* ¡Compártela aquí y el equipo te apoyará!",
    "🎨 *Si pudieras cambiar UNA cosa de tu espacio de trabajo, ¿qué sería?*",
    "🍕 *Pregunta importante:* Si el equipo pudiera tener un almuerzo juntos hoy, ¿qué pedirían?",
    "🎵 *¿Cuál es la canción que más escuchas cuando trabajas?* ¡Comparte tu playlist del trabajo!",
    "🌟 *¿Cuál ha sido tu mayor aprendizaje profesional este año?*",
    "😂 *¿Cuál es el meme que mejor describe tu semana?* ¡Súbelo aquí!",
    "🏠 *¿Prefieres trabajar desde casa, en la oficina o híbrido?* ¡Cuéntanos por qué!",
    "🚀 *Si pudieras agregar una herramienta o recurso a tu trabajo, ¿cuál sería?*",
    "💭 *¿Cuál es el consejo más valioso que alguien te ha dado en tu carrera?*",
    "🎯 *¿Qué proyecto del que has trabajado te ha llenado más de orgullo?*",
    "🌱 *¿En qué área te gustaría crecer profesionalmente en los próximos 6 meses?*",
    "🤩 *¿Cuál fue el momento más divertido que has tenido con el equipo?*",
    "📚 *¿Qué libro, podcast o video recomendarías a tus compañeros esta semana?*",
    "☕ *¿Eres de café, té o ninguno de los dos?* ¡Cuéntanos tu ritual matutino!",
    "🎬 *¿Qué película o serie estás viendo ahora?* ¡Danos una recomendación!",
    "🌎 *¿A qué lugar del mundo te gustaría viajar con el equipo si no hubiera límites?*",
]

# ─────────────────────────────────────────────────────────────
# CATEGORY: INVITACIONES A COMPARTIR / SHARING INVITATIONS
# ─────────────────────────────────────────────────────────────
COMPARTIR = [
    "📸 *¡Momento foto!* Comparte una foto de algo que te motivó hoy — puede ser tu café, tu escritorio, tu mascota o el paisaje desde tu ventana. ¡Todo cuenta! 🌟",
    "📖 *Cuéntanos una historia:* ¿Cuál fue el momento más memorable de tu carrera hasta ahora? ¡Nos encantaría escucharla!",
    "💌 *Deja un mensaje positivo para el equipo aquí abajo.* Puede ser una frase, un emoji o simplemente un \"¡los quiero, equipo!\" 💙",
    "🌟 *¿Qué cosa buena te pasó esta semana?* No importa si es grande o pequeña — ¡compártela aquí!",
    "🏆 *¡Momento de brillar!* Comparte un logro personal o profesional reciente. ¡Este es tu espacio para celebrarte!",
    "🎉 *¿Qué fue lo mejor de tu fin de semana?* ¡Cuéntanos con fotos, palabras o emojis!",
    "🌈 *Comparte algo que te haya hecho sonreír esta semana.* El equipo necesita más sonrisas hoy. 😊",
    "💪 *¿Superaste algún reto esta semana?* ¡Cuéntanos cómo lo lograste! Tu historia puede inspirar a alguien.",
    "🎨 *¡Creatividad libre!* Comparte algo que hayas creado recientemente — una receta, un dibujo, una foto, lo que sea.",
    "🙏 *¿Por qué cosa estás agradecido hoy?* Comparte tu gratitud aquí y contagia la energía positiva.",
    "🌻 *Comparte una foto de tu espacio de trabajo.* ¡Queremos conocer el lugar donde ocurre la magia!",
    "🎵 *¡Comparte la canción que define tu semana!* Pon el link y cuéntanos por qué la elegiste.",
    "📝 *Escribe en UNA palabra cómo ha sido tu semana.* Solo una palabra — ¡veamos qué dice el equipo!",
    "🌍 *Comparte una foto de tu lugar favorito en el mundo.* ¿Dónde te sientes más tú mismo?",
    "🍽️ *¡Comparte una receta favorita!* Algo que cocines en casa y que te encante. ¡Hagamos un recetario del equipo!",
]

# ─────────────────────────────────────────────────────────────
# CATEGORY: RECONOCIMIENTO / RECOGNITION
# ─────────────────────────────────────────────────────────────
RECONOCIMIENTO = [
    "🌟 *¡Momento de reconocimiento!* ¿Quién del equipo merece un aplauso esta semana? Menciónalos y diles por qué. 👏",
    "🏅 *Shoutout Friday!* Antes de cerrar la semana, reconoce a alguien que haya hecho una diferencia. ¡Etiquétalos aquí!",
    "💙 *El reconocimiento es gratuito y poderoso.* Hoy, dile a un compañero algo que admiras de él/ella.",
    "🎖️ *¿Quién fue tu MVP de esta semana?* ¡Nóminalos aquí y cuéntanos por qué se lo merecen!",
    "✨ *Pequeños gestos, gran impacto.* ¿Alguien te ayudó esta semana de una manera que marcó la diferencia? ¡Cuéntanos!",
    "🤝 *El trabajo en equipo se construye con reconocimiento.* Hoy, agradece públicamente a alguien del equipo.",
    "🌈 *¿Quién trajo más energía positiva al equipo esta semana?* ¡Dales crédito aquí!",
    "🚀 *Los grandes equipos celebran los logros juntos.* ¿Qué logro del equipo merece celebrarse hoy?",
]

# ─────────────────────────────────────────────────────────────
# CATEGORY: CULTURA DE EQUIPO / TEAM CULTURE
# ─────────────────────────────────────────────────────────────
CULTURA = [
    "🤝 *Cultura de equipo:* Un equipo fuerte no se construye solo con habilidades, sino con confianza y respeto mutuo. ¿Cómo están construyendo eso hoy?",
    "💡 *Reflexión del día:* ¿Qué hace único a nuestro equipo? ¡Comparte en los comentarios!",
    "🌱 *Los equipos que aprenden juntos, crecen juntos.* ¿Qué aprendiste esta semana que puedas compartir con el equipo?",
    "🏠 *Nuestro equipo es nuestra segunda familia.* ¿Qué valor de equipo es el más importante para ti?",
    "🎯 *Cuando el equipo gana, todos ganan.* ¿Cómo puedes contribuir hoy al éxito colectivo?",
    "💬 *La comunicación abierta es la base de un gran equipo.* ¿Hay algo que quieras compartir o proponer al equipo?",
    "🌟 *Los mejores equipos se apoyan en los momentos difíciles.* ¿Alguien necesita apoyo hoy? ¡Aquí estamos!",
    "🔗 *Cada persona en este equipo es un eslabón esencial.* Sin ti, esto no sería lo mismo. ¡Gracias por ser parte!",
]

# ─────────────────────────────────────────────────────────────
# CATEGORY: DIVERSIÓN / FUN
# ─────────────────────────────────────────────────────────────
DIVERSION = [
    "😄 *¡Hora del juego!* Completa esta frase: \"Si nuestro equipo fuera un superhéroe, su superpoder sería...\" 🦸",
    "🎭 *¿Con qué personaje de película o serie te identificas más en el trabajo?* ¡Cuéntanos por qué!",
    "🎲 *Dato curioso:* Los equipos que se ríen juntos son más creativos. ¡Comparte el meme o chiste de la semana!",
    "🌮 *Debate del día:* ¿Tacos o pizza para el próximo team lunch?* ¡Voten en los comentarios!",
    "🐾 *¡Viernes de mascotas!* Si tienes una mascota, sube su foto aquí. Si no, sube la foto de la mascota que desearías tener. 🐶🐱",
    "🎯 *¿Cuál sería tu título de trabajo más creativo?* No el real, sino el que describe lo que REALMENTE haces. 😂",
    "🌍 *¿A qué país te mudarias mañana si pudieras?* ¡Y por qué!",
    "🎵 *¡Karaoke virtual!* ¿Qué canción cantarías si hubiera karaoke en la oficina hoy?",
    "🤔 *Dilema del día:* ¿Reunión de 2 horas que pudo ser un email, o email de 2 páginas que pudo ser una llamada de 5 minutos?* 😅",
    "🦸 *Si cada miembro del equipo fuera un Avenger, ¿quién sería quién?* ¡Asigna roles!",
]

# ─────────────────────────────────────────────────────────────
# CATEGORY: REFLEXIÓN / REFLECTION
# ─────────────────────────────────────────────────────────────
REFLEXION = [
    "🌙 *Reflexión de cierre:* Antes de terminar el día, escribe UNA cosa por la que estás agradecido hoy.",
    "📅 *Fin de semana de reflexión:* ¿Qué harías diferente la próxima semana? ¿Qué repetirías?",
    "🌱 *Crecimiento personal:* ¿En qué área de tu vida (personal o profesional) has crecido más este año?",
    "💭 *Pregunta profunda:* ¿Qué legado quieres dejar en este equipo?",
    "🎯 *Revisión de metas:* ¿Cómo vas con las metas que te pusiste a principio de mes?",
    "🌟 *\"El éxito es la suma de pequeños esfuerzos repetidos día tras día.\"* — Robert Collier. ¿Cuál fue tu pequeño esfuerzo de hoy?",
    "🔮 *Visión a futuro:* ¿Dónde te ves profesionalmente en 2 años? ¡Comparte tu visión!",
    "💙 *Gratitud en equipo:* Escribe el nombre de alguien del equipo que haya impactado positivamente tu carrera.",
]

# ─────────────────────────────────────────────────────────────
# CATEGORY: CELEBRACIÓN / CELEBRATION
# ─────────────────────────────────────────────────────────────
CELEBRACION_CUMPLEANOS = [
    "🎂🎉 *¡HOY ES EL CUMPLEAÑOS DE {nombre}!* 🎉🎂\n\nEquipo, démosle un enorme abrazo virtual a {nombre} en su día especial. ¡Que este año esté lleno de éxitos, salud y mucha felicidad! 🥳🎈\n\n¡Déjale tus mejores deseos aquí abajo! 👇",
    "🎈🎁 *¡Feliz Cumpleaños, {nombre}!* 🎁🎈\n\n¡Hoy es el día de celebrar a una persona increíble que hace a este equipo mejor cada día! Equipo, ¡a llenar este canal de amor y buenos deseos para {nombre}! 🎂✨",
    "🥳 *¡ATENCIÓN EQUIPO!* Hoy celebramos el cumpleaños de *{nombre}* 🎂\n\nSin personas como {nombre}, este equipo no sería lo mismo. ¡Gracias por todo lo que aportas! Que tengas un día espectacular. 🌟🎉",
]

CELEBRACION_ANIVERSARIO = [
    "🏆✨ *¡{nombre} cumple {años} año(s) con nosotros hoy!* ✨🏆\n\nEquipo, démosle un enorme reconocimiento a {nombre} por su dedicación y compromiso. ¡{años} año(s) de hacer grande a este equipo! 🙌🎉\n\n¡Déjale un mensaje de agradecimiento aquí! 👇",
    "🌟 *¡Aniversario laboral!* 🌟\n\n*{nombre}* lleva *{años} año(s)* siendo parte de esta familia. ¡Eso merece una celebración! Gracias por tu esfuerzo, tu talento y tu energía. ¡Este equipo es mejor gracias a ti! 💙🎊",
    "🎖️ *¡{nombre} cumple {años} año(s) en la empresa!* 🎖️\n\nCelebrar la trayectoria de nuestros compañeros es celebrar el éxito de todos. ¡Gracias, {nombre}, por cada día que has dado lo mejor de ti! 🚀🌟",
]

CELEBRACION_LOGRO = [
    "🏆 *¡LOGRO DESBLOQUEADO!* 🏆\n\n*{nombre}* acaba de lograr: *{logro}* 🎉\n\n¡Equipo, démosle el reconocimiento que se merece! Este tipo de logros nos inspiran a todos. 👏🌟",
    "🚀 *¡Gran noticia!* 🚀\n\n*{nombre}* ha alcanzado una meta importante: *{logro}*\n\n¡Esto es exactamente de lo que estamos hechos como equipo! ¡Felicitaciones! 🎊💪",
    "⭐ *¡Celebremos juntos!* ⭐\n\n*{nombre}* logró *{logro}* — ¡y eso merece un aplauso enorme! 👏\n\nGracias por inspirarnos con tu dedicación. ¡Sigue brillando! ✨",
]

# ─────────────────────────────────────────────────────────────
# CATEGORY: MENCIONES ALEATORIAS / RANDOM MENTIONS
# ─────────────────────────────────────────────────────────────
MENCIONES_TEMPLATES = [
    "👋 *{mencion}, ¡te toca!* Comparte algo positivo que te haya pasado esta semana. ¡El equipo quiere saberlo! 🌟",
    "📸 *{mencion}, te retamos:* Sube una foto de algo que te motivó hoy. ¡Puede ser cualquier cosa! 📷",
    "💬 *{mencion}, la pregunta es para ti:* ¿Cuál ha sido tu mayor logro este mes? ¡Cuéntanos! 🏆",
    "🎯 *{mencion}, ¡spotlight!* ¿Qué meta te gustaría lograr antes de que termine el mes? 🚀",
    "🌟 *{mencion}, te nombramos embajador/a de la buena energía hoy.* ¡Comparte una frase motivadora para el equipo! 💪",
    "🤝 *{mencion}, pregunta especial:* ¿A quién del equipo le darías un reconocimiento hoy y por qué? 🏅",
    "😄 *{mencion}, ¡es tu turno!* Cuéntanos algo divertido o curioso que no muchos sepan de ti. 🎭",
    "☕ *{mencion}, ¡buenos días!* ¿Cómo empezaste el día hoy? ¡Cuéntanos tu ritual matutino! 🌅",
    "🌈 *{mencion}, te preguntamos:* Si pudieras cambiar UNA cosa de tu rutina de trabajo, ¿qué sería? 💡",
    "🎉 *{mencion}, ¡sorpresa!* Comparte una recomendación — puede ser un libro, serie, podcast o restaurante. ¡Lo que quieras! 📚",
]


def get_random_message(category: str) -> str:
    """Get a random message from a specific category."""
    categories = {
        "motivacion": MOTIVACION,
        "preguntas": PREGUNTAS_DINAMICAS,
        "compartir": COMPARTIR,
        "reconocimiento": RECONOCIMIENTO,
        "cultura": CULTURA,
        "diversion": DIVERSION,
        "reflexion": REFLEXION,
    }
    messages = categories.get(category, MOTIVACION)
    return random.choice(messages)


def get_random_mention_template() -> str:
    """Get a random mention template."""
    return random.choice(MENCIONES_TEMPLATES)


def get_birthday_message(nombre: str) -> str:
    """Get a birthday celebration message."""
    template = random.choice(CELEBRACION_CUMPLEANOS)
    return template.format(nombre=nombre)


def get_anniversary_message(nombre: str, años: int) -> str:
    """Get a work anniversary celebration message."""
    template = random.choice(CELEBRACION_ANIVERSARIO)
    return template.format(nombre=nombre, años=años)


def get_achievement_message(nombre: str, logro: str) -> str:
    """Get an achievement celebration message."""
    template = random.choice(CELEBRACION_LOGRO)
    return template.format(nombre=nombre, logro=logro)


# Daily schedule mapping: which categories to post on which days/times
DAILY_SCHEDULE = {
    "monday_morning":    "motivacion",
    "tuesday_morning":   "preguntas",
    "wednesday_morning": "compartir",
    "thursday_morning":  "cultura",
    "friday_morning":    "reconocimiento",
    "wednesday_midday":  "diversion",
    "friday_afternoon":  "reflexion",
}
