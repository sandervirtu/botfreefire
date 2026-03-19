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

            # Escribir el PIN en el campo "Código Pin"
            page.fill("input[placeholder='Código Pin'], input[type='text']", pin)

            # Clic en el botón "Canjear"
            page.click("button:has-text('Canjear')")
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            # ── PASO 2: Rellenar el formulario de datos ────────────────────
            # Nombre completo (siempre Alex Mendez)
            page.fill("input[placeholder='Nombre Completo'], input[name='name']", NOMBRE)

            # Fecha de nacimiento
            page.fill("input[placeholder='Fecha de Nacimiento'], input[name='birthday']", FECHA_NAC)

            # Seleccionar nacionalidad en el dropdown
            page.select_option("select", label=NACIONALIDAD)

            # ID del cliente (este es el dato dinámico que viene del bot)
            page.fill("input[placeholder='ID de usuario en el juego'], input[name='player_id']", str(cliente_id))

            # Marcar el checkbox de términos y condiciones
            checkbox = page.locator("input[type='checkbox']")
            if not checkbox.is_checked():
                checkbox.click()

            time.sleep(1)

            # Clic en "Verificar ID"
            page.click("button:has-text('Verificar ID')")
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # ── PASO 3: Clic en "¡Canjear Ahora!" ────────────────────────
            page.click("button:has-text('Canjear Ahora')")
            page.wait_for_load_state("networkidle")
            time.sleep(3)

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
