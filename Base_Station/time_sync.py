# time_sync.py

import ntptime
import time
import json

def sync_time():
    try:
        ntptime.host = "pool.ntp.org"
        ntptime.settime()
        print("NTP OK")
    except Exception as e:
        print("NTP error:", e)

def build_packet(lat, lon):
    tm = time.localtime()

    data = {
        "year": tm[0],
        "month": tm[1],
        "day": tm[2],
        "hour": tm[3],
        "minute": tm[4],
        "second": tm[5],
        "lat": lat,
        "lon": lon
    }

    print("TX packet:", data)
    return json.dumps(data)
