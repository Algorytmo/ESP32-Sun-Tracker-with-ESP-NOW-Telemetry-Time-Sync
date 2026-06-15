# hardware.py
from machine import ADC, Pin, I2C, PWM
from ina219 import INA219
import ssd1306
from config import VREF, MAX_ADC, FREQ
from logging_utils import write_log

def init_adc():
    adc_bat = ADC(Pin(34))
    adc_5v  = ADC(Pin(35))
    adc_3v3 = ADC(Pin(33))

    for a in (adc_bat, adc_5v, adc_3v3):
        a.atten(ADC.ATTN_11DB)
        a.width(ADC.WIDTH_12BIT)

    return adc_bat, adc_5v, adc_3v3

def read_voltage(adc):
    raw = adc.read()
    v_adc = raw * VREF / MAX_ADC
    v_real = v_adc * 2
    return v_real, raw

def init_power_monitor():
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    ina = INA219(0.1, i2c)
    ina.configure()
    return ina, i2c

def init_display(i2c):
    try:
        display = ssd1306.SSD1306_I2C(128, 64, i2c)
        return display, True
    except:
        print("Display non trovato")
        return None, False

def update_display(display, display_ok, mode, v, i, p, pan, tilt):
    if not display_ok:
        return
    display.fill(0)
    display.text("Mode: {}".format("MAN" if mode else "AUTO"), 0, 0)
    display.text("V: {:.2f}V".format(v), 0, 12)
    display.text("I: {:.1f}mA".format(i*1000), 0, 22)
    display.text("P: {:.3f}W".format(p), 0, 32)
    display.text("PAN: {}".format(pan), 0, 44)
    display.text("TILT: {}".format(tilt), 0, 54)
    display.show()

def angle_to_duty(angle):
    angle = max(0, min(180, angle))
    min_us = 500
    max_us = 2500
    us = min_us + (angle / 180) * (max_us - min_us)
    duty = int((us / 20000) * 1023)
    return duty

def init_servos():
    servo_pan = PWM(Pin(17), freq=FREQ)
    servo_tilt = PWM(Pin(16), freq=FREQ)
    return servo_pan, servo_tilt

def move_pan(servo, angle):
    servo.duty(angle_to_duty(angle))
    write_log({"servo_pan": angle}, "DEBUG")

def move_tilt(servo, logical_angle):
    servo_angle = 180 - logical_angle
    servo.duty(angle_to_duty(servo_angle))
    write_log({"servo_tilt": logical_angle}, "DEBUG")

def read_power(ina):
    try:
        voltage = ina.voltage()
        current = ina.current() / 1000
        power = voltage * current
        return voltage, current, power
    except:
        return 0, 0, 0
