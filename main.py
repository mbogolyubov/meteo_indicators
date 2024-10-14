import envs
import down_vec
import down_rast
import evg_vec
import evg_rast
import requests
import os
import time
import sys

#Функция удаления файлов из локальной директории
def delete_files(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        else:
            print(f"{item} не является файлом и не будет удалён")

try:
    #Проверка доспупности EverGIS
    response = requests.get(envs.sp_url)
    response.raise_for_status()
    evg_check = True
except requests.exceptions.RequestException as e:
    evg_check = False
    print(f"Произошла ошибка при доступе к {envs.sp_url}: {e}")
if evg_check == False:
    print("Повторите попытку позже")
    sys.exit()

retry_current = 0
status_down = 1
while retry_current < 3 and status_down != 0:
    #Скачивание растра с прогнозом температуры, скорости ветра и давления
    status_down, date = down_rast.meteo_indicators(envs.path_rast, envs.bound)
    if status_down == 1:
        time.sleep(envs.retry_wait)
    retry_current +=1

if status_down == 0:
    attributes_rast = {"Name":'1',
                       "dateofimage": date,
                       "Status":'new'}
    #Загрузка растра в EverGIS
    retry_current = 0
    status_up = 1
    while retry_current < 3 and status_up != 0:
        status_up = evg_rast.raster(envs.sp_url, envs.login, envs.password, 
                                 envs.filepath_rast, envs.filename_rast, 
                                 envs.tablename_rast, attributes_rast)
        if status_up == 1:
            time.sleep(envs.retry_wait)
        retry_current +=1
        
    delete_files(envs.path_rast)

retry_current = 0
status_down = 1
while retry_current < 3 and status_down != 0:
    #Сбор данных о метеорологических станциях
    status_down = down_vec.meteo_stations(envs.path_vec)
    if status_down == 1:
        time.sleep(envs.retry_wait)
    retry_current +=1

if status_down == 0:   
    #Загрузка метеорологических станций в EverGIS
    retry_current = 0
    status_up = 1
    while retry_current < 3 and status_up != 0:
        status_up = evg_vec.vector(envs.sp_url, envs.login, 
                                envs.password, envs.filepath_vec, 
                                envs.filename_vec, envs.tablename_vec)
        if status_up == 1:
            time.sleep(envs.retry_wait)
        retry_current +=1
        
    delete_files(envs.path_vec)
print('Загрузка данных прошла успешно')