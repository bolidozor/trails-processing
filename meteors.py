#Data procesing functions by ondra6ak ondra6ak@gmail.com
import pandas as pd
from numpy import random as rnd
from time import strftime
from datetime import datetime

def load_data(path_or_address):
    data = pd.read_csv(path_or_address, names = ["time", "beg_x", "beg_y", "beg_z", "end_x", "end_y", "end_z",
                                                 "lat","lon", "observer", "note"])
    for i in range(len(data)):
        data.time[i] = datetime.fromtimestamp(int(data.time[i]) / 1e3).strftime("%Y-%m-%d %H:%M:%S")

    return data


def fix_position(data):
    observers = {}

    class Observer:
        def __init__(self):
            self.lat = 0
            self.lon = 0

        def add_position(self, lat, lon):
            if lat != 0:
                self.lat = lat
            if lon != 0:
                self.lon = lon

    for i in range(len(data)):
        if not data["observer"][i] in observers:
            observers[data["observer"][i]] = Observer()
        observers[data["observer"][i]].add_position(data["lat"][i], data["lon"][i]);
    
    avg_lat, avg_lon = 0, 0
    for name in observers:
        avg_lat += observers[name].lat
        avg_lon += observers[name].lon
    avg_lat = avg_lat / len(observers)
    avg_lon = avg_lon / len(observers)

    for name in observers:
        if observers[name].lat == 0:
            observers[name].lat = avg_lat
        if observers[name].lon == 0:
            observers[name].lon = avg_lon
    
    for i in range(len(data)):
        if (data["lat"][i] == 0) and (data["lon"][i] == 0):
            data["lat"][i] = observers[data["observer"][i]].lat
            data["lon"][i] = observers[data["observer"][i]].lon
    
    return data

def hack():
    print("HACKNIG METEOR!")
    for i in range(100000000): pass
    print("HACKED METEOR:", rnd.normal(scale = 10000))