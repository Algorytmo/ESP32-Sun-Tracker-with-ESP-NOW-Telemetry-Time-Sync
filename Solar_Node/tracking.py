# tracking.py
import math
from logging_utils import write_log

def julian_day(y, m, d, h):
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + A // 4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5 + h/24

def sun_position(lat, lon, year, month, day, hour, minute, second):
    jd = julian_day(year, month, day, hour + minute/60 + second/3600)
    n = jd - 2451545.0

    L = (280.46 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)

    lambda_sun = math.radians(L + 1.915*math.sin(g) + 0.020*math.sin(2*g))
    epsilon = math.radians(23.439 - 0.0000004 * n)

    alpha = math.atan2(math.cos(epsilon)*math.sin(lambda_sun), math.cos(lambda_sun))
    delta = math.asin(math.sin(epsilon)*math.sin(lambda_sun))

    theta = math.radians((280.46061837 + 360.98564736629*(jd-2451545) + lon) % 360)

    H = theta - alpha

    lat_r = math.radians(lat)
    elevation = math.asin(
        math.sin(lat_r)*math.sin(delta) +
        math.cos(lat_r)*math.cos(delta)*math.cos(H)
    )

    azimuth = math.atan2(
        -math.sin(H),
        math.tan(delta)*math.cos(lat_r) - math.sin(lat_r)*math.cos(H)
    )

    return math.degrees(azimuth) % 360, math.degrees(elevation)

def track_sun(rtc, lat, lon, move_pan, move_tilt):
    (year, month, day, weekday, hour, minute, second, subsecs) = rtc.datetime()
    az, el = sun_position(lat, lon, year, month, day, hour, minute, second)

    pan_angle = int(az / 2)
    tilt_angle = max(0, min(90, int(el)))

    move_pan(pan_angle)
    move_tilt(tilt_angle)

    write_log({
        "sun_track": {
            "azimuth": az,
            "elevation": el,
            "pan": pan_angle,
            "tilt": tilt_angle
        }
    }, "INFO")

    return pan_angle, tilt_angle
