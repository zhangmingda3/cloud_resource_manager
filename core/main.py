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
    del_nat_rules_iplist = []
    del_elb_iplist = []
    for publicip in publicips:
        # print(publicip)
        if  not publicip['profile']['user_id']: # and publicip['bandwidth_share_type'] == 'PER'
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
                    if port_type != 'network:nat_gateway':#不是NAT网关的IP就删除
                        print(ipaddress, publicip['status'], publicip['port_id'], port_type)
                        del_active_notnat_results = delete.del_publicip(token, url_project, sub_project_id, publicip_id)
                        logger.logger('%s  publicip %s  not ant delete  result:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), ipaddress, del_active_notnat_results))
                        print(del_active_notnat_results)
                    else:
                        del_nat_rules_iplist.append(ipaddress)

                    # else:
                    #     print(ipaddress, publicip['status'], publicip['port_id'], port_type)
                    #     del_active_NAT_results = delete.del_publicip(token, url_project, sub_project_id, publicip_id)
                    #     logger.logger('%s  publicip %s delete result:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"), ipaddress, del_active_NAT_results))
                    #     print(del_active_NAT_results)
                elif publicip['status'] == 'ELB':
                    del_elb_iplist.append(ipaddress)
    # print('del_nat_rules_iplist:',del_nat_rules_iplist)
    manager_nat_rules(token, url_project, del_nat_rules_iplist)
    manager_elb(token, url_project, sub_project_id, del_elb_iplist)
                    # publicip_address = publicip['public_ip_address']
                    # create_time = publicip['create_time']
                    # print(ipaddress,id,create_time,bandwidth_charge_mode,publicip['status'])#bandwidth_charge_mode

def manager_nat_rules(token,url_project,del_nat_rules_iplist):
    if len(del_nat_rules_iplist) > 0:
        snat_list = search_list.search_snat_rules(token,url_project)
        for nat_ipaddress in del_nat_rules_iplist:
            for snat_rule in snat_list:
                if nat_ipaddress == snat_rule['floating_ip_address']:
                    # snat_rule_id = snat_rule['id']
                    # print('snat rule', nat_ipaddress, snat_rule_id)
                    del_snat_rule_result = delete.del_snat_rule(token, url_project, snat_rule['id'])
                    logger.logger('%s  delete snat_rules_ip %s return_code:%s.\n' % (time.strftime("%Y-%m-%d %H:%M:%S"),nat_ipaddress,del_snat_rule_result))

        dnat_list = search_list.search_dnat_rules(token, url_project)
        for nat_ipaddress in del_nat_rules_iplist:
            for dnat_rule in dnat_list:
                if nat_ipaddress == dnat_rule['floating_ip_address']:
                    # dnat_rule_id = dnat_rule['id']
                    # print('dnat rule', nat_ipaddress, dnat_rule_id)
                    del_dnat_rule_result = delete.del_dnat_rule(token, url_project, dnat_rule['id'])
                    logger.logger('%s  delete dnat_rules_ip %s return_code:%s.\n' % (
                    time.strftime("%Y-%m-%d %H:%M:%S"), nat_ipaddress, del_dnat_rule_result))
    # print(snat_list)
    # for snat in snat_list:
    #     snat_id = snat['id']
    #     create_time = snat['created_at']
    #     create_stamp = time.mktime(time.strptime(snat['created_at'], format(
    #         "%Y-%m-%dT%H:%M:%SZ"))) + 28800  # 将时间字符串转按指定格式换为元组<class 'time.struct_time'>
    #     print(snat_id,create_stamp)
    # dnat_list = search_list.search_dnat_rules(token, url_project)
    # print(dnat_list)

def manager_elb(token, url_project,sub_project_id,del_elb_iplist):
    if len(del_elb_iplist) > 0:
        pass
    # elb_list = search_list.search_elb_list(token, url_project,sub_project_id)
    # if type(elb_list) is list:
    #     print(elb_list)
    # else:
    #     print('elb_list is not list ',elb_list)
    # enhance_elb_list = search_list.search_enhance_elb_list(token, url_project)
    # if type(enhance_elb_list) is list:
    #     print(enhance_elb_list)
    # else:
    #     print('elb_list is not list ',enhance_elb_list)
    # # print(enhance_elb_list)

def run():
    for url_project in settings.Endpoint_project_id:
        # print(url_project)
        for sub_project in settings.Endpoint_project_id[url_project]:
            sub_project_id = settings.Endpoint_project_id[url_project][sub_project]
            # print(sub_project, sub_project_id,)
            token = get_token.get_token(settings.iam['domainname'], settings.iam['username'], settings.iam['password'],url_project,sub_project)
            if token:
                manager_elb(token, url_project, sub_project_id)
                # manager_nat_rules(token, url_project)
                # manager_ecs(token,url_project,sub_project_id)
                # manager_publicips(token, url_project, sub_project_id)
                # publicips = search_list.search_publicips(token, url_project, sub_project_id)


run()