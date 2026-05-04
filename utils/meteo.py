import requests

WEATHER_RISK = {
    "Potato___Late_blight":   {"desc": "Mildiou actif par temps frais (8-22C) et tres humide (>80%).",        "temp_range": (8,  22), "humidity_min": 80, "humidity_max": 100},
    "Tomato_Late_blight":     {"desc": "Mildiou actif entre 10-24C avec humidite >75%.",                     "temp_range": (10, 24), "humidity_min": 75, "humidity_max": 100},
    "Tomato_Early_blight":    {"desc": "Alternariose favorisee par temps chaud (24-30C) et humide.",         "temp_range": (24, 30), "humidity_min": 55, "humidity_max": 100},
    "Potato___Early_blight":  {"desc": "Alternariose favorisee par temps chaud (24-30C) et humide.",         "temp_range": (24, 30), "humidity_min": 55, "humidity_max": 100},
    "Tomato_Leaf_Mold":       {"desc": "Moisissure active par temps chaud/humide (21-24C, >85% HR).",        "temp_range": (21, 24), "humidity_min": 85, "humidity_max": 100},
    "Tomato_Bacterial_spot":  {"desc": "Bacteriose favorisee par pluies et temperatures de 25-30C.",         "temp_range": (25, 30), "humidity_min": 70, "humidity_max": 100},
    "Tomato_Septoria_leaf_spot": {"desc": "Septoriose active par temps humide et temperatures moderees.",    "temp_range": (20, 25), "humidity_min": 65, "humidity_max": 100},
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "desc": "Acariens proliferent par temps CHAUD et SEC (>26C, humidite <50%).",
        "temp_range": (26, 50), "humidity_min": 0, "humidity_max": 50,
    },
}

def get_weather_risk(city, api_key, disease_label):
    if not api_key or not city:
        return None
    try:
        url  = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return {"error": f"Ville introuvable ou cle API invalide (code {resp.status_code})."}
        data     = resp.json()
        temp     = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc_meteo = data["weather"][0]["description"]

        risk_info = WEATHER_RISK.get(disease_label)
        if not risk_info:
            return {"temp": temp, "humidity": humidity, "desc_meteo": desc_meteo, "risk": None,
                    "msg": "Pas de donnees de risque meteo pour cette maladie."}

        temp_min, temp_max = risk_info["temp_range"]
        hum_min  = risk_info.get("humidity_min", 0)
        hum_max  = risk_info.get("humidity_max", 100)

        risk_score = 0
        if temp_min <= temp <= temp_max:
            risk_score += 1
        if hum_min <= humidity <= hum_max:
            risk_score += 1

        risk_level = {2: "Eleve", 1: "Modere", 0: "Faible"}[risk_score]

        return {
            "temp":       temp,
            "humidity":   humidity,
            "desc_meteo": desc_meteo.capitalize(),
            "risk":       risk_level,
            "msg":        risk_info["desc"],
        }
    except Exception as e:
        return {"error": str(e)}
