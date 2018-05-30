#!/usr/bin/env python
# Author:Zhangmingda
import requests,time
from core import logger
def del_ecs(token,url_project,sub_project_id,ecs_id,ecs_name):
    '''调用v1接口批量删除云服务器'''
    url = 'https://ecs.{_project}.myhuaweicloud.com/v1/{tenant_id}/cloudservers/delete'.format(_project=url_project,tenant_id=sub_project_id)
    # print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    body ={
        "servers":[{"id": "%s"% ecs_id}],#DELETE_list,
        "delete_publicip": 'false',
        "delete_volume": 'false'
    }
    r = requests.post(url=url,json=body,headers=headers)
    if r.status_code == 200:
        logger.logger('delete_ecs','%s  ECS %s Delete result:%s return_code:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), ecs_name, r.json(),r.status_code))
    else:
        logger.logger('delete_ecs_err', '%s  ECS %s Delete Failed:%s return_code:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), ecs_name, r.json(), r.status_code))

def del_publicip(token,url_project,sub_project_id,publicip_id,ipaddress):
    '''调用V1接口删除单个IP地址'''
    url = 'https://vpc.{_project}.myhuaweicloud.com/v1/{tenant_id}/publicips/{publicip_id}'.format(_project=url_project,tenant_id=sub_project_id,publicip_id=publicip_id)
    print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.delete(url=url,headers=headers)
    if r.status_code == 204 :
        logger.logger('del_publicip','%s  publicip %s delete  return_code:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), ipaddress,r.status_code))
    else:
        logger.logger('del_publicip_err', '%s  publicip %s delete Failed_info:%s return_code:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), ipaddress,r.json(), r.status_code))
    # print('print del_publicip r.json():',r.json())
    # return r.status_code

def del_snat_rule(token,url_project,snat_rule_id,nat_ipaddress):
    url = 'https://nat.{_project}.myhuaweicloud.com/v2.0/snat_rules/{_snat_rule_id}'.format(_project=url_project,_snat_rule_id=snat_rule_id) #DELETE
    # print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.delete(url=url, headers=headers)
    if r.status_code == 204:
        logger.logger('del_snat_rule','%s  delete snat_rules_ip: %s Successful return_code:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), nat_ipaddress, r.status_code))
    else:
        logger.logger('del_snat_rule_err', '%s  delete snat_rules_ip: %s Failed info:%s return_code:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), nat_ipaddress,r.json(), r.status_code))

def del_dnat_rule(token,url_project,dnat_rule_id,nat_ipaddress):
    url = 'https://nat.{_project}.myhuaweicloud.com/v2.0/dnat_rules/{_dnat_rule_id}'.format(_project=url_project,_dnat_rule_id=dnat_rule_id) #DELETE
    # print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.delete(url=url, headers=headers)
    logger.logger('del_dnat_rule', '%s  delete dnat_rules_ip: %s info:%s return_code:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), nat_ipaddress, r.json(), r.status_code))
    # return r.status_code