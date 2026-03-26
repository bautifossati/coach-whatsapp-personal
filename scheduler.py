"""
scheduler.py — Mensajes automáticos del Coach Personal
Este archivo maneja los envíos proactivos sin que Bauti tenga que escribir primero.

Horarios configurados (hora Argentina):
  08:00 — Buenos días: cita motivadora + tareas del día
  13:00 — Check-in de mediodía: tareas pendientes del día
  21:00 — Cierre del día: reflexión + resumen de lo completado

Para correrlo: python scheduler.py
(Debe estar corriendo al mismo tiempo que main.py)
"""

import logging
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from agent import enviar_mensaje
from integrations import obtener_tareas_dia, obtener_tareas_pendientes, obtener_eventos_hoy
from citas import obtener_cita_aleatoria, obtener_cita_por_categoria
from config import MI_NUMERO_WHATSAPP, TIMEZONE

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Mensajes automáticos
# ─────────────────────────────────────────────────────────────

def buenos_dias():
    """
    Mensaje de las 8am:
    - Cita motivadora del día
    - Tareas programadas para hoy
    - Eventos del calendario de hoy
    """
    logger.info("🌅 Enviando mensaje de buenos días...")

    dia_semana = _dia_en_espanol(datetime.now().weekday())
    fecha = datetime.now().strftime("%d/%m/%Y")

    # Cita del día (rotar por categorías según el día)
    categorias = ["habitos", "disciplina", "proposito", "mindset", "productividad", "habitos", "disciplina"]
    categoria_hoy = categorias[datetime.now().weekday()]
    cita = obtener_cita_por_categoria(categoria_hoy)

    # Tareas del día
    tareas = obtener_tareas_dia()
    bloque_tareas = _formatear_tareas_mensaje(tareas)

    # Eventos del calendario
    eventos = obtener_eventos_hoy()
    bloque_eventos = _formatear_eventos_mensaje(eventos)

    mensaje = (
        f"☀️ *Buenos días, Bauti!* {dia_semana} {fecha}\n\n"
        f"Tu cita del día:\n{cita}\n\n"
        f"────────────────\n"
        f"{bloque_tareas}"
        f"{bloque_eventos}"
        f"¡Hoy es un día para avanzar 💪 Estoy por acá si necesitás algo!"
    )

    enviar_mensaje(MI_NUMERO_WHATSAPP, mensaje)
    logger.info("✅ Buenos días enviado")


def check_in_mediodia():
    """
    Mensaje de las 13hs:
    - Tareas pendientes que quedan del día
    - Recordatorio amigable de constancia
    """
    logger.info("☀️ Enviando check-in de mediodía...")

    pendientes = obtener_tareas_pendientes()
    pendientes_hoy = [t for t in pendientes
                      if str(t.get("Día", "")).strip().lower() in
                      [_dia_en_espanol(datetime.now().weekday()).lower()]]

    if not pendientes_hoy:
        mensaje = (
            "🎉 *Check-in de mediodía*\n\n"
            "¡No tenés tareas pendientes para hoy! O las terminaste todas, o el día está libre.\n\n"
            "Si surgió algo nuevo, avisame y lo agrego al Sheets. 📋"
        )
    else:
        lista = "\n".join([
            f"• {t.get('Tarea', 'Sin nombre')} [{t.get('Prioridad', 'Media')}]"
            for t in pendientes_hoy
        ])
        mensaje = (
            f"🕐 *Check-in de mediodía*\n\n"
            f"Estas son las tareas que te quedan para hoy:\n\n"
            f"{lista}\n\n"
            f"¿Cómo venís? Si terminaste alguna, avisame y la marco. 💪"
        )

    enviar_mensaje(MI_NUMERO_WHATSAPP, mensaje)
    logger.info("✅ Check-in de mediodía enviado")


def cierre_del_dia():
    """
    Mensaje de las 21hs:
    - Reflexión del día
    - Cita de cierre
    - Vistazo a mañana
    """
    logger.info("🌙 Enviando cierre del día...")

    cita = obtener_cita_por_categoria("mindset")
    dia_semana = _dia_en_espanol(datetime.now().weekday())

    mensaje = (
        f"🌙 *Cerrando el {dia_semana}*\n\n"
        f"Antes de descansar, un momento para vos:\n\n"
        f"{cita}\n\n"
        f"────────────────\n"
        f"Reflexión rápida de hoy:\n"
        f"¿Qué cosa, por pequeña que sea, hiciste hoy que te acercó a quien querés ser?\n\n"
        f"Mañana seguimos. Descansá bien 🙏"
    )

    enviar_mensaje(MI_NUMERO_WHATSAPP, mensaje)
    logger.info("✅ Cierre del día enviado")


# ─────────────────────────────────────────────────────────────
# Helpers de formato
# ─────────────────────────────────────────────────────────────

def _formatear_tareas_mensaje(tareas: list) -> str:
    """Convierte una lista de tareas en un bloque de texto para WhatsApp."""
    if not tareas:
        return "📋 *Tareas de hoy:* No encontré tareas en el Sheets para hoy.\n\n"

    pendientes = [t for t in tareas if str(t.get("Estado", "")).lower() not in ["completada", "completa"]]
    completadas = [t for t in tareas if str(t.get("Estado", "")).lower() in ["completada", "completa"]]

    lineas = ["📋 *Tareas de hoy:*"]
    for t in pendientes:
        prioridad = t.get("Prioridad", "Media")
        emoji = "🔴" if prioridad == "Alta" else "🟡" if prioridad == "Media" else "🟢"
        lineas.append(f"{emoji} {t.get('Tarea', 'Sin nombre')}")

    if completadas:
        lineas.append(f"\n✅ Completadas: {len(completadas)}")

    return "\n".join(lineas) + "\n\n"


def _formatear_eventos_mensaje(eventos: list) -> str:
    """Convierte una lista de eventos en un bloque de texto para WhatsApp."""
    if not eventos:
        return ""

    lineas = ["📅 *Eventos de hoy:*"]
    for e in eventos:
        lineas.append(f"• {e['hora_inicio']} — {e['titulo']}")

    return "\n".join(lineas) + "\n\n"


def _dia_en_espanol(numero: int) -> str:
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[numero]


# ─────────────────────────────────────────────────────────────
# Configuración del scheduler
# ─────────────────────────────────────────────────────────────

def iniciar_scheduler():
    """Configura y arranca el scheduler con los tres turnos del día."""
    scheduler = BlockingScheduler(timezone=TIMEZONE)

    # 8:00am — Buenos días
    scheduler.add_job(
        buenos_dias,
        trigger=CronTrigger(hour=8, minute=0, timezone=TIMEZONE),
        id="buenos_dias",
        name="Buenos días con cita y tareas"
    )

    # 13:00hs — Check-in de mediodía
    scheduler.add_job(
        check_in_mediodia,
        trigger=CronTrigger(hour=13, minute=0, timezone=TIMEZONE),
        id="check_in_mediodia",
        name="Check-in de mediodía"
    )

    # 21:00hs — Cierre del día
    scheduler.add_job(
        cierre_del_dia,
        trigger=CronTrigger(hour=21, minute=0, timezone=TIMEZONE),
        id="cierre_dia",
        name="Cierre del día"
    )

    logger.info("⏰ Scheduler iniciado. Horarios activos:")
    logger.info("   • 08:00 — Buenos días + tareas + cita")
    logger.info("   • 13:00 — Check-in de mediodía")
    logger.info("   • 21:00 — Cierre del día + reflexión")
    logger.info(f"   • Zona horaria: {TIMEZONE}")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler detenido.")


if __name__ == "__main__":
    iniciar_scheduler()
