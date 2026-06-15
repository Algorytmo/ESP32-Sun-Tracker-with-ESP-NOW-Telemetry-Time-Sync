# joystick.py
from machine import ADC, Pin
import esp32, time
from config import CENTER_X, CENTER_Y
from logging_utils import write_log

def init_joystick():
    try:
        vrx = ADC(Pin(39))
        vry = ADC(Pin(36))
        sw  = Pin(25, Pin.IN, Pin.PULL_UP)

        vrx.atten(ADC.ATTN_11DB)
        vry.atten(ADC.ATTN_11DB)

        wake_pin = Pin(39, Pin.IN)
        esp32.wake_on_ext0(pin=wake_pin, level=esp32.WAKEUP_ANY_HIGH)

        return vrx, vry, sw, True
    except:
        print("Joystick non trovato")
        return None, None, None, False

def run_manual(vrx, vry, pan_angle, tilt_angle, move_pan, move_tilt, last_move):
    x = vrx.read()
    y = vry.read()

    speed_pan  = int((y - CENTER_Y) / 250) * -1
    speed_tilt = int((x - CENTER_X) / 250) * -1

    if abs(speed_pan) > 1:
        pan_angle = max(0, min(180, pan_angle + speed_pan))
        move_pan(pan_angle)
        write_log({"pan": pan_angle, "speed_pan": speed_pan}, "DEBUG")
        last_move = time.ticks_ms()

    if abs(speed_tilt) > 1:
        tilt_angle = max(0, min(90, tilt_angle + speed_tilt))
        move_tilt(tilt_angle)
        write_log({"tilt": tilt_angle, "speed_tilt": speed_tilt}, "DEBUG")
        last_move = time.ticks_ms()

    time.sleep(0.02)
    return pan_angle, tilt_angle, last_move
