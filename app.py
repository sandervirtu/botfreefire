from flask import Flask, request, jsonify
from parser import parsear_mensaje
from whatsapp import enviar_mensaje
from scraper import ejecutar_bot
import threading

app = Flask(__name__)

def procesar_canje(telefono, datos):
    try:
        enviar_mensaje(telefono,
            f"⏳ Procesando tu canje...\n"
            f"💎 {datos['diamantes']} diamantes\n"
            f"🎮 ID: {datos['id']}\n"
            f"Espera unos segundos..."
        )

        resultado = ejecutar_bot(
            pin=datos["pin"],
            user_id=datos["id"],
            diamantes_esperados=datos["diamantes"]
        )

        if resultado["exitoso"]:
            enviar_mensaje(telefono,
                f"✅ *¡Recarga exitosa!*\n"
                f"💎 {resultado['diamantes_reales']} diamantes\n"
                f"🎮 ID: {datos['id']}\n"
                f"📌 PIN canjeado correctamente"
            )
        else:
            enviar_mensaje(telefono,
                f"❌ *Error en el canje*\n"
                f"Motivo: {resultado['error']}\n"
                f"Contacta al soporte."
            )

    except Exception as e:
        enviar_mensaje(telefono, f"❌ Error inesperado: {str(e)}")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print(f"📨 Webhook: {data}")

        # Estructura del webhook de WuzAPI
        tipo = data.get("type", "")
        if tipo not in ["message", "msg"]:
            return jsonify({"status": "ignorado"}), 200

        texto    = data.get("Body", "") or data.get("body", "")
        telefono = data.get("From", "") or data.get("from", "")
        telefono = telefono.replace("@s.whatsapp.net", "").replace("@c.us", "")

        if not texto or not telefono:
            return jsonify({"status": "sin datos"}), 200

        print(f"📱 De {telefono}: {texto}")

        datos = parsear_mensaje(texto)

        if not datos["valido"]:
            enviar_mensaje(telefono,
                f"{datos['error']}\n\n"
                f"📋 *Formato correcto:*\n"
                f"ID: 879209223\n"
                f"100 diamantes\n"
                f"pin: 98239-chbf87-2873h-2355"
            )
            return jsonify({"status": "formato invalido"}), 200

        hilo = threading.Thread(target=procesar_canje, args=(telefono, datos))
        hilo.start()

        return jsonify({"status": "procesando"}), 200

    except Exception as e:
        print(f"❌ Error webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
