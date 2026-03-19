from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import time

app = Flask(__name__)

# Datos fijos para el formulario (siempre los mismos)
NOMBRE = "Alex Mendez"
FECHA_NAC = "10/01/2001"
NACIONALIDAD = "Bolivia (Plurinational State of)"

@app.route("/canjear", methods=["POST"])
def canjear():
    data = request.json
    pin = data.get("pin")
    cliente_id = data.get("cliente_id")

    if not pin or not cliente_id:
        return jsonify({"exito": False, "mensaje": "Faltan datos: pin o cliente_id"})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # ── PASO 1: Ir a la web e ingresar el PIN ──────────────────────
            page.goto("https://redeempins.com/", timeout=30000)
            page.wait_for_load_state("networkidle")

            # Escribir el PIN en el primer input disponible
            page.locator("input").first.fill(pin)
            time.sleep(1)

            # Clic en el botón "Canjear"
            page.locator("button:has-text('Canjear')").first.click()
            time.sleep(4)

            # ── PASO 2: Rellenar el formulario de datos ────────────────────
            # Nombre completo
            try:
                page.get_by_placeholder("Nombre Completo").fill(NOMBRE)
            except:
                page.locator("input").nth(0).fill(NOMBRE)
            time.sleep(1)

            # Fecha de nacimiento
            try:
                page.get_by_placeholder("Fecha de Nacimiento").fill(FECHA_NAC)
            except:
                page.locator("input").nth(1).fill(FECHA_NAC)
            time.sleep(1)

            # Seleccionar nacionalidad en el dropdown
            page.locator("select").first.select_option(label=NACIONALIDAD)
            time.sleep(1)

            # ID del cliente
            try:
                page.get_by_placeholder("ID de usuario en el juego").fill(str(cliente_id))
            except:
                page.locator("input").nth(2).fill(str(cliente_id))
            time.sleep(1)

            # Marcar el checkbox de términos y condiciones
            checkbox = page.locator("input[type='checkbox']").first
            if not checkbox.is_checked():
                checkbox.click()
            time.sleep(1)

            # Clic en "Verificar ID"
            page.locator("button:has-text('Verificar ID')").first.click()
            time.sleep(4)

            # ── PASO 3: Clic en "¡Canjear Ahora!" ────────────────────────
            page.locator("button:has-text('Canjear Ahora')").first.click()
            time.sleep(4)

            # ── PASO 4: Verificar resultado ───────────────────────────────
            contenido = page.content().lower()

            if "proceso terminado" in contenido or "exitoso" in contenido or "success" in contenido:
                return jsonify({"exito": True, "mensaje": "Canje exitoso - diamantes entregados"})
            elif "error" in contenido or "invalido" in contenido or "invalid" in contenido:
                return jsonify({"exito": False, "mensaje": "PIN inválido o error en el canje"})
            else:
                # Capturar screenshot para debug si hay duda
                page.screenshot(path="/tmp/resultado.png")
                return jsonify({"exito": False, "mensaje": "Resultado desconocido - revisar manualmente"})

        except Exception as e:
            return jsonify({"exito": False, "mensaje": f"Error técnico: {str(e)}"})

        finally:
            browser.close()


@app.route("/ping", methods=["GET"])
def ping():
    # Endpoint para verificar que el servidor está vivo
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
