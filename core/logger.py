#!/usr/bin/env python
# Author:Zhangmingda
import  os,sys,json,time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(BASE_DIR)
sys.path.append(BASE_DIR)

def logger(message):
    log_file = "%s/logs/manager_cloud_resource.log" % BASE_DIR
    if  os.path.isfile(log_file):
        with open(log_file,'a+',encoding='utf-8') as f:
            f.write(message)
            f.flush()
            f.close()

    else:
        with open(log_file,'w',encoding='utf-8') as f:
            f.write(message)
            f.flush()
            f.close()
