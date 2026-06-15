# utils.py

from machine import Pin
import time
from config import LED_PIN

led = Pin(LED_PIN, Pin.OUT)

def blink_led(duration=0.05):
    led.value(1)
    time.sleep(duration)
    led.value(0)
