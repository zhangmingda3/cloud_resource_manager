#!/usr/bin/env python
# Author:Zhangmingda
import requests,time
from core import logger
def del_ecs(token,url_project,sub_project_id,DELETE_list):
    # print(DELETE_list['id'])
    '''调用v1接口批量删除云服务器'''
    url = 'https://ecs.{_project}.myhuaweicloud.com/v1/{tenant_id}/cloudservers/delete'.format(_project=url_project,tenant_id=sub_project_id)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    body ={
        "servers":DELETE_list['id'],#DELETE_list,
        "delete_publicip": 'false',
        "delete_volume": 'false'
    }
    r = requests.post(url=url,json=body,headers=headers)
    logger.logger('delete_ecs','%s  ECS %s Delete result:%s return_code:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), DELETE_list['username'], r.json(),r.status_code))

def del_publicip(token,url_project,sub_project_id,publicip_id):
    '''调用V1接口删除单个IP地址'''
    url = 'https://vpc.{_project}.myhuaweicloud.com/v1/{tenant_id}/publicips/{publicip_id}'.format(_project=url_project,tenant_id=sub_project_id,publicip_id=publicip_id)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.delete(url=url,headers=headers)
    return r.status_code

def del_snat_rule(token,url_project,snat_rule_id):
    url = 'https://nat.{_project}.myhuaweicloud.com/v2.0/snat_rules/{_snat_rule_id}'.format(_project=url_project,_snat_rule_id=snat_rule_id) #DELETE
    # print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.delete(url=url, headers=headers)
    return r.status_code
def del_dnat_rule(token,url_project,dnat_rule_id):
    url = 'https://nat.{_project}.myhuaweicloud.com/v2.0/dnat_rules/{_dnat_rule_id}'.format(_project=url_project,_dnat_rule_id=dnat_rule_id) #DELETE
    # print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.delete(url=url, headers=headers)
    return r.status_code