import requests
import os
from dotenv import load_dotenv

load_dotenv()

WUZAPI_URL   = os.getenv("WUZAPI_URL")
WUZAPI_TOKEN = os.getenv("WUZAPI_TOKEN")

def enviar_mensaje(telefono, mensaje):
    try:
        headers = {
            "Token": WUZAPI_TOKEN,
            "Content-Type": "application/json"
        }
        payload = {
            "Phone": f"{telefono}@s.whatsapp.net",
            "Body":  mensaje
        }
        response = requests.post(
            f"{WUZAPI_URL}/chat/send/text",
            json=payload,
            headers=headers,
            timeout=15
        )
        print(f"📤 WhatsApp enviado: {response.status_code} → {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error WhatsApp: {e}")
        return False