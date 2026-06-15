# geo.py

import urequests

def get_geo():
    try:
        r = urequests.get("http://ip-api.com/json/")
        data = r.json()
        r.close()

        if data.get("status") != "success":
            raise Exception("API error")

        return float(data["lat"]), float(data["lon"]), data["timezone"]

    except Exception as e:
        print("Geo error:", e)
        return 0.0, 0.0, "Europe/Rome"
