#!/usr/bin/env python3
# coding=utf-8

import json
from web3 import Web3

from config import *
from util import *

def adminSetResource(n, tokenAddress):
    with open("contracts/Bridge.json") as f:
        bridge_abi = json.load(f)['abi']

    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    bridge_address = n['bridge']
    bridge_contract = w3.eth.contract(bridge_address, abi=bridge_abi)

    func = bridge_contract.functions.adminSetResource(n['handler'], uni_resourceID, tokenAddress)
    tx_hash = sign_send_wait(w3, func)
    print("{} adminSetResource {} transaction hash: {}".format(n['name'], tokenAddress, tx_hash.hex()))

def adminSetTokenId(n, tokenId, tokenAddress, isBurn):
    with open("contracts/ColumbusAsset.json") as f:
        asset_abi = json.load(f)['abi']

    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    asset_address = n['asset']
    asset_contract = w3.eth.contract(asset_address, abi=asset_abi)

    func = asset_contract.functions.adminSetResource(tokenId, tokenAddress, isBurn)
    tx_hash = sign_send_wait(w3, func)
    print("{} adminSetTokenId {} transaction hash: {}".format(n['name'], tokenAddress, tx_hash.hex()))

def deployWarpTokenContract(w3, contract_json_path):
    return Deploy_Contract(w3, contract_json_path, ())

def fn_asset_create(memo, decimal):
    import os
    import base64

    endpoint = config.NetWork[0]['Provider'].split('8545')[0][:-1]
    os.popen("fn setup --owner-mnemonic-path {} --serv-addr {} 2>/dev/null".format(mnemonic_file_path, endpoint)).read()

    # code format: base64(bytes32("warpToken0000000000000000000Name"))
    code = base64.b64encode(bytes("warpToken"+memo.zfill(23), encoding='utf-8'))
    os.popen("fn asset --create --memo {} --decimal {} --code {} --transferable 2>/dev/null".format(mnemonic_file_path, decimal, code)).read()
    return code

def adminSetAssetMaping(w3, prism_address, _frc20, _asset, _isBurn, _decimal):
    with open("contracts/PrismXXAsset.json") as f:
        prism_abi = json.load(f)['abi']

    prism_contract = w3.eth.contract(prism_address, abi=prism_abi)

    func = prism_contract.functions.adminSetAssetMaping(_frc20, _asset, _isBurn, _decimal)
    tx_hash = sign_send_wait(w3, func)
    print("adminSetAssetMaping {} transaction hash: {}".format(_frc20, tx_hash.hex()))


def func_warptoken(args):
    # In Findora Network, Index 0
    n = config.NetWork[0]
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    focus_print("Deployment WarpToken Contract")
    warp_address = deployWarpTokenContract(w3, args.contract_json_path)

    with open(args.contract_json_path) as f:
        warp_abi = json.load(f)['abi']
    warp_contract = w3.eth.contract(warp_address, abi=warp_abi)
    decimals = warp_contract.functions.decimals().call()

    focus_print("Run fn asset create")
    asset_code = fn_asset_create(args.name, decimals)

    focus_print("Call PrismXXAsset.adminSetAssetMaping")
    adminSetAssetMaping(w3, n['prism'], warp_address, asset_code, True, decimals)

    config.Token.append(
        {
            "name": args.name,
            "warp": warp_address,
            "asset": asset_code,
            "address": {}
        }
    )


def func_token(args):
    n_id, n = config.get_Network(args.network)
    t_id, t = config.get_Token(args.name)

    focus_print("Call Bridge.adminSetResource")
    adminSetResource(n, args.address)
    focus_print("Call ColumbusAsset.adminSetTokenId")
    adminSetTokenId(n, t_id, args.address, args.burn)

    config.Token[t_id]['address'][args.network] = args.address


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='Add_Token SubCommand')
    subparsers.required = True

    parser_warptoken = subparsers.add_parser('warptoken', help='Create New warpToken in Privacy Network')
    parser_warptoken.add_argument('name', help="The Token Name for want to create wrapToken")
    parser_warptoken.add_argument('contract_json_path', help="warpToken Contract compiled json file path")
    parser_warptoken.set_defaults(func=func_warptoken)

    parser_token = subparsers.add_parser('token', help="manual input Token Address for one Network")
    parser_token.add_argument('network', help="Specific Network Name (Must exist in the config!!!)")
    parser_token.add_argument('name', help="Specific Token Name (Must exist in the config!!!)")
    parser_token.add_argument('address', help="The Address of Specific Token in Specific Network")
    parser_token.add_argument('--burn', help="isBurn Flag", action='store_true')
    parser_token.set_defaults(func=func_token)

    args = parser.parse_args()

    config = Deploy_Config()
    args.func(args)
    config.save()
