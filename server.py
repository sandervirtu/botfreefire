from flask import Flask, request, jsonify
import requests as req

app = Flask(__name__)

# ── Datos fijos del formulario ─────────────────────────────────────────────
NOMBRE = "Alex Mendez"
FECHA_NAC = "10/01/2001"
NACIONALIDAD_CODE = "BO"
COUNTRY_ID = "5"
REDEEM_COUNTRY_ID = "5"
COMPANY_NAME = "HypeMexico"
REDEEM_SOURCE_TYPE_ID = "3"
PRODUCT_ID = "2630"

# ── Cookies de sesión (renovar si dejan de funcionar) ─────────────────────
COOKIES = {
    "_hjSessionUser_2988074": "eyJpZCI6ImI2NjM5Y2EwLWRmOWEtNWJiNC05MThhLWMwNmZjYzk0OGRkZSIsImNyZWF0ZWQiOjE3NjQ3OTg0Mjg4MjIsImV4aXN0aW5nIjp0cnVlfQ==",
    "AdoptConsent": "N4Ig7gpgRgzglgFwgSQCIgFwgKwEMoAmUAjABzEC0pAnAMYAsF9ptAzBdQAwG0We0AzYgDZWAgOz0C9XCAA0IAG5x4CAPYAnZAUwhitYQXHYIAJgqnxBYUyimIVTtXEUBUeuNzV7BU7nHyIAiCAMoIGnAAdgDmugDCAIoAFgDSAHIAghnJ6VkA4gCuGXEZAKJpcQBqAGLRWfUNjU0AdMj1zQCaTY2BagAOCMiRACq40TCYANog0QAypawASmAAXsgAVgAKgRSRcLgA8tGoALZ9aYGmpgCy0QCeSRR9ABqlgYsI2BYhAOrCNoEUhRFgAhABSB3oimIIMCMBCMNoAGt6GDKgVAscAFqcTZ3SLrLHbBSRUwFTjPTimdZqZ6BACqeRBCAQWIoAEcQsSQBoAPoQYQpLEgtQCDqBAA24kUi2eCGuHR+YMCAAk1BlUNgwOJomlOJd6GpNgAPA4ZRbs9AKXCRDlQPoEJG8/UKPLPYaKNIrSrmPqBOIdTakDoJRYqhACEAAXQU/QQBwKCFG4ymMZAtDUkRgEEigx0WAgilmP2wIUCGazOYQlQgGngmcwxFYCgKDtwSAIGQQulMVJsnHYImGxGwGFY4gwnE4zXEpFMWJAAF8gA",
    "AdoptVisitorId": "IwYwbAJg7ArApgJgLQKhMSAsAjBckAcADAJxRIBm2mUAhiXhArVEA===",
}

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "es-US,es-419;q=0.9,es;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://redeem.hype.games",
    "Referer": "https://redeem.hype.games/widget/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
}


@app.route("/canjear", methods=["POST"])
def canjear():
    data = request.json
    pin = data.get("pin")
    cliente_id = data.get("cliente_id")

    if not pin or not cliente_id:
        return jsonify({"exito": False, "mensaje": "Faltan datos: pin o cliente_id"})

    try:
        # ── PASO 1: Verificar cuenta ──────────────────────────────────────
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
            "CaptchaToken": "",
        }

        resp_account = req.post(
            "https://redeem.hype.games/validate/account",
            data=payload_account,
            headers=HEADERS,
            cookies=COOKIES,
            timeout=30
        )

        if resp_account.status_code != 200:
            return jsonify({"exito": False, "mensaje": f"Error en validate/account: {resp_account.status_code}"})

        # ── PASO 2: Canjear el PIN ────────────────────────────────────────
        payload_validate = {
            "Key": pin,
            "CaptchaToken": "",
        }

        resp_validate = req.post(
            "https://redeem.hype.games/validate",
            data=payload_validate,
            headers=HEADERS,
            cookies=COOKIES,
            timeout=30
        )

        contenido = resp_validate.text.lower()

        if resp_validate.status_code == 200 and ("exitoso" in contenido or "success" in contenido or "proceso terminado" in contenido):
            return jsonify({"exito": True, "mensaje": "Canje exitoso - diamantes entregados"})
        else:
            return jsonify({"exito": False, "mensaje": f"Error en canje: {resp_validate.text[:200]}"})

    except Exception as e:
        return jsonify({"exito": False, "mensaje": f"Error tecnico: {str(e)}"})


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
