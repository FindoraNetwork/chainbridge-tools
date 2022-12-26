# coding=utf-8

from config import *
from util import *

from web3 import Web3

def display_resourceIDToHandlerAddress(w3, bridge_contract):
    print("{} _resourceIDToHandlerAddress: {}".format(bridge_contract.address, bridge_contract.functions._resourceIDToHandlerAddress(resourceID_301).call()))
    print("{} _resourceIDToHandlerAddress: {}".format(bridge_contract.address, bridge_contract.functions._resourceIDToHandlerAddress(resourceID_501).call()))

def display_resourceIDToContractAddress(w3, handler_contract):
    print("{} _resourceIDToHandlerAddress: {}".format(handler_contract.address, handler_contract.functions._resourceIDToContractAddress(resourceID_301).call()))
    print("{} _resourceIDToHandlerAddress: {}".format(handler_contract.address, handler_contract.functions._resourceIDToContractAddress(resourceID_501).call()))

def display_totalRelayers(w3, bridge_contract):
    print("{} _totalRelayers: {}".format(bridge_contract.address, bridge_contract.functions._totalRelayers().call()))


for n in config.NetWork:
    print(n['name'])
    w3 = Web3(Web3.HTTPProvider(n['Provider']))
    bridge_address = n["bridge"]
    bridge_contract = w3.eth.contract(bridge_address, abi=load_abi('Bridge'))
    handler_address = n["handler"]
    handler_contract = w3.eth.contract(handler_address, abi=load_abi('GenericHandler'))

    display_resourceIDToHandlerAddress(w3, bridge_contract)
    display_resourceIDToContractAddress(w3, handler_contract)
    display_totalRelayers(w3, bridge_contract)
