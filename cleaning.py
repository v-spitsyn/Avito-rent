# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:14:09 2019

@author: spitc
"""
import pickle
import pandas as pd
import numpy as np



scrap_date = '26-11-19'
with open('1room_flats_{}.pickle'.format(scrap_date), 'rb') as f:
    flats = pickle.load(f)   
flats_dict = {}
for inner_key in flats[list(flats.keys())[0]].keys():
    flats_dict[inner_key] = [flats[out_key][inner_key] for out_key in flats.keys()]
 
df = pd.DataFrame(data=flats_dict, index=flats.keys())
df.index = 'avito.ru' + df.index

df.dropna(inplace=True)
df.drop(df[df['currency'] != 'RUB'].index, axis=1, inplace=True)
df.drop(df[df.index.str.contains('zelenograd')].index, 
        inplace=True)
df.drop(df[df['address'].str.contains('Зеленоград').fillna(False)].index, 
        inplace=True)
df.drop(df[df['distances'].apply(lambda l: len(l) == 0)].index, 
        inplace=True)
df.drop(df[df['stations'].apply(lambda l: len(l) == 0)].index, 
        inplace=True)
df.drop(columns=['currency', 'address'], inplace=True)



def to_kilometers(l):
    dist_split = [it.split() for it in l]
    for it in dist_split:
        it[0] = it[0].replace(',', '.')
    return [float(it[0])/1000 if it[-1]=='м' else float(it[0]) for it in dist_split]

df['distances_km'] = df['distances'].apply(to_kilometers)
df['station'] = df.apply(lambda x: x['stations'][np.argmin(x['distances_km'])], 
                         axis=1)
df['station_dist'] = 10 * df['distances_km'].apply(lambda l: min(l))


main_params_map = {                            
                    'Этаж': 'floor',
                    'Этажей в доме': 'n_floors',
                    'Тип дома': 'house_type',
                    'Количество комнат': 'n_rooms',
                    'Общая площадь': 'area'
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

def to_dict(params_list):
    ru_keys = [key[0].strip() for key in [it.split(':') for it in params_list]]
#    en_keys = [main_params_map[key] for key in ru_keys]
    vals = [val[1].strip() for val in [it.split(':') for it in params_list]]
    params_dict = {}
    for key in main_params_map:
        if key in ru_keys:
            params_dict[main_params_map[key]] = vals[ru_keys.index(key)]
        else:
            params_dict[main_params_map[key]] = None
    return params_dict
            

df['main_params_dict'] = df['main_params'].apply(to_dict)

for param in main_params_map.values():
    df[param] = df['main_params_dict'].apply(lambda d: d[param])
df.dropna(inplace=True)    
    
for param in extra_params_map:
    df[param] = df['extra_params'].apply(lambda l: int(extra_params_map[param] in l))


df['studio'] = (df['n_rooms'] == 'студии').astype(int)
df.drop('n_rooms', axis=1, inplace=True)
df['landlord'] = df['landlord'].str.replace('\n|<<|>>|"', '').apply(lambda s: s.strip())

df['area'] = df['area'].apply(lambda s: s.split()[0])

for col in ('floor', 'n_floors', 'area'):
    df[col] = df[col].astype(float)
df['1st_floor'] = (df['floor'] == 1).astype(int)
df['last_floor'] = (df['floor'] == df['n_floors']).astype(int)


df['rent'] = df['rent'].astype(float)

def to_percent(row):
    deal = row['deal']
    if 'без залога' in deal:
        deposit = 0
    else:
        deposit_str = deal.split(',')[0]
        deposit = int(deposit_str.split()[1] + deposit_str.split()[2])
    deposit_percent = 100 * deposit/row['rent']
    if ('без комиссии' in deal) or (len(deal.split(',')) < 2):
        commission = 0
    else:
        commission_str = deal.split(',')[1]
        commission = int(commission_str.split()[1] + commission_str.split()[2])
    commission_percent = 100 * commission/row['rent']
    return (deposit_percent, commission_percent)
        
df[['deposit', 'commission']] = df.apply(to_percent, axis=1, result_type='expand')

df['rent'] = df['rent']/1000

df['house_type'] = df['house_type'].map({'кирпичный': 'brick', 'монолитный': 'monolithic', 
                                         'панельный': 'panel', 'блочный': 'block', 
                                         'деревянный': 'wood'})
df.drop(df[df['house_type'] == 'wood'].index, inplace=True)

df['landlord_type'] = df['landlord_type'].map({'Арендодатель': 'owner', 
                                               'Агентство': 'agency', 
                                               'Застройщик': 'developer'})


stations_df = pd.read_csv('stations.csv', index_col=0)
df['station'] = df['station'].apply(lambda s: s.lower())
df = df.join(stations_df, on='station', how='left')
clean_df = df[['area', '1st_floor', 'last_floor', 'studio', 'station_dist',
               'center_dist', 'circle', 'house_type', 'landlord_type', 'landlord',
               'commission', 'deposit', 'fridge', 'ac', 'balcony', 'microwave',
               'parking', 'stove', 'tv', 'wash_machine', 'wifi', 'rent']
             ]
clean_df.to_csv('clean_df.csv')