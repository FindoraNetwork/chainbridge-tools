# coding=utf-8

from config import *
from util import *

from web3 import Web3

def set_RelayerThreshold(w3, bridge_contract):
    print("{} _relayerThreshold: {}".format(bridge_contract.address, bridge_contract.functions._relayerThreshold().call()))

    func = bridge_contract.functions.adminChangeRelayerThreshold(2)
    sign_send_wait(w3, func)

    print("{} _relayerThreshold: {}".format(bridge_contract.address, bridge_contract.functions._relayerThreshold().call()))


for n in config.NetWork:
    print(n['name'])
    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    bridge_address = n["bridge"]
    bridge_contract = w3.eth.contract(bridge_address, abi=load_abi('Bridge'))

    set_RelayerThreshold(w3, bridge_contract)