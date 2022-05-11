#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3
import os
import base64

from config import *
from util import *

def Findora_w3():
    # In Findora Network, Index 0
    n = config.NetWork[0]
    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    return (n, w3)

def get_decimals(token_address):
    n, w3 = Findora_w3()
    erc20_abi = load_abi("ERC20")
    token_contract = w3.eth.contract(token_address, abi=erc20_abi)
    return token_contract.functions.decimals().call()

def adminSetTokenId_uni(tokenId, tokenAddress, network_name, isBurn=False, isFRA=False):
    n_id, n = config.get_Network(network_name)
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    columbus_asset_abi = load_abi("ColumbusAsset")
    columbus_asset_address = n['columbus']['asset']
    columbus_asset_contract = w3.eth.contract(columbus_asset_address, abi=columbus_asset_abi)

    if not isFRA:
        func = columbus_asset_contract.functions.adminSetTokenId(tokenId, tokenAddress, isBurn)
    else:
        func = columbus_asset_contract.functions.adminSetFraTokenId(tokenId, tokenAddress, isFRA, isBurn)

    tx_hash = sign_send_wait(w3, func)
    print("{} adminSetTokenId {} transaction hash: {}".format(n['name'], tokenAddress, tx_hash.hex()))

def deployWrapTokenContract(name, symbol, decimal):
    n, w3 = Findora_w3()
    _minter = n["prism"]["ledger"]
    return Deploy_Contract(w3, "WrapToken", (name, symbol, int(decimal), _minter))

def adminSetMinter_Relayer(wrap_address):
    n, w3 = Findora_w3()
    wrap_abi = load_abi("WrapToken")
    wrap_contract = w3.eth.contract(wrap_address, abi=wrap_abi)
    _minter = n["columbus"]["relayer"]
    func = wrap_contract.functions.adminSetMinter(_minter)
    tx_hash = sign_send_wait(w3, func)
    print("adminSetMinter {} transaction hash: {}".format(_minter, tx_hash.hex()))

def fn_asset_create(memo, decimal):
    endpoint = config.NetWork[0]['Provider'].split('8545')[0][:-1]
    os.popen("fn setup --owner-mnemonic-path {} --serv-addr {} 2>/dev/null".format(mnemonic_file_path, endpoint)).read()

    # code format: base64(bytes32("wrapToken0000000000000000000Name"))
    code = str(base64.b64encode(bytes("wrapToken"+memo.zfill(23), encoding='utf-8')), encoding='utf-8')
    os.popen("fn asset --create --memo {} --decimal {} --code {} --transferable 2>/dev/null".format(mnemonic_file_path, decimal, code)).read()
    return code

def adminSetAssetMaping(_frc20, _asset, _isBurn, _decimal):
    n, w3 = Findora_w3()

    prism_asset_abi = load_abi("PrismXXAsset")
    prism_asset_contract = w3.eth.contract(n['prism']['asset'], abi=prism_asset_abi)

    func = prism_asset_contract.functions.adminSetAssetMaping(_frc20, base64.b64decode(_asset), _isBurn, int(_decimal))
    tx_hash = sign_send_wait(w3, func)
    print("adminSetAssetMaping {} transaction hash: {}".format(_frc20, tx_hash.hex()))


def func_burn(args):
    focus_print("Deployment wrapToken Contract")
    wrap_address = deployWrapTokenContract(args.name, args.symbol, args.decimal)
    focus_print("warpToken.adminSetMinter To ColumbusRelayer")
    adminSetMinter_Relayer(wrap_address)

    focus_print("Run fn asset create")
    asset_code = fn_asset_create(args.name, args.decimal)

    focus_print("Call PrismXXAsset.adminSetAssetMaping")
    adminSetAssetMaping(wrap_address, asset_code, True, args.decimal)

    focus_print("Call ColumbusAsset.adminSetTokenId")
    # The reason is solidity mapping data structure
    # https://github.com/ysfinance/ys-contracts/blob/main/docs/qa02.md#tokenid
    tokenId = len(config.Token) + 1
    adminSetTokenId_uni(tokenId, wrap_address, network_name='Findora', isBurn=True)

    config.Token.append(
        {
            "name": args.name,
            "isWrap": True,
            "asset": asset_code,
            "address": {
                "Findora": wrap_address
            }
        }
    )

def func_lock(args):
    decimals = get_decimals(args.address)

    focus_print("Run fn asset create")
    asset_code = fn_asset_create(args.name, decimals)

    focus_print("Call PrismXXAsset.adminSetAssetMaping")
    adminSetAssetMaping(args.address, asset_code, False, decimals)

    focus_print("Call ColumbusAsset.adminSetTokenId")
    # The reason is solidity mapping data structure
    # https://github.com/ysfinance/ys-contracts/blob/main/docs/qa02.md#tokenid
    tokenId = len(config.Token) + 1
    adminSetTokenId_uni(tokenId, args.address, network_name='Findora', isBurn=False)

    config.Token.append(
        {
            "name": args.name,
            "isWrap": False,
            "asset": asset_code,
            "address": {
                "Findora": args.address
            }
        }
    )

def func_wFRA(args):
    focus_print("Call ColumbusAsset.adminSetTokenId")
    # The reason is solidity mapping data structure
    # https://github.com/ysfinance/ys-contracts/blob/main/docs/qa02.md#tokenid
    tokenId = len(config.Token) + 1
    adminSetTokenId_uni(tokenId, "0x0000000000000000000000000000000000000000", network_name='Findora', isBurn=False, isFRA=True)

    config.Token.append(
        {
            "name": "FRA",
            "address": {}
        }
    )

def func_destination(args):
    t_id, t = config.get_Token(args.name)

    focus_print("Call ColumbusAsset.adminSetTokenId")
    # adminSetTokenId_ColumbusAsset(n, t_id, args.address, args.burn)
    adminSetTokenId_uni(t_id, args.address, network_name=args.network, isBurn=args.burn)

    config.Token[t_id-1]['address'][args.network] = args.address


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='Add_Token SubCommand')
    subparsers.required = True

    parser_privacy = subparsers.add_parser('privacy', help='Init Findora Privacy Network')
    privacy_sub = parser_privacy.add_subparsers(dest="Add_Token Subcommand for Privacy Network")
    privacy_sub.required = True

    parser_burn = privacy_sub.add_parser('burn', help='Create New wrapToken in Privacy Network')
    parser_burn.add_argument('name', help="The Token Name for want to create wrapToken")
    parser_burn.add_argument('symbol', help="wrapToken symbol")
    parser_burn.add_argument('decimal', help="wrapToken decimal")
    parser_burn.set_defaults(func=func_burn)

    parser_wFRA = privacy_sub.add_parser('wFRA', help='If Add wFRA, Use this SubCommand.')
    parser_wFRA.set_defaults(func=func_wFRA)

    parser_lock = privacy_sub.add_parser('lock', help='Maping exist Token in Privacy Network')
    parser_lock.add_argument('name', help="The Token Name for exist Token")
    parser_lock.add_argument('address', help="The Address of exist Token")
    parser_lock.set_defaults(func=func_lock)

    parser_destination = subparsers.add_parser('destination', help="manual input Token Address for one Network")
    parser_destination.add_argument('network', help="Specific Network Name (Must exist in the config!!!)")
    parser_destination.add_argument('name', help="Specific Token Name (Must exist in the config!!!)")
    parser_destination.add_argument('address', help="The Address of Specific Token in Specific Network")
    parser_destination.add_argument('--burn', help="isBurn Flag", action='store_true')
    parser_destination.set_defaults(func=func_destination)

    args = parser.parse_args()

    config.check_0_exist()
    args.func(args)
    config.save()