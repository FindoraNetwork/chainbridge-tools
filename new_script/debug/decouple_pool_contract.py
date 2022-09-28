# coding=utf-8

from config import *
from util import *

from web3 import Web3

from Add_Network import deployColumbusPool, Pool_setColumbus, Deck_setColumbusPool
from InitFindora import Relayer_setColumbusPool

for n in config.NetWork:
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    pool_address = deployColumbusPool(w3)

    if n['name'] == 'Findora':
        # 301 standalone
        upgradeable_Update(w3, n['columbus']["chain301"]['relayer'], "ColumbusRelayer")

        relayer_address = n['columbus']["chain501"]['relayer']
        upgradeable_Update(w3, relayer_address, "ColumbusRelayer")
        Pool_setColumbus(w3, pool_address, relayer_address)
        Relayer_setColumbusPool(w3, relayer_address, pool_address)
        n['columbus']["chain501"]['pool'] = pool_address

    else:
        deck_address = n['columbus']['deck']
        upgradeable_Update(w3, deck_address, "ColumbusDeck")
        Pool_setColumbus(w3, pool_address, deck_address)
        Deck_setColumbusPool(w3, deck_address, pool_address)
        n['columbus']['pool'] = pool_address

    print("{} Pool: {}".format(n['name'], pool_address))

    config.save()

# --------------------------

from Add_Liquidity import adminSetMinter_LP, LP_addMarket, LP_addLiquidity, LP_setFeeShare

amount = 8000000

for n in config.NetWork:
    n_name = n['name']
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    for t in config.Token:
        t_name = t['name']
        if not n_name in t['address']:
            continue

        token_address = t['address'][n_name]
        token_contract = w3.eth.contract(token_address, abi=load_abi('ColumbusToken'))
        decimals = token_contract.functions.decimals().call()
        DECIMALS = 10 ** decimals

        if t_name != 'YES': # Fuck Farm!
            func = token_contract.functions.mint(load_owner().address, amount*DECIMALS)
            tx_hash = sign_send_wait(w3, func)
            print("{} {} Mint transaction hash: {}".format(n_name, t_name, tx_hash.hex()))

        if n_name == 'Findora':
            LP_address = n['columbus']["chain501"]['pool']
        else:
            LP_address = n['columbus']['pool']

        CToken_address = t['cToken'][n_name]
        focus_print("CToken.adminSetMinter To LP")
        adminSetMinter_LP(w3, CToken_address, LP_address)

        focus_print("Call LP.addMarket")
        minAdd = 100 * (10 ** (decimals-6))
        minFee = 60
        fixedFee = 10 * (10 ** (decimals-6))
        LP_addMarket(w3, LP_address, token_address, CToken_address, minAdd, minFee, fixedFee) # 100 60 10

        if t_name != 'YES': # Fuck Farm!
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

# --------------------------

for n in config.NetWork:
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    func_list = []

    if n['name'] == 'Findora':
        relayer_301 = w3.eth.contract(n['columbus']['chain301']['relayer'], abi=load_abi("ColumbusRelayer"))
        func_list.append(relayer_301.functions.adminSetBridgeAddress(n['bridge']))
        func_list.append(relayer_301.functions.adminSetColumbusAssetAddress(n['columbus']['chain301']['asset']))
        func_list.append(relayer_301.functions.adminSetGenericHandler(n['handler']))
        func_list.append(relayer_301.functions.adminSetGenericHandlerResourceId(resourceID_301))
        func_list.append(relayer_301.functions.adminSetPrismAddress(n['prism']['bridge']))
        func_list.append(relayer_301.functions.adminSetPrismLedgerAddress(n['prism']['ledger']))

        relayer_501 = w3.eth.contract(n['columbus']['chain501']['relayer'], abi=load_abi("ColumbusRelayer"))
        func_list.append(relayer_501.functions.adminSetBridgeAddress(n['bridge']))
        func_list.append(relayer_501.functions.adminSetColumbusAssetAddress(n['columbus']['chain501']['asset']))
        func_list.append(relayer_501.functions.adminSetGenericHandler(n['handler']))
        func_list.append(relayer_501.functions.adminSetGenericHandlerResourceId(resourceID_501))
        func_list.append(relayer_501.functions.adminSetPrismAddress(n['prism']['bridge']))
        func_list.append(relayer_501.functions.adminSetPrismLedgerAddress(n['prism']['ledger']))

        
    else:
        deck = w3.eth.contract(n['columbus']['deck'], abi=load_abi("ColumbusDeck"))
        func_list.append(deck.functions.adminSetGenericHandler(n['handler']))
        func_list.append(deck.functions.adminColumbusAssetAddress(n['columbus']['asset']))

    print('\n'+n['name'])
    for func in func_list:
        print(sign_send_wait(w3, func).hex())