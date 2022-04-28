#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3

from config import *
from util import *

from Add_Network import deployBridgeContract, deployGenericHandler, deployColumbusDeck, deployColumbusAsset

def deployColumbusRelayer(w3, _genericHandlerAddress, _prismxxAddress, _columbusWrapTokensAddress, _bridgeAddress):
    return Deploy_Contract(w3, "ColumbusRelayer", (
        _genericHandlerAddress,
        _prismxxAddress,
        _columbusWrapTokensAddress,
        uni_resourceID,
        _bridgeAddress
    ))

def deployColumbusSimBridge(w3, _prismBridgeAddress):
    return Deploy_Contract(w3, "ColumbusSimBridge", (_prismBridgeAddress,))

def deployColumbusWrap(w3):
    return Deploy_Contract(w3, "ColumbusWrap", ())


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
    columbus_simbridge_address = deployColumbusSimBridge(w3, args.prism_bridge)

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

def func_destination(args):
    config.check_0_exist()
    w3 = Web3(Web3.HTTPProvider(config.NetWork[0]['Provider']))

    focus_print("Deployment ColumbusDeck Contract")
    deck_address = deployColumbusDeck(w3, config.NetWork[0]['handler'])
    focus_print("Deployment ColumbusAsset Contract")
    asset_address = deployColumbusAsset(w3)

    config.NetWork[0]["columbus"]["deck"] = deck_address
    config.NetWork[0]["columbus"]["asset"] = asset_address


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='InitFindora SubCommand')
    subparsers.required = True

    parser_privacy = subparsers.add_parser('privacy', help='Init Findora Privacy Network')
    parser_privacy.add_argument('provider', help='Findora Privacy Network Provider')
    parser_privacy.add_argument('--prism-bridge', help='PrismXXBridge Contract Address', required=True)
    parser_privacy.add_argument('--prism-asset', help='PrismXXAsset Contract Address', required=True)
    parser_privacy.set_defaults(func=func_privacy)

    parser_privacy = subparsers.add_parser('destination', help='If Findora is destination chain, Use this SubCommand.')
    parser_privacy.set_defaults(func=func_destination)

    args = parser.parse_args()

    config = Deploy_Config()
    args.func(args)
    config.save()