from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://redeem.hype.games/', wait_until='networkidle')
    time.sleep(2)
    page.fill('input', '1DD76690-27D1-43D4-B237-EFE37C8DD26C')
    time.sleep(1)
    page.locator('button', has_text='CANJEAR').first.click()
    page.wait_for_load_state('networkidle')
    time.sleep(4)
    inputs = page.evaluate("""
        () => Array.from(document.querySelectorAll('input, select, textarea'))
              .map(el => ({tag: el.tagName, placeholder: el.placeholder, name: el.name, id: el.id}))
    """)
    for i in inputs:
        print(i)
    browser.close()