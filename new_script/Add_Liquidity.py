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

def LP_addMarket(w3, LP_address, _token, _cToken, _minAdd, _fee):
    LP_contract = w3.eth.contract(LP_address, abi=load_abi('ColumbusPool'))
    func = LP_contract.functions.addMarket(_token, _cToken, int(_minAdd), int(_fee))
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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('network', help="Specific Network Name (Must exist in the config!!!)")
    parser.add_argument('name', help="Specific Token Name (Must exist in the config!!!)")
    parser.add_argument('minAdd', help="set add liquidity min amount. Unit wei.")
    parser.add_argument('minFee', help="set liquidity fee. Unit wei.")
    parser.add_argument('--nativeWrap', help="nativeWrap Flag", action='store_true')
    parser.add_argument('--amount', help="Optional. then add token to liquidity. Unit ether.")
    args = parser.parse_args()

    config.check_0_exist()

    _, n = config.get_Network(args.network)
    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    _, t = config.get_Token(args.name)
    token_address = t['address'][args.network]

    if args.network == 'Findora':
        LP_address = n['columbus']["chain501"]['relayer']
    else:
        LP_address = n['columbus']['deck']

    focus_print("Deployment CToken Contract")
    CToken_address = deployCTokenContract(w3, token_address)
    focus_print("CToken.adminSetMinter To LP")
    adminSetMinter_LP(w3, CToken_address, LP_address)

    focus_print("Call LP.addMarket")
    LP_addMarket(w3, LP_address, token_address, CToken_address, args.minAdd, args.minFee)

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