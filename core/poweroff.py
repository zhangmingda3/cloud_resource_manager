#!/usr/bin/env python
# Author:Zhangmingda
import requests,json
def poweoff_ecs(token,url_project,sub_project_id,SHUT_list):
    '''调用V1接口批量关机云服务器'''
    url = 'https://ecs.{_project}.myhuaweicloud.com/v1/{tenant_id}/cloudservers/action'.format(_project=url_project,tenant_id=sub_project_id)
    body = {
        "os-stop": {
            "type": "HARD",
            "servers": SHUT_list
        }
    }
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.post(url,json=body,headers=headers)
    # print(r.json())
    return r.json()