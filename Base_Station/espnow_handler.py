# espnow_handler.py

import network
import espnow
from config import PEER
from utils import blink_led
from time_sync import build_packet

def espnow_init():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)

    e = espnow.ESPNow()
    e.active(True)

    try:
        e.add_peer(PEER)
    except OSError:
        pass

    return e

def wait_and_reply(e, lat, lon):
    host, msg = e.recv()  # BLOCCANTE
    if msg:
        blink_led()
        print("RX telemetria:", msg)

        packet = build_packet(lat, lon)
        e.send(PEER, packet)
        print("Orario inviato al nodo solare\n")
