import geopandas as gpd
import pandas as pd
import os
import requests
import re
from shapely.geometry import Point
from datetime import datetime

#Функция выполняющая сбор данных по метеостанциям России за последний срок
def meteo_stations(path_vec):
    #Поиск всех регионов России и составление таблицы с названиями и идентификаторыми
    os.environ['SHAPE_ENCODING']='utf-8'
    error = 0
    try:
        resp = requests.get(f'http://www.pogodaiklimat.ru/archive.php?id=ru')
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        error = 1
        print(f"Произошла ошибка при доступе к http://www.pogodaiklimat.ru/archive.php?id=ru: {e}")
        return error
    
    resp.encoding = 'utf-8'
    data = resp.text
    d=re.findall('region=\d*">\w.+</a>', data)
    s=[{'region': string.split('"')[0][7:], 'name': string.split('"')[1][1:-4]} for string in d]
    name_reg = []
    id_reg = []
    for i in s:
        name_reg.append(i['name'])
        id_reg.append(i['region'])
    data1 = {'region': id_reg, 'name': name_reg}
    regions = gpd.GeoDataFrame(data1)

    #Поиск всех метеостанций
    name_st = []
    id_st = []
    geom_st = []
    for reg in regions['region']:
        try:
            resp2 = requests.get(f'http://www.pogodaiklimat.ru/archive.php?id=ru&region={reg}')
            resp2.raise_for_status()
        except requests.exceptions.RequestException as e:
            error = 1
            print(f"Произошла ошибка при доступе к http://www.pogodaiklimat.ru/archive.php?id=ru&region={reg}: {e}")
            return error
            
        resp2.encoding = 'utf-8'
        data2 = resp2.text
        d2=re.findall('id=\d*">\w.+</a>', data2)
        s2=[{'id': string.split('"')[0][3:], 'name': string.split('"')[1][1:-4]} for string in d2]

        for i in s2:
            name_st.append(i['name'])
            id_st.append(i['id'])
            try:
                resp3=requests.get(f"http://www.pogodaiklimat.ru/weather.php?id={i['id']}")
                resp3.raise_for_status()
            except requests.exceptions.RequestException as e:
                error = 1
                print(f"Произошла ошибка при доступе к http://www.pogodaiklimat.ru/weather.php?id={i['id']}: {e}")
                return error
   
            resp3.encoding='utf-8'
            coordinates=re.findall('</span>: широта <span>.*</span> долгота  <span>.*</span>', resp3.text)[0]
            latitude = coordinates[22:27]
            longitude = coordinates[50:55]
            if (latitude == '</spa'):
                geom_st.append(None)
            else:
                geom_st.append(Point(float(longitude), float(latitude)))
                        
    #Составление геодатафрейма с идентификатором станции, названием и координатами, фильтрация NA значений, задание геометрии столбцу
    data2 = {'id': id_st, 'name': name_st, 'geom': geom_st}
    stations = gpd.GeoDataFrame(data2)
    stations.set_geometry('geom', inplace=True)
    gdf_clean = stations.dropna(subset=['geom'])

    #Составление списков по составленному геодатафрейму
    idp_st_new = list(gdf_clean['id'])
    name_st_new = list(gdf_clean['name'])
    geom_st_new = list(gdf_clean['geom'])

    current_datetime = datetime.now()
    year = current_datetime.year
    direction, velocity, visibility, phenomenon, cloud, T_C, Td_C, f, Te_C, Tes_C, Comfort, P_hPa, Po_hPa, Tmin_C, Tmax_C, R_mm, R24_mm, S_sm, Datetime = ([] for _ in range(19))
    lists = [direction, velocity, visibility, phenomenon, cloud, T_C, Td_C, f, Te_C, Tes_C, Comfort, P_hPa, Po_hPa, Tmin_C, Tmax_C, R_mm, R24_mm, S_sm, Datetime]

    #Поиск меторологических показателей по каждому пункту
    for d in idp_st_new:
        data_w = pd.read_html(f'http://www.pogodaiklimat.ru/weather.php?id={d}')
        df1=data_w[0]
        df2=data_w[1]
        df1.columns=['Time', 'Date']
        df2.columns=['Direction', 'Velocity_m', 'Visibility', 'Phenomenon', 'Cloud', 'T_C', 'Td_C', 'f', 'Te_C', 'Tes_C', 'Comfort', 'P_hPa', 'Po_hPa', 'Tmin_C', 'Tmax_C', 'R_mm', 'R24_mm', 'S_sm']
        df1=df1.drop(index=0)
        df2=df2.drop(index=0)
        df3=pd.concat(axis=1, objs=[df1, df2])
        df3['Datetime'] = pd.to_datetime(str(year)+'.'+df3['Date']+'.'+df3['Time'], format='%Y.%d.%m.%H', errors='coerce')
        df3.drop(columns=['Time', 'Date'], inplace=True)
        if len(df3) > 0:
            last_row = df3.iloc[-1]
            for i in range(len(lists)):
                lists[i].append(last_row.iloc[i])
        else:
            for i in range(len(lists)):
                lists[i].append(None)

    data1 = {'id': idp_st_new, 'name': name_st_new, 'geometry': geom_st_new, 'Datetime': Datetime,
            'Direction': direction, 'Velocity_m': velocity, 'Visibility': visibility, 
            'Phenomenon': phenomenon,'Cloud': cloud, 'T_C': T_C, 'Td_C': Td_C, 'f': f,
            'Te_C': Te_C, 'Tes_C': Tes_C, 'Comfort': Comfort, 'P_hPa': Po_hPa, 'Po_hPa': Po_hPa, 
            'Tmin_C': Tmin_C, 'Tmax_C': Tmax_C, 'R_mm': R_mm, 'R24_mm': R24_mm, 'S_sm': S_sm}
    data1['status'] = 'new'
    stations2 = gpd.GeoDataFrame(data1)

    stations2.to_file(f'{path_vec}/meteo_station.geojson', driver='GeoJSON')   

    return error