#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3

from config import *
from util import *

from Add_Network import deployBridgeContract, deployGenericHandler, deployColumbusAsset, deployColumbusPool, Pool_setColumbus

def deployColumbusRelayer(w3, _genericHandlerAddress, _prismxxBridgeAddress, _prismLedgerAddress, _columbusAssetAddress, _bridgeAddress, resourceID):
    _genericHandlerResourceId = resourceID
    return upgradeable_Deploy(w3, "ColumbusRelayer", (
        _genericHandlerAddress,
        _prismxxBridgeAddress,
        _prismLedgerAddress,
        _columbusAssetAddress,
        _genericHandlerResourceId,
        _bridgeAddress
    ))

def Relayer_setColumbusPool(w3, relayer_address, _addr):
    relayer_abi = load_abi("ColumbusRelayer")
    relayer_contract = w3.eth.contract(relayer_address, abi=relayer_abi)

    func = relayer_contract.functions.setColumbusPool(_addr)
    tx_hash = sign_send_wait(w3, func)
    print("Relayer_setColumbusPool {} transaction hash: {}".format(_addr, tx_hash.hex()))

def deployColumbusSimBridge(w3, _prismBridgeAddress, _prismBridgeLedger):
    return upgradeable_Deploy(w3, "ColumbusSimBridge", (_prismBridgeAddress, _prismBridgeLedger))

def adminSetGenericResource_Privacy(w3, bridge_address, handler_address, columbus_relayer_address, resourceID):
    bridge_abi = load_abi("Bridge")
    bridge_contract = w3.eth.contract(bridge_address, abi=bridge_abi)

    func = bridge_contract.functions.adminSetGenericResource(
        handler_address,
        resourceID,
        columbus_relayer_address,
        load_functionSig("ColumbusRelayer","withdrawToOtherChainCallback"),
        load_functionSig("ColumbusRelayer","depositFromOtherChain")
    )
    tx_hash = sign_send_wait(w3, func)
    print("adminSetGenericResource {} transaction hash: {}".format(columbus_relayer_address, tx_hash.hex()))

def deployPrismXXBridge(w3, _proxy_contract):
    return Deploy_Contract(w3, "PrismXXBridge", (_proxy_contract,))

def deployPrismXXAsset(w3, _bridge):
    return upgradeable_Deploy(w3, "PrismXXAsset", (_bridge,))

def deployPrismXXLedger(w3, _bridge, _asset):
    return upgradeable_Deploy(w3, "PrismXXLedger", (_bridge, _asset))

def Set_PrismProxy(w3, prism_proxy_address, _prismBridgeAddress):
    prism_proxy_abi = load_abi("PrismProxy")
    prism_proxy_contract = w3.eth.contract(prism_proxy_address, abi=prism_proxy_abi)

    func = prism_proxy_contract.functions.adminSetPrismBridgeAddress(_prismBridgeAddress)
    tx_hash = sign_send_wait(w3, func)
    print("adminSetPrismBridgeAddress {} transaction hash: {}".format(_prismBridgeAddress, tx_hash.hex()))

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

    focus_print("301 Deployment ColumbusAsset Contract")
    asset_address_301 = deployColumbusAsset(w3)
    focus_print("301 Deployment ColumbusRelayer Contract (upgradeable)")
    relayer_address_301 = deployColumbusRelayer(w3, handler_address, prism_bridge, prism_ledger, asset_address_301, bridge_address, resourceID_301)

    focus_print("501 Deployment ColumbusAsset Contract")
    asset_address_501 = deployColumbusAsset(w3)
    focus_print("501 Deployment ColumbusPool Contract (upgradeable)")
    pool_address_501 = deployColumbusPool(w3)
    focus_print("501 Deployment ColumbusRelayer Contract (upgradeable)")
    relayer_address_501 = deployColumbusRelayer(w3, handler_address, prism_bridge, prism_ledger, asset_address_501, bridge_address, resourceID_501)
    focus_print("501 Call Pool.setColumbus")
    Pool_setColumbus(w3, pool_address_501, relayer_address_501)
    focus_print("501 Call Relayer.setColumbusPool")
    Relayer_setColumbusPool(w3, relayer_address_501, pool_address_501)
    focus_print("501 Deployment ColumbusSimBridge Contract (upgradeable)")
    simbridge_address_501 = deployColumbusSimBridge(w3, prism_bridge, prism_ledger)

    focus_print("301 Call Bridge.adminSetGenericResource")
    adminSetGenericResource_Privacy(w3, bridge_address, handler_address, relayer_address_301, resourceID_301)

    focus_print("501 Call Bridge.adminSetGenericResource")
    adminSetGenericResource_Privacy(w3, bridge_address, handler_address, relayer_address_501, resourceID_501)

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
            "chain301": {
                "asset": asset_address_301,
                "relayer": relayer_address_301
            },
            "chain501": {
                "asset": asset_address_501,
                "relayer": relayer_address_501,
                "pool": pool_address_501,
                "simbridge": simbridge_address_501
            }
        }
    }

    if len(config.NetWork) == 0:
        config.NetWork.append(config_0)
    else:
        config.NetWork[0] = config_0

def func_prism(args):
    provider = args.provider
    prism_proxy = args.prism_proxy

    w3 = Web3(Web3.HTTPProvider(provider))

    focus_print("Deployment PrismXXBridge Contract")
    prism_bridge = deployPrismXXBridge(w3, prism_proxy)
    focus_print("call PrismProxy.adminSetPrismBridgeAddress")
    Set_PrismProxy(w3, prism_proxy, prism_bridge)
    focus_print("Deployment PrismXXAsset Contract (upgradeable)")
    prism_asset = deployPrismXXAsset(w3, prism_bridge)
    focus_print("Deployment PrismXXLedger Contract (upgradeable)")
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
    parser_prism.add_argument('--prism-proxy', help='PrismProxy System Contract Address', required=True)
    parser_prism.set_defaults(func=func_prism)

    args = parser.parse_args()

    args.func(args)
    config.save()