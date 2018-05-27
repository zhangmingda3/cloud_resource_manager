#!/usr/bin/env python
# Author:Zhangmingda
import requests
def del_ecs(token,url_project,sub_project_id,DELETE_list):
    '''调用v1接口批量删除云服务器'''
    url = 'https://ecs.{_project}.myhuaweicloud.com/v1/{tenant_id}/cloudservers/delete'.format(_project=url_project,tenant_id=sub_project_id)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    body ={
        "servers":DELETE_list,#DELETE_list,
        "delete_publicip": 'false',
        "delete_volume": 'false'
    }
    r = requests.post(url=url,json=body,headers=headers)
    # print(r.json())
    return r.json()