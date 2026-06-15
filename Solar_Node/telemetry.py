# telemetry.py
import time, json
from logging_utils import write_log
from hardware import read_voltage

def send_telemetry(e, peer, adc_bat, adc_5v, adc_3v3, ina, pan_angle, tilt_angle):
    ts = time.time()

    v_bat, r_bat = read_voltage(adc_bat)
    v_5v,  r_5v  = read_voltage(adc_5v)
    v_3v3, r_3v3 = read_voltage(adc_3v3)

    v_panel = ina.voltage()
    i_panel = ina.current()
    p_panel = ina.power()

    data = {
        "ts": ts,
        "bat_v": v_bat,
        "bat_raw": r_bat,
        "v5": v_5v,
        "v5_raw": r_5v,
        "v33": v_3v3,
        "v33_raw": r_3v3,
        "panel_v": v_panel,
        "panel_i": i_panel,
        "panel_p": p_panel,
        "pan": pan_angle,
        "tilt": tilt_angle
    }

    msg = json.dumps(data)
    write_log(data, "INFO")
    e.send(peer, msg)
