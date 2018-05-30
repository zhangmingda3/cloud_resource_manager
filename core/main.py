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
    SHUTOFF_list = {'id_dict':[],'username':[]}
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
            SHUTOFF_list['id_dict'].append({"id":ecs_id})
            SHUTOFF_list['username'].append(ecs_name)
        if ecs_id not in protected.ECS and time.time() > DELETE_time:
            delete.del_ecs(token, url_project, sub_project_id, ecs_id, ecs_name)
    if len(SHUTOFF_list['id']) >0:
        poweroff.poweoff_ecs(token, url_project, sub_project_id, SHUTOFF_list)

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
                    # bandwidth_charge_mode = search_list.search_bandwidth_charge_mode(token,url_project,sub_project_id,publicip['bandwidth_id'])
                    # print(ipaddress,publicip['status'],bandwidth_charge_mode)
                    delete.del_publicip(token,url_project,sub_project_id,publicip_id,ipaddress)
                elif publicip['status'] == 'ACTIVE':
                    port_type = search_list.search_port_owner(token,url_project,publicip['port_id'])
                    if port_type != 'network:nat_gateway':#不是NAT网关的IP就删除
                        delete.del_publicip(token, url_project, sub_project_id, publicip_id, ipaddress)
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
    # manager_elb(token, url_project, sub_project_id, del_elb_iplist)
                    # create_time = publicip['create_time']
                    # print(ipaddress,id,create_time,bandwidth_charge_mode,publicip['status'])#bandwidth_charge_mode

def manager_nat_rules(token,url_project,del_nat_rules_iplist):
    if len(del_nat_rules_iplist) > 0:
        # print(del_nat_rules_iplist)
        snat_list = search_list.search_snat_rules(token,url_project)
        for nat_ipaddress in del_nat_rules_iplist:
            for snat_rule in snat_list:
                if nat_ipaddress == snat_rule['floating_ip_address']:
                    # print(snat_rule)
                    # snat_rule_id = snat_rule['id']
                    # print('snat rule', nat_ipaddress, snat_rule_id)
                    delete.del_snat_rule(token, url_project, snat_rule['id'],nat_ipaddress)
        dnat_list = search_list.search_dnat_rules(token, url_project)
        for nat_ipaddress in del_nat_rules_iplist:
            for dnat_rule in dnat_list:
                if nat_ipaddress == dnat_rule['floating_ip_address']:
                    # dnat_rule_id = dnat_rule['id']
                    # print('dnat rule', nat_ipaddress, dnat_rule_id)
                    delete.del_dnat_rule(token, url_project, dnat_rule['id'],nat_ipaddress)
    # print(snat_list)
    # for snat in snat_list:
    #     snat_id = snat['id']
    #     create_time = snat['created_at']
    #     create_stamp = time.mktime(time.strptime(snat['created_at'], format(
    #         "%Y-%m-%dT%H:%M:%SZ"))) + 28800  # 将时间字符串转按指定格式换为元组<class 'time.struct_time'>
    #     print(snat_id,create_stamp)
    # dnat_list = search_list.search_dnat_rules(token, url_project)
    # print(dnat_list)

# def manager_elb(token, url_project,sub_project_id,del_elb_iplist):
#
#     if len(del_elb_iplist) > 0:
#         # pass
#         elb_list = search_list.search_elb_list(token, url_project,sub_project_id)
#     # if type(elb_list) is list:
#         print(elb_list)
#     # else:
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
                # manager_elb(token, url_project, sub_project_id,)
                # manager_nat_rules(token, url_project)

                # manager_ecs(token,url_project,sub_project_id)
                manager_publicips(token, url_project, sub_project_id)

                # publicips = search_list.search_publicips(token, url_project, sub_project_id)
                # elb_list = search_list.search_elb_list(token, url_project, sub_project_id)
                # print(elb_list)
                # enhance_elb_list = search_list.search_enhance_elb_list(token, url_project)
                # print(enhance_elb_list)
                # delete.del_ecs(token, url_project, sub_project_id, "e9f2ac2a-1a54-4b38-8348-0f741a0de447", 'zmd')
                #delete.del_publicip(token,url_project,sub_project_id,'5e7702c6-a72c-4de0-9e96-bfec9f72b015','114.115.146.228')



run()