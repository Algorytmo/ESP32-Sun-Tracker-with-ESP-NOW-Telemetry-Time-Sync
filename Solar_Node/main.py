# main.py

import machine
import time

from config import (
    PEER,
    SLEEP_MS,
    DEFAULT_LAT,
    DEFAULT_LON
)

from hardware import (
    init_adc,
    init_power_monitor,
    init_display,
    init_servos,
    move_pan,
    move_tilt,
    read_power,
    update_display
)

from joystick import init_joystick, run_manual
from tracking import track_sun
from telemetry import send_telemetry
from espnow_handler import init_espnow, wait_for_time
from power import go_sleep_timer, go_sleep_indef
from logging_utils import write_log


def start():
    # ============================================================
    #   VARIABILI DINAMICHE
    # ============================================================
    LAT = DEFAULT_LAT
    LON = DEFAULT_LON

    wake_reason = machine.wake_reason()
    woke_from_joystick = (wake_reason == machine.EXT0_WAKE)

    # ============================================================
    #   INIZIALIZZAZIONE HARDWARE
    # ============================================================
    adc_bat, adc_5v, adc_3v3 = init_adc()
    ina, i2c = init_power_monitor()
    display, DISPLAY_OK = init_display(i2c)
    servo_pan, servo_tilt = init_servos()
    vrx, vry, sw, JOYSTICK_OK = init_joystick()

    mode_pin = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_UP)

    # Posizioni iniziali
    pan_angle = 90
    tilt_angle = 90
    move_pan(servo_pan, pan_angle)
    move_tilt(servo_tilt, tilt_angle)

    # ESP-NOW
    e = init_espnow()

    last_move = time.ticks_ms()


    # ============================================================
    #   MAIN — MODALITÀ AUTOMATICA (NO JOYSTICK)
    # ============================================================
    if not woke_from_joystick:

        # 1) INVIA TELEMETRIA
        try:
            send_telemetry(
                e, PEER,
                adc_bat, adc_5v, adc_3v3,
                ina,
                pan_angle, tilt_angle
            )
            print("Telemetria inviata, attendo orario...")
        except Exception as err:
            write_log({"error_send": str(err)}, "ERROR")

        # 2) ASPETTA ORARIO DALLA BASE (BLOCCANTE)
        data = wait_for_time(e)
        if data:
            try:
                machine.RTC().datetime((
                    data["year"], data["month"], data["day"],
                    0,
                    data["hour"], data["minute"], data["second"],
                    0
                ))

                LAT = data["lat"]
                LON = data["lon"]

                print("Orario ricevuto:", data)

            except Exception as err:
                write_log({"rtc_error": str(err)}, "ERROR")

        # 3) TRACKING SOLARE
        try:
            pan_angle, tilt_angle = track_sun(
                machine.RTC(),
                LAT, LON,
                lambda a: move_pan(servo_pan, a),
                lambda a: move_tilt(servo_tilt, a)
            )
            time.sleep(2)
        except Exception as err:
            write_log({"error_track": str(err)}, "ERROR")

        # 4) DEEP SLEEP
        go_sleep_timer(SLEEP_MS, DISPLAY_OK, display, servo_pan, servo_tilt)



    # ============================================================
    #   MAIN — MODALITÀ MANUALE (JOYSTICK)
    # ============================================================
    else:
        while True:
            mode = mode_pin.value()
            v_panel, i_panel, p_panel = read_power(ina)

            if mode == 0 or not JOYSTICK_OK:
                # AUTO
                pan_angle, tilt_angle = track_sun(
                    machine.RTC(),
                    LAT, LON,
                    lambda a: move_pan(servo_pan, a),
                    lambda a: move_tilt(servo_tilt, a)
                )
                time.sleep(5)

            else:
                # MANUALE
                pan_angle, tilt_angle, last_move = run_manual(
                    vrx, vry,
                    pan_angle, tilt_angle,
                    lambda a: move_pan(servo_pan, a),
                    lambda a: move_tilt(servo_tilt, a),
                    last_move
                )

                if time.ticks_diff(time.ticks_ms(), last_move) > 5000:
                    go_sleep_indef(DISPLAY_OK, display, servo_pan, servo_tilt)

            update_display(
                display, DISPLAY_OK,
                mode,
                v_panel, i_panel, p_panel,
                pan_angle, tilt_angle
            )
