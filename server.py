from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
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

COOKIES = {
    "_hjSessionUser_2988074": "eyJpZCI6ImI2NjM5Y2EwLWRmOWEtNWJiNC05MThhLWMwNmZjYzk0OGRkZSIsImNyZWF0ZWQiOjE3NjQ3OTg0Mjg4MjIsImV4aXN0aW5nIjp0cnVlfQ==",
    "AdoptConsent": "N4Ig7gpgRgzglgFwgSQCIgFwgKwEMoAmUAjABzEC0pAnAMYAsF9ptAzBdQAwG0We0AzYgDZWAgOz0C9XCAA0IAG5x4CAPYAnZAUwhitYQXHYIAJgqnxBYUyimIVTtXEUBUeuNzV7BU7nHyIAiCAMoIGnAAdgDmugDCAIoAFgDSAHIAghnJ6VkA4gCuGXEZAKJpcQBqAGLRWfUNjU0AdMj1zQCaTY2BagAOCMiRACq40TCYANog0QAypawASmAAXsgAVgAKgRSRcLgA8tGoALZ9aYGmpgCy0QCeSRR9ABqlgYsI2BYhAOrCNoEUhRFgAhABSB3oimIIMCMBCMNoAGt6GDKgVAscAFqcTZ3SLrLHbBSRUwFTjPTimdZqZ6BACqeRBCAQWIoAEcQsSQBoAPoQYQpLEgtQCDqBAA24kUi2eCGuHR+YMCAAk1BlUNgwOJomlOJd6GpNgAPA4ZRbs9AKXCRDlQPoEJG8/UKPLPYaKNIrSrmPqBOIdTakDoJRYqhACEAAXQU/QQBwKCFG4ymMZAtDUkRgEEigx0WAgilmP2wIUCGazOYQlQgGngmcwxFYCgKDtwSAIGQQulMVJsnHYImGxGwGFY4gwnE4zXEpFMWJAAF8gA",
    "AdoptVisitorId": "IwYwbAJg7ArApgJgLQKhMSAsAjBckAcADAJxRIBm2mUAhiXhArVEA===",
}

BASE_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "es-US,es-419;q=0.9,es;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://redeem.hype.games",
    "Referer": "https://redeem.hype.games/widget/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
}


def obtener_captcha_token(pin, cliente_id):
    """Usa Playwright para obtener el CaptchaToken interceptando el request."""
    token = None

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Interceptar el request para capturar el CaptchaToken
        def handle_request(request):
            nonlocal token
            if "validate/account" in request.url and request.method == "POST":
                post_data = request.post_data or ""
                for part in post_data.split("&"):
                    if part.startswith("CaptchaToken="):
                        token = part.replace("CaptchaToken=", "")
                        break

        page.on("request", handle_request)

        try:
            page.goto("https://redeempins.com/", timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # Ingresar PIN
            page.locator("input").first.fill(pin)
            time.sleep(1)
            page.locator("button:has-text('Canjear')").first.click()
            time.sleep(5)

            # Rellenar formulario
            try:
                page.get_by_placeholder("Nombre Completo").fill(NOMBRE)
            except:
                page.locator("input").nth(0).fill(NOMBRE)
            time.sleep(1)

            try:
                page.get_by_placeholder("Fecha de Nacimiento").fill(FECHA_NAC)
            except:
                page.locator("input").nth(1).fill(FECHA_NAC)
            time.sleep(1)

            page.locator("select").first.select_option(label="Bolivia (Plurinational State of)")
            time.sleep(1)

            try:
                page.get_by_placeholder("ID de usuario en el juego").fill(str(cliente_id))
            except:
                page.locator("input").nth(2).fill(str(cliente_id))
            time.sleep(1)

            checkbox = page.locator("input[type='checkbox']").first
            if not checkbox.is_checked():
                checkbox.click()
            time.sleep(1)

            # Clic en Verificar ID — aquí se genera el CaptchaToken
            page.locator("button:has-text('Verificar ID')").first.click()
            time.sleep(5)

        except Exception as e:
            print(f"Error obteniendo token: {e}")
        finally:
            context.close()
            browser.close()

    return token


@app.route("/canjear", methods=["POST"])
def canjear():
    data = request.json
    pin = data.get("pin")
    cliente_id = data.get("cliente_id")

    if not pin or not cliente_id:
        return jsonify({"exito": False, "mensaje": "Faltan datos"})

    try:
        # Obtener CaptchaToken real via Playwright
        captcha_token = obtener_captcha_token(pin, cliente_id)

        if not captcha_token:
            return jsonify({"exito": False, "mensaje": "No se pudo obtener el CaptchaToken"})

        # PASO 1: Verificar cuenta con token real
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
            cookies=COOKIES,
            timeout=30
        )

        if resp_account.status_code != 200:
            return jsonify({"exito": False, "mensaje": f"Error cuenta: {resp_account.text[:200]}"})

        account_data = resp_account.json()
        if not account_data.get("Success"):
            return jsonify({"exito": False, "mensaje": f"Cuenta no válida: {account_data}"})

        # PASO 2: Canjear PIN
        payload_validate = {
            "Key": pin,
            "CaptchaToken": captcha_token,
        }

        resp_validate = req.post(
            "https://redeem.hype.games/validate",
            data=payload_validate,
            headers=BASE_HEADERS,
            cookies=COOKIES,
            timeout=30
        )

        contenido = resp_validate.text.lower()

        if resp_validate.status_code == 200 and ("exitoso" in contenido or "success" in contenido or "proceso terminado" in contenido or "true" in contenido):
            return jsonify({"exito": True, "mensaje": "Canje exitoso - diamantes entregados"})
        else:
            return jsonify({"exito": False, "mensaje": f"Error canje: {resp_validate.text[:200]}"})

    except Exception as e:
        return jsonify({"exito": False, "mensaje": f"Error tecnico: {str(e)}"})


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
