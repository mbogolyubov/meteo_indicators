import requests
from datetime import datetime, timezone, timedelta
import subprocess

#Общая функция, выполняющая поиск и скачивание данных с сайта NOAA и преобразование растра
def meteo_indicators(path_ras, bound):
    #Функция для создания формата, например, из '6' в '06' 
    def okey(value):
        if (value<10):
            value_end = str(f'0{value}')
        else:
            value_end = value
        return value_end
    
    #Функция определения цикла
    def cycling(time):
        if (time >= 0 and time <=6):
            cycle = 0
        if (time > 6 and time <=12):
            cycle = 6
        if (time > 12 and time <=18):
            cycle = 12
        if (time > 18 and time <=23):
            cycle = 18
        return cycle
    
    #Функция чтения ссылки с помощью requests и получение ответа
    def link(year, month_end, day_end, cycle_end, hour_end, path_ras):
        url = f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25_1hr.pl?dir=%2Fgfs.{year}{month_end}{day_end}%2F{cycle_end}%2Fatmos&file=gfs.t{cycle_end}z.pgrb2.0p25.f0{hour_end}&var_GUST=on&var_PRES=on&var_TMP=on&lev_surface=on"
        error = 0
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error = 1
            print(f'Ошибка при запросе на сайт {url}: {e}')
            return error

        try:
            with open(f'{path_ras}gfs_PRES_TMP_GUST_surface.grb2', 'wb') as file:
                file.write(response.content)
        except:
            print('Не удалось сохранить данные в файл gfs_PRES_TMP_GUST_surface')
            error = 1
        return error

    current_datetime = datetime.now(timezone.utc)
    day = current_datetime.day
    month = current_datetime.month
    year = current_datetime.year
    time = current_datetime.hour
    print(f'Настоящее время по UTC: {current_datetime}')

    cycle = cycling(time)
    hour = time - cycle

    var = [cycle, hour, month, day]
    var_end = [okey(value) for value in var]
    cycle_end, hour_end, month_end, day_end = var_end

    error = link(year, month_end, day_end, cycle_end, hour_end, path_ras)

    #Изменение даты, если в первой итерации была ошибка
    interval = 1
    while error == 1 and interval < 12:
        current_datetime = current_datetime - timedelta(hours=6*interval)
        day = current_datetime.day
        month = current_datetime.month
        year = current_datetime.year
        time = current_datetime.hour
        print(f'Измененное время по UTC: {current_datetime}')

        cycle = cycling(time)
        hour = hour+6*interval

        var = [cycle, hour, month, day]
        var_end = [okey(value) for value in var]
        cycle_end, hour_end, month_end, day_end = var_end

        error = link(year, month_end, day_end, cycle_end, hour_end, path_ras)
        interval+=1

    date = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    #Преобразование растра, изменение формата, системы координат
    if error == 0:
        try:
            subprocess.run(['C:/Program Files/QGIS 3.30.0/bin/gdalwarp.exe',
                            '-of', 'GTiff', 
                            '-t_srs', 'EPSG:4326',
                            '-dstnodata', '99999999.0',
                            '-cutline', bound,
                            '-crop_to_cutline', 
                            f'{path_ras}'+'gfs_PRES_TMP_GUST_surface.grb2',
                            f'{path_ras}'+'res_PRES_TMP_GUST_surface.tiff'])
        except:
            error = 1
            print('Не получилось преобразовать формат растра в tiff')
    return error, date