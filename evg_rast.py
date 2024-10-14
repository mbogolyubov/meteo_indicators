import evg_api
import time

def raster(sp_url, login, password, filepath, file_name, tablename, attributes):
    error = 0
    api = evg_api.API(sp_url, login, password)
    if api.client.a_session is None:
        error = 1
        return error
    
    res = api.delete_features_by_condition(tablename, tablename, "")
    if res is None:
        error = 1
        return error
    
    res = api.upload_file_local(filepath)
    if res is None:
        error = 1
        return error
    
    time.sleep(10)

    task = api.import_raster([file_name], tablename, attributes, bands=[1, 2, 3])
    if res is None:
        error = 1
        return error
     
    try:
        task_id = task.get('taskId', None)
        if task_id:
            api.task_get_process(task_id)
    except:
        error = 1
        print('Ошибка при загрузке растра')
    return error