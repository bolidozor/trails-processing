import json
from IPython.display import HTML
from collections import defaultdict
from gzip import GzipFile
from math import copysign
import coordinates
import time
import math
import pandas as pd
import calendar as cal
import numpy as np
from astropy import coordinates as astropycoor
import meteors


def parse_hipparcos(lines, magnitude_threshold):
    """Iterate across the `lines` of ``hip_main.dat`` and yield records."""
    for line in lines:
        s = line[41:46].strip()
        if not s:
            continue
        magnitude = float(s)
        if magnitude > magnitude_threshold:
            continue
        s = line[51:63].strip()
        if not s:
            continue
        ra = float(s)
        dec = float(line[64:76])
        s = line[245:251].strip()
        if not s:
            continue
        bv = float(s)
        yield ra, dec, magnitude, bv

def group_stars_by_magnitude(records):
    magnitude_groups = defaultdict(list)
    for ra, dec, magnitude, bv in records:
        radec = [-ra, dec]
        if bv < 0.00:
            color = 'blue'
        elif bv < 0.59:
            color = 'white'
        else:
            color = 'red'
        key = (int(magnitude), color)
        magnitude_groups[key].append(radec)
    return magnitude_groups

def build_boundary_data():
    """Load constellation boundaries.

    Boundary declination is always an integer number of minutes of arc;
    right ascension, an integral number of seconds of right ascension.
    We therefore represent them using these integers, which can both be
    represented more compactly in the JavaScript we produce, and which
    also remove rounding errors as we compute.

    """
    boundaries = defaultdict(list)

    with open('data/bound_verts_18.txt') as f:
        for line in f:
            vertex_key, ra_text, dec_text, con, cons = line.split(' ', 4)
            h, m, s = [int(s) for s in ra_text.split(':')]
            ra = (60 * h + m) * 60 + s
            d, m, s = [int(s) for s in dec_text.split(':')]
            assert s == 0
            m = copysign(m, d)
            dec = 60 * d + m
            boundaries[con].append([ra, dec])

    return {con: {"type": "Polygon", "coordinates": [list(boundary)]}
            for con, boundary in sorted(boundaries.items())}

def load_decision_data():
    with open('data/data.dat') as f:
        for line in f:
            ra0, ra1, dec, con = line.split()
            yield float(ra0) * 15.0, float(ra1) * 15.0, float(dec), con.upper()

def build_star_data(magnitude_threshold):
    with GzipFile('data/hip_main.dat.gz') as f:
        records = parse_hipparcos(f, magnitude_threshold)
        magnitude_groups = group_stars_by_magnitude(records)

    return [
        {
            "type": "MultiPoint",
            "coordinates": coordinates,
            "magnitude": mag,
            "color": color,
        }
        for ((mag, color), coordinates) in sorted(magnitude_groups.items())
        ]

def build_trails_data(data):
    """Builds meteor or other trails data.

    Draws meteors trails from Meteor-observer smartphone Android application.
    """
    beg_dec, beg_ra, end_dec, end_ra = np.zeros(len(data)), np.zeros(len(data)), np.zeros(len(data)), np.zeros(len(data))
    for i in range(len(data)):
        r, ele, az = astropycoor.cartesian_to_spherical(data["beg_x"].iloc[i], data["beg_y"].iloc[i], data["beg_z"].iloc[i])
        ele, az = math.degrees(ele), math.degrees(az)
        dec, ra = coordinates.horizontal_to_equatorial2(az + 180, ele, data["lat"].iloc[i], data["lon"].iloc[i], \
                                                        cal.timegm(time.strptime(data["date"].iloc[i], "%Y-%m-%d %H:%M:%S")))
        beg_dec[i], beg_ra[i] = dec, ra * 15
        
        r, ele, az = astropycoor.cartesian_to_spherical(data["end_x"].iloc[i], data["end_y"].iloc[i], data["end_z"].iloc[i])
        ele, az = math.degrees(ele), math.degrees(az)
        dec, ra = coordinates.horizontal_to_equatorial2(az + 180, ele, data["lat"].iloc[i], data["lon"].iloc[i], \
                                                        cal.timegm(time.strptime(data["date"].iloc[i], "%Y-%m-%d %H:%M:%S")))
        end_dec[i], end_ra[i] = dec, ra * 15
    
    return [{"type": "LineString", "coordinates": [[beg_ra[i], beg_dec[i]],
             [end_ra[i], end_dec[i]]]} for i in range(len(beg_dec))]


def jsonify(data):
    """Render `data` as compact JSON."""
    return json.dumps(data, separators=(',', ':')).replace('"', "'")

def starfield(data, magnitude_threshold = 5.0):
    with open('sky.js') as f:
        js_code = f.read()

    with open('sky.html') as f:
        html_template = f.read()

    html = html_template % {
        'boundary_data': jsonify(build_boundary_data()),
        'decision_data': jsonify(list(load_decision_data())),
        'star_data': jsonify(build_star_data(magnitude_threshold)),
        'trails_data':build_trails_data(data),
        'js_code': js_code,
        }
    html = html.replace('UNIQUE_ID', 'abcd')
    return HTML(html)

if __name__ == '__main__':
    print (build_boundary_data()['CEP']['coordinates'][0])
