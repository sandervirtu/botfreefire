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
WEBSITE_URL = "https://redeem.hype.games/widget/"

COOKIES = "AdoptVisitorId=IwYwbAJg7ArApgJgLQKhMSAsAjBckAcADAJxRIBm2mUAhiXhArVEA===; _ga=GA1.1.412054514.1764798429; _tt_enable_cookie=1; _ttp=01KBK2Y3YRYYB76JSW9QW5XR18_.tt.1; _hjSessionUser_2988074=eyJpZCI6ImI2NjM5Y2EwLWRmOWEtNWJiNC05MThhLWMwNmZjYzk0OGRkZSIsImNyZWF0ZWQiOjE3NjQ3OTg0Mjg4MjIsImV4aXN0aW5nIjp0cnVlfQ==; _fbp=fb.1.1764798626288.260048343647816775; _gcl_au=1.1.513644217.1773675420; _uetsid=a1f33e7023ba11f1ace54f33c85f463b; _uetvid=9de48150d09111f09298e35c4afde2b9; ttcsid=1773941992956::Ddw2ilpYhqjj8hFXVhjB.4.1773942002969.0; ttcsid_CCG8BNBC77U3OVB1GN10=1773941992956::_mTqd4yE4O4FzM4RByN5.4.1773942002970.1; _ga_WCJMJ224ST=GS2.1.s1773941989$o6$g1$t1773942037$j12$l0$h1305070224; AdoptConsent=N4Ig7gpgRgzglgFwgSQCIgFwgIZQBwAM2AnMQCYC0ALFQGzbUBMAjAMwV614QUDsvUZmVqMIAMyqMArCAA0IAG5x4CAPYAnZGUwhmAY1pleUiIwqNew6lFEcCxXhTFQqvEqLKNsvOSAR6xAGUEdTgAOwBzHQBhAEUACwBVADECAEEElPSAcQBXNOi0gFEAOWiAdWSItJrauvr6gDpkWsaATQb631UABwRkMIAVbAiYTABtEHKFEoBPBAAtVjIAa2jfGBKADQBHKgApFZ2IgFtfEqkVgC88MDaAJWTckABdeV6EAHlchGHRibeID0qjCMAgYX62iwACswm0ANJQAi+YGg8EIABqEHU8BBmGY8lyPTI2CQZDSCB0jAIjFoFAI7GYxEGzF4GCozAwBDwjWYUmYCxAAF8gA=; _clck=1dc1d32%5E2%5Eg4i%5E0%5E2163; _clsk=vkfxna%5E1773978023876%5E2%5E1%5En.clarity.ms%2Fcollect"

BASE_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "es-US,es-419;q=0.9,es;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://redeem.hype.games",
    "Referer": "https://redeem.hype.games/widget/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": COOKIES,
}


def obtener_captcha_token():
    try:
        payload = {
            "clientKey": CAPSOLVER_API_KEY,
            "task": {
                "type": "ReCaptchaV3TaskProxyLess",
                "websiteURL": WEBSITE_URL,
                "websiteKey": RECAPTCHA_SITE_KEY,
                "pageAction": "submit"
            }
        }
        print(f"[CAPSOLVER] Enviando tarea...")
        resp = req.post("https://api.capsolver.com/createTask", json=payload, timeout=30)
        data = resp.json()
        task_id = data.get("taskId")
        if not task_id:
            return None
        for i in range(30):
            time.sleep(5)
            result = req.post("https://api.capsolver.com/getTaskResult", json={"clientKey": CAPSOLVER_API_KEY, "taskId": task_id}, timeout=30)
            data = result.json()
            print(f"[CAPSOLVER] Intento {i+1}: {data.get('status')}")
            if data.get("status") == "ready":
                return data.get("solution", {}).get("gRecaptchaResponse")
        return None
    except Exception as e:
        print(f"[CAPSOLVER] Error: {str(e)}")
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

        session = req.Session()
        session.headers.update(BASE_HEADERS)

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

        resp_account = session.post(
            "https://redeem.hype.games/validate/account",
            data=payload_account,
            timeout=30
        )
        print(f"[ACCOUNT] {resp_account.status_code} - {resp_account.text[:300]}")

        if resp_account.status_code != 200:
            return jsonify({"exito": False, "mensaje": f"Error cuenta: {resp_account.text[:200]}"})

        account_data = resp_account.json()
        if not account_data.get("Success"):
            return jsonify({"exito": False, "mensaje": f"Cuenta invalida: {account_data}"})

        resp_validate = session.post(
            "https://redeem.hype.games/validate",
            data={"Key": pin, "CaptchaToken": captcha_token},
            timeout=30
        )
        print(f"[VALIDATE] {resp_validate.status_code} - {resp_validate.text[:300]}")
        contenido = resp_validate.text.lower()

        if resp_validate.status_code == 200 and ("true" in contenido or "success" in contenido or "proceso terminado" in contenido):
            return jsonify({"exito": True, "mensaje": "Canje exitoso"})
        else:
            return jsonify({"exito": False, "mensaje": f"Error: {resp_validate.text[:200]}"})

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"exito": False, "mensaje": f"Error tecnico: {str(e)}"})


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
