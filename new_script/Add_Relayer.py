#!/usr/bin/env python3
# coding=utf-8

import os
import json
import random

from web3 import Web3

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

def load_config():
    global config
    if os.path.exists(deploy_config_path):
        with open(deploy_config_path) as f:
            config = json.load(f)
    else:
        config = { "NetWork": [], "Relayer": [], "Token": [] }

def save_config():
    with open(deploy_config_path,'w') as f:
        json.dump(config,f, indent=4)

def focus_print(text):
    print("\n\033[1;36;40m{}\033[0m".format(text)) # 高亮青色前景色换行输出


def genkey():
    i = len(config['Relayer'])
    r_name = "Relayer{}".format(i)
    acct = Web3().eth.account.create()
    config['Relayer'].append(
        {
            "name": r_name,
            "address": acct.address,
            # "PrivateKey": acct.privateKey.hex()
        }
    )
    with open(key_dir_path + "/{}_keystore.json".format(r_name), 'w') as f:
        keystore = acct.encrypt(KEYSTORE_PASSWORD)
        json.dump(keystore,f, indent=4)
    return acct.privateKey.hex()

def build(privateKey):
    Relayer = config['Relayer']
    NetWork = config['NetWork']
    r = Relayer[-1]

    out_json = { "Chains":[] }
    for n in NetWork:
        cur_endpoint = random.choice(n['endpoint'])
        out_json['Chains'].append(
            {
                "name": n['name'],
                "type": "ethereum",
                "id": str(NetWork.index(n) + 1),
                "endpoint": cur_endpoint,
                "from": r['address'],
                "opts": {
                    "bridge": n['bridge'],
                    # "erc20Handler": "",
                    # "erc721Handler": "",
                    "genericHandler": n['handler'],
                    "gasLimit": gasLimit,
                    "maxGasPrice": maxGasPrice,
                    "startBlock": "0",
                    "http": str(not "https://" in cur_endpoint).lower()
                }
            }
        )
    
    with open(k8s_template_path, 'r') as f:
        k8s_template = f.read()
    k8s_template = k8s_template.replace("{{Key}}", privateKey)
    k8s_template = k8s_template.replace("{{KEYSTORE_PASSWORD}}", KEYSTORE_PASSWORD)
    k8s_template = k8s_template.replace("{{ConfigMap}}", r['name'].lower())

    r_dir = config_dir_path + "/{}".format(r['name'])
    os.mkdir(r_dir)
    with open(r_dir + "/config.json", 'w') as f:
        json.dump(out_json,f, indent=4)
    with open(r_dir + "/relayer-deployment.yaml", 'w') as f:
        f.write(k8s_template)

load_config()

focus_print("Generate Relayer key && Build config yaml")
build(genkey())


save_config()