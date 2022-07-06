#!/usr/bin/env python3
# coding=utf-8

from web3 import Web3

from config import *
from util import *

def deployCTokenContract(w3, token_address):
    erc20_abi = load_abi("ERC20")
    token_contract = w3.eth.contract(token_address, abi=erc20_abi)
    name = "c"+token_contract.functions.name().call() 
    symbol = token_contract.functions.symbol().call()
    decimals = token_contract.functions.decimals().call()

    return Deploy_Contract(w3, "CToken", (name, symbol, int(decimals), load_owner().address))

def adminSetMinter_LP(w3, CToken_address, LP_address):
    CToken_contract = w3.eth.contract(CToken_address, abi=load_abi("CToken"))
    func = CToken_contract.functions.adminSetMinter(LP_address)
    tx_hash = sign_send_wait(w3, func)
    print("adminSetMinter {} transaction hash: {}".format(LP_address, tx_hash.hex()))

def LP_setWrap(w3, LP_address, WFRA_address):
    LP_contract = w3.eth.contract(LP_address, abi=load_abi('ColumbusPool'))
    func = LP_contract.functions.setWrap(WFRA_address)
    tx_hash = sign_send_wait(w3, func)
    print("LP_setWrap {} transaction hash: {}".format(WFRA_address, tx_hash.hex()))

def LP_addMarket(w3, LP_address, _token, _cToken, _minAdd, _fee, _fixedFee):
    LP_contract = w3.eth.contract(LP_address, abi=load_abi('ColumbusPool'))
    func = LP_contract.functions.addMarket(_token, _cToken, int(_minAdd), int(_fee), int(_fixedFee))
    tx_hash = sign_send_wait(w3, func)
    print("LP_addMarket {} transaction hash: {}".format(_token, tx_hash.hex()))

def LP_addLiquidity(w3, LP_address, token_address, amount):
    erc20_abi = load_abi("ERC20")
    token_contract = w3.eth.contract(token_address, abi=erc20_abi)
    decimals = token_contract.functions.decimals().call()
    DECIMALS = 10 ** decimals
    
    func = token_contract.functions.approve(LP_address, int(amount)*DECIMALS)
    tx_hash = sign_send_wait(w3, func)
    print("Approve transaction hash: {}".format(tx_hash.hex()))

    LP_contract = w3.eth.contract(LP_address, abi=load_abi('ColumbusPool'))
    func = LP_contract.functions.addLiquidity(token_address, int(amount)*DECIMALS)
    tx_hash = sign_send_wait(w3, func)
    print("LP_addLiquidity {} transaction hash: {}".format(token_address, tx_hash.hex()))

def LP_addNativeLiquidity(w3, LP_address, amount):
    _amount = int(amount) * 10**18
    LP_contract = w3.eth.contract(LP_address, abi=load_abi('ColumbusPool'))
    func = LP_contract.functions.addNativeLiquidity(_amount)
    tx_hash = sign_send_wait(w3, func, value=_amount)
    print("LP_addNativeLiquidity transaction hash: {}".format(tx_hash.hex()))

def LP_setFeeShare(w3, LP_address, _kind, _point):
    LP_contract = w3.eth.contract(LP_address, abi=load_abi('ColumbusPool'))
    func = LP_contract.functions.setFeeShare(_kind, _point)
    tx_hash = sign_send_wait(w3, func)
    print("LP_setFeeShare kind {} transaction hash: {}".format(_kind, tx_hash.hex()))


def func_add(w3, LP_address, args):
    _, t = config.get_Token(args.name)
    token_address = t['address'][args.network]

    focus_print("Deployment CToken Contract")
    CToken_address = deployCTokenContract(w3, token_address)
    focus_print("CToken.adminSetMinter To LP")
    adminSetMinter_LP(w3, CToken_address, LP_address)

    focus_print("Call LP.addMarket")
    LP_addMarket(w3, LP_address, token_address, CToken_address, args.minAdd, args.minFee, args.fixedFee)

    if args.nativeWrap:
        focus_print("Call LP.setWrap")
        LP_setWrap(w3, LP_address, token_address) # token_address == WFRA address

    if not "cToken" in t:
        t["cToken"] = {}
    t["cToken"][args.network] = CToken_address

    config.save()

    if args.amount != None:
        focus_print("Call LP.addLiquidity")
        if args.nativeWrap:
            LP_addNativeLiquidity(w3, LP_address,args.amount)
        else:
            LP_addLiquidity(w3, LP_address, token_address, args.amount)

def func_setFeeShare(w3, LP_address, args):
    # 1: Provider, 2: Platform, 3: Contributor
    if args.Provider != None:
        focus_print("Call LP.setFeeShare To Provider")
        LP_setFeeShare(w3, LP_address, 1, int(args.Provider))
    if args.Platform != None:
        focus_print("Call LP.setFeeShare To Platform")
        LP_setFeeShare(w3, LP_address, 2, int(args.Platform))
    if args.Contributor != None:
        focus_print("Call LP.setFeeShare To Contributor")
        LP_setFeeShare(w3, LP_address, 3, int(args.Contributor))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='Add_Liquidity SubCommand')
    subparsers.required = True

    parser_add = subparsers.add_parser('add', help='Add new Token to the Market.')
    parser_add.add_argument('network', help="Specific Network Name (Must exist in the config!!!)")
    parser_add.add_argument('name', help="Specific Token Name (Must exist in the config!!!)")
    parser_add.add_argument('minAdd', help="set add liquidity min amount. Unit wei.")
    parser_add.add_argument('minFee', help="set liquidity fee. Unit wei.")
    parser_add.add_argument('fixedFee', help="set fixedFee. Unit wei.")
    parser_add.add_argument('--nativeWrap', help="nativeWrap Flag", action='store_true')
    parser_add.add_argument('--amount', help="Optional. then add token to liquidity. Unit ether.")
    parser_add.set_defaults(func=func_add)

    parser_setFeeShare = subparsers.add_parser('setFeeShare', help='Set the point for allocate fees.')
    parser_setFeeShare.add_argument('network', help="Specific Network Name (Must exist in the config!!!)")
    parser_setFeeShare.add_argument('--Provider', help="allocated point For Provider")
    parser_setFeeShare.add_argument('--Platform', help="allocated point For Platform")
    parser_setFeeShare.add_argument('--Contributor', help="allocated point For Contributor.")
    parser_setFeeShare.set_defaults(func=func_setFeeShare)

    args = parser.parse_args()

    config.check_0_exist()

    _, n = config.get_Network(args.network)
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    if args.network == 'Findora':
        LP_address = n['columbus']["chain501"]['relayer']
    else:
        LP_address = n['columbus']['deck']

    args.func(w3, LP_address, args)
