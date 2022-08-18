# coding=utf-8

from config import *
from util import *

from web3 import Web3
import os

def LP_setFeeAdmin(w3, LP_contract):
    admin=load_owner().address
    func = LP_contract.functions.setFeeAdmin(admin)
    tx_hash = sign_send_wait(w3, func)
    print("LP_setFeeAdmin {} transaction hash: {}".format(admin, tx_hash.hex()))

def LP_setMinAdd(w3, LP_contract, token_address, minAdd):
    func = LP_contract.functions.setMinAdd(token_address, minAdd)
    tx_hash = sign_send_wait(w3, func)
    print("LP_setMinAdd {} transaction hash: {}".format(token_address, tx_hash.hex()))

def LP_setFixedFee(w3, LP_contract, token_address, fixedFee):
    func = LP_contract.functions.setFixedFee(token_address, fixedFee)
    tx_hash = sign_send_wait(w3, func)
    print("LP_setFixedFee {} transaction hash: {}".format(token_address, tx_hash.hex()))


for n in config.NetWork:
    w3 = Web3(Web3.HTTPProvider(n['Provider']))

    if n['name'] == 'Findora':
        LP_address = n['columbus']["chain501"]['relayer']
        contract_name = "ColumbusRelayer"
    else:
        LP_address = n['columbus']['deck']
        contract_name = "ColumbusDeck"
    LP_contract = w3.eth.contract(LP_address, abi=load_abi(contract_name))

    n_name = n['name']
    print(n_name)
    LP_setFeeAdmin(w3, LP_contract)

    for t in config.Token:
        if n_name in t['address']:
            t_name, token_address = t['name'], t['address'][n_name]
            token_contract = w3.eth.contract(token_address, abi=load_abi("ERC20"))
            decimals = token_contract.functions.decimals().call()
            delta_decimal = decimals - 6

            minAdd = LP_contract.functions.minAdd(token_address).call()
            fixedFee = LP_contract.functions.fixedFee(token_address).call()

            if ( minAdd / 10 ) < delta_decimal or ( fixedFee / 10 ) < delta_decimal:
                print("{}\t{}\t{}".format(t_name, minAdd, fixedFee))

                minAdd = 100 * (10 ** delta_decimal)
                fixedFee = 10 * (10 ** delta_decimal)
                LP_setMinAdd(w3, LP_contract, token_address, minAdd)
                LP_setFixedFee(w3, LP_contract, token_address, fixedFee)
