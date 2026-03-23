import re

def parsear_mensaje(texto):
    resultado = {
        "id": None,
        "diamantes": None,
        "pin": None,
        "valido": False,
        "error": None
    }

    try:
        id_match = re.search(r'ID[:\s]+(\d+)', texto, re.IGNORECASE)
        if id_match:
            resultado["id"] = id_match.group(1).strip()

        dia_match = re.search(r'(\d+)\s*diamantes?', texto, re.IGNORECASE)
        if dia_match:
            resultado["diamantes"] = dia_match.group(1).strip()

        pin_match = re.search(r'pin[:\s]+([A-Za-z0-9\-]+)', texto, re.IGNORECASE)
        if pin_match:
            resultado["pin"] = pin_match.group(1).strip()

        if not resultado["id"]:
            resultado["error"] = "❌ No encontré el ID del jugador."
        elif not resultado["diamantes"]:
            resultado["error"] = "❌ No encontré la cantidad de diamantes."
        elif not resultado["pin"]:
            resultado["error"] = "❌ No encontré el PIN."
        else:
            resultado["valido"] = True

    except Exception as e:
        resultado["error"] = f"❌ Error: {str(e)}"

    return resultado