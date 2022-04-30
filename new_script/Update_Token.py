#!/usr/bin/env python3
# coding=utf-8

from unicodedata import decimal
from web3 import Web3
import base64

from config import *
from util import *

from Add_Token import Findora_w3, get_decimals, adminSetAssetMaping, adminSetTokenId_uni

def assetInfos(_frc20):
    n, w3 = Findora_w3()

    prism_asset_abi = load_abi("PrismXXAsset")
    prism_asset_contract = w3.eth.contract(n['prism']['asset'], abi=prism_asset_abi)

    result = prism_asset_contract.functions.assetInfos(_frc20).call()
    result.append(_frc20)
    return result

def tokenAddress_uni(tokenId, isPrivacy, network_name=None):
    if not isPrivacy:
        n_id, n = config.get_Network(network_name)
        w3 = Web3(Web3.HTTPProvider(n['Provider']))

        columbus_asset_abi = load_abi("ColumbusAsset")
        columbus_asset_address = n['columbus']['asset']
        columbus_asset_contract = w3.eth.contract(columbus_asset_address, abi=columbus_asset_abi)

        result = columbus_asset_contract.functions.tokenAddress(tokenId).call()

    else:
        n, w3 = Findora_w3()

        columbus_wrap_abi = load_abi("ColumbusWrap")
        columbus_wrap_address = n['columbus']['wrap']
        columbus_wrap_contract = w3.eth.contract(columbus_wrap_address, abi=columbus_wrap_abi)

        result = columbus_wrap_contract.functions.tokenAddress(tokenId).call()

    result.insert(0, tokenId)
    return result

def func_update_lock(args):
    t_id, t = config.get_Token(args.name)

    old_address= t["address"]["Findora"]
    new_address = args.address

    focus_print("Call PrismXXAsset.adminSetAssetMaping")
    print("Before: {}".format(assetInfos(old_address)))
    decimals = get_decimals(new_address)
    adminSetAssetMaping(new_address, t["asset"], False, decimals)
    print("After: {}".format(assetInfos(new_address)))

    focus_print("Call ColumbusWrap.adminSetTokenId")
    print("Before: {}".format(tokenAddress_uni(t_id, isPrivacy=True)))
    adminSetTokenId_uni(t_id, new_address, isPrivacy=True, isBurn=False)
    print("After: {}".format(tokenAddress_uni(t_id, isPrivacy=True)))

    config.Token[t_id-1]["address"]["Findora"] = new_address

def func_destination(args):
    t_id, t = config.get_Token(args.name)

    focus_print("Call ColumbusAsset.adminSetTokenId")
    print("Before: {}".format(tokenAddress_uni(t_id, isPrivacy=False, network_name=args.network)))
    adminSetTokenId_uni(t_id, args.address, isPrivacy=False, network_name=args.network, isBurn=args.burn)
    print("After: {}".format(tokenAddress_uni(t_id, isPrivacy=False, network_name=args.network)))

    config.Token[t_id-1]['address'][args.network] = args.address

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='Update_Token SubCommand')
    subparsers.required = True

    parser_privacy = subparsers.add_parser('privacy', help='Update_Token in Findora Privacy Network')
    parser_privacy.add_argument('name', help="The Token Name for exist Token (Must exist in the config!!!)")
    parser_privacy.add_argument('address', help="The New Address of exist Token")
    parser_privacy.set_defaults(func=func_update_lock)

    parser_destination = subparsers.add_parser('destination', help="Update_Token in Destination Network")
    parser_destination.add_argument('network', help="Specific Network Name (Must exist in the config!!!)")
    parser_destination.add_argument('name', help="Specific Token Name (Must exist in the config!!!)")
    parser_destination.add_argument('address', help="The Address of Specific Token in Specific Network")
    parser_destination.add_argument('--burn', help="isBurn Flag", action='store_true')
    parser_destination.set_defaults(func=func_destination)

    args = parser.parse_args()

    config.check_0_exist()
    args.func(args)
    config.save()