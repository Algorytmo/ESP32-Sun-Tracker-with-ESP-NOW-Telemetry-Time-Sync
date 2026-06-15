# espnow_handler.py
import network, espnow, json
from config import PEER
from logging_utils import write_log

def init_espnow():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)

    e = espnow.ESPNow()
    e.active(True)

    try:
        e.add_peer(PEER)
    except OSError:
        pass

    return e

def wait_for_time(e):
    host, msg = e.recv()  # bloccante
    if not msg:
        return None
    try:
        data = json.loads(msg)
        write_log({"rtc_sync": data}, "DEBUG")
        return data
    except Exception as err:
        write_log({"rtc_error": str(err)}, "ERROR")
        return None
