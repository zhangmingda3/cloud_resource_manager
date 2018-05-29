#!/usr/bin/env python
# Author:Zhangmingda
import  requests

def search_ecs(token,url_project,sub_project_id):
    url = 'https://ecs.{_project}.myhuaweicloud.com/v2/{tenant_id}/servers/detail'.format(_project=url_project,tenant_id=sub_project_id)
    print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.get(url=url,headers=headers)
    # print(r.json())
    return r.json()['servers']

def search_publicips(token,url_project,sub_project_id):
    url = 'https://vpc.{_project}.myhuaweicloud.com/v1/{tenant_id}/publicips'.format(_project=url_project,tenant_id=sub_project_id)
    print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.get(url=url,headers=headers)
    # print(r.json())
    return r.json()['publicips']

def search_bandwidth_charge_mode(token,url_project,sub_project_id,bandwidth_id):
    # if url_project != ''
    url = 'https://vpc.{_project}.myhuaweicloud.com/v1/{tenant_id}/bandwidths/{bandwidth_id}'.format(_project=url_project,tenant_id=sub_project_id,bandwidth_id=bandwidth_id)
    # print(url)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.get(url=url, headers=headers)
    # return r.json()
    try:
        r.json()['bandwidth']['charge_mode']
    except KeyError :
        return r.json()
    else:
        return r.json()['bandwidth']['charge_mode']
def search_port_owner(token,url_project,port_id):
    url = 'https://vpc.{_project}.myhuaweicloud.com/v1/ports/{_port_id}'.format(_project=url_project,_port_id=port_id)
    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    r = requests.get(url=url, headers=headers)
    try:
        device_owner= r.json()['port']['device_owner']
    except KeyError :
        return r.json()
    else:
        return device_owner
    # return r.json()['bandwidth']['charge_mode']
# https://vpc.ap-southeast-1.myhuaweicloud.com/v1/ccce0d1ed57e4621bce16ed18d8e8f71/publicips
# import os,sys,time
# BASE_NAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_NAME)
# from core import get_token
# from conf import settings
# token = get_token.get_token('hwcloudsom1', 'zhangmingda', '237828Zhang?','cn-north-1','cn-north-1')
# print(token)
# def search_user_id(token):
#     url = 'https://iam.myhuaweicloud.com/v3/users'
#     headers = {"Content-type": "application/json", "X-Auth-Token": token}
#     r = requests.get(url=url, headers=headers)
#     print(r.json())
# search_user_id(token)