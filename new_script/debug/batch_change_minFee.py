# coding=utf-8

from config import *
from util import *

from web3 import Web3

for n in config.NetWork:
    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    n_name = n['name']

    if n_name == 'Findora':
        LP_address = n['columbus']["chain501"]['relayer']
    else:
        LP_address = n['columbus']['deck']

    LP_contract = w3.eth.contract(LP_address, abi=load_abi('ColumbusPool'))

    for t in config.Token:
        if n_name in t['address'].keys():
            token_address = t['address'][n_name]
            minFee = LP_contract.functions.minFee(token_address).call()
            print("{} {} minFee {}".format(n_name, t['name'], minFee))
            func = LP_contract.functions.setFee(token_address, 60)
            sign_send_wait(w3, func)
            minFee = LP_contract.functions.minFee(token_address).call()
            print("{} {} minFee {}".format(n_name, t['name'], minFee))