# power.py
import time, machine

def go_sleep_indef(display_ok, display, servo_pan, servo_tilt):
    if display_ok:
        display.poweroff()
    servo_pan.deinit()
    servo_tilt.deinit()
    time.sleep(0.2)
    machine.deepsleep()

def go_sleep_timer(ms, display_ok, display, servo_pan, servo_tilt):
    if display_ok:
        display.poweroff()
    servo_pan.deinit()
    servo_tilt.deinit()
    time.sleep(0.2)
    machine.deepsleep(ms)
