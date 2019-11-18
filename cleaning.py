# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:14:09 2019

@author: spitc
"""
import pickle
import pandas as pd
import numpy as np
from geopy.distance import distance as coord_distance


with open('1room_flats_02.11.19', 'rb') as f:
    flats = pickle.load(f)   
flats_dict = {}
for inner_key in flats[list(flats.keys())[0]].keys():
    flats_dict[inner_key] = [flats[out_key][inner_key] for out_key in flats.keys()]
 
df = pd.DataFrame(data=flats_dict, index=flats.keys())
df.index = 'avito.ru' + df.index
df.dropna(subset=['header'], inplace=True)
df[df['landlord'].isna()]
df.loc[df['landlord'].isna(), ['landlord', 'landlord_type']] = ('ПИК-Аренда', 'Застройщик')
df.drop(df[df.index.str.contains('zelenograd')].index, inplace=True)
df.drop(df[df['address'].str.contains('Зеленоград').fillna(False)].index, inplace=True)
df.drop(df[df['distances'].apply(lambda l: len(l) == 0)].index, inplace=True)
df.drop(df[df['stations'].apply(lambda l: len(l) == 0)].index, inplace=True)

def to_kilometers(l):
    dist_split = [it.split() for it in l]
    for it in dist_split:
        it[0] = it[0].replace(',', '.')
    return [float(it[0])/1000 if it[-1]=='м' else float(it[0]) for it in dist_split]

df['distances_km'] = df['distances'].apply(to_kilometers)
df['station'] = df.apply(lambda x: x['stations'][np.argmin(x['distances_km'])], 
                         axis=1)
df['dist'] = df['distances_km'].apply(lambda l: min(l))
df['station_dist'] = df['dist']*10

main_params_map = {                            
                    'floor': 'Этаж',
                    'n_floors': 'Этажей в доме',
                    'house': 'Тип дома',
                    'n_rooms': 'Количество комнат',
                    'area': 'Общая площадь',
                    'liv_area': 'Жилая площадь',
                    'kitchen_area': 'Площадь кухни'
}
extra_params_map = {      
                    'wifi': 'Wi-Fi',
                    'tv': 'Кабельное / цифровое ТВ',
                    'fridge': 'Холодильник',
                    'stove': 'Плита', 
                    'microwave': 'Микроволновка', 
                    'ac': 'Кондиционер',
                    'wash_machine': 'Стиральная машина',
                    'balcony': 'Балкон / лоджия',
                    'parking': 'Парковочное место',
}
df['main_params_dict'] = df['main_params'].apply(lambda l: dict(zip([q[0].strip() for q in [it.split(':') for it in l]], 
                                                                    [q[1].strip() for q in [it.split(':') for it in l]])
                                                                )
                                                )
def complete_params(d):
    for param in main_params_map.values():
        if param not in d.keys():
            d[param] = None

df['main_params_dict'].apply(complete_params)
for param in main_params_map.keys():
    df[param] = df['main_params_dict'].apply(lambda d: d[main_params_map[param]])
for param in extra_params_map:
    df[param] = df['extra_params'].apply(lambda l: int(extra_params_map[param] in l))
df['studio'] = (df['n_rooms'] == 'студии').astype(int)
df.drop('n_rooms', axis=1, inplace=True)
df['landlord'] = df['landlord'].str.replace('\n|<<|>>|"', '').apply(lambda s: s.strip())
df['deposit'] = df['deal'].apply(lambda s: 
                                        s.split(',')[0].split()[1]+s.split(',')[0].split()[2] 
                                        if 'без залога' not in s else 0) 
df['comission'] = df['deal'].apply(lambda s: 
                                          s.split(',')[1].split()[1]+s.split(',')[1].split()[2] 
                                          if (('без комиссии' not in s) and (len(s.split(',')) > 1)) 
                                          else 0)
df['price'] = df['price'].astype(float)
df['deposit'] = (df['deposit'].astype(float)/df['price']) * 100
df['comission'] = (df['comission'].astype(float)/df['price']) * 100

df['house_type'] = df['house'].map({'кирпичный': 'brick', 'монолитный': 'monolithic', 
                                    'панельный': 'panel', 'блочный': 'block', 
                                    'деревянный': 'wood'})
df.drop(df[df['house_type'] == 'wood'].index, inplace=True)

df['landlord_type'] = df['landlord_type'].map({'Арендодатель': 'landrord', 
                                               'Агентство': 'agency', 
                                               'Застройщик': 'developer'})

for col in ('floor', 'n_floors'):
    df[col] = df[col].astype(int)
for col in ('area', 'liv_area', 'kitchen_area'):
    df[col] = df[col].apply(lambda s: float(s.split()[0]) if s is not None else None)

df.drop(['header', 'currency', 'stations', 'distances', 'main_params', 'address', 
         'deal', 'deal', 'dist', 'distances_km', 'main_params_dict', 'house'], 
        axis=1, inplace=True)
df['price'] = df['price']/1000

with open('/content/gdrive/My Drive/stations', 'rb') as f:
    stations_coord = pickle.load(f)   
km_zero = {'lat': 55.755919, 'lng': 37.617589}
distances_to_zero_km = [coord_distance((stations_coord[key]['lat'], stations_coord[key]['lng']),
                                        (km_zero['lat'], km_zero['lng'])
                                        ).km 
                        for key in stations_coord.keys()
                        ]
distances_to_zero_km_dict = dict(zip(stations_coord.keys(), distances_to_zero_km))
is_circle = dict(zip(stations_coord,
                     [stations_coord[key]['line'] == 'Кольцевая' for key in stations_coord]
                    )
                )
df['center_dist'] = df['station'].map(distances_to_zero_km_dict).round(3)
df['circle'] = df['station'].map(is_circle).astype(int)
df.drop(['liv_area', 'kitchen_area', 'floor', 'n_floors'], axis=1, inplace=True)
with open('clean_df', 'wb') as f:
    pickle.dump(df, f)