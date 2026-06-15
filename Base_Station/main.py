# main.py

import network
import time
from config import WIFI_SSID, WIFI_PASS
from geo import get_geo
from time_sync import sync_time
from espnow_handler import espnow_init, wait_and_reply

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    while not wlan.isconnected():
        time.sleep(0.2)

    print("WiFi OK:", wlan.ifconfig())
    return wlan

def start():
    wifi_connect()

    lat, lon, tz = get_geo()
    sync_time()

    e = espnow_init()

    print("BASE pronta. Aspetto telemetria...")

    while True:
        wait_and_reply(e, lat, lon)

