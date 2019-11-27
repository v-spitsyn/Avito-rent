# -*- coding: utf-8 -*-
import requests
import pickle
import pandas as pd
import numpy as np
from geopy.distance import distance



response = requests.get('https://api.hh.ru/metro')
response_json = response.json()
moscow = response_json[0]['lines']


stations_coord = {}
for i in range(len(moscow)):
    for j in range(len(moscow[i]['stations'])):
        station_dict = moscow[i]['stations'][j]
        station_name = station_dict['name'].strip().lower()
        stations_coord[station_name] = {'lat': station_dict['lat'], 
                                        'lng': station_dict['lng'],
                                        'line': moscow[i]['name']
                                        }        

km_zero = {'lat': 55.755919, 'lng': 37.617589}
station_names = stations_coord.keys()
zero_km_dist = dict(zip(station_names,
                        [distance((stations_coord[name]['lat'], stations_coord[name]['lng']),
                                  (km_zero['lat'], km_zero['lng'])
                                 ).km
                         for name in station_names
                         ]
                        )
                    )

stations_df = pd.DataFrame.from_dict(zero_km_dist, orient='index', columns=['center_dist'])
stations_df['circle'] = [int(stations_coord[ind]['line'] == 'Кольцевая')
                                for ind in stations_df.index]
stations_df.to_csv('stations.csv')