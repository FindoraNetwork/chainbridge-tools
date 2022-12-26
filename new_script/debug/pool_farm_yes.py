# coding=utf-8

from web3 import Web3

from config import *
from util import *

from Add_Network import Farm_Function_Library, Pool_setColumbus
from Add_Token import adminSetTokenId_501, adminSetTokenId_dest
from Add_Liquidity import LP_addMarket, LP_addLiquidity, LP_setFeeShare, Farm_add

for n in config.NetWork:
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    if n['name'] == 'Findora':
        pool_address = n['columbus']["chain501"]['pool']
        _addr = n['columbus']["chain501"]['relayer']
    else:
        pool_address = n['columbus']['pool']
        _addr = n['columbus']['deck']
    
    pool_address = deployColumbusPool(w3)

    if n['name'] == 'Findora':
        relayer_address = n['columbus']["chain501"]['relayer']
        Pool_setColumbus(w3, pool_address, relayer_address)
        Relayer_setColumbusPool(w3, relayer_address, pool_address)
        n['columbus']["chain501"]['pool'] = pool_address

    else:
        deck_address = n['columbus']['deck']
        Pool_setColumbus(w3, pool_address, deck_address)
        Deck_setColumbusPool(w3, deck_address, pool_address)
        n['columbus']['pool'] = pool_address

    print("{} Pool: {}".format(n['name'], pool_address))

    yes_address, farm_address = Farm_Function_Library(w3, 10, 1667390042, 1957330800, pool_address)

    n['columbus']['yes'] = yes_address
    n['columbus']['farm'] = farm_address
    config.save()


# --------------------------

    yes_address = n['columbus']['yes']
    focus_print("Call ColumbusAsset.adminSetTokenId")
    t_id, _ = config.get_Token("YES")
    if n['name'] == 'Findora':
        adminSetTokenId_501(t_id, yes_address, False)
    else:
        adminSetTokenId_dest(t_id, yes_address, network_name=n['name'], isBurn=False)
    config.Token[t_id-1]['address'][n['name']] = yes_address
    config.save()

# --------------------------

    farm_address = n["columbus"]["farm"]
    n_name = n['name']
    amount = 4000000
    for t in config.Token:
        t_name = t['name']
        if not n_name in t['address']:
            continue

        token_address = t['address'][n_name]
        token_contract = w3.eth.contract(token_address, abi=load_abi('YESToken'))
        decimals = token_contract.functions.decimals().call()
        DECIMALS = 10 ** decimals

        func = token_contract.functions.mint(load_owner().address, amount*2*DECIMALS)
        tx_hash = sign_send_wait(w3, func)
        print("{} {} Mint transaction hash: {}".format(n_name, t_name, tx_hash.hex()))

        LP_address = pool_address
        CToken_address = t['cToken'][n_name]
        focus_print("CToken.adminSetMinter To LP")
        adminSetMinter_LP(w3, CToken_address, LP_address)

        focus_print("Call LP.addMarket")
        minAdd = 100 * (10 ** (decimals-6))
        minFee = 60
        fixedFee = 10 * (10 ** (decimals-6))
        LP_addMarket(w3, LP_address, token_address, CToken_address, minAdd, minFee, fixedFee) # 100 60 10

        focus_print("Farm_add new lpToken")
        lpToken_address = CToken_address
        Farm_add(w3, farm_address, 100, lpToken_address)

        focus_print("Call LP.addLiquidity")
        LP_addLiquidity(w3, LP_address, token_address, amount)

    # 0: Provider, 1: Platform, 2: Contributor
    # --Provider 6000 --Platform 2500 --Contributor 1500
    focus_print("Call LP.setFeeShare To Provider")
    LP_setFeeShare(w3, LP_address, 0, 6000)
    focus_print("Call LP.setFeeShare To Platform")
    LP_setFeeShare(w3, LP_address, 1, 2500)
    focus_print("Call LP.setFeeShare To Contributor")
    LP_setFeeShare(w3, LP_address, 2, 1500)
