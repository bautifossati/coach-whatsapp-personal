"""
agent.py — El cerebro del Coach Personal
Usa Claude con herramientas (tool use) para que el agente pueda:
  - Leer tus tareas del Sheets
  - Agregar nuevas tareas al Sheets
  - Crear eventos en Google Calendar
  - Mandarte citas motivadoras
"""

import anthropic
import requests
import json
import logging
from config import WHATSAPP_TOKEN, PHONE_NUMBER_ID

logger = logging.getLogger(__name__)
client = anthropic.Anthropic()

# Memoria de conversación por usuario
conversaciones: dict[str, list] = {}

# ─────────────────────────────────────────────────────────────
# System Prompt del Coach
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Sos el Coach Personal de Bauti Fossati, su asistente de WhatsApp de cabecera.
Lo conocés bien, sabés lo que quiere lograr y tu misión es ayudarlo a ser la mejor versión de sí mismo.

━━━━━━━━━━━━━━━━━━━━━━━
QUIÉN ES BAUTI
━━━━━━━━━━━━━━━━━━━━━━━
Bautista Fossati, argentino. Trabaja en Drop Experiencias, una agencia de turismo deportivo.
Su objetivo principal del año es "DEBUTAR EN PRIMERA" — una metáfora de dar el salto de calidad en su vida.

METAS LABORALES 2026:
- Consolidar Drop como agencia de turismo que genera experiencias reales
- Llevar 50 pasajeros al Mundial
- Manejar 6 cuentas de Agencias Minoristas
- Generar 3 negocios turísticos con empresas
- Cerrar 8 giras, 8 colegios (viajes de egresados) y 8 grupos de ski week

METAS ECONÓMICAS 2026:
- Ahorrar 12 mil dólares
- Ganar 3.500 dólares al mes (sueldo + variable)
- Invertir 5 mil dólares de sus ganancias
- Destinar 10 mil dólares para viajar

METAS PERSONALES 2026:
- Aprender piano / teoría musical
- Hacer dos cursos que complementen Drop

METAS ESPIRITUALES 2026:
- Meditar 10 minutos todos los días
- Charlar con Sebi cada 2 semanas
- Escribir todos los días
- Manifestar y agradecer antes de dormir

━━━━━━━━━━━━━━━━━━━━━━━
SUS HÁBITOS A CONSTRUIR
━━━━━━━━━━━━━━━━━━━━━━━
- Leer antes de dormir
- Dejar el celular cargando en otro cuarto (no en la cama)
- Meditar apenas se levanta
- Escribir al terminar el día
- Trabajar en intervalos de 30 min sin celular
- Ir al gym a la mañana
- 1 estímulo de relajación por semana
- Planificar la semana los domingos
- Caminar al club, no usar auto
- Tomar 30 min de sol al día

━━━━━━━━━━━━━━━━━━━━━━━
SU RUTINA
━━━━━━━━━━━━━━━━━━━━━━━
MAÑANA: 8:00 levantarse → 8:10 meditar → 8:20 revisar pendientes → 8:30 desayuno → 9:00 agarrar el celular
NOCHE: 11:30 dejar el cel en otro cuarto → 11:40 escribir/lista pendientes → 12:00 lectura → 12:30 dormir

━━━━━━━━━━━━━━━━━━━━━━━
LIBROS QUE LEYÓ (los conoce bien, podés referenciarlos)
━━━━━━━━━━━━━━━━━━━━━━━
- Deja de Ser Tú (Joe Dispenza)
- Hábitos Atómicos (James Clear)
- Cómo Ganar Amigos e Influir Sobre las Personas (Dale Carnegie)
- Los Cuatro Acuerdos (Miguel Ruiz)
- El Poder del Ahora (Eckhart Tolle)
- Vendes o Vendes (Grant Cardone)
- El Método Briones

━━━━━━━━━━━━━━━━━━━━━━━
TU PERSONALIDAD COMO COACH
━━━━━━━━━━━━━━━━━━━━━━━
- Hablás en argentino, de manera cercana y directa (usás "vos", "te", "laburás")
- Sos motivador pero REALISTA — no sos un motivador de plástico que todo lo ve color de rosa
- Combinás energía positiva con pragmatismo: recordás sus compromisos con afecto pero con firmeza
- Cuando Bauti se queja o duda, lo empujás con cariño pero sin dejarle pasar excusas
- Si falla un hábito, no lo retás: lo ayudás a volver a subirse al tren sin drama
- Sos conciso: máximo 3-4 párrafos por mensaje. WhatsApp no es un ensayo.
- Usás emojis con moderación (1-2 por mensaje máximo)
- A veces podés preguntarle cómo le fue con algo específico que sabe que tenía pendiente

━━━━━━━━━━━━━━━━━━━━━━━
TUS CAPACIDADES
━━━━━━━━━━━━━━━━━━━━━━━
1. Leer sus tareas del Sheets (día o semana completa)
2. Agregar nuevas tareas al Sheets cuando te lo pida
3. Crear eventos en Google Calendar
4. Consultar el calendario
5. Mandar citas de sus libros favoritos
6. Hacer seguimiento de hábitos y constancia
7. Ser un espacio de reflexión, desahogo o coaching en cualquier momento

Cuando Bauti te escribe:
- "agregá esta tarea" / "anotá" / "tengo que hacer" → usá agregar_tarea
- "agendá" / "creá un evento" / "anotá en el calendar" → usá crear_evento
- "pendientes" / "tareas" / "qué tengo hoy" → usá obtener_tareas
- "qué tengo en el calendar" → usá obtener_eventos
- "cita" / "motivación" / "frase" → usá obtener_cita
- "marqué como hecha" / "terminé" → usá marcar_completa

Cuando uses herramientas:
- Confirmá lo que hiciste en lenguaje natural y amigable
- Si creaste un evento, confirmá día, hora y título
- Si no encontraste tareas, decíselo con buena onda

Recordá siempre: tu objetivo es que Bauti se vaya de cada chat sintiendo que puede lograr lo que se propuso.
Conocés sus metas. Conocés sus hábitos. Conocés sus libros. Usá ese contexto para dar respuestas que realmente lo muevan."""


# ─────────────────────────────────────────────────────────────
# Definición de herramientas (tools) para Claude
# ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "obtener_tareas",
        "description": "Lee las tareas de Bauti desde Google Sheets. Puede traer las del día de hoy o toda la semana.",
        "input_schema": {
            "type": "object",
            "properties": {
                "modo": {
                    "type": "string",
                    "enum": ["hoy", "semana", "pendientes"],
                    "description": "hoy = tareas de hoy, semana = todas las de la semana, pendientes = solo las que faltan completar"
                }
            },
            "required": ["modo"]
        }
    },
    {
        "name": "agregar_tarea",
        "description": "Agrega una nueva tarea al Google Sheets de organización semanal de Bauti.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dia": {
                    "type": "string",
                    "description": "Día de la semana en español (Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo)"
                },
                "tarea": {
                    "type": "string",
                    "description": "Descripción clara de la tarea"
                },
                "prioridad": {
                    "type": "string",
                    "enum": ["Alta", "Media", "Baja"],
                    "description": "Prioridad de la tarea. Por defecto Media si no se especifica."
                }
            },
            "required": ["dia", "tarea"]
        }
    },
    {
        "name": "marcar_completa",
        "description": "Marca una tarea del Sheets como completada.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nombre_tarea": {
                    "type": "string",
                    "description": "Nombre o parte del nombre de la tarea a marcar como completada"
                }
            },
            "required": ["nombre_tarea"]
        }
    },
    {
        "name": "crear_evento",
        "description": "Crea un evento en el Google Calendar de Bauti.",
        "input_schema": {
            "type": "object",
            "properties": {
                "titulo": {
                    "type": "string",
                    "description": "Nombre del evento (ej: 'Reunión con Marcos', 'Llamada con el cliente')"
                },
                "fecha": {
                    "type": "string",
                    "description": "Fecha en formato DD/MM/YYYY (ej: '26/03/2026')"
                },
                "hora_inicio": {
                    "type": "string",
                    "description": "Hora de inicio en formato HH:MM (ej: '10:00')"
                },
                "hora_fin": {
                    "type": "string",
                    "description": "Hora de fin en formato HH:MM (ej: '11:00')"
                },
                "descripcion": {
                    "type": "string",
                    "description": "Descripción o notas del evento (opcional)"
                },
                "invitados": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de emails de invitados (opcional)"
                }
            },
            "required": ["titulo", "fecha", "hora_inicio", "hora_fin"]
        }
    },
    {
        "name": "obtener_eventos",
        "description": "Consulta los eventos del Google Calendar de Bauti.",
        "input_schema": {
            "type": "object",
            "properties": {
                "modo": {
                    "type": "string",
                    "enum": ["hoy", "semana"],
                    "description": "hoy = eventos de hoy, semana = eventos de la semana"
                }
            },
            "required": ["modo"]
        }
    },
    {
        "name": "obtener_cita",
        "description": "Obtiene una cita motivadora de un libro de crecimiento personal.",
        "input_schema": {
            "type": "object",
            "properties": {
                "categoria": {
                    "type": "string",
                    "enum": ["habitos", "disciplina", "proposito", "mindset", "productividad", "aleatoria"],
                    "description": "Categoría de la cita. Usar 'aleatoria' si no se especifica."
                }
            },
            "required": ["categoria"]
        }
    }
]


# ─────────────────────────────────────────────────────────────
# Ejecución de herramientas
# ─────────────────────────────────────────────────────────────

def ejecutar_herramienta(nombre: str, parametros: dict) -> str:
    """Ejecuta la herramienta solicitada por Claude y devuelve el resultado."""
    try:
        if nombre == "obtener_tareas":
            from integrations import obtener_tareas_dia, obtener_tareas_semana, obtener_tareas_pendientes
            modo = parametros.get("modo", "hoy")
            if modo == "hoy":
                tareas = obtener_tareas_dia()
            elif modo == "pendientes":
                tareas = obtener_tareas_pendientes()
            else:
                tareas = obtener_tareas_semana()

            if not tareas:
                return "No encontré tareas."

            return json.dumps(tareas, ensure_ascii=False)

        elif nombre == "agregar_tarea":
            from integrations import agregar_tarea
            exito = agregar_tarea(
                dia=parametros["dia"],
                tarea=parametros["tarea"],
                prioridad=parametros.get("prioridad", "Media")
            )
            return "Tarea agregada correctamente." if exito else "No pude agregar la tarea."

        elif nombre == "marcar_completa":
            from integrations import marcar_tarea_completa
            exito = marcar_tarea_completa(parametros["nombre_tarea"])
            return "Tarea marcada como completada." if exito else "No encontré esa tarea en el Sheets."

        elif nombre == "crear_evento":
            from integrations import crear_evento
            resultado = crear_evento(
                titulo=parametros["titulo"],
                fecha=parametros["fecha"],
                hora_inicio=parametros["hora_inicio"],
                hora_fin=parametros["hora_fin"],
                descripcion=parametros.get("descripcion", ""),
                invitados=parametros.get("invitados", [])
            )
            return json.dumps(resultado, ensure_ascii=False)

        elif nombre == "obtener_eventos":
            from integrations import obtener_eventos_hoy, obtener_eventos_semana
            modo = parametros.get("modo", "hoy")
            eventos = obtener_eventos_hoy() if modo == "hoy" else obtener_eventos_semana()
            if not eventos:
                return "No encontré eventos en el calendario."
            return json.dumps(eventos, ensure_ascii=False)

        elif nombre == "obtener_cita":
            from citas import obtener_cita_por_categoria
            categoria = parametros.get("categoria", "aleatoria")
            return obtener_cita_por_categoria(categoria)

        else:
            return f"Herramienta desconocida: {nombre}"

    except Exception as e:
        logger.error(f"Error ejecutando herramienta '{nombre}': {e}")
        return f"Error al ejecutar {nombre}: {str(e)}"


# ─────────────────────────────────────────────────────────────
# Procesamiento de mensajes
# ─────────────────────────────────────────────────────────────

def procesar_mensaje(numero: str, texto: str) -> str:
    """
    Recibe el mensaje de Bauti, se lo pasa a Claude con las herramientas disponibles,
    ejecuta las herramientas si es necesario, y devuelve la respuesta final.
    """
    if numero not in conversaciones:
        conversaciones[numero] = []

    # Limitar historial a las últimas 10 interacciones
    conversaciones[numero].append({"role": "user", "content": texto})
    historial = conversaciones[numero][-10:]

    try:
        # Primera llamada a Claude — puede pedir usar una herramienta
        respuesta = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=700,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=historial
        )

        # Si Claude quiere usar herramientas, las ejecutamos
        while respuesta.stop_reason == "tool_use":
            tool_uses = [b for b in respuesta.content if b.type == "tool_use"]
            resultados_herramientas = []

            for tool_use in tool_uses:
                logger.info(f"🔧 Usando herramienta: {tool_use.name} con {tool_use.input}")
                resultado = ejecutar_herramienta(tool_use.name, tool_use.input)
                resultados_herramientas.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": resultado
                })

            # Agregar la respuesta de Claude y los resultados al historial
            historial.append({"role": "assistant", "content": respuesta.content})
            historial.append({"role": "user", "content": resultados_herramientas})

            # Segunda llamada con los resultados de las herramientas
            respuesta = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=700,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=historial
            )

        # Extraer el texto final de la respuesta
        texto_respuesta = next(
            (b.text for b in respuesta.content if hasattr(b, "text")),
            "Perdoná, no pude procesar tu mensaje. ¿Lo repetís?"
        )

    except Exception as e:
        logger.error(f"Error con Claude API: {e}")
        texto_respuesta = "Tuve un problema técnico momentáneo. ¿Me lo repetís en un segundo? 🙏"

    # Guardar en historial
    conversaciones[numero].append({"role": "assistant", "content": texto_respuesta})

    return texto_respuesta


# ─────────────────────────────────────────────────────────────
# Envío de mensajes por WhatsApp
# ─────────────────────────────────────────────────────────────

def enviar_mensaje(numero: str, texto: str) -> bool:
    """Envía un mensaje de texto por WhatsApp Business API."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"✅ Mensaje enviado a {numero}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error enviando a {numero}: {e}")
        return False
