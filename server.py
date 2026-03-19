from flask import Flask, request, jsonify
import requests as req
import time

app = Flask(__name__)

NOMBRE = "Alex Mendez"
FECHA_NAC = "10/01/2001"
NACIONALIDAD_CODE = "BO"
COUNTRY_ID = "5"
REDEEM_COUNTRY_ID = "5"
COMPANY_NAME = "HypeMexico"
REDEEM_SOURCE_TYPE_ID = "3"
PRODUCT_ID = "2630"

CAPSOLVER_API_KEY = "CAP-96332E07A26217212E0A4F1ECCC7C1C6953F67B38D67BFCE12383ED9D3D49262"
RECAPTCHA_SITE_KEY = "6Lf_DWEpAAAAAEg4rjruIXopl29ai0v9o6Vafx0A"
WEBSITE_URL = "https://redeempins.com/"

BASE_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "es-US,es-419;q=0.9,es;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://redeem.hype.games",
    "Referer": "https://redeem.hype.games/widget/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
}


def obtener_captcha_token():
    try:
        payload = {
            "clientKey": CAPSOLVER_API_KEY,
            "task": {
                "type": "ReCaptchaV3TaskProxyLess",
                "websiteURL": WEBSITE_URL,
                "websiteKey": RECAPTCHA_SITE_KEY,
                "pageAction": "verify"
            }
        }

        print(f"[CAPSOLVER] Enviando tarea...")
        resp = req.post("https://api.capsolver.com/createTask", json=payload, timeout=30)
        print(f"[CAPSOLVER] Status: {resp.status_code} - Response: {resp.text[:300]}")

        data = resp.json()
        task_id = data.get("taskId")

        if not task_id:
            print(f"[CAPSOLVER] Error: no taskId - {data}")
            return None

        print(f"[CAPSOLVER] Task ID: {task_id}")

        for i in range(30):
            time.sleep(5)
            result_payload = {
                "clientKey": CAPSOLVER_API_KEY,
                "taskId": task_id
            }
            result = req.post("https://api.capsolver.com/getTaskResult", json=result_payload, timeout=30)
            data = result.json()
            print(f"[CAPSOLVER] Intento {i+1}: {data.get('status')} - {str(data)[:200]}")

            if data.get("status") == "ready":
                token = data.get("solution", {}).get("gRecaptchaResponse")
                print(f"[CAPSOLVER] Token obtenido: {str(token)[:50]}...")
                return token

        print("[CAPSOLVER] Timeout esperando resultado")
        return None

    except Exception as e:
        print(f"[CAPSOLVER] Excepcion: {str(e)}")
        return None


@app.route("/canjear", methods=["POST"])
def canjear():
    data = request.json
    pin = data.get("pin")
    cliente_id = data.get("cliente_id")

    if not pin or not cliente_id:
        return jsonify({"exito": False, "mensaje": "Faltan datos"})

    try:
        captcha_token = obtener_captcha_token()

        if not captcha_token:
            return jsonify({"exito": False, "mensaje": "No se pudo resolver el captcha"})

        payload_account = {
            "QueryString": "",
            "RedeemCountryId": REDEEM_COUNTRY_ID,
            "ProductId": PRODUCT_ID,
            "CountryId": COUNTRY_ID,
            "CompanyName": COMPANY_NAME,
            "Key": pin,
            "CookieCardHypeInfo": "",
            "Customer.Name": NOMBRE,
            "Customer.BornAt": FECHA_NAC,
            "Customer.NationalityAlphaCode": NACIONALIDAD_CODE,
            "Customer.CountryId": COUNTRY_ID,
            "RedeemSourceTypeId": REDEEM_SOURCE_TYPE_ID,
            "Customer.CompanyName": COMPANY_NAME,
            "GameAccountId": str(cliente_id),
            "privacy": "on",
            "CaptchaToken": captcha_token,
        }

        resp_account = req.post(
            "https://redeem.hype.games/validate/account",
            data=payload_account,
            headers=BASE_HEADERS,
            timeout=30
        )

        print(f"[ACCOUNT] Status: {resp_account.status_code} - {resp_account.text[:300]}")

        if resp_account.status_code != 200:
            return jsonify({"exito": False, "mensaje": f"Error cuenta: {resp_account.text[:200]}"})

        account_data = resp_account.json()
        if not account_data.get("Success"):
            return jsonify({"exito": False, "mensaje": f"Cuenta invalida: {account_data}"})

        payload_validate = {
            "Key": pin,
            "CaptchaToken": captcha_token,
        }

        resp_validate = req.post(
            "https://redeem.hype.games/validate",
            data=payload_validate,
            headers=BASE_HEADERS,
            timeout=30
        )

        print(f"[VALIDATE] Status: {resp_validate.status_code} - {resp_validate.text[:300]}")
        contenido = resp_validate.text.lower()

        if resp_validate.status_code == 200 and ("true" in contenido or "exitoso" in contenido or "success" in contenido or "proceso terminado" in contenido):
            return jsonify({"exito": True, "mensaje": "Canje exitoso - diamantes entregados"})
        else:
            return jsonify({"exito": False, "mensaje": f"Error canje: {resp_validate.text[:200]}"})

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"exito": False, "mensaje": f"Error tecnico: {str(e)}"})


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
