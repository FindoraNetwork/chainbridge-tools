#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3

from config import *
from util import *

def deployBridgeContract(w3, chainID):
    return Deploy_Contract(w3, "Bridge", (chainID, [], 1, 0, 100))

def deployGenericHandler(w3, bridge_address):
    return Deploy_Contract(w3, "GenericHandler", (bridge_address, [], [], [], []))

def deployColumbusDeck(w3, genericHandlerAddress, columbusAssetAddress):
    return Deploy_Contract(w3, "ColumbusDeck", (genericHandlerAddress, columbusAssetAddress))

def deployColumbusAsset(w3):
    return Deploy_Contract(w3, "ColumbusAsset", ())

def adminSetGenericResource_Destination(w3, bridge_address, handler_address, deck_address):
    bridge_abi = load_abi("Bridge")
    bridge_contract = w3.eth.contract(bridge_address, abi=bridge_abi)

    func = bridge_contract.functions.adminSetGenericResource(
        handler_address,
        uni_resourceID,
        deck_address,
        load_functionSig("ColumbusDeck","deposit"),
        load_functionSig("ColumbusDeck","withdraw")
    )
    tx_hash = sign_send_wait(w3, func)
    print("adminSetGenericResource {} transaction hash: {}".format(deck_address, tx_hash.hex()))

def adminAddRelayer(bridge_address):
    bridge_abi = load_abi("Bridge")
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
    config.check_0_exist()

    focus_print("Deployment Bridge Contract")
    bridge_address = deployBridgeContract(w3, len(config.NetWork))
    focus_print("Deployment GenericHandler Contract")
    handler_address = deployGenericHandler(w3, bridge_address)
    focus_print("Deployment ColumbusAsset Contract")
    asset_address = deployColumbusAsset(w3)
    focus_print("Deployment ColumbusDeck Contract")
    deck_address = deployColumbusDeck(w3, handler_address, asset_address)

    focus_print("Call Bridge.adminSetGenericResource")
    adminSetGenericResource_Destination(w3, bridge_address, handler_address, deck_address)

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
            "columbus": {
                "deck": deck_address,
                "asset": asset_address,
            }
        }
    )

    config.save()