#!/usr/bin/env python
# Author:Zhangmingda
import os,sys,time
BASE_NAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_NAME)
from core import get_token,search_list
from conf import settings,protected

# project_id = '52fb7d7429d04068ae8ff9632106e701'
# if token:
for url_project in settings.Endpoint_project_id:
    print(url_project)
    for sub_project in settings.Endpoint_project_id[url_project]:
        sub_project_id = settings.Endpoint_project_id[url_project][sub_project]
        # print(sub_project, sub_project_id,)
        token = get_token.get_token(settings.iam['domainname'], settings.iam['username'], settings.iam['password'],url_project,sub_project)
        ecs_list = search_list.search_ecs(token,url_project,sub_project_id)
        for ecs in ecs_list:
            id = ecs['id']
            create_stamp = time.mktime(time.strptime(ecs['created'], format("%Y-%m-%dT%H:%M:%SZ"))) + 28800  # 将时间字符串转按指定格式换为元组<class 'time.struct_time'>
            SHUTOFF_time = create_stamp + settings.off_time['ecs'] * 3600
            ecs_status = ecs['status']
            user_id = ecs['user_id']
            ecs_name = ecs['name']
            if id not in protected.ECS and time.time() > SHUTOFF_time:
                    print(id,type(id),create_stamp,type(create_stamp),ecs_status,type(ecs_status),user_id,type(user_id),ecs_name)

        print(time.strftime("%Y-%m-%d %H:%M:%S"),'\033[32;1m查询sub_project:%s完毕!\033[0m'%sub_project)
