#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3

from config import *
from util import *

from Add_Network import deployBridgeContract, deployGenericHandler

def deployColumbusRelayer(w3, _genericHandlerAddress, _prismxxAddress, _columbusWrapTokensAddress, _bridgeAddress):
    return Deploy_Contract(w3, "ColumbusRelayer", (
        _genericHandlerAddress,
        _prismxxAddress,
        _columbusWrapTokensAddress,
        uni_resourceID,
        _bridgeAddress
    ))

def deployColumbusSimBridge(w3, _prismBridgeAddress, _prismBridgeLedger):
    return Deploy_Contract(w3, "ColumbusSimBridge", (_prismBridgeAddress, _prismBridgeLedger))

def deployColumbusWrap(w3):
    return Deploy_Contract(w3, "ColumbusWrap", ())

def adminSetGenericResource_Privacy(w3, bridge_address, handler_address, columbus_relayer_address):
    bridge_abi = load_abi("Bridge")
    bridge_contract = w3.eth.contract(bridge_address, abi=bridge_abi)

    func = bridge_contract.functions.adminSetGenericResource(
        handler_address,
        uni_resourceID,
        columbus_relayer_address,
        load_functionSig("ColumbusRelayer","withdrawToOtherChainCallback"),
        load_functionSig("ColumbusRelayer","depositFromOtherChain")
    )
    tx_hash = sign_send_wait(w3, func)
    print("adminSetGenericResource {} transaction hash: {}".format(columbus_relayer_address, tx_hash.hex()))


def func_privacy(args):
    w3 = Web3(Web3.HTTPProvider(args.provider))

    focus_print("Deployment Bridge Contract")
    bridge_address = deployBridgeContract(w3, 0)
    focus_print("Deployment GenericHandler Contract")
    handler_address = deployGenericHandler(w3, bridge_address)
    focus_print("Deployment ColumbusWrap Contract")
    columbus_wrap_address = deployColumbusWrap(w3)
    focus_print("Deployment ColumbusRelayer Contract")
    columbus_relayer_address = deployColumbusRelayer(w3, handler_address, args.prism_bridge, columbus_wrap_address, bridge_address)
    focus_print("Deployment ColumbusSimBridge Contract")
    columbus_simbridge_address = deployColumbusSimBridge(w3, args.prism_bridge, args.prism_ledger)

    focus_print("Call Bridge.adminSetGenericResource")
    adminSetGenericResource_Privacy(w3, bridge_address, handler_address, columbus_relayer_address)

    config.NetWork.append({
        "name": "Findora",
        "Provider": args.provider,
        "endpoint": [
            args.provider
        ],
        "bridge": bridge_address,
        "handler": handler_address,
        "prism": {
            "bridge": args.prism_bridge,
            "asset": args.prism_asset
        },
        "columbus": {
            "relayer": columbus_relayer_address,
            "simbridge": columbus_simbridge_address,
            "wrap": columbus_wrap_address
        }
    })


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('provider', help='Findora Privacy Network Provider')
    parser.add_argument('--prism-bridge', help='PrismXXBridge Contract Address', required=True)
    parser.add_argument('--prism-asset', help='PrismXXAsset Contract Address', required=True)
    parser.add_argument('--prism-ledger', help='PrismXXLedger Contract Address', required=True)

    args = parser.parse_args()

    func_privacy(args)
    config.save()