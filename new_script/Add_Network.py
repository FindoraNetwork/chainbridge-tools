#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3

from config import *
from util import *

def deployBridgeContract(w3, chainID):
    return Deploy_Contract(w3, "Bridge", (chainID, [], 2, 0, 100))

def deployGenericHandler(w3, bridge_address):
    return Deploy_Contract(w3, "GenericHandler", (bridge_address, [], [], [], []))

def deployColumbusDeck(w3, genericHandlerAddress, columbusAssetAddress):
    return upgradeable_Deploy(w3, "ColumbusDeck", (genericHandlerAddress, columbusAssetAddress))

def deployColumbusPool(w3):
    return upgradeable_Deploy(w3, "ColumbusPool", ())

def Pool_setColumbus(w3, pool_address, _addr):
    pool_abi = load_abi("ColumbusPool")
    pool_contract = w3.eth.contract(pool_address, abi=pool_abi)

    func = pool_contract.functions.setColumbus(_addr)
    tx_hash = sign_send_wait(w3, func)
    print("Pool_setColumbus {} transaction hash: {}".format(_addr, tx_hash.hex()))

def Deck_setColumbusPool(w3, deck_address, _addr):
    deck_abi = load_abi("ColumbusDeck")
    deck_contract = w3.eth.contract(deck_address, abi=deck_abi)

    func = deck_contract.functions.setColumbusPool(_addr)
    tx_hash = sign_send_wait(w3, func)
    print("Deck_setColumbusPool {} transaction hash: {}".format(_addr, tx_hash.hex()))

def deployColumbusAsset(w3):
    return Deploy_Contract(w3, "ColumbusAsset", ())

def adminSetGenericResource_Destination(w3, bridge_address, handler_address, deck_address):
    bridge_abi = load_abi("Bridge")
    bridge_contract = w3.eth.contract(bridge_address, abi=bridge_abi)

    func = bridge_contract.functions.adminSetGenericResource(
        handler_address,
        resourceID_301,
        deck_address,
        load_functionSig("ColumbusDeck","deposit"),
        load_functionSig("ColumbusDeck","withdraw")
    )
    tx_hash = sign_send_wait(w3, func)
    print("301 adminSetGenericResource {} transaction hash: {}".format(deck_address, tx_hash.hex()))

    func = bridge_contract.functions.adminSetGenericResource(
        handler_address,
        resourceID_501,
        deck_address,
        load_functionSig("ColumbusDeck","deposit"),
        load_functionSig("ColumbusDeck","withdraw")
    )
    tx_hash = sign_send_wait(w3, func)
    print("501 adminSetGenericResource {} transaction hash: {}".format(deck_address, tx_hash.hex()))

def adminAddRelayer(w3, bridge_address):
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

    config.check_0_exist()

    focus_print("Deployment Bridge Contract")
    bridge_address = deployBridgeContract(w3, len(config.NetWork))
    focus_print("Deployment GenericHandler Contract")
    handler_address = deployGenericHandler(w3, bridge_address)
    focus_print("Deployment ColumbusAsset Contract")
    asset_address = deployColumbusAsset(w3)
    focus_print("Deployment ColumbusPool Contract (upgradeable)")
    pool_address = deployColumbusPool(w3)
    focus_print("Deployment ColumbusDeck Contract (upgradeable)")
    deck_address = deployColumbusDeck(w3, handler_address, asset_address)
    focus_print("Call Pool.setColumbus")
    Pool_setColumbus(w3, pool_address, deck_address)
    focus_print("Call Deck.setColumbusPool")
    Deck_setColumbusPool(w3, deck_address, pool_address)

    focus_print("Call Bridge.adminSetGenericResource")
    adminSetGenericResource_Destination(w3, bridge_address, handler_address, deck_address)

    focus_print("adminAddRelayer for Existing Relayer")
    adminAddRelayer(w3, bridge_address)

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
                "pool": pool_address,
                "asset": asset_address
            }
        }
    )

    config.save()