"""
main.py — Servidor principal del Coach Personal de WhatsApp
Este archivo es el "timbre": recibe cada mensaje que te mandan por WhatsApp
y lo pasa al agente para que lo responda.
"""

from flask import Flask, request, jsonify
from agent import procesar_mensaje
from config import VERIFY_TOKEN
import logging

# Configurar logs para ver qué pasa cuando corre el servidor
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """
    GET: Meta verifica que el servidor es tuyo (una sola vez al configurar).
    POST: Meta te manda cada mensaje que recibís en WhatsApp.
    """

    # ── Verificación inicial de Meta ──────────────────────────────────────────
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("✅ Webhook verificado correctamente por Meta")
            return challenge, 200
        else:
            logger.warning("❌ Token de verificación incorrecto")
            return "Token inválido", 403

    # ── Mensajes entrantes ────────────────────────────────────────────────────
    if request.method == "POST":
        data = request.get_json()
        logger.info(f"📩 Mensaje recibido: {data}")

        try:
            entry = data["entry"][0]["changes"][0]["value"]

            # Solo procesar si hay mensajes (no notificaciones de estado)
            if "messajes" not in entry:
                return "OK", 200

            mensaje = entry["messajes"][0]
            numero = mensaje["from"]
            tipo = mensaje.get("type", "")

            # Solo procesamos mensajes de texto por ahora
            if tipo != "text":
                from agent import enviar_mensaje
                enviar_mensaje(numero, "¡Hola! Por ahora solo puedo leer mensajes de texto 😊")
                return "OK", 200

            texto = mensaje["text"]["body"]
            logger.info(f"💬 Mensaje de {numero}: {texto}")

            # El agente piensa y responde
            respuesta = procesar_mensaje(numero, texto)
            from agent import enviar_mensaje
            enviar_mensaje(numero, respuesta)

        except (KeyError, IndexError) as e:
            logger.error(f"Error procesando mensaje: {e}")

        return "OK", 200


@app.route("/health", methods=["GET"])
def health():
    """Chequeo de salud: para saber si el servidor está corriendo."""
    return jsonify({"status": "ok", "mensaje": "Coach WhatsApp corriendo 💪"}), 200


if __name__ == "__main__":
    logger.info("🚀 Iniciando Coach Personal WhatsApp...")
    app.run(host="0.0.0.0", port=5000, debug=False)
