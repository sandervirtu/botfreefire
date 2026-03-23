import capsolver
import os
from dotenv import load_dotenv

load_dotenv()
capsolver.api_key = os.getenv("CAPSOLVER_API_KEY")

def resolver_recaptcha(url):
    print("🔐 Resolviendo reCAPTCHA invisible con Capsolver...")
    
    solution = capsolver.solve({
        "type": "ReCaptchaV2TaskProxyless",
        "websiteURL": "https://redeem.hype.games",
        "websiteKey": "6Lf_DWEpAAAAAEg4rjruIXopl29ai0v9o6Vafx0A",
        "isInvisible": True,
    })

    token = solution["gRecaptchaResponse"]
    print("✅ Captcha resuelto!")
    return token