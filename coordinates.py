#Transforming coordinates functions by Povik martin.povik@gmail.com
import math
import datetime

def cartesian_to_horizontal(x, y, z):
    ele = math.degrees(math.atan2(z, math.sqrt(x * x + y * y)))
    az = math.degrees(math.atan2(y, x))
    return math.sqrt(x * x + y * y + z * z), ele, az

def horizontal_to_equatorial(az, ele, lat):
    az, ele = math.radians(az), math.radians(ele)
    at = math.radians(lat)
    cd_ct = math.cos(ele) * math.cos(az) * math.sin(lat) \
            + math.sin(ele) * math.cos(lat)
    cd_st = math.cos(ele) * math.sin(az)
    sd = -math.cos(ele) * math.cos(az) * math.cos(lat) + math.sin(ele) * math.sin(lat)
    cd = math.sqrt(cd_ct * cd_ct + cd_st * cd_st)
    return math.atan2(cd_st / cd, cd_ct / cd) * 12 / math.pi, \
           math.degrees(math.atan2(sd, cd))
     
def timestamp_to_jd(timestamp):
    return float(timestamp) / 86400 + 2440587.5

def timestamp_to_lst(timestamp, lon):
    timestamp = float(timestamp)
    timeofday = timestamp % 86400
    jd0 = timestamp_to_jd(timestamp - timeofday)
    T = (jd0 - 2451545) / 36525
    s0 = 6.697374558 + 2400.05133691 * T + 0.000025862 * T**2 \
         - 0.0000000017 * T**3
    return (s0 + 1.0027379093 * (timeofday / 86400) * 24.0 + float(lon) / 15) % 24

def horizontal_to_equatorial2(az, ele, lat, lon, timestamp):
    t, d = horizontal_to_equatorial(az, ele, lat)
    return d, (timestamp_to_lst(timestamp, lon) - t) % 24