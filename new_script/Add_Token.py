#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3

from config import *
from util import *

def Findora_w3():
    # In Findora Network, Index 0
    n = config.NetWork[0]
    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    return (n, w3)


def adminSetTokenId_dest(tokenId, tokenAddress, network_name, isBurn=False):
    _, n = config.get_Network(network_name)
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    columbus_asset_abi = load_abi("ColumbusAsset")
    columbus_asset_address = n['columbus']['asset']
    columbus_asset_contract = w3.eth.contract(columbus_asset_address, abi=columbus_asset_abi)

    func = columbus_asset_contract.functions.adminSetTokenId(tokenId, tokenAddress, isBurn)

    tx_hash = sign_send_wait(w3, func)
    print("{} adminSetTokenId {} transaction hash: {}".format(n['name'], tokenAddress, tx_hash.hex()))

def adminSetTokenId_301(tokenId, tokenAddress):
    isBurn = True
    n, w3 = Findora_w3()

    columbus_asset_abi = load_abi("ColumbusAsset")
    columbus_asset_address = n['columbus']["chain301"]['asset']
    columbus_asset_contract = w3.eth.contract(columbus_asset_address, abi=columbus_asset_abi)

    func = columbus_asset_contract.functions.adminSetTokenId(tokenId, tokenAddress, isBurn)

    tx_hash = sign_send_wait(w3, func)
    print("Findora 301 adminSetTokenId {} transaction hash: {}".format(tokenAddress, tx_hash.hex()))

def adminSetTokenId_501(tokenId, tokenAddress, isFRA=False):
    isBurn = False
    n, w3 = Findora_w3()

    columbus_asset_abi = load_abi("ColumbusAsset")
    columbus_asset_address = n['columbus']["chain501"]['asset']
    columbus_asset_contract = w3.eth.contract(columbus_asset_address, abi=columbus_asset_abi)

    if not isFRA:
        func = columbus_asset_contract.functions.adminSetTokenId(tokenId, tokenAddress, isBurn)
    else:
        tokenAddress = "0x0000000000000000000000000000000000000000"
        func = columbus_asset_contract.functions.adminSetFraTokenId(tokenId, tokenAddress, isFRA, isBurn)

    tx_hash = sign_send_wait(w3, func)
    print("Findora 501 adminSetTokenId {} transaction hash: {}".format(tokenAddress, tx_hash.hex()))

def deployWrapTokenContract(name, symbol, decimal):
    n, w3 = Findora_w3()
    _minter = n["prism"]["ledger"]
    return Deploy_Contract(w3, "WrapToken", (name, symbol, int(decimal), _minter))

def adminSetMinter_Relayer(wrap_address):
    n, w3 = Findora_w3()
    wrap_abi = load_abi("WrapToken")
    wrap_contract = w3.eth.contract(wrap_address, abi=wrap_abi)
    _minter = n["columbus"]["chain301"]["relayer"]
    func = wrap_contract.functions.adminSetMinter(_minter)
    tx_hash = sign_send_wait(w3, func)
    print("adminSetMinter {} transaction hash: {}".format(_minter, tx_hash.hex()))


def func_301(args):
    focus_print("Deployment wrapToken Contract")
    wrap_address = deployWrapTokenContract(args.name, args.symbol, args.decimal)
    focus_print("warpToken.adminSetMinter To ColumbusRelayer")
    adminSetMinter_Relayer(wrap_address)

    focus_print("Call ColumbusAsset.adminSetTokenId")
    # The reason is solidity mapping data structure
    # https://github.com/ysfinance/ys-contracts/blob/main/docs/qa02.md#tokenid
    tokenId = len(config.Token) + 1
    adminSetTokenId_301(tokenId, wrap_address)

    config.Token.append(
        {
            "name": args.name,
            "Wrap": wrap_address,
            "address": {}
        }
    )

def func_501(args):
    focus_print("Call ColumbusAsset.adminSetTokenId")
    # The reason is solidity mapping data structure
    # https://github.com/ysfinance/ys-contracts/blob/main/docs/qa02.md#tokenid
    t_id, _ = config.get_Token(args.name) # Get Flow 301 create tokenId
    adminSetTokenId_501(t_id, args.address, args.WFRA)

    # If add WFRA then must input WFRA address
    config.Token[t_id-1]['address']['Findora'] = args.address

def func_destination(args):
    t_id, _ = config.get_Token(args.name)

    focus_print("Call ColumbusAsset.adminSetTokenId")
    adminSetTokenId_dest(t_id, args.address, network_name=args.network, isBurn=args.burn)

    config.Token[t_id-1]['address'][args.network] = args.address


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='Add_Token SubCommand')
    subparsers.required = True

    parser_301 = subparsers.add_parser('301', help='Create New wrapToken in Privacy Network (Flow 301)')
    parser_301.add_argument('name', help="The Token Name for want to create wrapToken")
    parser_301.add_argument('symbol', help="wrapToken symbol")
    parser_301.add_argument('decimal', help="wrapToken decimal")
    parser_301.set_defaults(func=func_301)

    parser_501 = subparsers.add_parser('501', help='Maping exist Token in Privacy Network (Flow 501)')
    parser_501.add_argument('name', help="The Token Name for exist Token (Must exist in the config!!!)")
    parser_501.add_argument('address', help="The Address of exist Token. If add WFRA then must input WFRA address!!!")
    parser_501.add_argument('--WFRA', help="WFRA Flag", action='store_true')
    parser_501.set_defaults(func=func_501)

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