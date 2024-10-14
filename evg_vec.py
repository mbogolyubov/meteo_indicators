import evg_api

def vector(sp_url, login, password, filepath, filename, tablename):
    error = 0
    api = evg_api.API(sp_url, login, password)
    if api.client.a_session is None:
        error = 1
        return error
    
    res = api.upload_file_local(filepath)
    if res is None:
        error = 1
        return error
    
    file_layer_schema = api.import_dataschema(res)
    if file_layer_schema is None:
        error = 1
        return error

    merged_schema = file_layer_schema['layers'][0]
    merged_schema.update(
        {
            'fileName': filename,
            'layerName': tablename,
            'tableName': tablename,
            'type': 'staticTaskDataStorage'
        }
    )

    try:
        copy_task_params = api.task_copy_configuration(merged_schema)
    except:
        error = 1
        print('Ошибка при создании attributeMapping')

    task = api.task_run('copy', copy_task_params)
    if task is None:
        error = 1
        return error    

    try:
        task_id = task.get('taskId', None)
        if task_id:
            api.task_get_process(task_id)
    except:
        error = 1
        print('Ошибка при загрузке слоя с метеостанциями')
        return error
        

    r = api.delete_features_by_condition(tablename, tablename, "status == 'old'")
    if r is None:
        error = 1
        return error

    task_configuration = {"attribute":"status","editExpression":"'old'","condition":"","target":{"type":"layerTaskDataStorage","serviceName": tablename}}
    id_1 = api.task_run('editAttributes', task_configuration)
    if id_1 is None:
        error = 1
        return error
    
    try:
        task_id = id_1.get('taskId', None)
        if task_id:
            api.task_get_process(task_id)
    except:
        error = 1
        print('Ошибка при преобразование атрибутов метеостанций')
    return error
        