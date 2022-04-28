#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3
import json

from config import *
from util import *

def deployBridgeContract(chainID):
    return Deploy_Contract(w3, "contracts/Bridge.json", (chainID, [], 1, 0, 100))

def deployGenericHandler(bridge_address):
    return Deploy_Contract(w3, "contracts/GenericHandler.json", (bridge_address, [], [], [], []))

def deployColumbusDeck(genericHandlerAddress):
    return Deploy_Contract(w3, "contracts/ColumDeck.json", (genericHandlerAddress,))

def adminAddRelayer(bridge_address):
    with open("contracts/Bridge.json") as f:
        bridge_abi = json.load(f)['abi']

    bridge_contract = w3.eth.contract(bridge_address, abi=bridge_abi)

    for r in config.Relayer:
        func = bridge_contract.functions.adminAddRelayer(r['address'])
        tx_hash = sign_send_wait(w3, func)
        print("{} adminAddRelayer transaction hash: {}".format(r['name'], tx_hash.hex()))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='New Network Name', required=True)
    parser.add_argument('--provider', help='New Network Provider', required=True)
    args = parser.parse_args()

    Network_Name = args.name
    Network_Provider = args.provider
    w3 = Web3(Web3.HTTPProvider(Network_Provider))

    config = Deploy_Config()

    focus_print("Deployment Bridge Contract")
    bridge_address = deployBridgeContract(len(config.NetWork))
    focus_print("Deployment GenericHandler Contract")
    handler_address = deployGenericHandler(bridge_address)
    focus_print("Deployment ColumbusDeck Contract")
    deck_address = deployColumbusDeck(handler_address)
    focus_print("adminAddRelayer for Existing Relayer")
    adminAddRelayer(bridge_address)

    config.NetWork.append(
        {
            "name": Network_Name,
            "Provider": Network_Provider,
            "endpoint": [
                Network_Provider
            ],
            "bridge": bridge_address,
            "handler": handler_address,
            "deck": deck_address
        }
    )

    config.save()