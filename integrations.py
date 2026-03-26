"""
integrations.py — Conexiones con Google Sheets y Google Calendar
Acá están todas las funciones para leer y escribir en tu planilla
y para crear/consultar eventos en tu calendario.
"""

import gspread
import json
import logging
import os
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config import (
    GOOGLE_CREDENTIALS_PATH,
    SHEETS_ID,
    CALENDAR_ID,
    NOMBRE_HOJA_SEMANA,
    TIMEZONE
)

logger = logging.getLogger(__name__)

# Permisos que necesitamos de Google
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar"
]


# ─────────────────────────────────────────────────────────────
# GOOGLE SHEETS — Lectura y escritura
# ─────────────────────────────────────────────────────────────

def _get_credentials():
    """
    Devuelve las credenciales de Google.
    Primero intenta leer desde la variable de entorno GOOGLE_CREDENTIALS_JSON
    (útil en Railway/cloud). Si no existe, lee el archivo local.
    """
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
    if creds_json:
        info = json.loads(creds_json)
        return Credentials.from_service_account_info(info, scopes=SCOPES)
    return Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)


def _get_sheets_client():
    """Devuelve el cliente autenticado de Google Sheets."""
    creds = _get_credentials()
    return gspread.authorize(creds)


def obtener_tareas_dia() -> list[dict]:
    """
    Lee todas las tareas de la semana y filtra las del día de hoy.
    Espera que el Sheets tenga columnas: Día | Tarea | Estado | Prioridad
    """
    try:
        client = _get_sheets_client()
        sheet = client.open_by_key(SHEETS_ID).worksheet(NOMBRE_HOJA_SEMANA)
        todas = sheet.get_all_records()

        hoy = datetime.now().strftime("%A").lower()  # ej: "monday"
        hoy_es = _dia_en_espanol(datetime.now().weekday())  # ej: "Lunes"

        tareas_hoy = [
            t for t in todas
            if str(t.get("Día", "")).strip().lower() in [hoy, hoy_es.lower()]
        ]

        logger.info(f"📋 Tareas de hoy ({hoy_es}): {len(tareas_hoy)}")
        return tareas_hoy

    except Exception as e:
        logger.error(f"Error leyendo tareas del día: {e}")
        return []


def obtener_tareas_semana() -> list[dict]:
    """Devuelve todas las tareas de la semana desde el Sheets."""
    try:
        client = _get_sheets_client()
        sheet = client.open_by_key(SHEETS_ID).worksheet(NOMBRE_HOJA_SEMANA)
        tareas = sheet.get_all_records()
        logger.info(f"📋 Total tareas semana: {len(tareas)}")
        return tareas

    except Exception as e:
        logger.error(f"Error leyendo semana: {e}")
        return []


def obtener_tareas_pendientes() -> list[dict]:
    """Devuelve solo las tareas con estado Pendiente o En progreso."""
    todas = obtener_tareas_semana()
    pendientes = [
        t for t in todas
        if str(t.get("Estado", "")).strip().lower() in ["pendiente", "en progreso", "en proceso", ""]
    ]
    return pendientes


def agregar_tarea(dia: str, tarea: str, prioridad: str = "Media") -> bool:
    """
    Agrega una nueva fila de tarea al Sheets.

    Parámetros:
        dia: Día de la semana (ej: "Lunes", "Martes")
        tarea: Descripción de la tarea
        prioridad: "Alta", "Media" o "Baja"
    """
    try:
        client = _get_sheets_client()
        sheet = client.open_by_key(SHEETS_ID).worksheet(NOMBRE_HOJA_SEMANA)
        nueva_fila = [dia, tarea, "Pendiente", prioridad]
        sheet.append_row(nueva_fila)
        logger.info(f"✅ Tarea agregada: {tarea} ({dia})")
        return True

    except Exception as e:
        logger.error(f"Error agregando tarea: {e}")
        return False


def marcar_tarea_completa(nombre_tarea: str) -> bool:
    """
    Busca una tarea por nombre y la marca como Completada.
    Búsqueda parcial, no distingue mayúsculas.
    """
    try:
        client = _get_sheets_client()
        sheet = client.open_by_key(SHEETS_ID).worksheet(NOMBRE_HOJA_SEMANA)
        todas_las_celdas = sheet.get_all_values()

        # Fila 0 son los encabezados, buscamos desde la fila 1
        headers = [h.lower() for h in todas_las_celdas[0]]
        col_tarea = headers.index("tarea") + 1  # gspread usa índice 1
        col_estado = headers.index("estado") + 1

        for i, fila in enumerate(todas_las_celdas[1:], start=2):
            if nombre_tarea.lower() in fila[col_tarea - 1].lower():
                sheet.update_cell(i, col_estado, "Completada")
                logger.info(f"✅ Tarea marcada como completa: {fila[col_tarea - 1]}")
                return True

        logger.warning(f"No se encontró la tarea: {nombre_tarea}")
        return False

    except Exception as e:
        logger.error(f"Error marcando tarea: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# GOOGLE CALENDAR — Consultar y crear eventos
# ─────────────────────────────────────────────────────────────

def _get_calendar_service():
    """Devuelve el servicio autenticado de Google Calendar."""
    creds = _get_credentials()
    return build("calendar", "v3", credentials=creds)


def obtener_eventos_hoy() -> list[dict]:
    """Devuelve los eventos de tu calendario para el día de hoy."""
    try:
        service = _get_calendar_service()
        hoy = datetime.now()
        inicio = hoy.replace(hour=0, minute=0, second=0).isoformat() + "-03:00"
        fin = hoy.replace(hour=23, minute=59, second=59).isoformat() + "-03:00"

        resultado = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=inicio,
            timeMax=fin,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        eventos = resultado.get("items", [])
        logger.info(f"📅 Eventos de hoy: {len(eventos)}")
        return [
            {
                "titulo": e.get("summary", "Sin título"),
                "hora_inicio": _formatear_hora(e.get("start", {})),
                "hora_fin": _formatear_hora(e.get("end", {})),
                "descripcion": e.get("description", "")
            }
            for e in eventos
        ]

    except Exception as e:
        logger.error(f"Error leyendo calendario: {e}")
        return []


def obtener_eventos_semana() -> list[dict]:
    """Devuelve los eventos de la semana actual."""
    try:
        service = _get_calendar_service()
        hoy = datetime.now()
        inicio_semana = (hoy - timedelta(days=hoy.weekday())).replace(hour=0, minute=0, second=0)
        fin_semana = inicio_semana + timedelta(days=6, hours=23, minutes=59)

        resultado = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=inicio_semana.isoformat() + "-03:00",
            timeMax=fin_semana.isoformat() + "-03:00",
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        eventos = resultado.get("items", [])
        return [
            {
                "titulo": e.get("summary", "Sin título"),
                "fecha": _formatear_fecha(e.get("start", {})),
                "hora_inicio": _formatear_hora(e.get("start", {})),
                "hora_fin": _formatear_hora(e.get("end", {}))
            }
            for e in eventos
        ]

    except Exception as e:
        logger.error(f"Error leyendo eventos de la semana: {e}")
        return []


def crear_evento(titulo: str, fecha: str, hora_inicio: str, hora_fin: str,
                 descripcion: str = "", invitados: list[str] = None) -> dict:
    """
    Crea un evento en Google Calendar.

    Parámetros:
        titulo: Nombre del evento (ej: "Reunión con Marcos")
        fecha: Fecha en formato DD/MM/YYYY (ej: "26/03/2026")
        hora_inicio: Hora de inicio en HH:MM (ej: "10:00")
        hora_fin: Hora de fin en HH:MM (ej: "11:00")
        descripcion: Descripción opcional del evento
        invitados: Lista de emails (opcional)

    Devuelve: dict con 'exito' (bool), 'mensaje' (str) y 'link' (str) si se creó bien.
    """
    try:
        service = _get_calendar_service()

        inicio = datetime.strptime(f"{fecha} {hora_inicio}", "%d/%m/%Y %H:%M")
        fin = datetime.strptime(f"{fecha} {hora_fin}", "%d/%m/%Y %H:%M")

        if fin <= inicio:
            return {"exito": False, "mensaje": "La hora de fin debe ser después de la de inicio."}

        evento = {
            "summary": titulo,
            "description": descripcion,
            "start": {
                "dateTime": inicio.isoformat(),
                "timeZone": TIMEZONE
            },
            "end": {
                "dateTime": fin.isoformat(),
                "timeZone": TIMEZONE
            }
        }

        if invitados:
            evento["attendees"] = [{"email": email} for email in invitados]

        resultado = service.events().insert(
            calendarId=CALENDAR_ID,
            body=evento,
            sendUpdates="all" if invitados else "none"
        ).execute()

        link = resultado.get("htmlLink", "")
        logger.info(f"✅ Evento creado: {titulo} el {fecha} a las {hora_inicio}")
        return {
            "exito": True,
            "mensaje": f"Evento '{titulo}' creado para el {fecha} de {hora_inicio} a {hora_fin}.",
            "link": link,
            "id": resultado.get("id", "")
        }

    except ValueError as e:
        return {"exito": False, "mensaje": f"Formato de fecha u hora incorrecto: {e}"}
    except Exception as e:
        logger.error(f"Error creando evento: {e}")
        return {"exito": False, "mensaje": f"No pude crear el evento: {e}"}


# ─────────────────────────────────────────────────────────────
# Utilidades internas
# ─────────────────────────────────────────────────────────────

def _dia_en_espanol(numero: int) -> str:
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[numero]


def _formatear_hora(tiempo: dict) -> str:
    """Extrae la hora de un objeto de tiempo de Google Calendar."""
    if "dateTime" in tiempo:
        dt = datetime.fromisoformat(tiempo["dateTime"].replace("Z", "+00:00"))
        return dt.astimezone().strftime("%H:%M")
    return "Todo el día"


def _formatear_fecha(tiempo: dict) -> str:
    """Extrae la fecha de un objeto de tiempo de Google Calendar."""
    if "dateTime" in tiempo:
        dt = datetime.fromisoformat(tiempo["dateTime"].replace("Z", "+00:00"))
        return dt.astimezone().strftime("%d/%m/%Y")
    elif "date" in tiempo:
        return tiempo["date"]
    return ""
