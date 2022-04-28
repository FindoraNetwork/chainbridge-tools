#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3
import json

from config import *
from util import *

from Add_Network import deployBridgeContract, deployGenericHandler

def deployColumbusRelayer(_genericHandlerAddress, _prismxxAddress, _columbusWrapTokensAddress, _bridgeAddress):
    return Deploy_Contract(w3, "contracts/ColumbusRelayer.json", (
        _genericHandlerAddress,
        _prismxxAddress,
        _columbusWrapTokensAddress,
        uni_resourceID,
        _bridgeAddress
    ))

def deployColumbusSimBridge(_prismBridgeAddress):
    return Deploy_Contract(w3, "contracts/ColumbusSimBridge.json", (_prismBridgeAddress,))

def deployColumbusWrap():
    return Deploy_Contract(w3, "contracts/ColumbusWrapTokens.json", ())


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('provider', help='Findora Privacy Network Provider')
    parser.add_argument('--prism-bridge', help='PrismXXBridge Contract Address', required=True)
    parser.add_argument('--prism-asset', help='PrismXXAsset Contract Address', required=True)
    parser.add_argument('--Findora-is-destination-chain', help="If Findora is destination chain, Use this Flag.", action='store_true', dest='destination_flag')
    args = parser.parse_args()

    w3 = Web3(Web3.HTTPProvider(args.provider))

    config = Deploy_Config()

    focus_print("Deployment Bridge Contract")
    bridge_address = deployBridgeContract(0)
    focus_print("Deployment GenericHandler Contract")
    handler_address = deployGenericHandler(bridge_address)
    focus_print("Deployment ColumbusWrap Contract")
    columbus_wrap_address = deployColumbusWrap()
    focus_print("Deployment ColumbusRelayer Contract")
    columbus_relayer_address = deployColumbusRelayer(handler_address, args.prism_bridge, columbus_wrap_address, bridge_address)
    focus_print("Deployment ColumbusSimBridge Contract")
    columbus_simbridge_address = deployColumbusSimBridge(args.prism_bridge)

    config.NetWork[0] = {
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
    }

    config.save()