#!/usr/bin/env python
# Author:Zhangmingda
import os,sys,time

from core import get_token,search_list,poweroff,delete,logger,smn
from conf import settings,protected

def manager_ecs(token,url_project,sub_project_id,smn_token, smn_project, smn_project_id):
    '''清理一个sub_project_id下的ECS资源+短信通知'''
    ecs_list = search_list.search_ecs(token, url_project, sub_project_id)
    SHUTOFF_list = {'id_dict':[],'ecs_name':[]}
    for ecs in ecs_list:
        ecs_id = ecs["id"]
        create_stamp = time.mktime(time.strptime(ecs['created'], format("%Y-%m-%dT%H:%M:%SZ"))) + 28800  # 将时间字符串转按指定格式换为元组<class 'time.struct_time'>
        SHUTOFF_time = create_stamp + settings.off_time['ecs'] * 3600
        DELETE_time = create_stamp + settings.del_time['ecs'] * 3600
        ecs_status = ecs['status']
        user_id = ecs['user_id']
        ecs_name = ecs['name']
        if user_id in settings.userinfo:
            pass
        else:
            settings.userinfo[user_id] = {'phone': settings.all_phone, 'name': settings.iam['domainname']}
        smn_shut_info = '%s 您好，您的主机：%s 被你累的Down了， 当前自动关机时间为创建后 %d小时 从现在开始%d小时后将自焚。有重要数据请尽快做镜像备份or需长期使用找管理员添加白名单' % (settings.userinfo[user_id]['name'], ecs_name, settings.off_time['ecs'],settings.del_time['ecs'] - settings.off_time['ecs'])
        smn_del_info = '%s 您好，您的主机：%s 正在自焚....当前设置的自焚时间为创建后 %d小时。' % (settings.userinfo[user_id]['name'], ecs_name, settings.del_time['ecs'])

        if ecs_id not in protected.ECS and time.time() > SHUTOFF_time and ecs_status != "SHUTOFF" and settings.nodel_ecs_name not in ecs_name:
            SHUTOFF_list['id_dict'].append({"id":ecs_id})
            SHUTOFF_list['ecs_name'].append(ecs_name)
            smn.smn(smn_token, smn_project, smn_project_id, settings.userinfo[user_id]['phone'], smn_shut_info)
        if ecs_id not in protected.ECS and time.time() > DELETE_time and settings.nodel_ecs_name not in ecs_name:
            delete.del_ecs(token, url_project, sub_project_id, ecs_id, ecs_name)
            smn.smn(smn_token, smn_project, smn_project_id, settings.userinfo[user_id]['phone'], smn_del_info)

    if len(SHUTOFF_list['id_dict']) >0:
        poweroff.poweoff_ecs(token, url_project, sub_project_id, SHUTOFF_list)

def  manager_publicips(token, url_project, sub_project_id,smn_token, smn_project, smn_project_id):
    '''删除一个project下的弹性IP+短信通知'''
    publicips = search_list.search_publicips(token, url_project, sub_project_id)
    del_nat_rules_iplist = []
    del_elb_iplist = []
    for publicip in publicips:
        if  not publicip['profile']['user_id'] and publicip['public_ip_address'] not in protected.EIP: # and publicip['bandwidth_share_type'] == 'PER'
            '''not publicip['profile']['user_id']判断按需计费 PER为独享带宽'''
            create_stamp = time.mktime(time.strptime(publicip['create_time'], format("%Y-%m-%d %H:%M:%S"))) + 28800  # 将时间字符串转按指定格式换为元组<class 'time.struct_time'>
            DEL_time_stamp = create_stamp + settings.del_time['publicip'] * 3600
            if time.time() > DEL_time_stamp :
                publicip_id = publicip['id']
                ipaddress = publicip['public_ip_address']
                smn_del_ip_info = '%s 您好，您的IP：%s 已被删除，当前按需IP自动删除时间为创建后 %d小时' % (settings.iam['domainname'], ipaddress, settings.del_time['publicip'])
                if publicip['status'] == 'DOWN':
                    delete.del_publicip(token,url_project,sub_project_id,publicip_id,ipaddress)
                    # smn.smn(smn_token, smn_project, smn_project_id, settings.all_phone,smn_del_ip_info)
                elif publicip['status'] == 'ACTIVE':
                    port_type = search_list.search_port_owner(token,url_project,publicip['port_id'])
                    if port_type != 'network:nat_gateway':          #不是NAT网关的IP就删除
                        delete.del_publicip(token, url_project, sub_project_id, publicip_id, ipaddress)
                        # smn.smn(smn_token, smn_project, smn_project_id, settings.all_phone, smn_del_ip_info)
                    else:
                        del_nat_rules_iplist.append(ipaddress)
                elif publicip['status'] == 'ELB':
                    del_elb_iplist.append(ipaddress)
                else:
                    delete.del_publicip(token, url_project, sub_project_id, publicip_id, ipaddress)
                    # smn.smn(smn_token, smn_project, smn_project_id, settings.all_phone, smn_del_ip_info)

    manager_nat_rules(token, url_project, del_nat_rules_iplist)
    manager_elb(token, url_project, sub_project_id,del_elb_iplist,smn_token, smn_project, smn_project_id)

def manager_nat_rules(token,url_project,del_nat_rules_iplist):
    '''删除相关snat或者dnat规则'''
    if len(del_nat_rules_iplist) > 0:
        # print(del_nat_rules_iplist)
        snat_list = search_list.search_snat_rules(token,url_project)
        for nat_ipaddress in del_nat_rules_iplist:
            for snat_rule in snat_list:
                if nat_ipaddress == snat_rule['floating_ip_address']:
                    delete.del_snat_rule(token, url_project, snat_rule['id'],nat_ipaddress)
        dnat_list = search_list.search_dnat_rules(token, url_project)
        for nat_ipaddress in del_nat_rules_iplist:
            for dnat_rule in dnat_list:
                if nat_ipaddress == dnat_rule['floating_ip_address']:
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

def manager_elb(token, url_project,sub_project_id,del_elb_iplist,smn_token, smn_project, smn_project_id): #,del_elb_iplist
    '''删除经典负载均衡器里面的公网IP和负载均衡'''
    if len(del_elb_iplist) > 0 :
        elb_list = search_list.search_elb_list(token, url_project, sub_project_id)
        for elb_ip in del_elb_iplist:
            for elb in elb_list:
                if elb_ip == elb['vip_address']:
                    listeners = search_list.search_elb_listeners(token, url_project, sub_project_id, elb['id'])
                    for listener in listeners:
                        if listener['member_number'] > 0:
                            backend_ecs_list = search_list.search_elb_listen_backend_ecs_list(token, url_project, sub_project_id, listener['id'])
                            for backend_ecs in backend_ecs_list:
                                delete.remove_elb_listener_ecs(token, url_project, sub_project_id, listener['id'], backend_ecs)

                    time.sleep(3)
                    smn_del_ELBip_info = '%s 您好 您的经典型ELB IP：%s已飞灰湮灭。当前设置自动化蝶时间为按需IP创建后 %d小时' % (settings.iam['domainname'], elb_ip, settings.del_time['publicip'])
                    del_elb_result = delete.del_elb(token, url_project, sub_project_id, elb['id'], elb['vip_address'])
                    if del_elb_result:
                        smn.smn(smn_token, smn_project, smn_project_id, settings.all_phone, smn_del_ELBip_info)

# def manager_enhance_elb():
#     enhance_elb_list = search_list.search_enhance_elb_list(token, url_project)
#     for enhance_elb in enhance_elb_list:
#         # if ipaddress_list in enhance_elb['enhance_elb_listeners']:
#         print(enhance_elb_list)
#     # enhance_elb_listeners = search_list.search_enhance_elb_listeners(token, url_project)
#     # print(enhance_list)
#
#                 # print(backend_ecs_list)
#         # print(listeners)
#     # enhance_elb_list = search_list.search_enhance_elb_list(token, url_project)
#     # print('enhance_elb_list',enhance_elb_list)


def run():
    '''调用这个函数来获取token，token获取OK然后做资源的管理'''
    smn_token = get_token.get_token(settings.iam['domainname'], settings.iam['username'], settings.iam['password'],settings.smn_project, settings.smn_project)
    smn_project = settings.smn_project
    smn_project_id = settings.Endpoint_project_id[smn_project][smn_project]
    for url_project in settings.Endpoint_project_id:
        # print(url_project)
        for sub_project in settings.Endpoint_project_id[url_project]:
            sub_project_id = settings.Endpoint_project_id[url_project][sub_project]
            # print(sub_project, sub_project_id,)
            token = get_token.get_token(settings.iam['domainname'], settings.iam['username'], settings.iam['password'],url_project,sub_project)

            if token:
                manager_ecs(token, url_project, sub_project_id, smn_token, smn_project, smn_project_id)
                manager_publicips(token, url_project, sub_project_id, smn_token, smn_project, smn_project_id)
