#!/usr/bin/env python
# Author:Zhangmingda
import os,sys,time
BASE_NAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_NAME)
from core import get_token,search_list,poweroff,delete,logger
from conf import settings,protected

def manager_ecs(token,url_project,sub_project_id):
    '''清理一个sub_project_id下的ECS资源'''
    ecs_list = search_list.search_ecs(token, url_project, sub_project_id)
    SHUTOFF_list = {'id':[],'username':[]}
    DELETE_list = {'id':[],'username':[]}
    for ecs in ecs_list:
        ecs_id = ecs["id"]
        create_stamp = time.mktime(time.strptime(ecs['created'], format("%Y-%m-%dT%H:%M:%SZ"))) + 28800  # 将时间字符串转按指定格式换为元组<class 'time.struct_time'>
        SHUTOFF_time = create_stamp + settings.off_time['ecs'] * 3600
        DELETE_time = create_stamp + settings.del_time['ecs'] * 3600
        ecs_status = ecs['status']
        user_id = ecs['user_id']
        ecs_name = ecs['name']
        if ecs_id not in protected.ECS and time.time() > SHUTOFF_time and ecs_status != "SHUTOFF":
            SHUTOFF_list['id'].append({"id":ecs_id});SHUTOFF_list['username'].append(ecs_name)
            logger.logger('%s  ECS_name:%s  id:%s Will be Shut Off.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"),ecs_name,ecs_id))
        if ecs_id not in protected.ECS and time.time() > DELETE_time:
            DELETE_list['id'].append({'id':ecs_id});DELETE_list['username'].append(ecs_name)
            logger.logger('%s  ECS_name:%s  id:%s Will be DELETE!.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), ecs_name, ecs_id))
    if len(SHUTOFF_list['id']) >0:
        poweroff_results = poweroff.poweoff_ecs(token, url_project, sub_project_id, SHUTOFF_list['id'])
        logger.logger('%s   ECS %s Shut Off result:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), SHUTOFF_list['username'],poweroff_results))
    if len(DELETE_list['id']) >0:
        delete_results = delete.del_ecs(token,url_project,sub_project_id,DELETE_list['id'])
        logger.logger('%s  ECS %s Delete result:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"),DELETE_list['username'],delete_results))

def  manager_publicips(token, url_project, sub_project_id):
    publicips = search_list.search_publicips(token, url_project, sub_project_id)
    for publicip in publicips:
        # print(publicip)
        if  not publicip['profile']['user_id'] and publicip['bandwidth_share_type'] == 'PER':
            '''not publicip['profile']['user_id']判断按需计费 PER为独享带宽'''
            create_stamp = time.mktime(time.strptime(publicip['create_time'], format("%Y-%m-%d %H:%M:%S"))) + 28800  # 将时间字符串转按指定格式换为元组<class 'time.struct_time'>
            DEL_time_stamp = create_stamp + settings.del_time['publicip'] * 3600
            if DEL_time_stamp > create_stamp:
                publicip_id = publicip['id']
                ipaddress = publicip['public_ip_address']
                if publicip['status'] == 'DOWN':
                    bandwidth_charge_mode = search_list.search_bandwidth_charge_mode(token,url_project,sub_project_id,publicip['bandwidth_id'])
                    # print(ipaddress,publicip['status'],bandwidth_charge_mode)
                    del_down_results = delete.del_publicip(token,url_project,sub_project_id,publicip_id)
                    logger.logger('%s  publicip %s delete result:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"),ipaddress,del_down_results))
                    print(del_down_results)
                elif publicip['status'] == 'ACTIVE':
                    port_type = search_list.search_port_owner(token,url_project,publicip['port_id'])
                    if port_type != 'network:nat_gateway':
                        print(ipaddress, publicip['status'], publicip['port_id'], port_type)
                        del_active_notnat_results = delete.del_publicip(token, url_project, sub_project_id, publicip_id)
                        logger.logger('%s  publicip %s delete result:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), ipaddress, del_down_results))
                        print(del_active_notnat_results)

                    else:
                        print(ipaddress, publicip['status'], publicip['port_id'], port_type)
                        del_active_NAT_results = delete.del_publicip(token, url_project, sub_project_id, publicip_id)
                        logger.logger('%s  publicip %s delete result:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), ipaddress, del_active_NAT_results))
                        print(del_active_NAT_results)
                elif publicip['status'] == 'ELB':
                    pass

                    # print(del_down_results)


                    # publicip_address = publicip['public_ip_address']
                    # create_time = publicip['create_time']
                    # print(ipaddress,id,create_time,bandwidth_charge_mode,publicip['status'])#bandwidth_charge_mode

def run():
    for url_project in settings.Endpoint_project_id:
        # print(url_project)
        for sub_project in settings.Endpoint_project_id[url_project]:
            sub_project_id = settings.Endpoint_project_id[url_project][sub_project]
            # print(sub_project, sub_project_id,)
            token = get_token.get_token(settings.iam['domainname'], settings.iam['username'], settings.iam['password'],url_project,sub_project)
            if token:
                manager_ecs(token,url_project,sub_project_id)
                manager_publicips(token, url_project, sub_project_id)
                # publicips = search_list.search_publicips(token, url_project, sub_project_id)

run()