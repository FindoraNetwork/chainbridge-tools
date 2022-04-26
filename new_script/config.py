# coding=utf-8

import os

config_dir_path = os.getcwd() + "/config"
if not os.path.exists(config_dir_path):
    os.mkdir(config_dir_path)
key_dir_path = os.getcwd() + "/keys"
if not os.path.exists(key_dir_path):
    os.mkdir(key_dir_path)

deploy_config_path = config_dir_path + "/deploy_config.json"
owner_key_path = key_dir_path + "/owner_keystore.json"
k8s_template_path = "k8s_yaml/relayer-deployment.yaml"

gasLimit = "1000000"
maxGasPrice = "20000000"

KEYSTORE_PASSWORD = "passw0rd"