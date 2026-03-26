"""
config.py — Configuración del Coach Personal WhatsApp
Cargá tus claves en el archivo .env y este archivo las lee automáticamente.
NO subas el archivo .env to GitHub ni compartas estas claves con nadie.
"""

import os
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# ─────────────────────────────────────────────────────────────
# WhatsApp Business API (Meta)
# ─────────────────────────────────────────────────────────────

# Tu token de acceso de WhatsApp Business (lo obtenés en Meta for Developers)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")

# El ID de tu número de teléfono de WhatsApp Business
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")

# Token que vos inventás para verificar el webhook con Meta (cualquier texto)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mi-coach-personal-2024")

# ─────────────────────────────────────────────────────────────
# Tu número de WhatsApp personal
# ─────────────────────────────────────────────────────────────

# Formato internacional sin el +: ejemplo 5491134567890 para Argentina
MI_NUMERO_WHATSAPP = os.getenv("MI_NUMERO_WHATSAPP", "")

# ─────────────────────────────────────────────────────────────
# Anthropic (Claude)
# ─────────────────────────────────────────────────────────────

# Tu API Key de Anthropic (la obtenés en console.anthropic.com)
# NO hace falta asignarla acá: el cliente de Anthropic la lee automáticamente
# desde la variable de entorno ANTHROPIC_API_KEY

# ─────────────────────────────────────────────────────────────
# Google (Sheets + Calendar)
# ─────────────────────────────────────────────────────────────

# Ruta al archivo JSON de credenciales de tu cuenta de servicio de Google
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

# ID de tu Google Sheets (es la parte larga de la URL entre /d/ y /edit)
# Ejemplo: https://docs.google.com/spreadsheets/d/1ABC123.../edit ↲ "1ABC123..."
SHEETS_ID = os.getenv("SHEETS_ID", "")

# Nombre de la hoja dentro del Sheets donde organizás tu semana
# Por defecto "Semana", cambialo si tuya se llama diferente
NOMBRE_HOJA_SEMAND = os.getenv("NOMBRE_HOJA_SEMANA", "Semana")

# ID del calendario de Google Calendar donde querés que el agente cree eventos
# Para tu calendario principal, usá "primary"
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")

# ─────────────────────────────────────────────────────────────
# Zona horaria y configuración regional
# ─────────────────────────────────────────────────────────────

TIMEZONE = "America/Argentina/Buenos_Aires"

# ─────────────────────────────────────────────────────────────
# Validación al iniciar
# ─────────────────────────────────────────────────────────────

def validar_configuracion():
    """Verifica que las claves esenciales estén configuradas."""
    problemas = []

    if not WHATSAPP_TOKEN:
        problemas.append("❌ WHATSAPP_TOKEN no está configurado")
    if not PHONE_NUMBER_ID:
        problemas.append("❌ PHONE_NUMBER_ID no está configurado")
    if not MI_NUMERO_WHATSAPP:
        problemas.append("❌ SI_NUMERO_WHATSAPP no está configurado")
    if not SHEETS_ID:
        problemas.append("⚨️  SHEETS_ID no está configurado (Sheets no va a funcionar)")
    if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
        problemas.append(f"⚨️  No se encontró el archivo de credenciales de Google en '{GOOGLE_CREDENTIALS_PATH}'")

    if problemas:
        print("\n🚨 Problemas de configuración encontrados:")
        for p in problemas:
            print(f"   {p}")
        print("\n📖 Revisá el README.md para instrucciones de configuración.\n")
    else:
        print("✅ Configuración completa. El agente está listo para arrancar.")

    return len([p for p in problemas if p.startswith("❌")]) == 0  # True si no hay errores críticos
