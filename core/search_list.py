#!/usr/bin/env python
# Author:Zhangmingda
import  requests

def search_ecs(token,url_project,sub_project_id):
    url = 'https://ecs.{_project}.myhuaweicloud.com/v2/{tenant_id}/servers/detail'.format(_project=url_project,tenant_id=sub_project_id)
    # print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.get(url=url,headers=headers)
    # print(r.json())
    return r.json()['servers']
