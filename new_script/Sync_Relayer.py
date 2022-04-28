#!/usr/bin/env python3
# coding=utf-8

from config import *
from util import *
import time

def rebuild_all():
    Build_Relayer_Config(config)

def reload_all():
    for r in config.Relayer:
        r_name = r['name']
        r_dir = config_dir_path + "/{}".format(r_name )
        print(os.popen("kubectl scale deployment {} --replicas=0".format(r_name .lower())).read())
        print(os.popen("kubectl delete cm {}".format(r_name .lower())).read())
        print(os.popen("kubectl create cm {} --from-file={}".format(r_name .lower(), r_dir + "/config.json")).read())
        print(os.popen("kubectl scale deployment {} --replicas=1".format(r_name .lower())).read())
        time.sleep(5)

        
if __name__ == "__main__":
    config = Deploy_Config()
    config.check_0_exist()

    focus_print("Rebuild All Relayer config")
    rebuild_all()

    focus_print("Reload All Relayer")
    reload_all()