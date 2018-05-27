#!/usr/bin/env python
# Author:Zhangmingda
import os,sys,requests

def get_token(domainname,username,password,url_project,sub_project):
        """通过用户名密码获取token"""
        domainname = domainname
        username = username
        password = password
        #requests模块所需参数如下
        post_data = {"auth": {"identity": {"methods": ["password"],"password": {"user": {"name": username,"password": password,"domain": {"name": domainname}}}},"scope": {"project": {"name":sub_project}}}}
        headers = {"content-type":"application/json",}
        url_str = "https://iam.{_project}.myhuaweicloud.com/v3/auth/tokens".format(_project=url_project)
        # print(url_str)
        #使用requests模块发起gettoken动作
        r = requests.post(url=url_str, json=post_data, headers=headers)
        if r.status_code == 201:
                print('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tiam_code = 201')
                token = r.headers['X-Subject-Token']
                # print(token)
                return token
        else:
                print('用户名or密码错误')
