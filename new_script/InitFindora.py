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

def deployPrismXXAsset(w3):
    return Deploy_Contract(w3, "PrismXXAsset", ())

def deployPrismXXLedger(w3, _bridge, _asset):
    return Deploy_Contract(w3, "PrismXXLedger", (_bridge, _asset))

def Set_PrismXXBridge(w3, prism_bridge_address, _asset_contract, _ledger_contract):
    prism_bridge_abi = load_abi("PrismXXBridge")
    prism_bridge_contract = w3.eth.contract(prism_bridge_address, abi=prism_bridge_abi)

    func = prism_bridge_contract.functions.adminSetAsset(_asset_contract)
    tx_hash = sign_send_wait(w3, func)
    print("adminSetAsset {} transaction hash: {}".format(_asset_contract, tx_hash.hex()))

    func = prism_bridge_contract.functions.adminSetLedger(_ledger_contract)
    tx_hash = sign_send_wait(w3, func)
    print("adminSetLedger {} transaction hash: {}".format(_ledger_contract, tx_hash.hex()))

def func_columbus(args):
    if args.provider != None:    
        provider = args.provider
        prism_bridge = args.prism_bridge
        prism_asset = args.prism_asset
        prism_ledger = args.prism_ledger
    else:
        config.check_0_exist()
        n = config.NetWork[0]
        provider = n['Provider']
        prism_bridge = n['prism']['bridge']
        prism_asset = n['prism']['asset']
        prism_ledger = n['prism']['ledger']

    w3 = Web3(Web3.HTTPProvider(provider))

    focus_print("Deployment Bridge Contract")
    bridge_address = deployBridgeContract(w3, 0)
    focus_print("Deployment GenericHandler Contract")
    handler_address = deployGenericHandler(w3, bridge_address)
    focus_print("Deployment ColumbusWrap Contract")
    columbus_wrap_address = deployColumbusWrap(w3)
    focus_print("Deployment ColumbusRelayer Contract")
    columbus_relayer_address = deployColumbusRelayer(w3, handler_address, prism_bridge, columbus_wrap_address, bridge_address)
    focus_print("Deployment ColumbusSimBridge Contract")
    columbus_simbridge_address = deployColumbusSimBridge(w3, prism_bridge, prism_ledger)

    focus_print("Call Bridge.adminSetGenericResource")
    adminSetGenericResource_Privacy(w3, bridge_address, handler_address, columbus_relayer_address)

    config_0 = {
        "name": "Findora",
        "Provider": provider,
        "endpoint": [
            provider
        ],
        "bridge": bridge_address,
        "handler": handler_address,
        "prism": {
            "bridge": prism_bridge,
            "asset": prism_asset,
            "ledger": prism_ledger
        },
        "columbus": {
            "relayer": columbus_relayer_address,
            "simbridge": columbus_simbridge_address,
            "wrap": columbus_wrap_address
        }
    }

    if len(config.NetWork) == 0:
        config.NetWork.append(config_0)
    else:
        config.NetWork[0] = config_0

def func_prism(args):
    provider = args.provider
    prism_bridge = args.prism_bridge

    w3 = Web3(Web3.HTTPProvider(provider))

    focus_print("Deployment PrismXXAsset Contract")
    prism_asset = deployPrismXXAsset(w3)
    focus_print("Deployment PrismXXLedger Contract")
    prism_ledger = deployPrismXXLedger(w3, prism_bridge, prism_asset)
    focus_print("call PrismXXBridge.adminSetAsset && PrismXXBridge.adminSetLedger")
    Set_PrismXXBridge(w3, prism_bridge, prism_asset, prism_ledger)

    config_0 = {
        "name": "Findora",
        "Provider": provider,
        "endpoint": [
            provider
        ],
        "bridge": "",
        "handler": "",
        "prism": {
            "bridge": prism_bridge,
            "asset": prism_asset,
            "ledger": prism_ledger
        },
        "columbus": {}
    }

    config.NetWork.append(config_0)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='''
    You can use this tool to initialize Columbus Project and Prism Project. Here are two ways:
    1. If you have already prepared Prism project in Findroa chain. You can specify arguments to the `columbus` subcommand to initialize Columbus.
    2. You can also specify arguments to the `prism` subcommand to initialize Prism. Then run the `columbus` subcommand with default arguments to initialize Columbus.
    ''')
    subparsers = parser.add_subparsers(dest='InitFindora SubCommand')
    subparsers.required = True

    parser_columbus = subparsers.add_parser('columbus', help='Init Columbus Project in Findora Privacy Network')
    parser_columbus.add_argument('--provider', help='Findora Privacy Network Provider')
    parser_columbus.add_argument('--prism-bridge', help='PrismXXBridge Contract Address')
    parser_columbus.add_argument('--prism-asset', help='PrismXXAsset Contract Address')
    parser_columbus.add_argument('--prism-ledger', help='PrismXXLedger Contract Address')
    parser_columbus.set_defaults(func=func_columbus)

    parser_prism = subparsers.add_parser('prism', help='Init Prism Project in Findora Privacy Network')
    parser_prism.add_argument('--provider', help='Findora Privacy Network Provider', required=True)
    parser_prism.add_argument('--prism-bridge', help='PrismXXBridge Contract Address', required=True)
    parser_prism.set_defaults(func=func_prism)

    args = parser.parse_args()

    args.func(args)
    config.save()