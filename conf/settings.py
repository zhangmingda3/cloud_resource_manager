#!/usr/bin/env python
# Author:Zhangmingda
import time
#设置测试账号的用户名和密码
iam = {
    'domainname':'hwcloudsom1',
    'username':'zhangmingda',
    'password':'237828Zhang?'
    # 'domainname': 'XXXXX',
    # 'username': 'hXXXXXXX',
    # 'password': 'XXXXXXXXXXXXXXX'
}
#设置不同时段的主机关机和删除时间
if 9 * 3600 < time.time()%86400 + 28800 < 19 * 3600:
    off_time = {
        'ecs': 7  # 关机时间
    }
    del_time = {
        'ecs': 9,  # 删除时间
        'publicip': 9
    }
else:
    off_time = {
        'ecs':3 #小时后关机
    }
    del_time = {
        'ecs':4, #小时后删除
        'publicip':4
    }

#设置不被关机和删除的ECS名字。创建包含这样名字的主机将不会被管理关机和删除
nodel_ecs_name = '爱你哟铭达'
#账户下的不同地区的详细项目名称和项目ID
Endpoint_project_id = {
    'cn-north-1':{'cn-north-1':'10a85dd37bac4e8abf6f6c349c7edfdd'},
    # 'cn-northeast-1':{'cn-northeast-1':'b5295dc8e09042a981b73175e8507050'},
    'cn-east-2':{ 'cn-east-2':'e30de5f42aee4f8586b6ff28fe713422'},#上海,
    'cn-south-1':{'cn-south-1':'521f1245f60341ba84107aaca247688c'},#广州
    'ap-southeast-1':{ 'ap-southeast-1':'dafc92e501c84cbcb2d29fef11a9e67f'}#香港cn-south-1_monitor-Tencent
}
#短信功能使用的项目名称
smn_project = 'cn-north-1'
#IAM子用户ID和名字电话设置(发送短信通知使用)
userinfo = {
    '626b3bca369c4b57aedf113a712bbd27':{'name':'亲爱的张铭达','phone':[11231231231]},
}
#全员电话列表(发送短信通知使用，当被创建的资源无法区分为哪个子用户，关机&删除时发送给全员)
all_phone = []
for user_ID in userinfo:
    for phone in userinfo[user_ID]['phone']:
        all_phone.append(phone)

