# logging_utils.py
import json
import time
import os

LOG_FILE = "log.txt"
MAX_LOG_SIZE = 200 * 1024   # 200 KB

def write_log(data, level="INFO"):
    try:
        # --- Rotazione automatica del file ---
        try:
            if LOG_FILE in os.listdir():
                size = os.stat(LOG_FILE)[6]
                if size > MAX_LOG_SIZE:
                    ts = int(time.time())
                    os.rename(LOG_FILE, "log_old_{}.txt".format(ts))
        except:
            pass

        # --- Entry ordinata ---
        entry = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "level": level,
            "data": data
        }

        # JSON compatto ma leggibile
        line = json.dumps(entry, separators=(",", ": "))

        # --- Scrittura ---
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")

    except Exception as e_log:
        print("Errore scrivendo il log:", e_log)
