#Параметры для получения метеорологических станций
path_vec = "D:/meteo_stations"

#Параметры для получения растра с прогнозом
path_rast = "D:/forecast/"
bound = "D:/boundary.geojson"

#Общие параметры при загрузке
sp_url = "https://map.evergis.ai/sp/"
login = 'login'
password = 'password'

#Загрузка метеостанций в эвергис
filepath_vec = "D:/meteo_station.geojson"
filename_vec = 'meteo_station.geojson'
tablename_vec = 'login.meteo_stations'

#Загрузка растра в эвергис
filepath_rast = "D:/res_PRES_TMP_GUST_surface.tiff"
filename_rast = 'res_PRES_TMP_GUST_surface.tiff'
tablename_rast = 'login.forecast'

retry_wait = 60