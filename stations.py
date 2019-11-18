# -*- coding: utf-8 -*-
import requests
import pickle

response = requests.get('https://api.hh.ru/metro')
response_json = response.json()
moscow = response_json[0]['lines']

stations_coord = {}
for i in range(len(moscow)):
    for j in range(len(moscow[i]['stations'])):
        station_dict = moscow[i]['stations'][j]
        stations_coord[station_dict['name']] = {'lat': station_dict['lat'], 
                                                'lng': station_dict['lng'],
                                                'line': moscow[i]['name']
                                                }

with open('stations', 'wb') as f:
    pickle.dump(stations_coord, f)