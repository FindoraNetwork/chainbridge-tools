#!/usr/bin/env python3
# coding=utf-8

import os
from web3 import Web3

from config import *
from util import *

def genkey():
    for i in range(6):
        r_name = "Relayer{}".format(i)

        gen_result = os.popen("{} accounts generate --password {}".format(chainbridge_bin_path, KEYSTORE_PASSWORD)).read()
        print(gen_result)
        
        for a in gen_result.split():
            if "address" in a:
                r_address = (a.split('=')[1])

        config.Relayer.append(
            {
                "name": r_name,
                "address": r_address,
                "group": i // 2
            }
        )

def build(action):
    if action == 'init':
        for n in config.NetWork:
            n["Relayer_opts"] = {
                "gasLimit": gasLimit,
                "maxGasPrice": maxGasPrice,
                "executeWatchLimit": executeWatchLimit,
                "blockConfirmations": blockConfirmations
            }
        config.save()
        
        r_dir = config_dir_path + "/Relayer"
        os.mkdir(r_dir)

    Build_Relayer_Config()

def adminAddRelayer():
    bridge_abi = load_abi("Bridge")

    for n in config.NetWork:
        w3 = Web3(Web3.HTTPProvider(n['Provider']))
        bridge_contract = w3.eth.contract(n['bridge'], abi=bridge_abi)

        for r in config.Relayer:
            func = bridge_contract.functions.adminAddRelayer(r['address'])
            # txn = bridge_contract.functions.adminRemoveRelayer(config.Relayer[-1]['address']).buildTransaction({'from': owner_acct.address, 'nonce': w3.eth.getTransactionCount(owner_acct.address), "gasPrice": w3.eth.gas_price})
            tx_hash = sign_send_wait(w3, func)
            print("{} adminAddRelayer {} transaction hash: {}".format(n['name'], r['name'], tx_hash.hex()))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['init', 'sync'])
    args = parser.parse_args()

    config.check_0_exist()

    if args.action == 'init':
        focus_print("Generate 6x Relayer key")
        genkey()
        config.save()

        focus_print("call Bridge Contract adminAddRelayer for each Networks")
        adminAddRelayer()

    focus_print("Build 6x Config")
    build(args.action)