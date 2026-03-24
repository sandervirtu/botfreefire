import os
import re
import time
from playwright.sync_api import sync_playwright
from capsolver_helper import resolver_recaptcha
from dotenv import load_dotenv

load_dotenv()

NOMBRE       = "Alex Mendez"
FECHA        = "10-10-2002"
NACIONALIDAD = "BO"

def extraer_diamantes_pagina(page):
    """Extrae la cantidad de diamantes que aparece en la página después de ingresar el PIN"""
    try:
        time.sleep(2)
        contenido = page.inner_text("body")
        
        # Busca patrones como "1060 Diamond", "100 Diamond", "520 Diamond"
        match = re.search(r'(\d+)\s*Diamond', contenido, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # También busca "1060 Diamantes"
        match2 = re.search(r'(\d+)\s*[Dd]iamantes?', contenido)
        if match2:
            return match2.group(1)
            
        return None
    except Exception as e:
        print(f"⚠️ Error extrayendo diamantes: {e}")
        return None

def ejecutar_bot(pin=None, user_id=None, diamantes_esperados=None):
    if pin is None:
        pin = "DE3283B5-A8EF-41BD-B05D-C3F218923C13"
    if user_id is None:
        user_id = "225211031"

    resultado = {
        "exitoso": False,
        "diamantes_reales": None,
        "diamantes_esperados": diamantes_esperados,
        "error": None
    }

    try:
        with sync_playwright() as p:
            print("🌐 Abriendo navegador...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # ── PASO 1 ──────────────────────────────
            print("📌 Paso 1: Abriendo redeem.hype.games...")
            page.goto("https://redeem.hype.games/", wait_until="networkidle")
            time.sleep(2)

            # ── PASO 2 ──────────────────────────────
            print("📌 Paso 2: Escribiendo PIN...")
            page.wait_for_selector("#pininput", timeout=10000)
            page.fill("#pininput", pin)
            time.sleep(1)

            # ── PASO 3 ──────────────────────────────
            print("📌 Paso 3: Resolviendo reCAPTCHA...")
            token = resolver_recaptcha("https://redeem.hype.games")
            page.evaluate(f"""
                () => {{
                    let el = document.getElementById('g-recaptcha-response');
                    if (!el) {{
                        el = document.createElement('textarea');
                        el.id = 'g-recaptcha-response';
                        el.name = 'g-recaptcha-response';
                        el.style.display = 'none';
                        document.body.appendChild(el);
                    }}
                    el.value = '{token}';
                }}
            """)
            time.sleep(1)

            # ── PASO 4 ──────────────────────────────
            print("📌 Paso 4: Click en CANJEAR...")
            page.locator("button", has_text="CANJEAR").first.click()
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # ── PASO 5: VERIFICAR DIAMANTES ──────────
            print("📌 Paso 5: Verificando diamantes del PIN...")
            diamantes_en_web = extraer_diamantes_pagina(page)
            print(f"💎 Web muestra: {diamantes_en_web} diamonds")
            print(f"💎 Cliente pidió: {diamantes_esperados} diamonds")

            resultado["diamantes_reales"] = diamantes_en_web

            # Si el cliente especificó diamantes, verificar que coincidan
            if diamantes_esperados and diamantes_en_web:
                if str(diamantes_en_web) != str(diamantes_esperados):
                    resultado["error"] = (
                        f"PIN incorrecto: el PIN es de {diamantes_en_web} diamantes "
                        f"pero se esperaban {diamantes_esperados} diamantes."
                    )
                    browser.close()
                    return resultado
                else:
                    print(f"✅ Verificación correcta: {diamantes_en_web} diamantes")

            # ── PASO 6 ──────────────────────────────
            print("📌 Paso 6: Escribiendo nombre...")
            page.wait_for_selector("#Name", timeout=10000)
            page.fill("#Name", NOMBRE)
            time.sleep(0.5)

            # ── PASO 7 ──────────────────────────────
            print("📌 Paso 7: Escribiendo fecha...")
            page.fill("#BornAt", FECHA)
            time.sleep(0.5)

            # ── PASO 8 ──────────────────────────────
            print("📌 Paso 8: Seleccionando nacionalidad...")
            page.select_option("#NationalityAlphaCode", value=NACIONALIDAD)
            time.sleep(0.5)

            # ── PASO 9 ──────────────────────────────
            print("📌 Paso 9: Escribiendo ID del cliente...")
            page.fill("#GameAccountId", user_id)
            time.sleep(0.5)

            # ── PASO 10 ─────────────────────────────
            print("📌 Paso 10: Aceptando términos...")
            checkbox = page.locator("#privacy")
            if not checkbox.is_checked():
                checkbox.check()
            time.sleep(0.5)

            # ── PASO 11 ─────────────────────────────
            print("📌 Paso 11: Click VERIFICAR ID...")
            page.locator("button", has_text="VERIFICAR ID").first.click()
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # ── PASO 12 ─────────────────────────────
            print("📌 Paso 12: Click CANJEAR final...")
            page.locator("button", has_text="CANJEAR").first.click()
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            page.screenshot(path="resultado.png")
            resultado["exitoso"] = True
            print("🎉 ¡Canje exitoso!")
            browser.close()

    except Exception as e:
        resultado["error"] = str(e)
        print(f"❌ Error: {e}")

    return resultado

if __name__ == "__main__":
    res = ejecutar_bot(
        pin="DE3283B5-A8EF-41BD-B05D-C3F218923C13",
        user_id="225211031",
        diamantes_esperados="100"
    )
    print(res)