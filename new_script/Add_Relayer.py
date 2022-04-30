#!/usr/bin/env python3
# coding=utf-8

import os
import json
from web3 import Web3

from config import *
from util import *

def genkey():
    i = len(config.Relayer)
    r_name = "Relayer{}".format(i)
    acct = Web3().eth.account.create()
    config.Relayer.append(
        {
            "name": r_name,
            "address": acct.address,
            # "PrivateKey": acct.privateKey.hex()
        }
    )
    with open(key_dir_path + "/{}_keystore.json".format(r_name), 'w') as f:
        keystore = acct.encrypt(KEYSTORE_PASSWORD)
        json.dump(keystore,f, indent=4)
    # return acct.privateKey.hex()

def build():
    r_name = config.Relayer[-1]['name']

    r_dir = config_dir_path + "/{}".format(r_name)
    os.mkdir(r_dir)

    Build_Relayer_Config(config, -1)
    Build_Relayer_YAML(r_name)

def adminAddRelayer():
    bridge_abi = load_abi("Bridge")

    for n in config.NetWork:
        w3 = Web3(Web3.HTTPProvider(n['Provider']))
        bridge_contract = w3.eth.contract(n['bridge'], abi=bridge_abi)

        func = bridge_contract.functions.adminAddRelayer(config.Relayer[-1]['address'])
        # txn = bridge_contract.functions.adminRemoveRelayer(config.Relayer[-1]['address']).buildTransaction({'from': owner_acct.address, 'nonce': w3.eth.getTransactionCount(owner_acct.address), "gasPrice": w3.eth.gas_price})
        tx_hash = sign_send_wait(w3, func)
        print("{} adminAddRelayer transaction hash: {}".format(n['name'], tx_hash.hex()))

def deploy():
    r_name = config.Relayer[-1]['name']
    r_dir = config_dir_path + "/{}".format(r_name )
    print(os.popen("kubectl create cm {} --from-file={}".format(r_name .lower(), r_dir + "/config.json")).read())
    print(os.popen("kubectl apply -f {}".format(r_dir + "/relayer-deployment.yaml")).read())


if __name__ == "__main__":
    config.check_0_exist()

    focus_print("Generate New Relayer key")
    genkey()
    focus_print("Build New config and yaml")
    build()
    focus_print("call Bridge Contract adminAddRelayer for each Networks")
    adminAddRelayer()
    focus_print("Deployment Relayer In Kubernetes Cluster")
    deploy()

    config.save()